import logging
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, Request, File, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from convert_media import *


# Logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("media_converter")


app = FastAPI()


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
