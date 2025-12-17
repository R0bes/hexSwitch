#!/usr/bin/env python3
"""Upload package to PyPI or TestPyPI."""

import os
from pathlib import Path
import subprocess
import sys

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
    BLUE = ""
    RESET = ""
    STEP_PREFIX = "[*] "
    INFO_PREFIX = "[i] "
    WARNING_PREFIX = "[!] "
    ERROR_PREFIX = "[X] "
    SUCCESS_MARKER = "[OK]"
else:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    STEP_PREFIX = "▶ "
    INFO_PREFIX = "ℹ "
    WARNING_PREFIX = "⚠ "
    ERROR_PREFIX = "✗ "
    SUCCESS_MARKER = "✓"


def print_step(message: str) -> None:
    """Print a step message."""
    print(f"{GREEN}{STEP_PREFIX}{RESET}{message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"{BLUE}{INFO_PREFIX}{RESET}{message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}{WARNING_PREFIX}{RESET}{message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{RED}{ERROR_PREFIX}{RESET}{message}")


def check_dist_files() -> bool:
    """Check if distribution files exist."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print_error("dist/ directory not found")
        print_info("Run scripts/build-package.py first")
        return False

    files = list(dist_dir.glob("*"))
    if not files:
        print_error("No files found in dist/")
        print_info("Run scripts/build-package.py first")
        return False

    print_step(f"Found {len(files)} file(s) in dist/:")
    for file in files:
        print(f"    - {file.name}")
    return True


def upload_to_pypi(test: bool = False, skip_existing: bool = False) -> bool:
    """Upload package to PyPI or TestPyPI."""
    repo_name = "TestPyPI" if test else "PyPI"

    print_step(f"Uploading to {repo_name}...")

    cmd = [sys.executable, "-m", "twine", "upload"]

    if test:
        cmd.extend(["--repository", "testpypi"])

    if skip_existing:
        cmd.append("--skip-existing")

    cmd.append("dist/*")

    try:
        subprocess.run(cmd, check=True)
        print(f"{GREEN}{SUCCESS_MARKER} Upload successful!{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Upload failed: {e}")
        return False


def main() -> int:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Upload HexSwitch package to PyPI or TestPyPI"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files that already exist on the repository"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run (don't actually upload)"
    )

    args = parser.parse_args()

    print(f"{GREEN}HexSwitch Package Uploader{RESET}\n")

    # Change to project root
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)

    # Check if dist files exist
    if not check_dist_files():
        return 1

    # Check if twine is installed
    try:
        subprocess.run([sys.executable, "-m", "twine", "--version"],
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("twine is not installed")
        print_info("Install with: pip install twine")
        return 1

    repository = "TestPyPI" if args.test else "PyPI"

    if args.dry_run:
        print_info(f"DRY RUN: Would upload to {repository}")
        print_info("Run without --dry-run to actually upload")
        return 0

    print_warning(f"You are about to upload to {repository}")
    if not args.test:
        print_warning("This will publish the package to the public PyPI!")

    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print_info("Upload cancelled")
        return 0

    # Upload
    if upload_to_pypi(test=args.test, skip_existing=args.skip_existing):
        print(f"\n{GREEN}{SUCCESS_MARKER} Package uploaded successfully!{RESET}")
        if args.test:
            print("\nTest installation:")
            print("  pip install -i https://test.pypi.org/simple/ hexswitch")
        else:
            print("\nInstallation:")
            print("  pip install hexswitch")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())

