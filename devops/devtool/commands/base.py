"""Base command class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseCommand(ABC):
    """Base class for all commands."""

    def __init__(self, config: Dict[str, Any], runner):
        """
        Initialize command.

        Args:
            config: Command configuration from devtool.toml
            runner: CommandRunner instance
        """
        self.config = config
        self.runner = runner

    @abstractmethod
    def execute(self, **kwargs) -> int:
        """
        Execute the command.

        Args:
            **kwargs: Additional arguments

        Returns:
            Exit code (0 = success)
        """
        pass

    def get_description(self) -> str:
        """
        Get command description.

        Returns:
            Description string
        """
        return self.config.get("description", "")

    def get_help(self) -> str:
        """
        Get help text for command.

        Returns:
            Help text
        """
        description = self.get_description()
        command = self.config.get("command", "")
        return f"{description}\n\nCommand: {command}"

    def validate(self) -> bool:
        """
        Validate command configuration.

        Returns:
            True if valid
        """
        if "command" not in self.config:
            return False
        return True

