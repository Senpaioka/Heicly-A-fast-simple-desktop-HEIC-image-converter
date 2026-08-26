"""Background thread worker for batch HEIC image conversion."""

import time
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QThread, Signal

from app.core.converter import OutputPathResolver, validate_batch_preconditions
from app.core.image import ImageProcessor
from app.core.types import BatchStats, ConversionOptions, ConversionResult
from app.utils.logger import get_logger

logger = get_logger()


class ConversionWorker(QThread):
    """Executes batch image conversion in a background QThread."""

    progress_updated = Signal(BatchStats)
    file_started = Signal(str)
    file_completed = Signal(ConversionResult)
    batch_finished = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        input_files: List[Path],
        options: ConversionOptions,
        parent: Optional[QThread] = None,
    ) -> None:
        super().__init__(parent)
        self.input_files: List[Path] = input_files
        self.options: ConversionOptions = options
        self._is_cancelled: bool = False

        self.processor: ImageProcessor = ImageProcessor()
        self.resolver: OutputPathResolver = OutputPathResolver()

    def cancel(self) -> None:
        """Flag worker job for immediate cancellation."""
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self._is_cancelled

    def run(self) -> None:
        """Thread execution body for batch processing."""
        valid, err_msg = validate_batch_preconditions(self.options)
        if not valid:
            self.error_occurred.emit(err_msg)
            self.batch_finished.emit()
            return

        total_files: int = len(self.input_files)
        if total_files == 0:
            self.batch_finished.emit()
            return

        processed_count: int = 0
        success_count: int = 0
        error_count: int = 0
        skipped_count: int = 0

        start_time: float = time.time()
        file_durations: List[float] = []

        for input_path in self.input_files:
            if self._is_cancelled:
                logger.info("Batch conversion cancelled by user.")
                break

            self.file_started.emit(str(input_path))
            file_start_time: float = time.time()

            # 1. Deduplication / Identical Image Skip Check
            if self.resolver.is_identical_skip(input_path, self.options):
                skipped_count += 1
                processed_count += 1
                result = ConversionResult(
                    input_path=input_path,
                    output_path=None,
                    status="skipped",
                    message="Skipped identical duplicate file",
                    duration_sec=0.0,
                )
                self.file_completed.emit(result)
                self._emit_stats(
                    total_files,
                    processed_count,
                    success_count,
                    error_count,
                    skipped_count,
                    start_time,
                    file_durations,
                )
                continue

            # 2. Output Path Collision Resolution
            target_path, should_skip = self.resolver.resolve_output_path(input_path, self.options)
            if should_skip or target_path is None:
                skipped_count += 1
                processed_count += 1
                result = ConversionResult(
                    input_path=input_path,
                    output_path=target_path,
                    status="skipped",
                    message="Skipped existing output file",
                    duration_sec=0.0,
                )
                self.file_completed.emit(result)
                self._emit_stats(
                    total_files,
                    processed_count,
                    success_count,
                    error_count,
                    skipped_count,
                    start_time,
                    file_durations,
                )
                continue

            # 3. Perform Image Conversion
            res: ConversionResult = self.processor.convert(input_path, target_path, self.options)
            file_elapsed: float = time.time() - file_start_time
            file_durations.append(file_elapsed)

            processed_count += 1
            if res.status == "success":
                success_count += 1
            else:
                error_count += 1

            self.file_completed.emit(res)

            self._emit_stats(
                total_files,
                processed_count,
                success_count,
                error_count,
                skipped_count,
                start_time,
                file_durations,
            )

            # 4. Error Strategy Check
            if res.status == "error" and self.options.error_strategy == "stop":
                logger.warning(f"Halting batch on first error due to error_strategy='stop': {res.message}")
                self.error_occurred.emit(f"Stopped on first error: {res.message}")
                break

        self.batch_finished.emit()

    def _emit_stats(
        self,
        total: int,
        processed: int,
        success: int,
        errors: int,
        skipped: int,
        start_time: float,
        durations: List[float],
    ) -> None:
        elapsed: float = max(0.001, time.time() - start_time)
        speed_fps: float = processed / elapsed

        # Calculate ETR using rolling average duration if available
        remaining: int = total - processed
        if len(durations) > 0:
            avg_duration: float = sum(durations[-10:]) / len(durations[-10:])
            etr_seconds: float = remaining * avg_duration
        elif speed_fps > 0:
            etr_seconds = remaining / speed_fps
        else:
            etr_seconds = 0.0

        stats = BatchStats(
            total_files=total,
            processed_files=processed,
            success_count=success,
            error_count=errors,
            skipped_count=skipped,
            elapsed_seconds=elapsed,
            speed_fps=speed_fps,
            etr_seconds=etr_seconds,
        )
        self.progress_updated.emit(stats)
