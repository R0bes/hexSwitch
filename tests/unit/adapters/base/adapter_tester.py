"""Comprehensive adapter testing utility with security focus."""

import asyncio
import logging
import socket
import threading
import time
from typing import Any, Callable

import pytest

from hexswitch.adapters.exceptions import AdapterConnectionError, AdapterStartError, AdapterStopError
from hexswitch.adapters.base import InboundAdapter, OutboundAdapter

logger = logging.getLogger(__name__)


class AdapterTester:
    """Utility class for comprehensive adapter testing."""

    @staticmethod
    def find_free_port() -> int:
        """Find a free port for testing.

        Returns:
            Free port number.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @staticmethod
    def test_inbound_lifecycle(
        adapter_class: type[InboundAdapter],
        config_factory: Callable[[], dict[str, Any]],
        sleep_time: float = 0.2,
    ) -> None:
        """Test standard inbound adapter lifecycle.

        Args:
            adapter_class: Adapter class to test.
            config_factory: Function that returns adapter config.
            sleep_time: Time to wait after start.
        """
        config = config_factory()
        if "port" in config and config["port"] == 0:
            config["port"] = AdapterTester.find_free_port()

        adapter = adapter_class("test", config)
        assert adapter.is_running() is False

        adapter.start()
        assert adapter.is_running() is True
        time.sleep(sleep_time)

        adapter.stop()
        assert adapter.is_running() is False

    @staticmethod
    def test_outbound_lifecycle(
        adapter_class: type[OutboundAdapter],
        config_factory: Callable[[], dict[str, Any]],
    ) -> None:
        """Test standard outbound adapter lifecycle.

        Args:
            adapter_class: Adapter class to test.
            config_factory: Function that returns adapter config.
        """
        config = config_factory()
        adapter = adapter_class("test", config)
        assert adapter.is_connected() is False

        # Try to connect (may fail if server not available, that's OK)
        try:
            adapter.connect()
            assert adapter.is_connected() is True
            adapter.disconnect()
            assert adapter.is_connected() is False
        except AdapterConnectionError:
            # Expected if server not running
            pass

    @staticmethod
    def test_start_twice(
        adapter_class: type[InboundAdapter],
        config_factory: Callable[[], dict[str, Any]],
        sleep_time: float = 0.2,
    ) -> None:
        """Test starting adapter twice doesn't cause errors.

        Args:
            adapter_class: Adapter class to test.
            config_factory: Function that returns adapter config.
            sleep_time: Time to wait after start.
        """
        config = config_factory()
        if "port" in config and config["port"] == 0:
            config["port"] = AdapterTester.find_free_port()

        adapter = adapter_class("test", config)
        adapter.start()
        time.sleep(sleep_time)
        adapter.start()  # Should not raise error
        adapter.stop()

    @staticmethod
    def test_stop_when_not_running(
        adapter_class: type[InboundAdapter],
        config_factory: Callable[[], dict[str, Any]],
    ) -> None:
        """Test stopping adapter when not running doesn't cause errors.

        Args:
            adapter_class: Adapter class to test.
            config_factory: Function that returns adapter config.
        """
        config = config_factory()
        adapter = adapter_class("test", config)
        adapter.stop()  # Should not raise error
        assert adapter.is_running() is False

    @staticmethod
    def test_connect_twice(
        adapter_class: type[OutboundAdapter],
        config_factory: Callable[[], dict[str, Any]],
    ) -> None:
        """Test connecting adapter twice doesn't cause errors.

        Args:
            adapter_class: Adapter class to test.
            config_factory: Function that returns adapter config.
        """
        config = config_factory()
        adapter = adapter_class("test", config)

        try:
            adapter.connect()
            adapter.connect()  # Should not raise error
            adapter.disconnect()
        except AdapterConnectionError:
            # Expected if server not running
            pass

    @staticmethod
    def test_disconnect_when_not_connected(
        adapter_class: type[OutboundAdapter],
        config_factory: Callable[[], dict[str, Any]],
    ) -> None:
        """Test disconnecting adapter when not connected doesn't cause errors.

        Args:
            adapter_class: Adapter class to test.
            config_factory: Function that returns adapter config.
        """
        config = config_factory()
        adapter = adapter_class("test", config)
        adapter.disconnect()  # Should not raise error
        assert adapter.is_connected() is False

    @staticmethod
    def test_initialization(
        adapter_class: type[InboundAdapter] | type[OutboundAdapter],
        config: dict[str, Any],
        expected_attrs: dict[str, Any] | None = None,
    ) -> None:
        """Test adapter initialization.

        Args:
            adapter_class: Adapter class to test.
            config: Adapter configuration.
            expected_attrs: Dictionary of expected attribute values.
        """
        adapter = adapter_class("test", config)
        assert adapter.name == "test"
        assert adapter.config == config

        if expected_attrs:
            for attr, value in expected_attrs.items():
                assert hasattr(adapter, attr)
                assert getattr(adapter, attr) == value

        if isinstance(adapter, InboundAdapter):
            assert adapter.is_running() is False
        else:
            assert adapter.is_connected() is False

    @staticmethod
    def test_concurrent_requests(
        adapter: InboundAdapter,
        num_threads: int = 10,
        requests_per_thread: int = 100,
    ) -> None:
        """Test concurrent requests to adapter.

        Args:
            adapter: Running adapter instance.
            num_threads: Number of concurrent threads.
            requests_per_thread: Requests per thread.
        """
        if not adapter.is_running():
            pytest.skip("Adapter not running")

        # This is a placeholder - adapter-specific implementations needed
        # Each adapter will have its own concurrent request test
        pass

    @staticmethod
    def create_malicious_payloads() -> list[str]:
        """Create list of malicious payloads for security testing.

        Returns:
            List of malicious payload strings.
        """
        return [
            # SQL Injection
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users--",
            # XSS
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            # Path Traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            # Command Injection
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            # Buffer Overflow attempts
            "A" * 10000,
            "\x00" * 1000,
            # Protocol anomalies
            "\r\n\r\n",
            "\x00\x01\x02",
        ]

    @staticmethod
    def generate_load_pattern(pattern_type: str) -> list[dict[str, Any]]:
        """Generate load patterns for stress testing.

        Args:
            pattern_type: Type of load pattern ('burst', 'steady', 'ramp').

        Returns:
            List of request configurations.
        """
        if pattern_type == "burst":
            return [{"delay": 0} for _ in range(100)]
        elif pattern_type == "steady":
            return [{"delay": 0.1} for _ in range(100)]
        elif pattern_type == "ramp":
            return [{"delay": i * 0.01} for i in range(100)]
        return []




