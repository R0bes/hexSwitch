"""Integration tests for runtime lifecycle: clean start and stop without hanging threads/tasks."""

import socket
import threading
import time

import pytest

from hexswitch.runtime import Runtime
from hexswitch.shared.config import validate_config

# Timeout for integration tests that start runtime (in seconds)
RUNTIME_TEST_TIMEOUT = 20


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_runtime_clean_start_stop() -> None:
    """Test that runtime starts and stops cleanly without hanging threads/tasks."""
    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "lifecycle-test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [],
            }
        },
        "outbound": {
            "http_client": {
                "enabled": True,
                "base_url": "https://api.example.com",
                "timeout": 5,
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    # Get initial thread count
    initial_threads = threading.active_count()

    try:
        # Start runtime
        runtime.start()
        time.sleep(0.2)  # Give adapters time to start

        # Verify all adapters started
        assert len(runtime.inbound_adapters) > 0
        assert len(runtime.outbound_adapters) > 0

        # Verify adapters are running
        for adapter in runtime.inbound_adapters:
            assert adapter.is_running() is True

        for adapter in runtime.outbound_adapters:
            assert adapter.is_connected() is True

        # Get thread count after start
        threads_after_start = threading.active_count()

        # Stop runtime
        runtime.stop()
        time.sleep(0.2)  # Give adapters time to stop

        # Verify all adapters stopped
        assert len(runtime.inbound_adapters) == 0
        assert len(runtime.outbound_adapters) == 0

        # Verify no hanging threads
        # Allow some time for threads to clean up
        time.sleep(0.5)
        threads_after_stop = threading.active_count()

        # Thread count should be close to initial (allow for some variance)
        # We check that we don't have significantly more threads than we started with
        thread_increase = threads_after_stop - initial_threads
        assert thread_increase <= 2, f"Too many threads remaining: {thread_increase}"

        # Verify resources are cleaned up
        # Check that adapters are no longer in lists
        assert runtime.inbound_adapters == []
        assert runtime.outbound_adapters == []

    finally:
        # Ensure runtime is stopped even if test fails
        if runtime.inbound_adapters or runtime.outbound_adapters:
            runtime.stop()


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_runtime_start_stop_multiple_adapters() -> None:
    """Test runtime start/stop with multiple adapters."""
    # Find free ports
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        http_port1 = s.getsockname()[1]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        http_port2 = s.getsockname()[1]

    config = {
        "service": {"name": "multi-adapter-test"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": http_port1,
                "routes": [],
            },
        },
        "outbound": {
            "http_client": {
                "enabled": True,
                "base_url": "https://api.example.com",
                "timeout": 5,
            },
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        # Start runtime
        runtime.start()
        time.sleep(0.3)  # Give all adapters time to start

        # Verify all adapters started
        assert len(runtime.inbound_adapters) == 1
        assert len(runtime.outbound_adapters) == 1

        # Verify all adapters are running/connected
        for adapter in runtime.inbound_adapters:
            assert adapter.is_running() is True

        for adapter in runtime.outbound_adapters:
            assert adapter.is_connected() is True

        # Stop runtime
        runtime.stop()
        time.sleep(0.3)  # Give all adapters time to stop

        # Verify all adapters stopped
        assert len(runtime.inbound_adapters) == 0
        assert len(runtime.outbound_adapters) == 0

    finally:
        if runtime.inbound_adapters or runtime.outbound_adapters:
            runtime.stop()


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_runtime_graceful_shutdown_no_hanging_threads() -> None:
    """Test graceful shutdown without hanging threads."""
    import sys
    from types import ModuleType

    # Create test handler
    test_module = ModuleType("test_lifecycle_handlers")

    def slow_handler(envelope):
        time.sleep(0.1)  # Simulate slow handler
        return envelope

    test_module.slow = slow_handler
    sys.modules["test_lifecycle_handlers"] = test_module

    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "shutdown-test"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [
                    {
                        "path": "/slow",
                        "method": "GET",
                        "handler": "test_lifecycle_handlers:slow",
                    }
                ],
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    initial_threads = threading.active_count()

    try:
        runtime.start()
        time.sleep(0.2)

        # Request shutdown
        runtime.request_shutdown()

        # Stop runtime
        runtime.stop()
        time.sleep(0.3)  # Give time for cleanup

        # Verify no hanging threads
        final_threads = threading.active_count()
        thread_increase = final_threads - initial_threads
        assert thread_increase <= 2, f"Too many threads remaining: {thread_increase}"

        # Verify adapters are stopped
        assert len(runtime.inbound_adapters) == 0

    finally:
        if runtime.inbound_adapters or runtime.outbound_adapters:
            runtime.stop()
        if "test_lifecycle_handlers" in sys.modules:
            del sys.modules["test_lifecycle_handlers"]


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_runtime_start_stop_resources_cleaned() -> None:
    """Test that runtime resources are properly cleaned up on stop."""
    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "resource-cleanup-test"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [],
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        # Start runtime
        runtime.start()
        time.sleep(0.2)

        # Verify runtime has resources
        assert runtime._tracer is not None
        assert runtime._metrics is not None
        assert len(runtime.inbound_adapters) > 0

        # Stop runtime
        runtime.stop()
        time.sleep(0.2)

        # Verify adapters are cleaned up
        assert len(runtime.inbound_adapters) == 0
        assert len(runtime.outbound_adapters) == 0

        # Verify shutdown flag is set
        assert runtime._shutdown_requested is True

    finally:
        if runtime.inbound_adapters or runtime.outbound_adapters:
            runtime.stop()

