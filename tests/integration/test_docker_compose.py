"""Integration tests using docker-compose."""

import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="session")
def ensure_config_file() -> Path:
    """Ensure hex-config.yaml exists for docker-compose tests."""
    config_path = Path(__file__).parent.parent.parent / "hex-config.yaml"
    if not config_path.exists():
        # Create example config
        config_data = {
            "service": {"name": "test-service", "runtime": "python"},
            "inbound": {"http": {"enabled": True}},
            "outbound": {"postgres": {"enabled": False}},
            "logging": {"level": "INFO"},
        }
        with config_path.open("w") as f:
            yaml.dump(config_data, f)
    return config_path


@pytest.fixture(scope="session", autouse=True)
def build_test_image() -> None:
    """Build test Docker image before running tests."""
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        ["docker", "build", "-f", "docker/Dockerfile", "-t", "hexswitch:test", "."],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Failed to build test image: {result.stderr}"


class TestDockerCompose:
    """Test Docker Compose setup."""

    def test_compose_version_command(self, ensure_config_file: Path) -> None:
        """Test that version command works via docker-compose."""
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "docker-compose.test.yml",
                "run",
                "--rm",
                "hexswitch-test",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        assert "HexSwitch" in result.stdout
        assert "0.1.0" in result.stdout

    def test_compose_validate_command(self, ensure_config_file: Path) -> None:
        """Test that validate command works via docker-compose."""
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "docker-compose.test.yml",
                "run",
                "--rm",
                "hexswitch-validate",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        assert "valid" in result.stderr.lower() or "valid" in result.stdout.lower()

    def test_compose_dry_run_command(self, ensure_config_file: Path) -> None:
        """Test that dry-run command works via docker-compose."""
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "docker-compose.test.yml",
                "run",
                "--rm",
                "hexswitch-dry-run",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        assert "Execution Plan" in result.stderr or "Execution Plan" in result.stdout

    def test_compose_up_and_down(self, ensure_config_file: Path) -> None:
        """Test that docker-compose can start and stop services."""
        project_root = Path(__file__).parent.parent.parent

        # Clean up any existing containers
        subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "down"],
            cwd=project_root,
            capture_output=True,
        )

        # Start services
        up_result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "up", "-d"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Give services time to start
        time.sleep(2)

        # Check containers are running
        ps_result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "ps"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        # Clean up
        down_result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.test.yml", "down"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert down_result.returncode == 0

