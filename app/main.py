"""Application entry point for Heicly."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def main() -> int:
    """Launch Heicly desktop application GUI."""
    app = QApplication(sys.argv)
    app.setApplicationName("Heicly")
    app.setOrganizationName("Heicly")

    window = MainWindow()
    window.show()

    return app.exec()



if __name__ == "__main__":
    sys.exit(main())
