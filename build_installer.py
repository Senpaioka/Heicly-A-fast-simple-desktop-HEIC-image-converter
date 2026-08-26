"""PyInstaller build script to bundle Heicly into a single Windows EXE."""

import subprocess
import sys
from pathlib import Path


def build_executable() -> None:
    """Invoke PyInstaller to build Heicly.exe."""
    project_root = Path(__file__).parent.resolve()
    main_script = project_root / "app" / "main.py"

    icon_path = project_root / "app" / "assets" / "icon.png"
    assets_dir = project_root / "app" / "assets"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=Heicly",
        "--clean",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};app/assets",
        "--hidden-import=pillow_heif",
        "--collect-all=pillow_heif",
        str(main_script),
    ]

    print("Building Windows Executable with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode == 0:
        exe_path = project_root / "dist" / "Heicly.exe"
        print("\n==========================================")
        print("BUILD SUCCESSFUL!")
        print(f"Executable generated at: {exe_path}")
        print("==========================================")
    else:
        print("\nBUILD FAILED with exit code:", result.returncode)
        sys.exit(result.returncode)


if __name__ == "__main__":
    build_executable()
