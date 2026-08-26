"""Application entry point for HEIC Converter."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> int:
    """Launch HEIC Converter desktop application GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("HEIC Converter")
    app.setOrganizationName("HEICConverter")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
