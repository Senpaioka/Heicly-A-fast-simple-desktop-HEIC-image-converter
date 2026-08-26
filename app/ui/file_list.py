"""File queue list and table widget with conversion status indicators."""

from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.types import ConversionResult
from app.utils.file_utils import format_bytes


class FileListView(QFrame):
    """Table view displaying the queue of HEIC files and conversion status."""

    queue_changed = Signal(int)  # Total item count

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.queued_paths: List[Path] = []
        self.path_to_row: Dict[str, int] = {}
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header bar
        header_layout = QHBoxLayout()
        self.label_title = QLabel("Conversion Queue", self)
        self.label_title.setObjectName("sectionHeader")

        self.label_count = QLabel("(0 files)", self)
        self.label_count.setObjectName("subtitleLabel")

        header_layout.addWidget(self.label_title)
        header_layout.addWidget(self.label_count)
        header_layout.addStretch()

        self.btn_remove_selected = QPushButton("Remove Selected", self)
        self.btn_remove_selected.clicked.connect(self._remove_selected)

        self.btn_clear_all = QPushButton("Clear All", self)
        self.btn_clear_all.clicked.connect(self.clear_queue)

        header_layout.addWidget(self.btn_remove_selected)
        header_layout.addWidget(self.btn_clear_all)

        layout.addLayout(header_layout)

        # Table widget
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File Name", "Size", "Status", "Output Path"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

    def add_files(self, paths: List[Path]) -> None:
        """Add new files to the queue, ignoring duplicates."""
        for p in paths:
            abs_str = str(p.resolve())
            if abs_str not in self.path_to_row:
                self.queued_paths.append(p)
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.path_to_row[abs_str] = row

                # File Name
                item_name = QTableWidgetItem(p.name)
                item_name.setToolTip(str(p))
                self.table.setItem(row, 0, item_name)

                # Size
                try:
                    size_str = format_bytes(p.stat().st_size)
                except OSError:
                    size_str = "Unknown"
                item_size = QTableWidgetItem(size_str)
                item_size.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 1, item_size)

                # Status
                item_status = QTableWidgetItem("Pending")
                item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_status.setForeground(QColor("#a6adc8"))
                self.table.setItem(row, 2, item_status)

                # Output Path
                item_out = QTableWidgetItem("-")
                self.table.setItem(row, 3, item_out)

        self._update_count_label()

    def get_files(self) -> List[Path]:
        """Get ordered list of files currently in queue."""
        return list(self.queued_paths)

    def mark_started(self, input_path_str: str) -> None:
        """Update status of file currently converting."""
        row = self._find_row(input_path_str)
        if row is not None:
            item = self.table.item(row, 2)
            if item:
                item.setText("Converting...")
                item.setForeground(QColor("#89b4fa"))

    def mark_completed(self, result: ConversionResult) -> None:
        """Update file status and output path upon completion."""
        row = self._find_row(str(result.input_path))
        if row is not None:
            item_status = self.table.item(row, 2)
            item_out = self.table.item(row, 3)

            if item_status:
                if result.status == "success":
                    item_status.setText("Done")
                    item_status.setForeground(QColor("#a6e3a1"))
                elif result.status == "skipped":
                    item_status.setText("Skipped")
                    item_status.setForeground(QColor("#fab387"))
                else:
                    item_status.setText("Error")
                    item_status.setForeground(QColor("#f38ba8"))
                    item_status.setToolTip(result.message)

            if item_out and result.output_path:
                item_out.setText(result.output_path.name)
                item_out.setToolTip(str(result.output_path))

    def reset_statuses(self) -> None:
        """Reset all status badges back to Pending."""
        for row in range(self.table.rowCount()):
            item_status = self.table.item(row, 2)
            item_out = self.table.item(row, 3)
            if item_status:
                item_status.setText("Pending")
                item_status.setForeground(QColor("#a6adc8"))
            if item_out:
                item_out.setText("-")

    def clear_queue(self) -> None:
        """Clear all files from table and queue."""
        self.table.setRowCount(0)
        self.queued_paths.clear()
        self.path_to_row.clear()
        self._update_count_label()

    def _remove_selected(self) -> None:
        """Remove currently highlighted rows from queue."""
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        for row in selected_rows:
            path = self.queued_paths[row]
            abs_str = str(path.resolve())
            if abs_str in self.path_to_row:
                del self.path_to_row[abs_str]
            del self.queued_paths[row]
            self.table.removeRow(row)

        # Re-index path_to_row dictionary
        self.path_to_row = {str(p.resolve()): i for i, p in enumerate(self.queued_paths)}
        self._update_count_label()

    def _find_row(self, path_str: str) -> Optional[int]:
        try:
            abs_str = str(Path(path_str).resolve())
            return self.path_to_row.get(abs_str)
        except Exception:
            return None

    def _update_count_label(self) -> None:
        cnt = len(self.queued_paths)
        self.label_count.setText(f"({cnt} {'file' if cnt == 1 else 'files'})")
        self.queue_changed.emit(cnt)
