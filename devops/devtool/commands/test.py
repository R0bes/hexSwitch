"""Test command."""

import sys
from pathlib import Path

from .base import BaseCommand


class TestCommand(BaseCommand):
    """Command for running tests."""

    def execute(self, **kwargs) -> int:
        """Execute test command."""
        if not self.validate():
            print("Error: Invalid test command configuration")
            return 1

        command = self.config.get("command", "")
        env = self.config.get("env", {})
        background = self.config.get("background", False)

        print("Running tests...")
        exit_code = self.runner.execute(command, env=env, background=background)
        
        # Always show coverage summary after tests (even if tests failed)
        try:
            from devops.devtool.coverage_summary import print_summary
            print_summary()
        except Exception:
            # If summary fails, just continue
            pass
        
        return exit_code

