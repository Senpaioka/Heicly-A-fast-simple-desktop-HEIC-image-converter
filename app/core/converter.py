"""Core path resolution and batch conversion helpers."""

from pathlib import Path
from typing import Optional, Set, Tuple

from app.core.types import ConversionOptions, ConversionResult
from app.utils.file_utils import get_file_sha256, has_enough_disk_space
from app.utils.logger import get_logger

logger = get_logger()


class OutputPathResolver:
    """Resolves output target file paths based on naming options and overwrite strategies."""

    def __init__(self) -> None:
        self.processed_hashes: Set[str] = set()

    def resolve_output_path(self, input_path: Path, options: ConversionOptions) -> Tuple[Optional[Path], bool]:
        """Determine target destination path for conversion.

        Returns:
            Tuple[Optional[Path], bool]: (target_path, should_skip)
            If target_path is None or should_skip is True, the conversion should be skipped.
        """
        stem: str = input_path.stem
        if options.filename_suffix:
            stem = f"{stem}{options.filename_suffix}"

        ext: str = options.output_format.lower()
        if ext == "jpeg":
            ext = "jpg"

        target_dir: Path = options.output_dir
        target_path: Path = target_dir / f"{stem}.{ext}"

        if options.overwrite_mode == "overwrite":
            return target_path, False

        if options.overwrite_mode == "skip":
            if target_path.exists():
                logger.info(f"Output file {target_path} already exists. Skipping due to 'skip' mode.")
                return target_path, True
            return target_path, False

        # Mode: 'autoname' (Smart auto-naming on collision)
        if not target_path.exists():
            return target_path, False

        counter: int = 1
        while True:
            candidate: Path = target_dir / f"{stem}_{counter}.{ext}"
            if not candidate.exists():
                return candidate, False
            counter += 1

    def is_identical_skip(self, input_path: Path, options: ConversionOptions) -> bool:
        """Check if identical file has already been processed in current session."""
        file_hash: str = get_file_sha256(input_path)
        if file_hash and file_hash in self.processed_hashes:
            return True
        if file_hash:
            self.processed_hashes.add(file_hash)
        return False


def validate_batch_preconditions(options: ConversionOptions) -> Tuple[bool, str]:
    """Validate output directory and disk space before starting batch conversion."""
    try:
        options.output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as err:
        return False, f"Cannot create output directory {options.output_dir}: {err}"

    if not has_enough_disk_space(options.output_dir, required_bytes=20 * 1024 * 1024):
        return False, f"Low disk space on drive containing {options.output_dir}"

    return True, "OK"
