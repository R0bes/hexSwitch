"""Unit tests for configuration loading and validation."""

from pathlib import Path
import tempfile

import pytest
import tomli_w
import tomllib

from hexswitch.shared.config import (
    DEFAULT_CONFIG_PATH,
    ConfigError,
    get_example_config,
    load_config,
    validate_config,
)


def test_load_config_file_not_found() -> None:
    """Test that loading non-existent config file raises ConfigError."""
    with pytest.raises(ConfigError, match="Configuration file not found"):
        load_config("nonexistent-config.toml")


def test_load_config_invalid_toml() -> None:
    """Test that loading invalid TOML raises ConfigError."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(b"invalid toml content [")
        f.flush()
        temp_path = Path(f.name)

    try:
        with pytest.raises(ConfigError, match="Invalid TOML"):
            load_config(temp_path)
    finally:
        temp_path.unlink()


def test_load_config_empty_file() -> None:
    """Test that loading empty config file raises ConfigError."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(b"")
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

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".toml", delete=False) as f:
        f.write(tomli_w.dumps(config_data).encode("utf-8"))
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
    with pytest.raises(ConfigError):
        validate_config(config)


def test_validate_config_missing_service_name() -> None:
    """Test that validation fails when service.name is missing."""
    config = {"service": {}}
    with pytest.raises(ConfigError):
        validate_config(config)


def test_validate_config_invalid_inbound_type() -> None:
    """Test that validation fails when inbound is not a dictionary."""
    config = {"service": {"name": "test"}, "inbound": "invalid"}
    with pytest.raises(ConfigError):
        validate_config(config)


def test_validate_config_adapter_enabled_not_boolean() -> None:
    """Test that validation fails when adapter enabled flag is not boolean.

    Note: Pydantic automatically converts truthy strings to True, so we test with
    a value that cannot be converted to boolean.
    """
    config = {
        "service": {"name": "test"},
        "inbound": {"http": {"enabled": 123}},  # Integer, not boolean
    }
    with pytest.raises(ConfigError):
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
    """Test that example config is valid TOML and structure."""
    example = get_example_config()
    assert isinstance(example, str)

    # Parse as TOML to verify it's valid
    import io
    config = tomllib.load(io.BytesIO(example.encode("utf-8")))
    assert isinstance(config, dict)
    assert "service" in config
    assert config["service"]["name"] == "example-service"


def test_default_config_path() -> None:
    """Test that DEFAULT_CONFIG_PATH is set correctly."""
    assert DEFAULT_CONFIG_PATH == "hex-config.toml"

