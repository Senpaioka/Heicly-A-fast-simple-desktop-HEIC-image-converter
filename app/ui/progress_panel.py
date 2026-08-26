"""Batch progress display and conversion control panel widget."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.types import BatchStats
from app.utils.file_utils import format_seconds


class ProgressPanel(QFrame):
    """Panel showing live batch conversion progress, speed, ETR, and control buttons."""

    start_requested = Signal()
    cancel_requested = Signal()
    open_folder_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Batch Progress", self)
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Stats readout row
        stats_layout = QHBoxLayout()
        self.label_files = QLabel("Processed: 0 / 0", self)
        self.label_speed = QLabel("Speed: -", self)
        self.label_etr = QLabel("ETR: -", self)

        stats_layout.addWidget(self.label_files)
        stats_layout.addStretch()
        stats_layout.addWidget(self.label_speed)
        stats_layout.addStretch()
        stats_layout.addWidget(self.label_etr)

        # Action buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_convert = QPushButton("Convert All", self)
        self.btn_convert.setObjectName("primaryButton")
        self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert.clicked.connect(self.start_requested.emit)

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.setObjectName("dangerButton")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)

        self.btn_open_folder = QPushButton("Open Output Folder", self)
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.clicked.connect(self.open_folder_requested.emit)

        btn_layout.addWidget(self.btn_convert)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_open_folder)

        layout.addWidget(self.progress_bar)
        layout.addLayout(stats_layout)
        layout.addLayout(btn_layout)

    def update_stats(self, stats: BatchStats) -> None:
        """Update progress bar and statistical readout labels."""
        if stats.total_files > 0:
            pct = int((stats.processed_files / stats.total_files) * 100)
        else:
            pct = 0

        self.progress_bar.setValue(pct)
        self.label_files.setText(f"Processed: {stats.processed_files} / {stats.total_files}")

        if stats.speed_fps > 0:
            self.label_speed.setText(f"Speed: {stats.speed_fps:.1f} img/s")
        else:
            self.label_speed.setText("Speed: -")

        if stats.etr_seconds > 0 and stats.processed_files < stats.total_files:
            self.label_etr.setText(f"ETR: {format_seconds(stats.etr_seconds)}")
        else:
            self.label_etr.setText("ETR: Completed" if pct == 100 else "ETR: -")

    def set_converting_state(self, is_converting: bool) -> None:
        """Toggle button enable states during active conversion."""
        self.btn_convert.setEnabled(not is_converting)
        self.btn_cancel.setEnabled(is_converting)

    def reset_progress(self) -> None:
        """Reset progress bar and stats readout."""
        self.progress_bar.setValue(0)
        self.label_files.setText("Processed: 0 / 0")
        self.label_speed.setText("Speed: -")
        self.label_etr.setText("ETR: -")
