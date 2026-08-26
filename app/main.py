"""Application entry point for Heicly."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.utils.file_utils import get_asset_path


def main() -> int:
    """Launch Heicly desktop application GUI."""
    # Set explicit AppUserModelID on Windows for proper taskbar icon grouping
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Heicly.HEICConverter.App.1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Heicly")
    app.setOrganizationName("Heicly")

    icon_path = get_asset_path("icon.png")
    if not icon_path.exists():
        icon_path = get_asset_path("icon.ico")

    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

