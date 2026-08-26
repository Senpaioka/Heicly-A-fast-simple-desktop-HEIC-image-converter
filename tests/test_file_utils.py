"""Unit tests for file utility functions."""

from pathlib import Path
from app.utils.file_utils import format_bytes, format_seconds, get_file_sha256, is_heic_file, has_enough_disk_space


def test_format_bytes() -> None:
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1048576) == "1.0 MB"
    assert format_bytes(1073741824) == "1.0 GB"


def test_format_seconds() -> None:
    assert format_seconds(0) == "0s"
    assert format_seconds(45) == "45s"
    assert format_seconds(65) == "1m 5s"
    assert format_seconds(3665) == "1h 1m 5s"


def test_is_heic_file_nonexistent(tmp_path: Path) -> None:
    fake = tmp_path / "fake.heic"
    assert not is_heic_file(fake)


def test_has_enough_disk_space(tmp_path: Path) -> None:
    assert has_enough_disk_space(tmp_path, required_bytes=100)
