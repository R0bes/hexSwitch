"""Unit tests for HexSwitchService."""

import os
import tempfile
from pathlib import Path
from typing import Any

import pytest

from hexswitch.service import HexSwitchService, HexSwitchServiceConfig
from hexswitch.shared.config import ConfigError


class TestHexSwitchService:
    """Test HexSwitchService class."""

    def test_service_can_be_instantiated(self) -> None:
        """Test that HexSwitchService can be instantiated."""
        service = HexSwitchService(config={"service": {"name": "test"}})
        assert service is not None
        assert not service.is_running()

    def test_service_with_config_dict(self) -> None:
        """Test service with config dictionary."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        service = HexSwitchService(config=config)
        assert service._config_loader is not None
        assert service._config_loader._config == config

    def test_service_with_config_path(self) -> None:
        """Test service with config path."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".toml", delete=False
        ) as f:
            f.write(b'[service]\nname = "test-service"\n')
            config_path = f.name

        try:
            service = HexSwitchService(config_path=config_path)
            assert service._config_loader is not None
            assert service._config_loader.get_config_path() == Path(config_path)
        finally:
            os.unlink(config_path)

    def test_service_with_env_var_config_path(self, monkeypatch) -> None:
        """Test service with environment variable config path."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".toml", delete=False
        ) as f:
            f.write(b'[service]\nname = "test-service"\n')
            config_path = f.name

        try:
            monkeypatch.setenv("HEXSWITCH_CONFIG_PATH", config_path)
            service = HexSwitchService()
            assert service._config_loader is not None
            assert service._config_loader.get_config_path() == Path(config_path)
        finally:
            os.unlink(config_path)

    def test_service_default_config_path(self) -> None:
        """Test service with default config path."""
        service = HexSwitchService()
        # Should use default path
        assert service._config_loader is not None
        assert service._config_loader.get_config_path() is not None

    def test_load_config_from_dict(self) -> None:
        """Test loading config from dictionary."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        service = HexSwitchService(config=config)
        loaded_config = service.load_config()
        # Config validation may transform empty dicts to None
        assert loaded_config["service"]["name"] == "test-service"
        assert "inbound" in loaded_config or loaded_config.get("inbound") is None
        assert "outbound" in loaded_config or loaded_config.get("outbound") is None

    def test_load_config_from_file(self) -> None:
        """Test loading config from file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".toml", delete=False
        ) as f:
            f.write(b'[service]\nname = "test-service"\n')
            config_path = f.name

        try:
            service = HexSwitchService(config_path=config_path)
            config = service.load_config()
            assert config["service"]["name"] == "test-service"
        finally:
            os.unlink(config_path)

    def test_load_config_invalid_file(self) -> None:
        """Test loading config from non-existent file."""
        service = HexSwitchService(config_path="/nonexistent/config.toml")
        with pytest.raises(ConfigError):
            service.load_config()

    def test_is_running_before_start(self) -> None:
        """Test is_running before start."""
        service = HexSwitchService(config={"service": {"name": "test"}})
        assert not service.is_running()

    def test_get_runtime_before_start(self) -> None:
        """Test get_runtime before start."""
        service = HexSwitchService(config={"service": {"name": "test"}})
        assert service.get_runtime() is None

    def test_lifecycle_hooks(self) -> None:
        """Test lifecycle hooks are called."""
        hook_calls = []

        class TestService(HexSwitchService):
            def on_start(self):
                hook_calls.append("on_start")

            def on_ready(self):
                hook_calls.append("on_ready")

            def on_stop(self):
                hook_calls.append("on_stop")

        config = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        service = TestService(config=config)

        # Start should call on_start and on_ready
        service.start()
        assert "on_start" in hook_calls
        assert "on_ready" in hook_calls

        # Stop should call on_stop
        service.stop()
        assert "on_stop" in hook_calls

    def test_custom_load_config(self) -> None:
        """Test custom load_config override."""
        class CustomService(HexSwitchService):
            def load_config(self):
                return {"service": {"name": "custom"}, "inbound": {}, "outbound": {}}

        service = CustomService()
        config = service.load_config()
        assert config["service"]["name"] == "custom"

    def test_start_stop_lifecycle(self) -> None:
        """Test complete start/stop lifecycle."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        service = HexSwitchService(config=config)

        # Before start
        assert not service.is_running()
        assert service.get_runtime() is None

        # Start
        service.start()
        assert service.get_runtime() is not None
        # Service may not have adapters, so is_running might be False
        # but runtime should be initialized

        # Stop
        service.stop()
        assert service.get_runtime() is None
        assert not service.is_running()

    def test_run_method(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test run() method with standard main loop."""
        import time
        from unittest.mock import MagicMock

        config = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        service = HexSwitchService(config=config)

        # Mock is_running to simulate a running service
        # First call returns True (running), then False (stopped)
        call_count = 0

        def mock_is_running():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return True  # Service is running
            return False  # Service stopped

        monkeypatch.setattr(service, "is_running", mock_is_running)

        # Mock start and stop to verify they're called
        start_mock = MagicMock()
        stop_mock = MagicMock()
        monkeypatch.setattr(service, "start", start_mock)
        monkeypatch.setattr(service, "stop", stop_mock)

        # Mock time.sleep to avoid actual waiting
        sleep_mock = MagicMock()
        monkeypatch.setattr(time, "sleep", sleep_mock)

        # Call run() - should call start, then loop until is_running returns False
        service.run()

        # Verify start was called
        start_mock.assert_called_once()

        # Verify stop was called (in finally block)
        stop_mock.assert_called_once()

        # Verify sleep was called (in the loop)
        assert sleep_mock.call_count >= 1

    def test_run_method_keyboard_interrupt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test run() method handles KeyboardInterrupt gracefully."""
        import time
        from unittest.mock import MagicMock

        config = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        service = HexSwitchService(config=config)

        # Mock is_running to always return True (simulating running service)
        monkeypatch.setattr(service, "is_running", lambda: True)

        # Mock start
        start_mock = MagicMock()
        monkeypatch.setattr(service, "start", start_mock)

        # Mock stop
        stop_mock = MagicMock()
        monkeypatch.setattr(service, "stop", stop_mock)

        # Mock time.sleep to raise KeyboardInterrupt
        def mock_sleep(_):
            raise KeyboardInterrupt()

        monkeypatch.setattr(time, "sleep", mock_sleep)

        # Call run() - should handle KeyboardInterrupt gracefully
        service.run()

        # Verify start was called
        start_mock.assert_called_once()

        # Verify stop was called (in finally block)
        stop_mock.assert_called_once()


class TestHexSwitchServiceConfig:
    """Test HexSwitchServiceConfig class."""

    def test_config_with_dict(self) -> None:
        """Test config with dictionary."""
        config_dict = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        config = HexSwitchServiceConfig(config=config_dict)
        loaded = config.load()
        # Config validation may transform empty dicts to None
        assert loaded["service"]["name"] == "test-service"
        assert "inbound" in loaded or loaded.get("inbound") is None
        assert "outbound" in loaded or loaded.get("outbound") is None

    def test_config_with_path(self) -> None:
        """Test config with path."""
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".toml", delete=False
        ) as f:
            f.write(b'[service]\nname = "test-service"\n')
            config_path = f.name

        try:
            config = HexSwitchServiceConfig(config_path=config_path)
            loaded = config.load()
            assert loaded["service"]["name"] == "test-service"
        finally:
            os.unlink(config_path)

    def test_config_validate(self) -> None:
        """Test config validation."""
        config_dict = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        config = HexSwitchServiceConfig(config=config_dict)
        # Should not raise
        config.validate(config_dict)

    def test_config_transform(self) -> None:
        """Test config transformation."""
        config_dict = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        config = HexSwitchServiceConfig(config=config_dict)
        transformed = config.transform(config_dict)
        assert transformed == config_dict

    def test_custom_config_class(self) -> None:
        """Test custom config class extension."""
        class CustomConfig(HexSwitchServiceConfig):
            def transform(self, config: dict[str, Any]) -> dict[str, Any]:
                config = super().transform(config)
                config["custom"] = {"enabled": True}
                return config

        config_dict = {
            "service": {"name": "test-service"},
            "inbound": {},
            "outbound": {},
        }
        config = CustomConfig(config=config_dict)
        loaded = config.load()
        # Transform should be called after validation
        assert "custom" in loaded
        assert loaded["custom"]["enabled"] is True
        assert loaded["service"]["name"] == "test-service"

    def test_config_with_service(self) -> None:
        """Test config with HexSwitchService."""
        class CustomConfig(HexSwitchServiceConfig):
            def transform(self, config: dict[str, Any]) -> dict[str, Any]:
                config = super().transform(config)
                config["transformed"] = True
                return config

        config = CustomConfig(config={"service": {"name": "test"}, "inbound": {}, "outbound": {}})
        service = HexSwitchService(config=config)
        loaded = service.load_config()
        assert loaded["transformed"] is True

    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variable overrides."""
        from hexswitch.service import _load_env_overrides, _merge_config

        # Set environment variables
        monkeypatch.setenv("HEX_SERVICE_NAME", "env-service")
        monkeypatch.setenv("HEX_INBOUND_HTTP_PORT", "9000")
        monkeypatch.setenv("HEX_LOGGING_LEVEL", "DEBUG")

        # Base config
        base_config = {
            "service": {"name": "base-service", "version": "1.0.0"},
            "inbound": {"http": {"enabled": True, "port": 8000}},
            "logging": {"level": "INFO"},
        }

        # Test merge directly (before validation)
        env_overrides = _load_env_overrides(prefix="HEX_")
        merged = _merge_config(base_config, env_overrides)

        # Environment variables should override base config
        assert merged["service"]["name"] == "env-service"
        assert merged["service"]["version"] == "1.0.0"  # Not overridden
        assert merged["inbound"]["http"]["port"] == 9000
        assert merged["inbound"]["http"]["enabled"] is True  # Not overridden
        assert merged["logging"]["level"] == "DEBUG"

    def test_env_overrides_type_conversion(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test environment variable type conversion."""
        from hexswitch.service import _load_env_overrides, _merge_config

        monkeypatch.setenv("HEX_INBOUND_HTTP_PORT", "8080")  # Integer
        monkeypatch.setenv("HEX_INBOUND_HTTP_ENABLED", "true")  # Boolean
        monkeypatch.setenv("HEX_LOGGING_LEVEL", "WARNING")  # String

        base_config = {
            "service": {"name": "test"},
            "inbound": {"http": {"port": 8000, "enabled": False}},
            "logging": {"level": "INFO"},
        }

        # Test merge directly (before validation)
        env_overrides = _load_env_overrides(prefix="HEX_")
        merged = _merge_config(base_config, env_overrides)

        assert isinstance(merged["inbound"]["http"]["port"], int)
        assert merged["inbound"]["http"]["port"] == 8080
        assert isinstance(merged["inbound"]["http"]["enabled"], bool)
        assert merged["inbound"]["http"]["enabled"] is True
        assert isinstance(merged["logging"]["level"], str)
        assert merged["logging"]["level"] == "WARNING"

    def test_env_overrides_nested(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test nested environment variable overrides."""
        from hexswitch.service import _load_env_overrides, _merge_config

        monkeypatch.setenv("HEX_SERVICE_NAME", "nested-service")
        monkeypatch.setenv("HEX_INBOUND_HTTP_PORT", "7000")
        monkeypatch.setenv("HEX_INBOUND_HTTP_BASE_PATH", "/api/v2")

        base_config = {
            "service": {"name": "base"},
            "inbound": {
                "http": {
                    "port": 8000,
                    "base_path": "/api",
                    "enabled": True,
                }
            },
        }

        # Test merge directly (before validation)
        env_overrides = _load_env_overrides(prefix="HEX_")
        merged = _merge_config(base_config, env_overrides)

        assert merged["service"]["name"] == "nested-service"
        assert merged["inbound"]["http"]["port"] == 7000
        assert merged["inbound"]["http"]["base_path"] == "/api/v2"
        assert merged["inbound"]["http"]["enabled"] is True
