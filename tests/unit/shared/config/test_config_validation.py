"""Unit tests for config validation."""

import pytest

from hexswitch.shared.config.config import ConfigError, validate_config
from hexswitch.shared.config.models import ConfigModel


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_minimal_config(self) -> None:
        """Test validation of minimal config."""
        config = {
            "service": {"name": "test-service"},
        }
        validate_config(config)  # Should not raise

    def test_validate_config_with_nats(self) -> None:
        """Test validation of config with NATS."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "subjects": [
                        {
                            "subject": "test.subject",
                            "port": "test_handler",
                        }
                    ],
                }
            },
        }
        validate_config(config)  # Should not raise

    def test_validate_config_with_nats_client(self) -> None:
        """Test validation of config with NATS client."""
        config = {
            "service": {"name": "test-service"},
            "outbound": {
                "nats_client": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "timeout": 30.0,
                }
            },
        }
        validate_config(config)  # Should not raise

    def test_validate_config_with_gui(self) -> None:
        """Test validation of config with GUI."""
        config = {
            "service": {
                "name": "test-service",
                "gui": {
                    "enabled": True,
                    "port": 8080,
                },
            },
        }
        validate_config(config)  # Should not raise

    def test_validate_nats_subject_without_handler_or_port(self) -> None:
        """Test validation fails when NATS subject has no handler or port."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "subjects": [
                        {
                            "subject": "test.subject",
                        }
                    ],
                }
            },
        }
        with pytest.raises(ConfigError):
            validate_config(config)

    def test_validate_nats_subject_with_invalid_handler(self) -> None:
        """Test validation fails with invalid handler format."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "subjects": [
                        {
                            "subject": "test.subject",
                            "handler": "invalid_format",
                        }
                    ],
                }
            },
        }
        with pytest.raises(ConfigError):
            validate_config(config)

    def test_validate_nats_servers_string(self) -> None:
        """Test validation with NATS servers as string."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": "nats://localhost:4222",
                    "subjects": [
                        {
                            "subject": "test.subject",
                            "port": "test_handler",
                        }
                    ],
                }
            },
        }
        validate_config(config)  # Should not raise

    def test_validate_nats_servers_list(self) -> None:
        """Test validation with NATS servers as list."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": ["nats://server1:4222", "nats://server2:4222"],
                    "subjects": [
                        {
                            "subject": "test.subject",
                            "port": "test_handler",
                        }
                    ],
                }
            },
        }
        validate_config(config)  # Should not raise

    def test_validate_nats_with_queue_group(self) -> None:
        """Test validation with NATS queue group."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "subjects": [
                        {
                            "subject": "test.subject",
                            "port": "test_handler",
                        }
                    ],
                    "queue_group": "workers",
                }
            },
        }
        validate_config(config)  # Should not raise

    def test_config_model_from_dict_with_nats(self) -> None:
        """Test ConfigModel.from_dict with NATS config."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "nats": {
                    "enabled": True,
                    "servers": ["nats://localhost:4222"],
                    "subjects": [
                        {
                            "subject": "test.subject",
                            "port": "test_handler",
                        }
                    ],
                }
            },
        }
        model = ConfigModel.from_dict(config)
        assert model.inbound is not None
        assert model.inbound.nats is not None
        assert model.inbound.nats.enabled is True

    def test_config_model_from_dict_with_gui(self) -> None:
        """Test ConfigModel.from_dict with GUI config."""
        config = {
            "service": {
                "name": "test-service",
                "gui": {
                    "enabled": True,
                    "port": 8080,
                },
            },
        }
        model = ConfigModel.from_dict(config)
        assert model.service.gui is not None
        assert model.service.gui.enabled is True
        assert model.service.gui.port == 8080

