"""Unit tests for configuration loading and validation."""

import tempfile
from pathlib import Path

import pytest
import yaml

from hexswitch.config import (
    ConfigError,
    DEFAULT_CONFIG_PATH,
    get_example_config,
    load_config,
    validate_config,
)


def test_load_config_file_not_found() -> None:
    """Test that loading non-existent config file raises ConfigError."""
    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config("nonexistent-config.yaml")


def test_load_config_invalid_yaml() -> None:
    """Test that loading invalid YAML raises ConfigError."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content: [")
        f.flush()
        temp_path = Path(f.name)

    try:
        with pytest.raises(ConfigError, match="Invalid YAML syntax"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_load_config_empty_file() -> None:
    """Test that loading empty config file raises ConfigError."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("")
        f.flush()
        temp_path = Path(f.name)

    try:
        with pytest.raises(ConfigError, match="Configuration file is empty"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_load_config_valid() -> None:
    """Test loading valid configuration file."""
    config_data = {
        "service": {"name": "test-service", "runtime": "python"},
        "inbound": {"http": {"enabled": True}},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()
        temp_path = Path(f.name)

    try:
        config = load_config(temp_path)
        assert config["service"]["name"] == "test-service"
        assert config["inbound"]["http"]["enabled"] is True
    finally:
        temp_path.unlink()


def test_validate_config_missing_service() -> None:
    """Test that validation fails when service section is missing."""
    config = {"inbound": {}}
    with pytest.raises(ConfigError, match="Missing required section: service"):
        validate_config(config)


def test_validate_config_missing_service_name() -> None:
    """Test that validation fails when service.name is missing."""
    config = {"service": {}}
    with pytest.raises(ConfigError, match="Section 'service' must contain 'name'"):
        validate_config(config)


def test_validate_config_invalid_inbound_type() -> None:
    """Test that validation fails when inbound is not a dictionary."""
    config = {"service": {"name": "test"}, "inbound": "invalid"}
    with pytest.raises(ConfigError, match="Section 'inbound' must be a dictionary"):
        validate_config(config)


def test_validate_config_adapter_enabled_not_boolean() -> None:
    """Test that validation fails when adapter enabled flag is not boolean."""
    config = {
        "service": {"name": "test"},
        "inbound": {"http": {"enabled": "yes"}},
    }
    with pytest.raises(ConfigError, match="'enabled' must be a boolean"):
        validate_config(config)


def test_validate_config_valid() -> None:
    """Test that validation passes for valid configuration."""
    config = {
        "service": {"name": "test-service", "runtime": "python"},
        "inbound": {"http": {"enabled": True}},
        "outbound": {"postgres": {"enabled": False}},
        "logging": {"level": "INFO"},
    }
    # Should not raise
    validate_config(config)


def test_validate_config_minimal() -> None:
    """Test that validation passes for minimal valid configuration."""
    config = {"service": {"name": "test-service"}}
    # Should not raise
    validate_config(config)


def test_get_example_config() -> None:
    """Test that example config is valid YAML and structure."""
    example = get_example_config()
    assert isinstance(example, str)

    # Parse as YAML to verify it's valid
    config = yaml.safe_load(example)
    assert isinstance(config, dict)
    assert "service" in config
    assert config["service"]["name"] == "example-service"


def test_default_config_path() -> None:
    """Test that DEFAULT_CONFIG_PATH is set correctly."""
    assert DEFAULT_CONFIG_PATH == "hex-config.yaml"

