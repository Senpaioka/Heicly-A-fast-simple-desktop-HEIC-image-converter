"""Settings manager using PySide6 QSettings for user configuration persistence."""

from pathlib import Path
from typing import Tuple

from PySide6.QtCore import QSettings

from app.core.types import ConversionOptions


class SettingsManager:
    """Manages application setting persistence across sessions."""

    def __init__(self) -> None:
        self.settings = QSettings("HEICConverter", "HEICConverterApp")

    def get_output_dir(self) -> Path:
        """Get saved output directory or default to User Pictures folder."""
        default_dir = Path.home() / "Pictures" / "Converted"
        val = str(self.settings.value("output_dir", str(default_dir)))
        return Path(val)

    def set_output_dir(self, path: Path) -> None:
        """Save output directory preference."""
        self.settings.setValue("output_dir", str(path))

    def get_output_format(self) -> str:
        """Get target image format (JPG, PNG, JPEG, WEBP)."""
        return str(self.settings.value("output_format", "JPG")).upper()

    def set_output_format(self, fmt: str) -> None:
        """Save target image format preference."""
        self.settings.setValue("output_format", fmt.upper())

    def get_quality(self) -> int:
        """Get image quality (50 - 100)."""
        val = str(self.settings.value("quality", 90))
        try:
            return int(val)
        except (ValueError, TypeError):
            return 90

    def set_quality(self, quality: int) -> None:
        """Save quality preference."""
        self.settings.setValue("quality", max(50, min(100, quality)))

    def get_theme(self) -> str:
        """Get current UI theme preference ('dark' or 'light')."""
        return str(self.settings.value("theme", "dark")).lower()

    def set_theme(self, theme: str) -> None:
        """Save UI theme preference."""
        self.settings.setValue("theme", theme.lower())

    def get_overwrite_mode(self) -> str:
        """Get filename collision policy ('skip', 'autoname', 'overwrite')."""
        return str(self.settings.value("overwrite_mode", "autoname")).lower()

    def set_overwrite_mode(self, mode: str) -> None:
        """Save filename collision policy."""
        self.settings.setValue("overwrite_mode", mode.lower())

    def get_error_strategy(self) -> str:
        """Get error handling strategy ('resume', 'stop')."""
        return str(self.settings.value("error_strategy", "resume")).lower()

    def set_error_strategy(self, strategy: str) -> None:
        """Save error handling strategy."""
        self.settings.setValue("error_strategy", strategy.lower())

    def get_filename_suffix(self) -> str:
        """Get filename suffix string."""
        return str(self.settings.value("filename_suffix", ""))

    def set_filename_suffix(self, suffix: str) -> None:
        """Save filename suffix."""
        self.settings.setValue("filename_suffix", suffix)

    def get_preserve_exif(self) -> bool:
        """Get EXIF preservation flag."""
        val = self.settings.value("preserve_exif", True)
        return str(val).lower() in ("true", "1")

    def set_preserve_exif(self, val: bool) -> None:
        """Save EXIF preservation flag."""
        self.settings.setValue("preserve_exif", val)

    def get_preserve_orientation(self) -> bool:
        """Get orientation preservation flag."""
        val = self.settings.value("preserve_orientation", True)
        return str(val).lower() in ("true", "1")

    def set_preserve_orientation(self, val: bool) -> None:
        """Save orientation preservation flag."""
        self.settings.setValue("preserve_orientation", val)

    def get_background_color(self) -> Tuple[int, int, int, int]:
        """Get transparency background color RGBA tuple."""
        r = int(str(self.settings.value("bg_r", 255)))
        g = int(str(self.settings.value("bg_g", 255)))
        b = int(str(self.settings.value("bg_b", 255)))
        a = int(str(self.settings.value("bg_a", 255)))
        return (r, g, b, a)

    def set_background_color(self, rgba: Tuple[int, int, int, int]) -> None:
        """Save transparency background color RGBA tuple."""
        self.settings.setValue("bg_r", rgba[0])
        self.settings.setValue("bg_g", rgba[1])
        self.settings.setValue("bg_b", rgba[2])
        self.settings.setValue("bg_a", rgba[3])

    def to_conversion_options(
        self,
        resize_w: float | None = None,
        resize_h: float | None = None,
        keep_aspect: bool = True,
    ) -> ConversionOptions:
        """Construct ConversionOptions from current saved settings."""
        rw = int(resize_w) if resize_w and resize_w > 0 else None
        rh = int(resize_h) if resize_h and resize_h > 0 else None

        return ConversionOptions(
            output_format=self.get_output_format(),
            quality=self.get_quality(),
            resize_width=rw,
            resize_height=rh,
            preserve_aspect=keep_aspect,
            preserve_exif=self.get_preserve_exif(),
            preserve_orientation=self.get_preserve_orientation(),
            output_dir=self.get_output_dir(),
            filename_suffix=self.get_filename_suffix(),
            bg_color=self.get_background_color(),
            overwrite_mode=self.get_overwrite_mode(),
            error_strategy=self.get_error_strategy(),
        )
