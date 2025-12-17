"""Unit tests for logging module."""

import io
import json
import logging
import sys
from unittest.mock import patch

import pytest

from hexswitch.shared.logging import (
    LogFormat,
    LoggingConfig,
    get_logger,
    setup_logging,
)


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == LogFormat.TEXT
        assert config.include_timestamp is True
        assert config.service_name is None
        assert config.logger_name == "hexswitch"
        assert config.stream == sys.stderr

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        stream = io.StringIO()
        config = LoggingConfig(
            level="DEBUG",
            format=LogFormat.JSON,
            include_timestamp=False,
            service_name="test-service",
            logger_name="test",
            stream=stream,
            extra_fields={"env": "test"},
        )
        assert config.level == "DEBUG"
        assert config.format == LogFormat.JSON
        assert config.include_timestamp is False
        assert config.service_name == "test-service"
        assert config.logger_name == "test"
        assert config.stream == stream
        assert config.extra_fields == {"env": "test"}

    def test_invalid_level(self) -> None:
        """Test that invalid log level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level"):
            LoggingConfig(level="INVALID")


class TestSetupLogging:
    """Test setup_logging function."""

    def test_setup_text_logging(self) -> None:
        """Test setting up text logging."""
        stream = io.StringIO()
        setup_logging(
            level="INFO",
            format=LogFormat.TEXT,
            stream=stream,
            service_name="test-service",
        )

        logger = logging.getLogger("hexswitch")
        logger.info("Test message")

        output = stream.getvalue()
        assert "Test message" in output
        assert "INFO" in output
        assert "test-service" in output

    def test_setup_json_logging(self) -> None:
        """Test setting up JSON logging."""
        stream = io.StringIO()
        setup_logging(
            level="INFO",
            format=LogFormat.JSON,
            stream=stream,
            service_name="test-service",
        )

        logger = logging.getLogger("hexswitch")
        logger.info("Test message")

        output = stream.getvalue()
        log_data = json.loads(output.strip())
        assert log_data["message"] == "Test message"
        assert log_data["level"] == "INFO"
        assert log_data["service"] == "test-service"

    def test_setup_logging_with_extra_fields(self) -> None:
        """Test setting up logging with extra fields."""
        stream = io.StringIO()
        setup_logging(
            level="INFO",
            format=LogFormat.JSON,
            stream=stream,
            extra_fields={"env": "test", "version": "1.0.0"},
        )

        logger = logging.getLogger("hexswitch")
        logger.info("Test message")

        output = stream.getvalue()
        log_data = json.loads(output.strip())
        assert log_data["env"] == "test"
        assert log_data["version"] == "1.0.0"

    def test_setup_logging_different_levels(self) -> None:
        """Test setting up logging with different levels."""
        stream = io.StringIO()
        setup_logging(level="DEBUG", stream=stream)

        logger = logging.getLogger("hexswitch")
        logger.debug("Debug message")
        logger.info("Info message")

        output = stream.getvalue()
        assert "Debug message" in output
        assert "Info message" in output

    def test_setup_logging_custom_logger_name(self) -> None:
        """Test setting up logging with custom logger name."""
        stream = io.StringIO()
        setup_logging(level="INFO", logger_name="custom", stream=stream)

        logger = logging.getLogger("custom")
        logger.info("Test message")

        output = stream.getvalue()
        assert "Test message" in output

    def test_setup_logging_without_timestamp(self) -> None:
        """Test setting up logging without timestamp."""
        stream = io.StringIO()
        setup_logging(
            level="INFO",
            format=LogFormat.TEXT,
            include_timestamp=False,
            stream=stream,
        )

        logger = logging.getLogger("hexswitch")
        logger.info("Test message")

        output = stream.getvalue()
        # Should not contain timestamp format
        assert "Test message" in output

    def test_setup_logging_exception_handling(self) -> None:
        """Test logging exception information."""
        stream = io.StringIO()
        setup_logging(level="ERROR", format=LogFormat.JSON, stream=stream)

        logger = logging.getLogger("hexswitch")
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.exception("Exception occurred")

        output = stream.getvalue()
        log_data = json.loads(output.strip())
        assert log_data["level"] == "ERROR"
        assert "exception" in log_data
        assert "Test error" in log_data["exception"]


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_default(self) -> None:
        """Test getting logger with default settings."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "hexswitch.test_module"

    def test_get_logger_custom_root(self) -> None:
        """Test getting logger with custom root name."""
        logger = get_logger("test_module", logger_name="custom")
        assert logger.name == "custom.test_module"

    def test_get_logger_root_logger(self) -> None:
        """Test getting logger with root logger name."""
        logger = get_logger("test_module", logger_name="root")
        assert logger.name == "test_module"

    def test_get_logger_propagate(self) -> None:
        """Test logger propagation setting."""
        logger = get_logger("test_module", propagate=False)
        assert logger.propagate is False

        logger2 = get_logger("test_module2", propagate=True)
        assert logger2.propagate is True

    def test_get_logger_usage(self) -> None:
        """Test that logger from get_logger works correctly."""
        stream = io.StringIO()
        setup_logging(level="INFO", stream=stream)

        logger = get_logger("test_module")
        logger.info("Test message")

        output = stream.getvalue()
        assert "Test message" in output
        assert "test_module" in output

    def test_get_logger_prevents_duplication(self) -> None:
        """Test that get_logger prevents duplicate logger name prefixes."""
        logger1 = get_logger("hexswitch.runtime")
        assert logger1.name == "hexswitch.runtime"

        logger2 = get_logger("hexswitch.app")
        assert logger2.name == "hexswitch.app"

        logger3 = get_logger("other.module", logger_name="hexswitch")
        assert logger3.name == "hexswitch.other.module"


class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_logging_integration(self) -> None:
        """Test complete logging workflow."""
        stream = io.StringIO()
        setup_logging(
            level="DEBUG",
            format=LogFormat.JSON,
            stream=stream,
            service_name="integration-test",
            extra_fields={"test": True},
        )

        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        logger1.debug("Debug message")
        logger2.info("Info message")
        logger1.warning("Warning message")
        logger2.error("Error message")

        output = stream.getvalue()
        lines = [json.loads(line.strip()) for line in output.strip().split("\n") if line.strip()]

        assert len(lines) == 4
        assert all(line["service"] == "integration-test" for line in lines)
        assert all(line["test"] is True for line in lines)
        assert lines[0]["level"] == "DEBUG"
        assert lines[1]["level"] == "INFO"
        assert lines[2]["level"] == "WARNING"
        assert lines[3]["level"] == "ERROR"

    def test_multiple_setup_calls(self) -> None:
        """Test that multiple setup calls don't create duplicate handlers."""
        stream = io.StringIO()
        setup_logging(level="INFO", stream=stream)
        setup_logging(level="INFO", stream=stream)

        logger = logging.getLogger("hexswitch")
        # Should only have one handler (duplicates are removed)
        assert len(logger.handlers) == 1

