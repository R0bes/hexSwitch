"""Unit tests for CLI entry point."""

import subprocess
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_cli_version_flag() -> None:
    """Test that --version flag works and returns exit code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app", "--version"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "HexSwitch" in result.stdout
    assert "0.1.0" in result.stdout


def test_cli_help_flag() -> None:
    """Test that --help flag works and returns exit code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app", "--help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "HexSwitch" in result.stdout
    assert "config-driven microservices" in result.stdout


def test_cli_default_run() -> None:
    """Test that CLI runs without arguments and returns exit code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0


def test_cli_config_flag_warning() -> None:
    """Test that --config flag shows warning about not being implemented."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app", "--config", "test.yaml"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "not implemented" in result.stderr.lower() or "not implemented" in result.stdout.lower()

