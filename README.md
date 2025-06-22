![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker) ![FastAPI](https://img.shields.io/badge/fastapi-async%20api-green?logo=fastapi)

# 🎶 Media Converter API

> Fast, lightweight API to convert audio and video files between different formats using FFmpeg.

---

## 🚀 Features

- 🔄 Convert media files (audio & video) between multiple formats
- ⚡ FastAPI-powered REST API
- 🐳 Docker-ready
- 🌐 CORS enabled — easy to connect from any frontend or automation
- ✅ Supports a wide range of audio and video formats.

---

## 📦 Supported Formats

| Format    | Input | Output |
| --------- | :---: | :----: |
| **Audio** |       |        |
| mp3       |  ✅   |   ✅   |
| wav       |  ✅   |   ✅   |
| m4a       |  ✅   |   ✅   |
| flac      |  ✅   |   ✅   |
| ogg       |  ✅   |   ✅   |
| aac       |  ✅   |   ✅   |
| wma       |  ✅   |   ✅   |
| ac3       |  ✅   |   ✅   |
| aiff      |  ✅   |   ✅   |
| amr       |  ✅   |   ✅   |
| **Video** |       |        |
| mp4       |  ✅   |   ✅   |
| avi       |  ✅   |   ✅   |
| mkv       |  ✅   |   ✅   |
| mov       |  ✅   |   ✅   |
| webm      |  ✅   |   ✅   |
| flv       |  ✅   |   ✅   |
| wmv       |  ✅   |   ✅   |
| mpeg      |  ✅   |   ✅   |
| mpg       |  ✅   |   ✅   |
| 3gp       |  ✅   |   ✅   |
| ogv       |  ✅   |   ✅   |
| vob       |  ✅   |   ✅   |
| ts        |  ✅   |   ✅   |
| m2ts      |  ✅   |   ✅   |
| asf       |  ✅   |   ✅   |
| swf       |  ✅   |   ✅   |

---

## 🐳 Running with Docker

```bash
# Build the Docker image
docker build -t media-converter .

# Run the container, mapping host port 3002 to container port 3002
docker run -p 3002:3002 media-converter
```

**Note:** If you are using `docker-compose.yml`, you can simply run `docker-compose up --build -d` from the directory containing your `docker-compose.yml` file.

---

## ▶️ Running Locally

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI application with Uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 3002
```

---

## 📚 API Usage

### 🔗 Endpoint

```http
POST /convert_media/?output_format=<format>
```

### 📤 Request

- `multipart/form-data`
- Body:
  - `file`: Media file (audio or video) to upload

### ✅ Example with cURL

```bash
# Example converting a MOV video to MP4
curl -X POST "http://127.0.0.1:3002/convert_media/?output_format=mp4" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@video.mov" \
  --output converted.mp4

# Example converting an audio file to MP3
curl -X POST "http://127.0.0.1:3002/convert_media/?output_format=mp3" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  --output converted.mp3
```

### 🔥 Health Check

```http
GET /health
```

---

## 🏗️ Project Structure

```plaintext
.
├── convert_media.py   # Core media conversion logic using FFmpeg
├── main.py            # FastAPI application setup and endpoint
├── requirements.txt   # Python dependencies
├── docker-compose.yml # (optional) Docker compose
└── Dockerfile         # Docker build instructions for the container
```

---

## 🧠 Requirements

- Python 3.11+
- FFmpeg (installed in your system or via Docker)
- Or just use Docker 🐳
