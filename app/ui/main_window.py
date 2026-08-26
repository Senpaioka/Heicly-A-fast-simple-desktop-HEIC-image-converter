"""Main window layout and application controller."""

import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.core.settings import SettingsManager
from app.core.types import BatchStats, ConversionOptions, ConversionResult
from app.ui.drop_zone import DropZoneWidget
from app.ui.file_list import FileListView
from app.ui.options_panel import OptionsPanel
from app.ui.progress_panel import ProgressPanel
from app.ui.styles import DARK_THEME, LIGHT_THEME
from app.utils.logger import get_logger
from app.workers.conversion_worker import ConversionWorker

logger = get_logger()


class MainWindow(QMainWindow):
    """Main application window container."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("HEIC Converter for Windows")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        self.settings_mgr = SettingsManager()
        self.worker: Optional[ConversionWorker] = None

        self._init_ui()
        self._apply_saved_theme()

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # 1. Header Toolbar Bar
        header_frame = QFrame(self)
        header_frame.setObjectName("card")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)

        app_title = QLabel("🖼️ HEIC Converter", self)
        app_title.setObjectName("titleLabel")

        app_desc = QLabel("Fast, offline HEIC/HEIF image conversion tool", self)
        app_desc.setObjectName("subtitleLabel")

        header_info = QVBoxLayout()
        header_info.addWidget(app_title)
        header_info.addWidget(app_desc)

        header_layout.addLayout(header_info)
        header_layout.addStretch()

        # Theme Toggle Button
        self.btn_theme = QPushButton("🌓 Toggle Theme", self)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.btn_theme)

        # About Dialog Button
        self.btn_about = QPushButton("ℹ️ About", self)
        self.btn_about.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about.clicked.connect(self._show_about)
        header_layout.addWidget(self.btn_about)

        main_layout.addWidget(header_frame)

        # 2. Main Content Splitter (Left: DropZone + FileList, Right: Options + Progress)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left Pane
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self.drop_zone = DropZoneWidget(self)
        self.drop_zone.files_dropped.connect(self._on_files_dropped)

        self.file_list = FileListView(self)

        left_layout.addWidget(self.drop_zone, stretch=1)
        left_layout.addWidget(self.file_list, stretch=2)

        # Right Pane
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        self.options_panel = OptionsPanel(self.settings_mgr, self)
        self.progress_panel = ProgressPanel(self)

        self.progress_panel.start_requested.connect(self._start_conversion)
        self.progress_panel.cancel_requested.connect(self._cancel_conversion)
        self.progress_panel.open_folder_requested.connect(self._open_output_folder)

        right_layout.addWidget(self.options_panel)
        right_layout.addWidget(self.progress_panel)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # 3. Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Drag and drop HEIC files to get started.")

    def _on_files_dropped(self, paths: List[Path]) -> None:
        """Add dropped files to table view."""
        self.file_list.add_files(paths)
        self.status_bar.showMessage(f"Added {len(paths)} file(s) to queue.")

    def _start_conversion(self) -> None:
        """Start batch conversion background worker."""
        files = self.file_list.get_files()
        if not files:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please add HEIC files to the queue before converting.",
            )
            return

        options: ConversionOptions = self.options_panel.get_options()

        self.file_list.reset_statuses()
        self.progress_panel.reset_progress()
        self.progress_panel.set_converting_state(True)
        self.options_panel.setEnabled(False)
        self.status_bar.showMessage("Converting images...")

        self.worker = ConversionWorker(files, options)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.file_started.connect(self._on_file_started)
        self.worker.file_completed.connect(self._on_file_completed)
        self.worker.batch_finished.connect(self._on_batch_finished)
        self.worker.error_occurred.connect(self._on_worker_error)

        self.worker.start()

    def _cancel_conversion(self) -> None:
        """Cancel running batch worker."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_bar.showMessage("Cancelling conversion...")

    def _on_file_started(self, input_path_str: str) -> None:
        self.file_list.mark_started(input_path_str)

    def _on_file_completed(self, result: ConversionResult) -> None:
        self.file_list.mark_completed(result)

    def _on_progress_updated(self, stats: BatchStats) -> None:
        self.progress_panel.update_stats(stats)

    def _on_batch_finished(self) -> None:
        self.progress_panel.set_converting_state(False)
        self.options_panel.setEnabled(True)
        self.status_bar.showMessage("Batch conversion completed.")
        logger.info("Batch conversion completed successfully.")

    def _on_worker_error(self, message: str) -> None:
        QMessageBox.critical(self, "Conversion Error", message)
        self.status_bar.showMessage(f"Error: {message}")

    def _open_output_folder(self) -> None:
        out_dir = self.options_panel.get_options().output_dir
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(out_dir)))
        except Exception as err:
            QMessageBox.warning(self, "Folder Error", f"Could not open output folder: {err}")

    def _apply_saved_theme(self) -> None:
        theme = self.settings_mgr.get_theme()
        app = QApplication.instance()
        if app:
            if theme == "light":
                app.setStyleSheet(LIGHT_THEME)  # type: ignore
            else:
                app.setStyleSheet(DARK_THEME)  # type: ignore

    def _toggle_theme(self) -> None:
        curr = self.settings_mgr.get_theme()
        new_theme = "light" if curr == "dark" else "dark"
        self.settings_mgr.set_theme(new_theme)
        self._apply_saved_theme()
        self.status_bar.showMessage(f"Switched theme to {new_theme.title()} mode.")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About HEIC Converter",
            "<h3>HEIC Converter v0.1.0</h3>"
            "<p>A fast, offline desktop utility for Windows to convert HEIC/HEIF images "
            "to JPG, PNG, JPEG, or WEBP.</p>"
            "<p><b>Features:</b> Batch processing, drag & drop, EXIF preservation, "
            "smart auto-naming, quality options, image resizing, and dark/light mode.</p>",
        )
