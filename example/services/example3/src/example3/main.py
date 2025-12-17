"""Main entry point for example3 service."""

from pathlib import Path
import sys

try:
    # Try to import hexswitch as installed package first
    from hexswitch.app import main
except ImportError:
    # Fallback: Add parent directory to path for development
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))
    from hexswitch.app import main

if __name__ == "__main__":
    sys.exit(main())

