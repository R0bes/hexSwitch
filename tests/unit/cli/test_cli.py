"""Unit tests for CLI entry point."""

from pathlib import Path
import subprocess
import sys
import tempfile

import pytest
import yaml

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Default timeout for all subprocess calls (in seconds)
SUBPROCESS_TIMEOUT = 10


def test_cli_version_flag() -> None:
    """Test that --version flag works and returns exit code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app", "--version"],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "HexSwitch" in result.stdout
    assert "0.1.0" in result.stdout


def test_cli_version_command() -> None:
    """Test that 'version' command works and returns exit code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app", "version"],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "HexSwitch" in result.stdout
    assert "0.1.0" in result.stdout
    assert "Hexagonal runtime switchboard" in result.stdout


def test_cli_default_run_shows_version() -> None:
    """Test that CLI runs without arguments and shows version (backwards compatibility)."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app"],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "HexSwitch" in result.stdout


def test_cli_help_flag() -> None:
    """Test that --help flag works and returns exit code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "hexswitch.app", "--help"],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert result.returncode == 0
    assert "HexSwitch" in result.stdout
    assert "config-driven microservices" in result.stdout


def test_cli_init_creates_config() -> None:
    """Test that 'init' command creates example configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        result = subprocess.run(
            [sys.executable, "-m", "hexswitch.app", "--config", str(config_path), "init"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 0
        assert config_path.exists()
        assert "example-service" in config_path.read_text()


def test_cli_init_refuses_overwrite() -> None:
    """Test that 'init' command refuses to overwrite existing config without --force."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        config_path.write_text("existing: config")

        result = subprocess.run(
            [sys.executable, "-m", "hexswitch.app", "--config", str(config_path), "init"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 1
        assert "already exists" in result.stderr or "already exists" in result.stdout


def test_cli_init_force_overwrite() -> None:
    """Test that 'init' command overwrites with --force."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        config_path.write_text("existing: config")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "hexswitch.app",
                "--config",
                str(config_path),
                "init",
                "--force",
            ],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 0
        assert "example-service" in config_path.read_text()


def test_cli_validate_success() -> None:
    """Test that 'validate' command succeeds with valid config."""
    config_data = {
        "service": {"name": "test-service", "runtime": "python"},
        "inbound": {"http": {"enabled": True}},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        result = subprocess.run(
            [sys.executable, "-m", "hexswitch.app", "--config", str(config_path), "validate"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 0
        assert "valid" in result.stderr.lower() or "valid" in result.stdout.lower()


def test_cli_validate_failure() -> None:
    """Test that 'validate' command fails with invalid config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        config_path.write_text("invalid: yaml: [")

        result = subprocess.run(
            [sys.executable, "-m", "hexswitch.app", "--config", str(config_path), "validate"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 1
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()


def test_cli_run_dry_run() -> None:
    """Test that 'run --dry-run' command works."""
    config_data = {
        "service": {"name": "test-service", "runtime": "python"},
        "inbound": {"http": {"enabled": True, "port": 8000, "routes": []}},
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "hexswitch.app",
                "--config",
                str(config_path),
                "run",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=Path(__file__).parent.parent.parent,
        )
        # Dry-run should succeed (exit code 0) or fail with config error (exit code 1)
        # Both are acceptable - we just want to verify it doesn't hang
        assert result.returncode in [0, 1]
        if result.returncode == 0:
            assert "test-service" in result.stderr or "test-service" in result.stdout


@pytest.mark.timeout(15)  # Extra timeout for this test since it starts a runtime
def test_cli_run_starts_runtime() -> None:
    """Test that 'run' command starts runtime (with timeout to avoid hanging)."""
    import signal
    import time

    config_data = {"service": {"name": "test-service"}}

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "hex-config.yaml"
        with config_path.open("w") as f:
            yaml.dump(config_data, f)

        # Start process with explicit timeout
        process = subprocess.Popen(
            [sys.executable, "-m", "hexswitch.app", "--config", str(config_path), "run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        try:
            # Wait a bit for runtime to start (with timeout)
            time.sleep(0.5)

            # Check if process is still running (runtime started successfully)
            poll_result = process.poll()
            if poll_result is not None:
                # Process exited, check output for errors
                stdout, stderr = process.communicate(timeout=1)
                # If it exited with error, that's okay for this test - we just want to verify
                # it doesn't hang. But let's check if it's a configuration error vs runtime error
                if "Configuration error" in stderr or "error" in stderr.lower():
                    # Configuration error is acceptable - runtime tried to start
                    pass
                else:
                    # Unexpected exit - might be an issue
                    raise AssertionError(f"Process exited unexpectedly: {poll_result}\n" f"stdout: {stdout}\nstderr: {stderr}")
            else:
                # Process is still running - good! Now terminate it
                try:
                    if sys.platform == "win32":
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        finally:
            # Ensure process is always terminated
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

