#!/usr/bin/env python3
"""Build package for PyPI distribution."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows compatibility
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Colors for output (use simple text on Windows)
if sys.platform == "win32":
    GREEN = ""
    YELLOW = ""
    RED = ""
    RESET = ""
    STEP_PREFIX = "[*] "
    WARNING_PREFIX = "[!] "
    ERROR_PREFIX = "[X] "
else:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    STEP_PREFIX = "▶ "
    WARNING_PREFIX = "⚠ "
    ERROR_PREFIX = "✗ "


def print_step(message: str) -> None:
    """Print a step message."""
    print(f"{GREEN}{STEP_PREFIX}{RESET}{message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}{WARNING_PREFIX}{RESET}{message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{RED}{ERROR_PREFIX}{RESET}{message}")


def clean_build_dirs() -> None:
    """Clean build directories."""
    print_step("Cleaning build directories...")
    dirs_to_clean = ["build", "dist", "src/hexswitch.egg-info"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print_step(description)
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(cmd)}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False


def check_prerequisites() -> bool:
    """Check if build tools are installed."""
    print_step("Checking prerequisites...")
    
    # Check build module
    try:
        subprocess.run([sys.executable, "-m", "build", "--version"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Missing tool: build")
        print("  Install with: pip install build")
        return False
    
    # Check twine module
    try:
        subprocess.run([sys.executable, "-m", "twine", "--version"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Missing tool: twine")
        print("  Install with: pip install twine")
        return False
    
    print("  All prerequisites met")
    return True


def build_package() -> bool:
    """Build the package."""
    print_step("Building package...")
    
    # Build source distribution and wheel
    if not run_command(
        [sys.executable, "-m", "build"],
        "Building source distribution and wheel..."
    ):
        return False
    
    print_step("Build completed successfully!")
    return True


def verify_package() -> bool:
    """Verify the built package."""
    print_step("Verifying package...")
    
    # Check if dist directory exists and has files
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print_error("dist/ directory not found")
        return False
    
    files = list(dist_dir.glob("*"))
    if not files:
        print_error("No files found in dist/")
        return False
    
    print(f"  Found {len(files)} file(s) in dist/:")
    for file in files:
        print(f"    - {file.name}")
    
    # Check package with twine
    if not run_command(
        [sys.executable, "-m", "twine", "check", "dist/*"],
        "Checking package with twine..."
    ):
        return False
    
    return True


def main() -> int:
    """Main function."""
    print(f"{GREEN}HexSwitch Package Builder{RESET}\n")
    
    # Change to project root
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Clean old builds
    clean_build_dirs()
    
    # Build package
    if not build_package():
        return 1
    
    # Verify package
    if not verify_package():
        return 1
    
    success_marker = "✓" if sys.platform != "win32" else "[OK]"
    print(f"\n{GREEN}{success_marker} Package built successfully!{RESET}")
    print("\nNext steps:")
    print("  1. Test the package locally:")
    print("     pip install dist/hexswitch-*.whl")
    print("  2. Upload to TestPyPI:")
    print("     python -m twine upload --repository testpypi dist/*")
    print("  3. Upload to PyPI:")
    print("     python -m twine upload dist/*")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

