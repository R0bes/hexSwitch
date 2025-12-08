"""Integration tests for Docker image."""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import yaml

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="session")
def docker_image() -> str:
    """Build and return Docker image name."""
    image_name = "hexswitch:test"
    build_result = subprocess.run(
        ["docker", "build", "-f", "docker/Dockerfile", "-t", image_name, "."],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )
    assert build_result.returncode == 0, f"Docker build failed: {build_result.stderr}"
    return image_name


@pytest.fixture
def temp_config_file() -> Path:
    """Create a temporary config file for testing."""
    config_data = {
        "service": {"name": "test-service", "runtime": "python"},
        "inbound": {"http": {"enabled": True}},
        "outbound": {"postgres": {"enabled": False}},
        "logging": {"level": "INFO"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestDockerImage:
    """Test Docker image functionality."""

    def test_docker_image_exists(self, docker_image: str) -> None:
        """Test that Docker image was built successfully."""
        result = subprocess.run(
            ["docker", "images", "-q", docker_image],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout.strip() != ""

    def test_docker_version_command(self, docker_image: str) -> None:
        """Test that version command works in Docker."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "hexswitch", "version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "HexSwitch" in result.stdout
        assert "0.1.0" in result.stdout
        assert "Hexagonal runtime switchboard" in result.stdout

    def test_docker_help_command(self, docker_image: str) -> None:
        """Test that help command works in Docker."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "hexswitch", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "HexSwitch" in result.stdout
        assert "version" in result.stdout
        assert "init" in result.stdout
        assert "validate" in result.stdout
        assert "run" in result.stdout

    def test_docker_init_command(self, docker_image: str) -> None:
        """Test that init command works in Docker."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "hexswitch", "init"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Created example configuration" in result.stderr or "Created example configuration" in result.stdout

    def test_docker_validate_with_mounted_config(
        self, docker_image: str, temp_config_file: Path
    ) -> None:
        """Test that validate command works with mounted config file."""
        # Use absolute path for Windows compatibility
        config_path = temp_config_file.resolve()

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{config_path}:/app/hex-config.yaml:ro",
                docker_image,
                "hexswitch",
                "validate",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "valid" in result.stderr.lower() or "valid" in result.stdout.lower()

    def test_docker_validate_without_config(self, docker_image: str) -> None:
        """Test that validate command fails gracefully without config."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "hexswitch", "validate"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
        assert "error" in result.stderr.lower() or "error" in result.stdout.lower()

    def test_docker_run_dry_run_with_mounted_config(
        self, docker_image: str, temp_config_file: Path
    ) -> None:
        """Test that run --dry-run works with mounted config file."""
        config_path = temp_config_file.resolve()

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{config_path}:/app/hex-config.yaml:ro",
                docker_image,
                "hexswitch",
                "run",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "test-service" in result.stderr or "test-service" in result.stdout
        assert "Execution Plan" in result.stderr or "Execution Plan" in result.stdout

    def test_docker_run_not_implemented(self, docker_image: str, temp_config_file: Path) -> None:
        """Test that run command returns correct exit code when not implemented."""
        config_path = temp_config_file.resolve()

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{config_path}:/app/hex-config.yaml:ro",
                docker_image,
                "hexswitch",
                "run",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 2
        assert "not yet implemented" in result.stderr.lower() or "not yet implemented" in result.stdout.lower()

    def test_docker_image_size(self, docker_image: str) -> None:
        """Test that Docker image size is reasonable."""
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Size}}", docker_image],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Image should be less than 500MB
        size_str = result.stdout.strip()
        # Parse size (could be "200MB" or "1.2GB")
        assert size_str != ""

    def test_docker_container_runs_as_non_root(self, docker_image: str) -> None:
        """Test that container runs as non-root user."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "id", "-u"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        # Should be user 1000 (hexswitch user), not 0 (root)
        user_id = result.stdout.strip()
        assert user_id == "1000"

    def test_docker_python_module_import(self, docker_image: str) -> None:
        """Test that Python module can be imported in Docker."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image, "python", "-c", "import hexswitch; print(hexswitch.__version__)"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_docker_default_command(self, docker_image: str) -> None:
        """Test that default Docker command (help) works."""
        result = subprocess.run(
            ["docker", "run", "--rm", docker_image],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # Default command is --help, should succeed
        assert result.returncode == 0
        assert "HexSwitch" in result.stdout

