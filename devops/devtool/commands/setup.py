"""Setup command."""

import os
import sys
from pathlib import Path

from .base import BaseCommand


class SetupCommand(BaseCommand):
    """Command for project setup."""

    def execute(self, **kwargs) -> int:
        """Execute setup command."""
        if not self.validate():
            print("Error: Invalid setup command configuration")
            return 1

        # Use the current Python interpreter (not dev.exe) to avoid import issues
        current_python = sys.executable
        
        # Check if venv already exists
        venv_path = Path(".venv")
        if os.name == "nt":  # Windows
            venv_python = venv_path / "Scripts" / "python.exe"
        else:  # Unix
            venv_python = venv_path / "bin" / "python"
        
        venv_exists = venv_path.exists() and venv_python.exists()
        
        if venv_exists:
            print("Virtual environment already exists. Installing/updating dependencies...")
            # Use venv python directly to avoid self-deinstallation issue
            # The venv python is different from the running dev.exe, so it can reinstall safely
            python_cmd = str(venv_python)
            # Upgrade pip first, then install/upgrade package and dependencies
            command = f"{python_cmd} -m pip install --upgrade pip && {python_cmd} -m pip install --upgrade -e \".[dev]\""
        else:
            # Create new venv first using current Python
            print("Creating virtual environment...")
            # Use current Python to create venv, then install
            if os.name == "nt":  # Windows
                command = f"{current_python} -m venv .venv && .venv\\Scripts\\python.exe -m pip install --upgrade pip && .venv\\Scripts\\python.exe -m pip install -e \".[dev]\""
            else:  # Unix
                command = f"{current_python} -m venv .venv && .venv/bin/python -m pip install --upgrade pip && .venv/bin/python -m pip install -e \".[dev]\""
        
        env = self.config.get("env", {})
        background = self.config.get("background", False)

        print("Setting up project...")
        return self.runner.execute(command, env=env, background=background)

