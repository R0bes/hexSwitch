"""Command runner for executing commands."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class CommandRunner:
    """Executes commands with platform support and environment variables."""

    def __init__(self, working_dir: Optional[Path] = None):
        """
        Initialize command runner.

        Args:
            working_dir: Working directory for commands. Defaults to current directory.
        """
        self.working_dir = working_dir or Path.cwd()
        self.platform = self._detect_platform()
        self.background_processes: List[subprocess.Popen] = []

    @staticmethod
    def _detect_platform() -> str:
        """
        Detect current platform.

        Returns:
            Platform name ('windows' or 'unix')
        """
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        return "unix"

    def substitute_env_vars(self, command: str, env: Optional[Dict[str, str]] = None) -> str:
        """
        Substitute environment variables in command string.

        Args:
            command: Command string with potential env vars
            env: Additional environment variables

        Returns:
            Command with substituted variables
        """
        # Merge with system environment
        merged_env = dict(os.environ)
        if env:
            merged_env.update(env)

        # Substitute ${VAR} or $VAR
        result = command
        for key, value in merged_env.items():
            result = result.replace(f"${{{key}}}", value)
            result = result.replace(f"${key}", value)

        return result

    def split_command(self, command: str) -> List[str]:
        """
        Split command string into list of arguments.

        Handles both simple commands and shell commands.

        Args:
            command: Command string

        Returns:
            List of command parts
        """
        # For shell commands (with &&, ||, etc.), return as-is for shell execution
        if "&&" in command or "||" in command or ";" in command:
            return [command]

        # Simple command splitting
        return command.split()

    def execute(
        self,
        command: str,
        env: Optional[Dict[str, str]] = None,
        background: bool = False,
        shell: Optional[bool] = None,
    ) -> int:
        """
        Execute a command.

        Args:
            command: Command to execute
            env: Environment variables
            background: Run in background
            shell: Use shell execution (None = auto-detect)

        Returns:
            Exit code (0 for background processes)
        """
        # Substitute environment variables
        command = self.substitute_env_vars(command, env)

        # Determine if we need shell
        if shell is None:
            shell = "&&" in command or "||" in command or ";" in command

        # Prepare environment
        exec_env = dict(os.environ)
        if env:
            exec_env.update(env)

        try:
            if background:
                # Run in background
                if shell:
                    if self.platform == "windows":
                        proc = subprocess.Popen(
                            command,
                            shell=True,
                            cwd=self.working_dir,
                            env=exec_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                    else:
                        proc = subprocess.Popen(
                            command,
                            shell=True,
                            cwd=self.working_dir,
                            env=exec_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            start_new_session=True,
                        )
                else:
                    cmd_parts = self.split_command(command)
                    proc = subprocess.Popen(
                        cmd_parts,
                        cwd=self.working_dir,
                        env=exec_env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                self.background_processes.append(proc)
                print(f"Started background process (PID: {proc.pid})")
                return 0
            else:
                # Run in foreground
                if shell:
                    result = subprocess.run(
                        command,
                        shell=True,
                        cwd=self.working_dir,
                        env=exec_env,
                    )
                else:
                    cmd_parts = self.split_command(command)
                    result = subprocess.run(
                        cmd_parts,
                        cwd=self.working_dir,
                        env=exec_env,
                    )

                return result.returncode

        except Exception as e:
            print(f"Error executing command: {e}")
            return 1

    def stop_background_processes(self) -> int:
        """
        Stop all background processes.

        Returns:
            Number of processes stopped
        """
        stopped = 0
        for proc in self.background_processes:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                stopped += 1
            except Exception as e:
                print(f"Error stopping process {proc.pid}: {e}")

        self.background_processes.clear()
        return stopped

    def stop_by_pattern(self, pattern: str) -> int:
        """
        Stop processes matching a pattern.

        Args:
            pattern: Pattern to match (process name or command)

        Returns:
            Number of processes stopped
        """
        if self.platform == "windows":
            # Windows: Use taskkill
            try:
                result = subprocess.run(
                    ["taskkill", "/F", "/IM", pattern],
                    capture_output=True,
                    text=True,
                )
                return 0 if result.returncode == 0 else 1
            except Exception:
                return 1
        else:
            # Unix: Use pkill
            try:
                result = subprocess.run(
                    ["pkill", "-f", pattern],
                    capture_output=True,
                    text=True,
                )
                return 0 if result.returncode == 0 else 1
            except Exception:
                return 1

