import logging
import time
import uuid
import os
import asyncio
from pathlib import Path

from fastapi import FastAPI, UploadFile, Request, File, Query, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from convert_media import *


# Logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("media_converter")


app = FastAPI()

# Ensure exports directory exists
EXPORTS_DIR = Path("exports")
EXPORTS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/exports", StaticFiles(directory="exports"), name="exports")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["http://morfeu.like","http://192.168.1.100:2005"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/convert_media/")
async def convert_media_endpoint(
    file: UploadFile = File(...),
    output_format: str = Query(...)
):
    filename = sanitize_filename(file.filename)
    suffix = Path(filename).suffix.lower().lstrip('.')

    try:
        media_type = get_media_type(suffix)

        if output_format not in SUPPORTED_FORMATS["audio"] and output_format not in SUPPORTED_FORMATS["video"]:
            raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")

        converted = convert_media(file, output_format)

        mime = (
            f"audio/{output_format}" if output_format in SUPPORTED_FORMATS["audio"]
            else f"video/{output_format}"
        )

        logger.info(f"File received: {filename}")
        logger.info(f"File received Type: {media_type}")
        logger.info(f"Output format: {output_format}")
        logger.info(f"MIME type: {mime}")

        return StreamingResponse(
            converted,
            media_type=mime,
            headers={
                "Content-Disposition": f"attachment; filename={Path(filename).stem}.{output_format}"
            }
        )

    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error converting {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion error: {e}")


async def delete_file_after_delay(file_path: str, delay: int = 3600):
    """Delete a file after a certain delay in seconds."""
    await asyncio.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Auto-deleted expired file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to delete expired file {file_path}: {e}")


@app.post("/crop_media/")
async def crop_media_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    duration: int = Query(..., description="Duration to crop in seconds from the start")
):
    filename = sanitize_filename(file.filename)
    stem = Path(filename).stem
    suffix = Path(filename).suffix.lower().lstrip('.')

    try:
        # Validate media type
        _ = get_media_type(suffix)

        logger.info(f"Cropping file: {filename} to {duration}s")
        
        cropped_data = crop_media(file, duration)

        # Generate unique filename for storage
        unique_id = uuid.uuid4().hex
        output_filename = f"{stem}_{unique_id}.{suffix}"
        output_path = EXPORTS_DIR / output_filename

        # Save to disk
        with open(output_path, "wb") as f:
            f.write(cropped_data.getbuffer())

        # Schedule deletion after 1 hour
        background_tasks.add_task(delete_file_after_delay, str(output_path))

        # Generate URL
        base_url = str(request.base_url).rstrip("/")
        file_url = f"{base_url}/exports/{output_filename}"

        return JSONResponse(content={
            "status": "success",
            "filename": output_filename,
            "url": file_url,
            "expires_in": 3600
        })

    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error cropping {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Crop error: {e}")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = f"{request.method} {request.url}"
    logger.info(f"🔵 Receiving request: {idem}")

    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    logger.info(f"🟢 {idem} finished in {process_time:.2f}ms with status {response.status_code}")
    return response


@app.get("/health")
def health_check():
    return {"status": "ok"}
