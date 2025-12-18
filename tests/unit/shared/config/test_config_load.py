"""Unit tests for config loading functions."""

import tempfile
from pathlib import Path

import pytest
import yaml

from hexswitch.shared.config.config import ConfigError, load_config


class TestLoadConfig:
    """Test load_config function."""

    def test_load_config_from_file(self) -> None:
        """Test loading config from file."""
        config_data = {
            "service": {"name": "test-service"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            config = load_config(config_path)
            assert config["service"]["name"] == "test-service"
        finally:
            Path(config_path).unlink()

    def test_load_config_file_not_found(self) -> None:
        """Test loading config from non-existent file."""
        with pytest.raises(ConfigError, match="not found"):
            load_config("/nonexistent/path/config.yaml")

    def test_load_config_invalid_yaml(self) -> None:
        """Test loading config with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            with pytest.raises(ConfigError, match="Invalid YAML"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()

    def test_load_config_empty_file(self) -> None:
        """Test loading empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            config_path = f.name

        try:
            with pytest.raises(ConfigError, match="empty"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()

    def test_load_config_not_dict(self) -> None:
        """Test loading config that is not a dictionary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(["list", "not", "dict"], f)
            config_path = f.name

        try:
            with pytest.raises(ConfigError, match="must be a dictionary"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()

    def test_load_config_file_read_error(self) -> None:
        """Test loading config with file read error."""
        # Create a path that exists but is a directory (will cause read error)
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ConfigError, match="Error reading"):
                load_config(tmpdir)

