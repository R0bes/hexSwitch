#!/usr/bin/env python3
"""Automatically bump version in pyproject.toml."""

import re
import sys
from pathlib import Path


def get_current_version(pyproject_path: Path) -> str:
    """Get current version from pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def bump_version(version: str, bump_type: str = "patch") -> str:
    """Bump version string.
    
    Args:
        version: Current version (e.g., "0.1.0")
        bump_type: Type of bump - "major", "minor", or "patch"
    
    Returns:
        New version string
    """
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    
    major, minor, patch = map(int, parts)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump_type: {bump_type}. Must be 'major', 'minor', or 'patch'")
    
    return f"{major}.{minor}.{patch}"


def update_version(pyproject_path: Path, new_version: str) -> None:
    """Update version in pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    # Replace version line
    content = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content,
        count=1
    )
    pyproject_path.write_text(content, encoding="utf-8")


def main() -> int:
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml")
    parser.add_argument(
        "--type",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Type of version bump (default: patch)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    
    args = parser.parse_args()
    
    # Find pyproject.toml
    script_dir = Path(__file__).parent.parent
    pyproject_path = script_dir / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found", file=sys.stderr)
        return 1
    
    try:
        current_version = get_current_version(pyproject_path)
        new_version = bump_version(current_version, args.type)
        
        if args.dry_run:
            print(f"Current version: {current_version}")
            print(f"New version: {new_version}")
            print(f"Bump type: {args.type}")
            return 0
        
        update_version(pyproject_path, new_version)
        print(f"Version bumped from {current_version} to {new_version}")
        # Output for GitHub Actions
        print(f"::set-output name=version::{new_version}")
        print(f"::set-output name=old_version::{current_version}")
        # Also print to stdout for easy parsing
        print(f"NEW_VERSION={new_version}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

