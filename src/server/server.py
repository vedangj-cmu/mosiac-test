"""
Mosaic API Server
src/server/server.py

Run with: uvicorn server:app --reload
"""

from fastapi import FastAPI, HTTPException, Query, status
from typing import List
from datetime import datetime
from models import Directory, File, Feed, GroundTruth, BoundingBox

app = FastAPI(title="Mosaic API", version="1.0.0")

# Mock data store
MOCK_DIRECTORIES = {
    "data_20250912": Directory(
        name="data_20250912",
        file_count=8,
        files=[
            File(
                name="sensor_data_20250916_162938_0.mcap",
                size_bytes=123456789,
                created_at=datetime(2025, 9, 16, 16, 29, 38),
                thumbnail_url="https://cdn.example.com/thumb1.jpg",
            ),
            File(
                name="sensor_data_20250916_163132_0.mcap",
                size_bytes=98765432,
                created_at=datetime(2025, 9, 16, 16, 31, 32),
                thumbnail_url="https://cdn.example.com/thumb2.jpg",
            ),
        ],
    )
}

MOCK_FEEDS = {
    "sensor_data_20250916_162938_0.mcap": [
        Feed(name="/center_rear/camera_info", enabled=True),
        Feed(name="/passenger_rear/camera_info", enabled=False),
    ]
}

MOCK_GROUNDTRUTH = {
    "sensor_data_20250916_162938_0.mcap": [
        GroundTruth(
            layer_name="Nucleus",
            enabled=True,
            boxes=[
                BoundingBox(
                    id="b1",
                    label="Car",
                    confidence=1.0,
                    x=325,
                    y=210,
                    width=240,
                    height=180,
                )
            ],
        ),
        GroundTruth(
            layer_name="ML Output",
            enabled=True,
            boxes=[
                BoundingBox(
                    id="b2",
                    label="Truck",
                    confidence=0.62,
                    x=320,
                    y=205,
                    width=250,
                    height=190,
                )
            ],
        ),
    ]
}


@app.get("/")
def root():
    """Health check."""
    return {"status": "ok", "service": "Mosaic API"}


@app.get("/directory", response_model=Directory)
def get_directory(name: str = Query(..., description="Directory name")):
    """
    Get directory and files inside.

    Error Codes:
    - 400 INVALID_PARAM: Missing or invalid directory name
    - 404 DIRECTORY_NOT_FOUND: Directory does not exist
    - 500 SERVER_ERROR: Internal server error
    """
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAM",
                "message": "Directory name is required",
                "retryable": False,
            },
        )

    if name not in MOCK_DIRECTORIES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DIRECTORY_NOT_FOUND",
                "message": f"Directory '{name}' not found",
                "details": {"directory": name},
                "retryable": False,
            },
        )

    return MOCK_DIRECTORIES[name]


@app.get("/file", response_model=File)
def get_file(name: str = Query(..., description="File name")):
    """
    Get file by name.

    Error Codes:
    - 400 INVALID_PARAM: Missing or invalid file name
    - 404 FILE_NOT_FOUND: File does not exist
    - 403 FORBIDDEN: No access to file
    - 500 SERVER_ERROR: Internal server error
    """
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAM",
                "message": "File name is required",
                "retryable": False,
            },
        )

    # Search for file in all directories
    for directory in MOCK_DIRECTORIES.values():
        for file in directory.files:
            if file.name == name:
                return file

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "FILE_NOT_FOUND",
            "message": f"File '{name}' not found",
            "details": {"filename": name},
            "retryable": False,
        },
    )


@app.get("/feeds", response_model=List[Feed])
def get_feeds(file: str = Query(..., description="File name")):
    """
    Get feeds for a file.

    Error Codes:
    - 400 INVALID_PARAM: Missing or invalid file parameter
    - 404 FILE_NOT_FOUND: File does not exist
    - 404 FEED_NOT_AVAILABLE: No feeds available for this file
    - 500 SERVER_ERROR: Internal server error
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAM",
                "message": "File parameter is required",
                "retryable": False,
            },
        )

    if file not in MOCK_FEEDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FEED_NOT_AVAILABLE",
                "message": f"No feeds available for file '{file}'",
                "details": {"filename": file},
                "retryable": False,
            },
        )

    return MOCK_FEEDS[file]


@app.get("/groundtruth", response_model=List[GroundTruth])
def get_groundtruth(file: str = Query(..., description="File name")):
    """
    Get ground truth annotations for a file.

    Error Codes:
    - 400 INVALID_PARAM: Missing or invalid file parameter
    - 404 FILE_NOT_FOUND: File does not exist
    - 404 GROUNDTRUTH_NOT_FOUND: No ground truth data for this file
    - 500 SERVER_ERROR: Internal server error
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAM",
                "message": "File parameter is required",
                "retryable": False,
            },
        )

    if file not in MOCK_GROUNDTRUTH:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "GROUNDTRUTH_NOT_FOUND",
                "message": f"No ground truth data for file '{file}'",
                "details": {"filename": file},
                "retryable": False,
            },
        )

    return MOCK_GROUNDTRUTH[file]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
