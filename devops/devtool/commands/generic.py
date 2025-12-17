"""Generic command for custom commands."""

from .base import BaseCommand


class GenericCommand(BaseCommand):
    """Generic command handler for custom commands."""

    def execute(self, **kwargs) -> int:
        """Execute generic command."""
        if not self.validate():
            print("Error: Invalid command configuration")
            return 1

        command = self.config.get("command", "")
        env = self.config.get("env", {})
        background = self.config.get("background", False)

        return self.runner.execute(command, env=env, background=background)

