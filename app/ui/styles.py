"""QSS Theme definitions for Dark and Light UI themes."""


DARK_THEME = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #181825;
}

QFrame#card {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 12px;
}

QFrame#dropZone {
    background-color: #181825;
    border: 2px dashed #45475a;
    border-radius: 12px;
}

QFrame#dropZone:hover {
    border-color: #89b4fa;
    background-color: #1e1e2e;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #cdd6f4;
}

QLabel#subtitleLabel {
    font-size: 12px;
    color: #a6adc8;
}

QLabel#sectionHeader {
    font-size: 14px;
    font-weight: 600;
    color: #89b4fa;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#primaryButton {
    background-color: #89b4fa;
    color: #11111b;
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 20px;
}

QPushButton#primaryButton:hover {
    background-color: #b4befa;
}

QPushButton#dangerButton {
    background-color: #f38ba8;
    color: #11111b;
    border: none;
    font-weight: bold;
}

QPushButton#dangerButton:hover {
    background-color: #f5e0dc;
}

QComboBox, QLineEdit, QSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 6px 10px;
}

QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
    border-color: #89b4fa;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #313244;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #89b4fa;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #cdd6f4;
    border: 2px solid #89b4fa;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QProgressBar {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    text-align: center;
    color: #cdd6f4;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 7px;
}

QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #313244;
    color: #89b4fa;
}

QHeaderView::section {
    background-color: #1e1e2e;
    color: #a6adc8;
    padding: 6px;
    border: none;
    font-weight: bold;
}

QCheckBox, QRadioButton {
    spacing: 8px;
    color: #cdd6f4;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
    border: 1px solid #45475a;
    background-color: #181825;
    border-radius: 4px;
}

QRadioButton::indicator:unchecked {
    border-radius: 8px;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    border: 1px solid #89b4fa;
    background-color: #89b4fa;
    border-radius: 4px;
}

QRadioButton::indicator:checked {
    border-radius: 8px;
}

QStatusBar {
    background-color: #11111b;
    color: #a6adc8;
}
"""


LIGHT_THEME = """
QWidget {
    background-color: #ffffff;
    color: #1e293b;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #f8fafc;
}

QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
}

QFrame#dropZone {
    background-color: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
}

QFrame#dropZone:hover {
    border-color: #2563eb;
    background-color: #eff6ff;
}

QLabel#titleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #0f172a;
}

QLabel#subtitleLabel {
    font-size: 12px;
    color: #64748b;
}

QLabel#sectionHeader {
    font-size: 14px;
    font-weight: 600;
    color: #2563eb;
}

QPushButton {
    background-color: #f1f5f9;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #e2e8f0;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 20px;
}

QPushButton#primaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#dangerButton {
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    font-weight: bold;
}

QPushButton#dangerButton:hover {
    background-color: #dc2626;
}

QComboBox, QLineEdit, QSpinBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
}

QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
    border-color: #2563eb;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #2563eb;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #2563eb;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QProgressBar {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    text-align: center;
    color: #1e293b;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 7px;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #eff6ff;
    color: #2563eb;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    padding: 6px;
    border: none;
    font-weight: bold;
}

QStatusBar {
    background-color: #f1f5f9;
    color: #64748b;
}
"""
