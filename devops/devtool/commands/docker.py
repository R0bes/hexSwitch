"""Docker Compose command with subcommands."""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from .base import BaseCommand


class DockerCommand(BaseCommand):
    """Docker Compose command with subcommands."""

    def execute(self, subcommand: Optional[str] = None, **kwargs) -> int:
        """
        Execute docker compose command.

        Args:
            subcommand: Subcommand (up, down, re, logs)
            **kwargs: Additional arguments

        Returns:
            Exit code (0 = success)
        """
        if not subcommand:
            print("Usage: devtool d <subcommand>")
            print("   or: dev d <subcommand>")
            print()
            print("Subcommands:")
            print("  up    - Start Docker Compose services (docker-compose up -d)")
            print("  down  - Stop Docker Compose services (docker-compose down)")
            print("  re    - Down, rebuild, and up (docker-compose down && build && up -d)")
            print("  logs  - Show Docker Compose logs (docker-compose logs -f)")
            return 1

        subcommand = subcommand.lower()

        if subcommand == "up":
            return self._run_command("docker-compose up -d")
        elif subcommand == "down":
            return self._run_command("docker-compose down")
        elif subcommand == "re":
            # Down, rebuild, up
            print("Stopping services...")
            result = self._run_command("docker-compose down")
            if result != 0:
                return result

            print("Rebuilding images...")
            result = self._run_command("docker-compose build")
            if result != 0:
                return result

            print("Starting services...")
            return self._run_command("docker-compose up -d")
        elif subcommand == "logs":
            return self._run_command("docker-compose logs -f")
        else:
            print(f"Error: Unknown subcommand '{subcommand}'")
            print("Available subcommands: up, down, re, logs")
            return 1

    def _run_command(self, command: str) -> int:
        """
        Run a shell command in devops/ directory.

        Args:
            command: Command to run

        Returns:
            Exit code
        """
        try:
            # Find devops directory (could be in current dir or parent)
            current = Path.cwd()
            devops_dir = None
            
            # Check current and parent directories for devops/
            for _ in range(3):
                potential = current / "devops"
                if potential.exists() and potential.is_dir():
                    devops_dir = potential
                    break
                parent = current.parent
                if parent == current:
                    break
                current = parent
            
            if devops_dir is None:
                print("Error: devops/ directory not found")
                return 1
            
            result = subprocess.run(
                command,
                shell=True,
                check=False,
                cwd=devops_dir,
            )
            return result.returncode
        except Exception as e:
            print(f"Error executing command: {e}")
            return 1

