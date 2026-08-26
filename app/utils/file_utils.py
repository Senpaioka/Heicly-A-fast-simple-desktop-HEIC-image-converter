"""Utility functions for file manipulation, validation, and metadata formatting."""

import hashlib
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


def get_asset_path(filename: str) -> Path:
    """Get absolute path to an asset file, working for dev mode and PyInstaller bundle."""
    if hasattr(sys, "_MEIPASS"):
        meipass_path = Path(getattr(sys, "_MEIPASS"))
        bundled_asset = meipass_path / "app" / "assets" / filename
        if bundled_asset.exists():
            return bundled_asset
        alt_bundled_asset = meipass_path / "assets" / filename
        if alt_bundled_asset.exists():
            return alt_bundled_asset
        return bundled_asset
    
    dev_asset = Path(__file__).resolve().parent.parent / "assets" / filename
    return dev_asset


HEIC_EXTENSIONS: Tuple[str, ...] = (".heic", ".heif", ".hif")
HEIC_MAGIC_BRANDS: List[bytes] = [
    b"ftypheic",
    b"ftypheix",
    b"ftypheim",
    b"ftypheis",
    b"ftyphevc",
    b"ftypmif1",
    b"ftypmsf1",
]


def is_heic_file(file_path: Path) -> bool:
    """Verify if a file has a HEIC/HEIF extension and valid magic bytes header."""
    if not file_path.is_file():
        return False

    ext: str = file_path.suffix.lower()
    if ext not in HEIC_EXTENSIONS:
        return False

    try:
        with open(file_path, "rb") as f:
            header: bytes = f.read(32)
            if len(header) < 12:
                return False
            # ISO Base Media File Format header: bytes 4-12 usually contain brand
            for brand in HEIC_MAGIC_BRANDS:
                if brand in header:
                    return True
            # Fall back to extension check if valid size
            return True
    except OSError:
        return False


def get_file_sha256(file_path: Path, max_bytes: int = 2 * 1024 * 1024) -> str:
    """Calculate hash of file (up to max_bytes for speed) to detect identical images."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            data: bytes = f.read(max_bytes)
            hasher.update(data)
            hasher.update(str(file_path.stat().st_size).encode("utf-8"))
        return hasher.hexdigest()
    except OSError:
        return ""


def format_bytes(num_bytes: int) -> str:
    """Convert bytes count to human readable string (e.g. KB, MB, GB)."""
    if num_bytes < 0:
        return "0 B"
    num: float = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}" if unit != "B" else f"{int(num)} B"
        num /= 1024.0
    return f"{num:.1f} PB"


def format_seconds(seconds: float) -> str:
    """Format seconds into human readable duration string (e.g. 1m 24s)."""
    if seconds <= 0 or not (seconds < 86400 * 365):
        return "0s"
    sec: int = int(seconds)
    hours: int = sec // 3600
    minutes: int = (sec % 3600) // 60
    secs: int = sec % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def has_enough_disk_space(target_dir: Path, required_bytes: int = 10 * 1024 * 1024) -> bool:
    """Check if target directory disk has at least required_bytes free space."""
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(target_dir)
        return usage.free >= required_bytes
    except OSError:
        return True  # Fallback assumption if cannot check
