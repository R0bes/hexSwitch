"""Configuration loader for DevTool."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to use tomllib (Python 3.11+) or fallback to tomli
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: tomli is required. Install with: pip install tomli")
        sys.exit(1)


class DevToolConfig:
    """Configuration manager for DevTool."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to devtool.toml. If None, searches from current directory.
        """
        if config_path is None:
            config_path = self._find_config_file()

        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()

    def _find_config_file(self) -> Optional[Path]:
        """
        Find devtool.toml in current directory or parent directories.
        Also checks devops/devtool/devtool.toml.

        Returns:
            Path to devtool.toml or None if not found
        """
        current = Path.cwd()

        # Check current directory and parents (up to 5 levels)
        for _ in range(5):
            # First check devops/devtool/devtool.toml (preferred location)
            devops_config = current / "devops" / "devtool" / "devtool.toml"
            if devops_config.exists():
                return devops_config
            
            # Then check devtool.toml in root
            config_file = current / "devtool.toml"
            if config_file.exists():
                return config_file

            parent = current.parent
            if parent == current:  # Reached root
                break
            current = parent

        return None

    def load(self) -> None:
        """Load configuration from devtool.toml."""
        if self.config_path is None or not self.config_path.exists():
            self.config = self._get_default_config()
            return

        try:
            with open(self.config_path, "rb") as f:
                data = tomllib.load(f)
                # Load tool.devtool section
                tool_config = data.get("tool", {}).get("devtool", {})
                # Load commands from top-level (they're defined as [commands.xxx])
                commands = data.get("commands", {})
                # Merge them into config
                self.config = {**tool_config, "commands": commands}
        except Exception as e:
            print(f"Warning: Could not load devtool.toml: {e}")
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "name": "devtool",
            "version": "0.1.0",
            "commands": {},
        }

    def get_commands(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configured commands.

        Returns:
            Dictionary of command configurations
        """
        return self.config.get("commands", {})

    def get_command(self, command_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific command.

        Args:
            command_name: Name of the command

        Returns:
            Command configuration or None if not found
        """
        commands = self.get_commands()
        return commands.get(command_name)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get tool metadata.

        Returns:
            Metadata dictionary (name, version, etc.)
        """
        return {
            "name": self.config.get("name", "devtool"),
            "version": self.config.get("version", "0.1.0"),
        }

    def is_command_available(self, command_name: str, platform: Optional[str] = None) -> bool:
        """
        Check if a command is available for the current platform.

        Args:
            command_name: Name of the command
            platform: Platform to check (None = auto-detect)

        Returns:
            True if command is available
        """
        command = self.get_command(command_name)
        if command is None:
            return False

        platforms = command.get("platforms", [])
        if not platforms:
            return True  # Available on all platforms

        if platform is None:
            platform = self._detect_platform()

        return platform in platforms

    @staticmethod
    def _detect_platform() -> str:
        """
        Detect current platform.

        Returns:
            Platform name ('windows' or 'unix')
        """
        import platform

        system = platform.system().lower()
        if system == "windows":
            return "windows"
        return "unix"

