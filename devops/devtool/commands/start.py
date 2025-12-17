"""Start command."""

from .base import BaseCommand


class StartCommand(BaseCommand):
    """Command for starting services."""

    def execute(self, **kwargs) -> int:
        """Execute start command."""
        if not self.validate():
            print("Error: Invalid start command configuration")
            return 1

        command = self.config.get("command", "")
        env = self.config.get("env", {})
        # Start commands typically run in background
        background = self.config.get("background", True)

        print("Starting services...")
        return self.runner.execute(command, env=env, background=background)

