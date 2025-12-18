"""Unit tests for config functions."""

import tempfile
from pathlib import Path

import pytest
import yaml

from hexswitch.shared.config.config import ConfigError, load_config, validate_config


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


class TestValidateConfig:
    """Test validate_config function."""

    def test_validate_minimal_config(self) -> None:
        """Test validation of minimal config."""
        config = {
            "service": {"name": "test-service"},
        }
        validate_config(config)  # Should not raise

    def test_validate_config_with_all_adapters(self) -> None:
        """Test validation with all adapter types."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "http": {"enabled": True, "port": 8000},
                "grpc": {"enabled": True, "port": 50051},
                "websocket": {"enabled": True, "port": 8080},
                "nats": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "subjects": [{"subject": "test", "port": "test_handler"}],
                },
            },
            "outbound": {
                "http_client": {"enabled": True, "base_url": "http://localhost:8000"},
                "grpc_client": {"enabled": True, "server_url": "localhost:50051"},
                "websocket_client": {"enabled": True, "url": "ws://localhost:9000"},
                "mcp_client": {"enabled": True, "server_url": "https://mcp.example.com"},
                "nats_client": {"enabled": True, "servers": ["nats://localhost:4222"]},
            },
        }
        validate_config(config)  # Should not raise

    def test_validate_config_invalid_service(self) -> None:
        """Test validation fails with invalid service config."""
        config = {}  # Missing service
        with pytest.raises(ConfigError):
            validate_config(config)

