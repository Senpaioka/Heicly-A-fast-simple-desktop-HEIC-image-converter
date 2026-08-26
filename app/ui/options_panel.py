"""Options configuration panel widget."""

import os
from pathlib import Path
from typing import Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.settings import SettingsManager
from app.core.types import ConversionOptions


class OptionsPanel(QFrame):
    """Panel containing settings for image format, quality, resizing, and directory."""

    options_changed = Signal()

    def __init__(self, settings_mgr: SettingsManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.settings_mgr: SettingsManager = settings_mgr
        self.bg_color: Tuple[int, int, int, int] = self.settings_mgr.get_background_color()
        self._init_ui()
        self.load_from_settings()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        header = QLabel("Conversion Options", self)
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(10)

        row = 0

        # 1. Output Format
        grid.addWidget(QLabel("Output Format:", self), row, 0)
        self.combo_format = QComboBox(self)
        self.combo_format.addItems(["JPG", "PNG", "JPEG", "WEBP"])
        self.combo_format.currentTextChanged.connect(self._on_format_changed)
        grid.addWidget(self.combo_format, row, 1, 1, 2)

        row += 1

        # 2. Quality Slider
        self.label_quality_tag = QLabel("JPG Quality:", self)
        grid.addWidget(self.label_quality_tag, row, 0)

        slider_layout = QHBoxLayout()
        self.slider_quality = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_quality.setRange(50, 100)
        self.slider_quality.setValue(90)

        self.label_quality_val = QLabel("90%", self)
        self.slider_quality.valueChanged.connect(self._on_quality_slider_changed)

        slider_layout.addWidget(self.slider_quality)
        slider_layout.addWidget(self.label_quality_val)
        grid.addLayout(slider_layout, row, 1, 1, 2)

        row += 1

        # 3. Output Directory
        grid.addWidget(QLabel("Output Folder:", self), row, 0)

        dir_layout = QHBoxLayout()
        self.edit_output_dir = QLineEdit(self)
        self.btn_browse_dir = QPushButton("Browse...", self)
        self.btn_browse_dir.clicked.connect(self._browse_output_dir)

        dir_layout.addWidget(self.edit_output_dir)
        dir_layout.addWidget(self.btn_browse_dir)
        grid.addLayout(dir_layout, row, 1, 1, 2)

        row += 1

        # 4. Filename Suffix
        grid.addWidget(QLabel("Filename Suffix:", self), row, 0)
        self.edit_suffix = QLineEdit(self)
        self.edit_suffix.setPlaceholderText("e.g. _converted (optional)")
        grid.addWidget(self.edit_suffix, row, 1, 1, 2)

        row += 1

        # 5. Transparency Background Color
        grid.addWidget(QLabel("Background (for Alpha):", self), row, 0)

        bg_layout = QHBoxLayout()
        self.btn_bg_color = QPushButton("Pick Color", self)
        self.btn_bg_color.clicked.connect(self._pick_bg_color)
        self.label_color_preview = QLabel(self)
        self.label_color_preview.setFixedSize(24, 24)
        self.label_color_preview.setStyleSheet("border-radius: 4px; border: 1px solid #777;")
        self._update_color_preview_swatch()

        bg_layout.addWidget(self.label_color_preview)
        bg_layout.addWidget(self.btn_bg_color)
        bg_layout.addStretch()
        grid.addLayout(bg_layout, row, 1, 1, 2)

        row += 1

        # 6. Resize Options
        self.chk_enable_resize = QCheckBox("Resize Images", self)
        self.chk_enable_resize.toggled.connect(self._toggle_resize_inputs)
        grid.addWidget(self.chk_enable_resize, row, 0)

        resize_layout = QHBoxLayout()
        self.spin_width = QSpinBox(self)
        self.spin_width.setRange(1, 10000)
        self.spin_width.setValue(1920)
        self.spin_width.setPrefix("W: ")

        self.spin_height = QSpinBox(self)
        self.spin_height.setRange(1, 10000)
        self.spin_height.setValue(1080)
        self.spin_height.setPrefix("H: ")

        self.chk_aspect = QCheckBox("Keep Aspect Ratio", self)
        self.chk_aspect.setChecked(True)

        resize_layout.addWidget(self.spin_width)
        resize_layout.addWidget(self.spin_height)
        resize_layout.addWidget(self.chk_aspect)
        grid.addLayout(resize_layout, row, 1, 1, 2)

        row += 1

        # 7. Metadata Checkboxes
        grid.addWidget(QLabel("Metadata:", self), row, 0)
        meta_layout = QHBoxLayout()
        self.chk_exif = QCheckBox("Preserve EXIF", self)
        self.chk_exif.setChecked(True)
        self.chk_orientation = QCheckBox("Preserve Orientation", self)
        self.chk_orientation.setChecked(True)

        meta_layout.addWidget(self.chk_exif)
        meta_layout.addWidget(self.chk_orientation)
        grid.addLayout(meta_layout, row, 1, 1, 2)

        row += 1

        # 8. Overwrite Policy
        grid.addWidget(QLabel("File Collisions:", self), row, 0)
        col_layout = QHBoxLayout()
        self.radio_autoname = QRadioButton("Auto-name (_1)", self)
        self.radio_skip = QRadioButton("Skip Existing", self)
        self.radio_overwrite = QRadioButton("Overwrite", self)
        self.radio_autoname.setChecked(True)

        col_layout.addWidget(self.radio_autoname)
        col_layout.addWidget(self.radio_skip)
        col_layout.addWidget(self.radio_overwrite)
        grid.addLayout(col_layout, row, 1, 1, 2)

        row += 1

        # 9. Error Strategy
        grid.addWidget(QLabel("Error Policy:", self), row, 0)
        err_layout = QHBoxLayout()
        self.radio_resume_err = QRadioButton("Resume batch after error", self)
        self.radio_stop_err = QRadioButton("Stop on first error", self)
        self.radio_resume_err.setChecked(True)

        err_layout.addWidget(self.radio_resume_err)
        err_layout.addWidget(self.radio_stop_err)
        grid.addLayout(err_layout, row, 1, 1, 2)

        layout.addLayout(grid)
        self._toggle_resize_inputs(False)

    def load_from_settings(self) -> None:
        """Load settings into UI widgets."""
        self.combo_format.setCurrentText(self.settings_mgr.get_output_format())
        self.slider_quality.setValue(self.settings_mgr.get_quality())
        self.edit_output_dir.setText(str(self.settings_mgr.get_output_dir()))
        self.edit_suffix.setText(self.settings_mgr.get_filename_suffix())
        self.chk_exif.setChecked(self.settings_mgr.get_preserve_exif())
        self.chk_orientation.setChecked(self.settings_mgr.get_preserve_orientation())

        mode = self.settings_mgr.get_overwrite_mode()
        if mode == "skip":
            self.radio_skip.setChecked(True)
        elif mode == "overwrite":
            self.radio_overwrite.setChecked(True)
        else:
            self.radio_autoname.setChecked(True)

        err_strat = self.settings_mgr.get_error_strategy()
        if err_strat == "stop":
            self.radio_stop_err.setChecked(True)
        else:
            self.radio_resume_err.setChecked(True)

    def save_to_settings(self) -> None:
        """Save UI selections into persistent QSettings."""
        self.settings_mgr.set_output_format(self.combo_format.currentText())
        self.settings_mgr.set_quality(self.slider_quality.value())
        self.settings_mgr.set_output_dir(Path(self.edit_output_dir.text()))
        self.settings_mgr.set_filename_suffix(self.edit_suffix.text())
        self.settings_mgr.set_preserve_exif(self.chk_exif.isChecked())
        self.settings_mgr.set_preserve_orientation(self.chk_orientation.isChecked())
        self.settings_mgr.set_background_color(self.bg_color)

        if self.radio_skip.isChecked():
            self.settings_mgr.set_overwrite_mode("skip")
        elif self.radio_overwrite.isChecked():
            self.settings_mgr.set_overwrite_mode("overwrite")
        else:
            self.settings_mgr.set_overwrite_mode("autoname")

        if self.radio_stop_err.isChecked():
            self.settings_mgr.set_error_strategy("stop")
        else:
            self.settings_mgr.set_error_strategy("resume")

    def get_options(self) -> ConversionOptions:
        """Construct ConversionOptions snapshot from current UI state."""
        self.save_to_settings()

        fmt = self.combo_format.currentText()
        quality = self.slider_quality.value()
        out_dir = Path(self.edit_output_dir.text().strip() or str(self.settings_mgr.get_output_dir()))
        suffix = self.edit_suffix.text().strip()

        rw = self.spin_width.value() if self.chk_enable_resize.isChecked() else None
        rh = self.spin_height.value() if self.chk_enable_resize.isChecked() else None

        if self.radio_skip.isChecked():
            ow_mode = "skip"
        elif self.radio_overwrite.isChecked():
            ow_mode = "overwrite"
        else:
            ow_mode = "autoname"

        err_strat = "stop" if self.radio_stop_err.isChecked() else "resume"

        return ConversionOptions(
            output_format=fmt,
            quality=quality,
            resize_width=rw,
            resize_height=rh,
            preserve_aspect=self.chk_aspect.isChecked(),
            preserve_exif=self.chk_exif.isChecked(),
            preserve_orientation=self.chk_orientation.isChecked(),
            output_dir=out_dir,
            filename_suffix=suffix,
            bg_color=self.bg_color,
            overwrite_mode=ow_mode,
            error_strategy=err_strat,
        )

    def _on_format_changed(self, fmt: str) -> None:
        is_lossy = fmt.upper() in ("JPG", "JPEG", "WEBP")
        self.slider_quality.setEnabled(is_lossy)
        self.label_quality_tag.setText(f"{fmt.upper()} Quality:")

    def _on_quality_slider_changed(self, val: int) -> None:
        self.label_quality_val.setText(f"{val}%")

    def _toggle_resize_inputs(self, enabled: bool) -> None:
        self.spin_width.setEnabled(enabled)
        self.spin_height.setEnabled(enabled)
        self.chk_aspect.setEnabled(enabled)

    def _browse_output_dir(self) -> None:
        curr = self.edit_output_dir.text()
        chosen = QFileDialog.getExistingDirectory(self, "Select Output Folder", curr)
        if chosen:
            self.edit_output_dir.setText(chosen)

    def _pick_bg_color(self) -> None:
        initial = QColor(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
        color = QColorDialog.getColor(initial, self, "Select Background Color for Alpha Channels")
        if color.isValid():
            self.bg_color = (color.red(), color.green(), color.blue(), color.alpha())
            self._update_color_preview_swatch()

    def _update_color_preview_swatch(self) -> None:
        r, g, b, _ = self.bg_color
        self.label_color_preview.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); border-radius: 4px; border: 1px solid #777;"
        )
