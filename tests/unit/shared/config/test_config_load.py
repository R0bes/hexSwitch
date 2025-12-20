"""Unit tests for config loading functions."""

from pathlib import Path
import tempfile

import pytest
import tomli_w

from hexswitch.shared.config.config import ConfigError, load_config


class TestLoadConfig:
    """Test load_config function."""

    def test_load_config_from_file(self) -> None:
        """Test loading config from file."""
        config_data = {
            "service": {"name": "test-service"},
        }

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
            f.write(tomli_w.dumps(config_data).encode("utf-8"))
            config_path = f.name

        try:
            config = load_config(config_path)
            assert config["service"]["name"] == "test-service"
        finally:
            Path(config_path).unlink()

    def test_load_config_file_not_found(self) -> None:
        """Test loading config from non-existent file."""
        with pytest.raises(ConfigError, match="not found"):
            load_config("/nonexistent/path/config.toml")

    def test_load_config_invalid_toml(self) -> None:
        """Test loading config with invalid TOML."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
            f.write(b"invalid toml content [")
            config_path = f.name

        try:
            with pytest.raises(ConfigError, match="Invalid TOML"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()

    def test_load_config_empty_file(self) -> None:
        """Test loading empty config file."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
            f.write(b"")
            config_path = f.name

        try:
            with pytest.raises(ConfigError, match="empty"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()

    def test_load_config_not_dict(self) -> None:
        """Test loading config that is not a dictionary."""
        # TOML always parses to a dict (root must be a table)
        # This test is less relevant for TOML, but we keep it for completeness
        # Empty file is already tested above
        pass

    def test_load_config_file_read_error(self) -> None:
        """Test loading config with file read error."""
        # Create a path that exists but is a directory (will cause read error)
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ConfigError, match="Error reading"):
                load_config(tmpdir)

