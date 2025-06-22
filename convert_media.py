import logging
import io
import re
import unicodedata
import subprocess
import tempfile
from pathlib import Path

import ffmpeg
from fastapi import UploadFile


# Logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("media_converter")


# Supported Formats
SUPPORTED_FORMATS = {
    "audio": {
        "mp3", "wav", "m4a", "flac", "ogg", "aac",
        "wma", "ac3", "aiff", "amr"
    },
    "video": {
        "mp4", "avi", "mkv", "mov", "webm", "flv", "wmv",
        "mpeg", "mpg", "3gp", "ogv", "vob", "ts", "m2ts",
        "asf", "swf"
    }
}


# Utils
def sanitize_filename(filename: str) -> str:
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    filename = re.sub(r'[^\w\-_\. ]', '_', filename)
    return filename


def get_media_type(suffix: str) -> str:
    """Return 'audio', 'video' or raise error."""
    suffix = suffix.lstrip(".").lower()
    if suffix in SUPPORTED_FORMATS["audio"]:
        return "audio"
    if suffix in SUPPORTED_FORMATS["video"]:
        return "video"
    raise ValueError(f"Unsupported file type: {suffix}")


# Conversion Logic
def convert_media(file: UploadFile, output_format: str) -> io.BytesIO:
    input_suffix = Path(file.filename).suffix
    output_suffix = f".{output_format}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=input_suffix) as temp_in, \
         tempfile.NamedTemporaryFile(delete=False, suffix=output_suffix) as temp_out:
        
        temp_in.write(file.file.read())
        temp_in.flush()

        try:
            input_stream = ffmpeg.input(temp_in.name)

            is_audio_input = input_suffix.lstrip(".").lower() in SUPPORTED_FORMATS["audio"]
            is_video_output = output_format.lower() in SUPPORTED_FORMATS["video"]

            if is_audio_input and is_video_output:
                audio = input_stream.audio
                video = ffmpeg.input(
                    'color=size=1280x720:duration=0.1:rate=25:color=black',
                    f='lavfi'
                )
                stream = ffmpeg.output(
                    video, audio, temp_out.name
                )
            elif output_format in SUPPORTED_FORMATS["audio"]:
                stream = input_stream.output(temp_out.name, vn=None)
            elif output_format in {"mp4", "mov"}:
                stream = input_stream.output(
                    temp_out.name,
                    movflags='frag_keyframe+empty_moov'
                )
            else:
                stream = input_stream.output(temp_out.name)

            stream.run(quiet=True, overwrite_output=True)

            with open(temp_out.name, "rb") as out_f:
                data = io.BytesIO(out_f.read())
                data.seek(0)

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg command failed: {e.stderr.decode()}")
            raise RuntimeError(f"FFmpeg conversion error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during FFmpeg conversion: {e}")
            raise RuntimeError(f"Unexpected error: {e}")
        finally:
            Path(temp_in.name).unlink(missing_ok=True)
            Path(temp_out.name).unlink(missing_ok=True)

    return data

