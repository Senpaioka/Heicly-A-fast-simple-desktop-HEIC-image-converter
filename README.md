# Heicly

**Heicly** is a high-performance, privacy-first, 100% offline desktop application for Windows to convert Apple HEIC/HEIF images into universal formats such as JPG, PNG, JPEG, and WEBP.

Built with **Python 3.10+**, **PySide6 (Qt for Python)**, and **pillow-heif**, Heicly offers a modern responsive user interface, background batch conversion, metadata preservation, and flexible output customization without sending your data to any external server.

---

## Key Features

- **Batch Conversion**: Process single image files, multiple selected files, or entire folders simultaneously.
- **Drag & Drop Interface**: Easily drag and drop `.heic`, `.heif`, or `.hif` images directly into the workspace.
- **Multi-Format Export**: Convert to **JPG**, **PNG**, **JPEG**, or **WEBP**.
- **Quality & Compression Tuning**: Adjustable output compression quality (50%–100%) with format-specific optimizations.
- **Image Resizing**: Resize output images with optional aspect ratio preservation using high-quality **LANCZOS** resampling.
- **EXIF & Orientation Preservation**: Retain camera metadata (EXIF) and automatically transpose orientation based on image headers.
- **Alpha Channel Handling**: Customizable solid background composite color (RGBA) for images with transparency when exporting to lossy formats like JPG.
- **Smart Collision Resolution**: Flexible output file collision handling (`Autoname`, `Skip`, or `Overwrite`).
- **Session Deduplication**: SHA-256 hash checks prevent duplicate processing within the same session.
- **Non-Blocking Background Threading**: Multi-threaded conversion worker prevents UI freezing during large batch jobs and provides real-time progress, speed (FPS), and ETR (Estimated Time Remaining).
- **Theme Support**: Integrated Dark Mode and Light Mode support.
- **Offline & Private**: 100% local execution ensuring your personal photos never leave your device.

---

## How It Works

Heicly separates user interaction, background job execution, image decoding/transformation, and settings persistence into decoupled modules.

```
Heicly Application
├── UI Layer (PySide6 / Qt)
│   ├── MainWindow & DropZone (Drag & Drop, file collection)
│   ├── OptionsPanel (Format, Quality, Resizing, EXIF, Theme)
│   └── ProgressPanel (Batch progress, Speed FPS, ETR, Status)
│
├── Background Worker (QThread)
│   └── Batch Conversion Worker (Async job execution & signal updates)
│
├── Core Engine (app/core/)
│   ├── ImageProcessor (pillow-heif decoding, Pillow encoding, LANCZOS resize)
│   ├── OutputPathResolver (Smart naming collision, SHA-256 deduplication)
│   └── SettingsManager (QSettings persistent preferences)
│
└── Packaging (PyInstaller)
    └── Standalone Windows Binary (Heicly.exe)
```

### Conversion Pipeline Workflow

1. **File Ingestion**: Files are added via file dialogs or dropped onto the `DropZone`. File types are validated against supported HEIC extensions (`.heic`, `.heif`, `.hif`).
2. **Pre-flight Checks**: Validates output directory access and verifies sufficient disk space.
3. **Session Hash Check**: Computes SHA-256 hashes to detect identical duplicate inputs and prevent redundant processing.
4. **Decoding & Manipulation (`ImageProcessor`)**:
   - Decodes raw HEIC/HEIF bytes via `pillow-heif`.
   - Transposes rotation based on camera EXIF tags (`ImageOps.exif_transpose`).
   - Resizes image to specified dimensions using LANCZOS filtering.
   - Composites alpha transparency against user-defined background color if exporting to JPG/JPEG.
5. **Encoding & Export**: Encodes pixel data to target format (JPEG, PNG, WEBP) with specified quality settings and retains EXIF metadata if enabled.
6. **Progress & Telemetry**: Emits Qt signals (`progress_updated`, `file_completed`, `batch_finished`) to update the GUI smoothly without blocking the main event loop.

---

## Project Architecture

```
heic-converter/
├── app/
│   ├── assets/           # Icons and visual assets
│   ├── core/
│   │   ├── converter.py  # Path resolution, collision logic, disk checks
│   │   ├── image.py      # Core HEIC decoding and image transformation engine
│   │   ├── settings.py   # Persistent QSettings configuration manager
│   │   └── types.py      # Strongly-typed NamedTuples (ConversionOptions, BatchStats, etc.)
│   ├── ui/
│   │   ├── drop_zone.py      # Interactive drag-and-drop file target
│   │   ├── file_list.py      # Table view for loaded files and status indicators
│   │   ├── main_window.py    # Main Qt application window
│   │   ├── options_panel.py  # Conversion options & preferences controls
│   │   ├── progress_panel.py # Batch conversion progress & metrics bar
│   │   └── styles.py         # Modern QSS stylesheet rules (Dark/Light themes)
│   ├── utils/
│   │   ├── file_utils.py # SHA-256 hashing, disk space checkers
│   │   └── logger.py     # Application logger setup
│   ├── workers/
│   │   └── conversion_worker.py # QThread worker running background conversions
│   └── main.py           # Application entry point
├── tests/                # Automated pytest suite
├── build_installer.py    # PyInstaller packaging script
├── Heicly.spec           # PyInstaller specification configuration
├── pyproject.toml        # Project metadata and dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

- **Windows 10 / 11**
- **Python 3.10+** (Python 3.14 recommended)
- [`uv`](https://github.com/astral-sh/uv) (recommended) or standard `pip`

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Senpaioka/Heicly-A-fast-simple-desktop-HEIC-image-converter.git
   cd Heicly-A-fast-simple-desktop-HEIC-image-converter
   ```

2. **Set up virtual environment & install dependencies**:

   Using `uv` (recommended):
   ```bash
   uv sync
   ```

   Or using standard `pip`:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```

---

## Usage

### Running the Application

Using `uv`:
```bash
uv run heicly
```

Or directly via Python:
```bash
python -m app.main
```

### Running Tests & Type Checks

Execute unit tests with `pytest`:
```bash
uv run pytest
```

Run static type checking with `mypy`:
```bash
uv run mypy app
```

---

## Building Standalone Executable

To bundle Heicly into a self-contained, single-file Windows executable (`Heicly.exe`):

```bash
python build_installer.py
```

The compiled binary will be placed inside the `dist/` directory:
```
dist/Heicly.exe
```

---

## Tech Stack & Dependencies

- **Language**: Python 3.10+
- **GUI Framework**: [PySide6](https://pypi.org/project/PySide6/) (Qt for Python)
- **HEIC Engine**: [pillow-heif](https://pypi.org/project/pillow-heif/)
- **Image Processing**: [Pillow (PIL)](https://pypi.org/project/pillow/)
- **Build System**: [PyInstaller](https://pyinstaller.org/) & `setuptools`

---

## License

Distributed under the MIT License. See `LICENSE` for details.

