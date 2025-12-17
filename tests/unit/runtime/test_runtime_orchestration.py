"""Unit tests for runtime orchestration."""

import pytest

from hexswitch.runtime import Runtime

# Timeout for runtime tests (in seconds)
RUNTIME_TEST_TIMEOUT = 10


def test_runtime_initialization() -> None:
    """Test Runtime initialization."""
    config = {"service": {"name": "test-service"}}
    runtime = Runtime(config)
    assert runtime.config == config
    assert runtime.inbound_adapters == []
    assert runtime.outbound_adapters == []
    assert runtime._shutdown_requested is False


def test_runtime_create_http_adapter() -> None:
    """Test Runtime creating HTTP adapter."""
    config = {
        "service": {"name": "test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": 8000,
                "routes": [],
            }
        },
    }
    runtime = Runtime(config)
    adapter = runtime._create_inbound_adapter("http", config["inbound"]["http"])
    assert adapter.name == "http"
    assert adapter.is_running() is False


def test_runtime_create_unsupported_inbound_adapter() -> None:
    """Test Runtime with unsupported inbound adapter type."""
    config = {"service": {"name": "test-service"}}
    runtime = Runtime(config)
    with pytest.raises(ValueError, match="Unsupported inbound adapter type"):
        runtime._create_inbound_adapter("unsupported_adapter", {"enabled": True})


def test_runtime_create_unsupported_outbound_adapter() -> None:
    """Test Runtime with unsupported outbound adapter type."""
    config = {"service": {"name": "test-service"}}
    runtime = Runtime(config)
    with pytest.raises(ValueError, match="Unsupported outbound adapter type"):
        runtime._create_outbound_adapter("postgres", {"enabled": True})


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_runtime_start_stop() -> None:
    """Test Runtime start and stop lifecycle."""
    import socket

    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [],
            }
        },
    }
    runtime = Runtime(config)

    try:
        runtime.start()
        assert len(runtime.inbound_adapters) == 1
        assert runtime.inbound_adapters[0].is_running() is True
    finally:
        runtime.stop()
        assert len(runtime.inbound_adapters) == 0


def test_runtime_start_no_adapters() -> None:
    """Test Runtime start with no adapters enabled."""
    config = {
        "service": {"name": "test-service"},
        "inbound": {"http": {"enabled": False}},
    }
    runtime = Runtime(config)

    runtime.start()
    assert len(runtime.inbound_adapters) == 0
    runtime.stop()


def test_runtime_request_shutdown() -> None:
    """Test Runtime shutdown request."""
    config = {"service": {"name": "test-service"}}
    runtime = Runtime(config)
    assert runtime._shutdown_requested is False

    runtime.request_shutdown()
    assert runtime._shutdown_requested is True


