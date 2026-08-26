"""Core data structures and types for HEIC Converter."""

from pathlib import Path
from typing import NamedTuple, Optional, Tuple


class ImageDimensions(NamedTuple):
    """Image dimensions in pixels."""

    width: int
    height: int


class ExifData(NamedTuple):
    """EXIF metadata container."""

    raw_data: Optional[bytes]
    orientation: int


class ConversionOptions(NamedTuple):
    """Configuration options for image conversion."""

    output_format: str  # "JPG", "PNG", "JPEG", "WEBP"
    quality: int  # 50 - 100
    resize_width: Optional[int]
    resize_height: Optional[int]
    preserve_aspect: bool
    preserve_exif: bool
    preserve_orientation: bool
    output_dir: Path
    filename_suffix: str
    bg_color: Tuple[int, int, int, int]  # RGBA for transparency composite
    overwrite_mode: str  # "skip", "autoname", "overwrite"
    error_strategy: str  # "resume", "stop"


class BatchStats(NamedTuple):
    """Statistics for an active batch conversion job."""

    total_files: int
    processed_files: int
    success_count: int
    error_count: int
    skipped_count: int
    elapsed_seconds: float
    speed_fps: float
    etr_seconds: float


class ConversionResult(NamedTuple):
    """Result status of a single image conversion operation."""

    input_path: Path
    output_path: Optional[Path]
    status: str  # "success", "error", "skipped"
    message: str
    duration_sec: float
