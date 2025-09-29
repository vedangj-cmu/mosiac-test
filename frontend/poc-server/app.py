from pathlib import Path
from fastapi import FastAPI
from fastapi import Response
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException


app = FastAPI()
CHUNK_SIZE = 1024 * 1024

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/video")
async def video_endpoint(filename: str, range: str = Header(None)):
    video_path = Path(filename)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    file_size = video_path.stat().st_size
    start_s, end_s = range.replace("bytes=", "").split("-")
    start = int(start_s)
    end = int(end_s) if end_s else start + CHUNK_SIZE - 1
    if end >= file_size:
        end = file_size - 1
    length = end - start + 1

    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(length)
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
        "X-Filename": video_path.name,
    }
    return Response(data, status_code=206, headers=headers, media_type="video/mp4")
