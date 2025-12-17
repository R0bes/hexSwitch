"""Stop command."""

from .base import BaseCommand


class StopCommand(BaseCommand):
    """Command for stopping services."""

    def execute(self, **kwargs) -> int:
        """Execute stop command."""
        # First try to stop background processes
        stopped = self.runner.stop_background_processes()
        if stopped > 0:
            print(f"Stopped {stopped} background process(es)")

        # Then execute configured stop command if available
        if not self.validate():
            # If no command configured, just stopping background processes is enough
            return 0

        command = self.config.get("command", "")
        if not command:
            return 0

        env = self.config.get("env", {})
        background = self.config.get("background", False)

        print("Stopping services...")
        return self.runner.execute(command, env=env, background=background)

