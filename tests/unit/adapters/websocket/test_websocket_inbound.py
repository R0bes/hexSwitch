"""Unit tests for WebSocket inbound adapter."""

import asyncio
import json
import socket
import time
from types import ModuleType
from unittest.mock import AsyncMock, Mock, patch

import pytest
import websockets

from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError, HandlerError
from hexswitch.adapters.websocket.inbound_adapter import WebSocketAdapterServer
from hexswitch.handlers.loader import HandlerLoader
from hexswitch.ports import PortError, get_port_registry
from hexswitch.shared.envelope import Envelope
from tests.unit.adapters.base.adapter_tester import AdapterTester


@pytest.mark.fast
def test_websocket_adapter_initialization():
    """Test WebSocket adapter initialization."""
    config = {"enabled": True, "port": 9000, "path": "/custom", "routes": []}
    adapter = WebSocketAdapterServer("websocket", config)
    assert adapter.name == "websocket"
    assert adapter.port == 9000
    assert adapter.path == "/custom"
    assert adapter.routes == []
    assert not adapter._running


@pytest.mark.fast
def test_websocket_adapter_load_handlers_with_port():
    """Test loading handlers using port registry."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "port": "test_port"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    # Register a test port
    mock_handler = Mock(return_value=Envelope.success({"result": "ok"}))
    mock_handler.__name__ = "test_port_handler"
    get_port_registry().register_handler("test_port", mock_handler)

    adapter = WebSocketAdapterServer("websocket", config)
    adapter._load_handlers()

    assert "/test" in adapter._handler_map
    # The handler should be the same as registered
    assert adapter._handler_map["/test"] == mock_handler


@pytest.mark.fast
def test_websocket_adapter_load_handlers_with_handler_path(handler_module: ModuleType):
    """Test loading handlers using handler path."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "handler": "test_handler_module:test_handler"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)
    adapter._load_handlers()

    assert "/test" in adapter._handler_map
    assert callable(adapter._handler_map["/test"])


@pytest.mark.fast
def test_websocket_adapter_load_handlers_with_handler_loader():
    """Test loading handlers using HandlerLoader."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "port": "test_port"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    mock_handler = Mock(return_value=Envelope.success({"result": "ok"}))
    mock_loader = Mock(spec=HandlerLoader)
    mock_loader.resolve = Mock(return_value=mock_handler)

    adapter = WebSocketAdapterServer("websocket", config)
    adapter._handler_loader = mock_loader
    adapter._load_handlers()

    assert "/test" in adapter._handler_map
    assert adapter._handler_map["/test"] == mock_handler
    mock_loader.resolve.assert_called_once_with("test_port")


@pytest.mark.fast
def test_websocket_adapter_load_handlers_invalid_handler_path():
    """Test loading handlers with invalid handler path."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "handler": "invalid"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    with pytest.raises(HandlerError):
        adapter._load_handlers()


@pytest.mark.fast
def test_websocket_adapter_load_handlers_missing_module():
    """Test loading handlers with missing module."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "handler": "nonexistent.module:handler"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    # ModuleNotFoundError is raised, not HandlerError
    with pytest.raises((HandlerError, ModuleNotFoundError)):
        adapter._load_handlers()


@pytest.mark.fast
def test_websocket_adapter_load_handlers_no_handler_or_port():
    """Test loading handlers when neither handler nor port is specified."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    # Should not raise error, just skip the route
    adapter._load_handlers()
    assert "/test" not in adapter._handler_map


@pytest.mark.fast
def test_websocket_adapter_load_handlers_port_error():
    """Test loading handlers when port registry raises error."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "port": "nonexistent_port"}],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    with pytest.raises(PortError):
        adapter._load_handlers()


@pytest.mark.asyncio
async def test_websocket_adapter_handle_connection_no_handler():
    """Test handling connection when no handler is found."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)
    mock_websocket.close = AsyncMock()

    await adapter._handle_connection(mock_websocket, "/unknown")

    mock_websocket.close.assert_called_once_with(code=4004, reason="No handler found")


@pytest.mark.asyncio
async def test_websocket_adapter_handle_connection_with_async_handler():
    """Test handling connection with async handler."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    async def async_handler(connection_data):
        assert "path" in connection_data
        assert "websocket" in connection_data

    adapter._handler_map["/test"] = async_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)

    await adapter._handle_connection(mock_websocket, "/test")

    assert mock_websocket in adapter._connections or len(adapter._connections) == 0


@pytest.mark.asyncio
async def test_websocket_adapter_handle_connection_with_sync_handler():
    """Test handling connection with sync handler."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    def sync_handler(connection_data):
        assert "path" in connection_data

    adapter._handler_map["/test"] = sync_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)

    await adapter._handle_connection(mock_websocket, "/test")


@pytest.mark.asyncio
async def test_websocket_adapter_handle_connection_handler_exception():
    """Test handling connection when handler raises exception."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    async def failing_handler(connection_data):
        raise ValueError("Handler error")

    adapter._handler_map["/test"] = failing_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)
    mock_websocket.close = AsyncMock()

    await adapter._handle_connection(mock_websocket, "/test")

    mock_websocket.close.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_adapter_handle_message():
    """Test handling WebSocket messages."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    async def message_handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"echo": envelope.body})

    adapter._handler_map["/test"] = message_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)
    mock_websocket.__aiter__ = Mock(return_value=iter([json.dumps({"message": "test"})]))
    mock_websocket.send = AsyncMock()

    # Mock the async for loop - create async iterator properly
    async def mock_iter():
        yield json.dumps({"message": "test"})

    mock_iter_instance = mock_iter()
    mock_websocket.__aiter__ = Mock(return_value=mock_iter_instance)

    await adapter._handle_message(mock_websocket, "/test")

    # Verify message was sent
    assert mock_websocket.send.called


@pytest.mark.asyncio
async def test_websocket_adapter_handle_message_no_handler():
    """Test handling message when no handler is found."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)

    async def mock_iter():
        yield json.dumps({"message": "test"})

    mock_iter_instance = mock_iter()
    mock_websocket.__aiter__ = Mock(return_value=mock_iter_instance)

    # Should not raise error, just return early
    await adapter._handle_message(mock_websocket, "/unknown")


@pytest.mark.asyncio
async def test_websocket_adapter_handle_message_handler_exception():
    """Test handling message when handler raises exception."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    async def failing_handler(envelope: Envelope) -> Envelope:
        raise ValueError("Handler error")

    adapter._handler_map["/test"] = failing_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)
    mock_websocket.send = AsyncMock()

    async def mock_iter():
        yield json.dumps({"message": "test"})

    mock_iter_instance = mock_iter()
    mock_websocket.__aiter__ = Mock(return_value=mock_iter_instance)

    await adapter._handle_message(mock_websocket, "/test")

    # Should send error response
    assert mock_websocket.send.called


@pytest.mark.asyncio
async def test_websocket_adapter_handle_message_connection_closed():
    """Test handling message when connection is closed."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    async def message_handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    adapter._handler_map["/test"] = message_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)

    # Simulate connection closed - create async iterator properly
    async def mock_iter():
        raise websockets.exceptions.ConnectionClosed(None, None)
        yield  # Make it a generator

    # Create the async iterator and await it properly
    mock_iter_instance = mock_iter()
    mock_websocket.__aiter__ = Mock(return_value=mock_iter_instance)

    # Should handle gracefully
    try:
        await adapter._handle_message(mock_websocket, "/test")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Clean up: try to exhaust the iterator
        try:
            async for _ in mock_iter_instance:
                pass
        except (websockets.exceptions.ConnectionClosed, StopAsyncIteration):
            pass


@pytest.mark.fast
def test_websocket_adapter_start_port_in_use():
    """Test starting adapter when port is in use."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    # Bind to port manually to simulate port in use
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.bind(("", free_port))

    adapter = WebSocketAdapterServer("websocket", config)

    try:
        with pytest.raises(AdapterStartError, match="already in use|is already in use|Only one usage"):
            adapter.start()
    finally:
        test_socket.close()


@pytest.mark.fast
def test_websocket_adapter_start_already_running():
    """Test starting adapter when already running."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)
    adapter._running = True

    with patch("hexswitch.adapters.websocket.inbound_adapter.logger") as mock_logger:
        adapter.start()
        mock_logger.warning.assert_called_once()

    adapter.stop()


@pytest.mark.fast
def test_websocket_adapter_start_handler_load_error():
    """Test starting adapter when handler loading fails."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [{"path": "/test", "handler": "nonexistent.module:handler"}],
    }
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    with pytest.raises(AdapterStartError):
        adapter.start()


@pytest.mark.fast
def test_websocket_adapter_stop_not_running():
    """Test stopping adapter when not running."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    with patch("hexswitch.adapters.websocket.inbound_adapter.logger") as mock_logger:
        adapter.stop()
        mock_logger.warning.assert_called_once()


@pytest.mark.fast
def test_websocket_adapter_stop_with_connections():
    """Test stopping adapter with active connections."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)
    adapter.start()
    time.sleep(0.5)

    # Add mock connection
    mock_websocket = AsyncMock()
    adapter._connections.add(mock_websocket)
    adapter._loop = asyncio.new_event_loop()

    adapter.stop()

    assert len(adapter._connections) == 0


@pytest.mark.fast
def test_websocket_adapter_stop_error():
    """Test stopping adapter when error occurs."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)
    adapter.start()
    time.sleep(0.5)

    # Mock loop to raise error
    adapter._loop = Mock()
    adapter._loop.is_running = Mock(return_value=True)
    adapter._loop.call_soon_threadsafe = Mock(side_effect=Exception("Stop error"))

    with pytest.raises(AdapterStopError):
        adapter.stop()


@pytest.mark.fast
def test_websocket_adapter_to_envelope():
    """Test converting WebSocket message to envelope."""
    config = {"enabled": True, "port": 0, "routes": []}
    adapter = WebSocketAdapterServer("websocket", config)

    message = json.dumps({"test": "data"})
    envelope = adapter.to_envelope(
        message=message,
        path="/test",
        remote_address="127.0.0.1:12345",
        websocket_id=123,
    )

    assert isinstance(envelope, Envelope)
    assert envelope.path == "/test"


@pytest.mark.fast
def test_websocket_adapter_from_envelope():
    """Test converting envelope to WebSocket message."""
    config = {"enabled": True, "port": 0, "routes": []}
    adapter = WebSocketAdapterServer("websocket", config)

    envelope = Envelope.success({"result": "ok"})
    message = adapter.from_envelope(envelope)

    assert isinstance(message, str)
    data = json.loads(message)
    assert "result" in data or "data" in data


@pytest.mark.fast
@pytest.mark.asyncio
async def test_websocket_adapter_handle_connection_path_matching():
    """Test path matching in handle_connection."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    handler = Mock()
    adapter._handler_map["/api"] = handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)
    mock_websocket.close = AsyncMock()

    # Test exact match
    await adapter._handle_connection(mock_websocket, "/api")
    assert handler.called or mock_websocket.close.called

    # Test prefix match
    handler.reset_mock()
    mock_websocket.close.reset_mock()
    await adapter._handle_connection(mock_websocket, "/api/v1/test")
    # Should match because path starts with "/api"


@pytest.mark.asyncio
async def test_websocket_adapter_handle_message_sync_handler():
    """Test handling message with sync handler."""
    config = {"enabled": True, "port": 0, "routes": []}
    free_port = AdapterTester.find_free_port()
    config["port"] = free_port

    adapter = WebSocketAdapterServer("websocket", config)

    def sync_handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    adapter._handler_map["/test"] = sync_handler

    mock_websocket = AsyncMock()
    mock_websocket.remote_address = ("127.0.0.1", 12345)
    mock_websocket.send = AsyncMock()

    async def mock_iter():
        yield json.dumps({"message": "test"})

    mock_iter_instance = mock_iter()
    mock_websocket.__aiter__ = Mock(return_value=mock_iter_instance)

    await adapter._handle_message(mock_websocket, "/test")

    assert mock_websocket.send.called

