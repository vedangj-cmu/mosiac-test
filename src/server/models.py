"""
Mosaic API - Data Models
src/server/models.py
"""

from pydantic import BaseModel
from typing import List, Optional, Type, Any
from datetime import datetime


class Topic(BaseModel):
    name: str
    schema_name: str
    schema_type: Type[Any] | None = None


class File(BaseModel):
    """File in a dataset."""

    name: str
    size_bytes: int
    created_at: datetime
    thumbnail_url: Optional[str] = None


class Directory(BaseModel):
    """Dataset directory with files."""

    name: str
    files: List[File]
    file_count: int


class Feed(BaseModel):
    """Camera/sensor feed."""

    name: str
    enabled: bool


class BoundingBox(BaseModel):
    """Bounding box annotation."""

    id: str
    label: str
    confidence: Optional[float] = None

    x: int
    y: int
    width: int
    height: int


class GroundTruth(BaseModel):
    """Ground truth annotations."""

    layer_name: str
    enabled: bool
    boxes: List[BoundingBox]


class ErrorResponse(BaseModel):
    """Standard error response."""

    code: str
    message: str
    details: Optional[dict] = None
    retryable: bool = False
