"""Version management utilities."""

import re
import subprocess
import sys
from pathlib import Path


def get_version_from_git() -> str:
    """
    Get version from git tags.
    
    Returns:
        Version string (e.g., "0.1.0")
    """
    try:
        # Get latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip()
        # Remove 'v' prefix if present
        version = version.lstrip("v")
        return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to version in __version__.py
        version_file = Path(__file__).parent.parent / "src" / "__version__.py"
        if version_file.exists():
            content = version_file.read_text(encoding="utf-8")
            match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        return "0.1.0"


def bump_version(current_version: str, bump_type: str = "patch") -> str:
    """
    Bump version number.
    
    Args:
        current_version: Current version string (e.g., "0.1.0")
        bump_type: Type of bump ("major", "minor", or "patch")
    
    Returns:
        New version string
    """
    parts = current_version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current_version}")
    
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
        raise ValueError(f"Invalid bump_type: {bump_type}. Use 'major', 'minor', or 'patch'")
    
    return f"{major}.{minor}.{patch}"


def update_version_files(version: str) -> None:
    """
    Update version in all relevant files.
    
    Args:
        version: Version string to set
    """
    project_root = Path(__file__).parent.parent
    
    # Update src/__version__.py
    version_file = project_root / "src" / "__version__.py"
    version_file.write_text(f'"""Version information for MenuMouse."""\n\n__version__ = "{version}"\n\n', encoding="utf-8")
    print(f"Updated {version_file}")
    
    # Update pyproject.toml
    pyproject_file = project_root / "pyproject.toml"
    content = pyproject_file.read_text(encoding="utf-8")
    content = re.sub(r'version = "[^"]*"', f'version = "{version}"', content)
    pyproject_file.write_text(content, encoding="utf-8")
    print(f"Updated {pyproject_file}")
    
    # Update devtool.toml if it has version
    devtool_file = project_root / "devops" / "devtool" / "devtool.toml"
    if devtool_file.exists():
        content = devtool_file.read_text(encoding="utf-8")
        if 'version =' in content:
            content = re.sub(r'version = "[^"]*"', f'version = "{version}"', content)
            devtool_file.write_text(content, encoding="utf-8")
            print(f"Updated {devtool_file}")


def create_git_tag(version: str, message: str = None) -> None:
    """
    Create a git tag for the version.
    
    Args:
        version: Version string
        message: Tag message (optional)
    """
    tag_name = f"v{version}"
    if message is None:
        message = f"Release {tag_name}"
    
    try:
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", message],
            check=True,
        )
        print(f"Created tag: {tag_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating tag: {e}")
        sys.exit(1)


def main():
    """CLI entry point for version management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Version management utility")
    parser.add_argument(
        "command",
        choices=["get", "bump", "set"],
        help="Command to execute",
    )
    parser.add_argument(
        "--type",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Bump type (for 'bump' command)",
    )
    parser.add_argument(
        "--version",
        help="Version string (for 'set' command)",
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        help="Create git tag after bumping/setting",
    )
    
    args = parser.parse_args()
    
    if args.command == "get":
        version = get_version_from_git()
        print(version)
    
    elif args.command == "bump":
        current_version = get_version_from_git()
        new_version = bump_version(current_version, args.type)
        update_version_files(new_version)
        print(f"Bumped version: {current_version} -> {new_version}")
        
        if args.tag:
            create_git_tag(new_version)
    
    elif args.command == "set":
        if not args.version:
            print("Error: --version required for 'set' command")
            sys.exit(1)
        update_version_files(args.version)
        print(f"Set version to: {args.version}")
        
        if args.tag:
            create_git_tag(args.version)


if __name__ == "__main__":
    main()

