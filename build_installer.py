"""PyInstaller build script to bundle HEIC Converter into a single Windows EXE."""

import subprocess
import sys
from pathlib import Path


def build_executable() -> None:
    """Invoke PyInstaller to build HEICConverter.exe."""
    project_root = Path(__file__).parent.resolve()
    main_script = project_root / "app" / "main.py"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=HEICConverter",
        "--clean",
        "--hidden-import=pillow_heif",
        "--collect-all=pillow_heif",
        str(main_script),
    ]

    print("Building Windows Executable with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode == 0:
        exe_path = project_root / "dist" / "HEICConverter.exe"
        print("\n==========================================")
        print("BUILD SUCCESSFUL!")
        print(f"Executable generated at: {exe_path}")
        print("==========================================")
    else:
        print("\nBUILD FAILED with exit code:", result.returncode)
        sys.exit(result.returncode)


if __name__ == "__main__":
    build_executable()
