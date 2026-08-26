"""Drag & Drop zone widget for selecting HEIC image files and folders."""

from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.utils.file_utils import HEIC_EXTENSIONS, is_heic_file


class DropZoneWidget(QFrame):
    """Interactive drag and drop container with file picker triggers."""

    files_dropped = Signal(list)  # List[Path]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 32, 24, 32)

        # Icon / Header label
        self.icon_label = QLabel("📥", self)
        self.icon_label.setStyleSheet("font-size: 38px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel("Drag & Drop HEIC files or folders here", self)
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sub_label = QLabel("Supports .heic, .heif, .hif format images", self)
        self.sub_label.setObjectName("subtitleLabel")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_select_files = QPushButton("Browse Files", self)
        self.btn_select_files.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_files.clicked.connect(self._on_browse_files)

        self.btn_select_folder = QPushButton("Browse Folder", self)
        self.btn_select_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select_folder.clicked.connect(self._on_browse_folder)

        btn_layout.addWidget(self.btn_select_files)
        btn_layout.addWidget(self.btn_select_folder)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.sub_label)
        layout.addLayout(btn_layout)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Accept drag if event mime data contains URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event: QWidget.dragLeaveEvent) -> None:  # type: ignore
        """Reset styling on drag leave."""
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle dropped files and directories."""
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        if not urls:
            return

        collected_paths: List[Path] = []
        for url in urls:
            local_path = Path(url.toLocalFile())
            if local_path.is_file():
                if is_heic_file(local_path) or local_path.suffix.lower() in HEIC_EXTENSIONS:
                    collected_paths.append(local_path)
            elif local_path.is_dir():
                collected_paths.extend(self._scan_directory(local_path))

        if collected_paths:
            self.files_dropped.emit(collected_paths)

    def _scan_directory(self, folder: Path) -> List[Path]:
        """Scan directory recursively for HEIC images."""
        found: List[Path] = []
        try:
            for p in folder.rglob("*"):
                if p.is_file() and (is_heic_file(p) or p.suffix.lower() in HEIC_EXTENSIONS):
                    found.append(p)
        except Exception:
            pass
        return found

    def _on_browse_files(self) -> None:
        """Open native file dialog for HEIC images."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select HEIC Files",
            "",
            "HEIC Images (*.heic *.heif *.hif);;All Files (*.*)",
        )
        if files:
            paths = [Path(f) for f in files]
            self.files_dropped.emit(paths)

    def _on_browse_folder(self) -> None:
        """Open native folder dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing HEIC Files")
        if folder:
            paths = self._scan_directory(Path(folder))
            if paths:
                self.files_dropped.emit(paths)
