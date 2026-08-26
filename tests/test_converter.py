"""Unit tests for OutputPathResolver and path generation."""

from pathlib import Path
from app.core.converter import OutputPathResolver
from app.core.types import ConversionOptions


def make_options(
    out_dir: Path,
    fmt: str = "JPG",
    suffix: str = "",
    mode: str = "autoname",
) -> ConversionOptions:
    return ConversionOptions(
        output_format=fmt,
        quality=90,
        resize_width=None,
        resize_height=None,
        preserve_aspect=True,
        preserve_exif=True,
        preserve_orientation=True,
        output_dir=out_dir,
        filename_suffix=suffix,
        bg_color=(255, 255, 255, 255),
        overwrite_mode=mode,
        error_strategy="resume",
    )


def test_resolve_output_path_normal(tmp_path: Path) -> None:
    resolver = OutputPathResolver()
    options = make_options(tmp_path, fmt="JPG")
    input_file = tmp_path / "test.heic"

    target_path, should_skip = resolver.resolve_output_path(input_file, options)
    assert should_skip is False
    assert target_path == tmp_path / "test.jpg"


def test_resolve_output_path_suffix(tmp_path: Path) -> None:
    resolver = OutputPathResolver()
    options = make_options(tmp_path, fmt="PNG", suffix="_converted")
    input_file = tmp_path / "sample.heic"

    target_path, should_skip = resolver.resolve_output_path(input_file, options)
    assert should_skip is False
    assert target_path == tmp_path / "sample_converted.png"


def test_resolve_output_path_autoname_collision(tmp_path: Path) -> None:
    resolver = OutputPathResolver()
    options = make_options(tmp_path, fmt="JPG", mode="autoname")

    # Create existing collision file
    (tmp_path / "photo.jpg").write_text("existing")

    input_file = tmp_path / "photo.heic"
    target_path, should_skip = resolver.resolve_output_path(input_file, options)
    assert should_skip is False
    assert target_path == tmp_path / "photo_1.jpg"


def test_resolve_output_path_skip_mode(tmp_path: Path) -> None:
    resolver = OutputPathResolver()
    options = make_options(tmp_path, fmt="JPG", mode="skip")

    (tmp_path / "photo.jpg").write_text("existing")

    input_file = tmp_path / "photo.heic"
    target_path, should_skip = resolver.resolve_output_path(input_file, options)
    assert should_skip is True
