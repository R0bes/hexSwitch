"""Unit tests for WebSocket outbound adapter."""

import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
import websockets

from hexswitch.adapters.exceptions import AdapterConnectionError
from hexswitch.adapters.websocket.outbound_adapter import WebSocketAdapterClient
from hexswitch.shared.envelope import Envelope


class TestWebSocketAdapterClient:
    """Test WebSocket client outbound adapter."""

    def test_initialization(self) -> None:
        """Test adapter initialization."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        assert adapter.name == "test_ws"
        assert adapter.url == "ws://localhost:9000"
        assert adapter.timeout == 30
        assert adapter.reconnect is True
        assert adapter.reconnect_interval == 5
        assert not adapter._connected

    def test_initialization_custom_config(self) -> None:
        """Test adapter initialization with custom config."""
        config = {
            "url": "ws://example.com:8080",
            "timeout": 60,
            "reconnect": False,
            "reconnect_interval": 10,
        }
        adapter = WebSocketAdapterClient("test_ws", config)
        assert adapter.url == "ws://example.com:8080"
        assert adapter.timeout == 60
        assert adapter.reconnect is False
        assert adapter.reconnect_interval == 10

    def test_connect_success(self) -> None:
        """Test successful connection."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)

        with patch("hexswitch.adapters.websocket.outbound_adapter.websockets.connect") as mock_connect:
            mock_ws = AsyncMock()
            mock_connect.return_value = mock_ws

            with patch.object(adapter, "_run_event_loop") as mock_loop:
                with patch("asyncio.run_coroutine_threadsafe") as mock_run:
                    # Mock successful connection
                    mock_future = Mock()
                    mock_future.result.return_value = None
                    mock_run.return_value = mock_future

                    adapter.connect()
                    assert adapter._connected

    def test_connect_already_connected(self) -> None:
        """Test connecting when already connected."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True

        with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
            adapter.connect()
            mock_logger.warning.assert_called_once()

    def test_connect_missing_url(self) -> None:
        """Test connection with missing URL."""
        config = {}
        adapter = WebSocketAdapterClient("test_ws", config)

        with pytest.raises(AdapterConnectionError) as exc_info:
            adapter.connect()
        assert "url is required" in str(exc_info.value)

    def test_connect_error(self) -> None:
        """Test connection error."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        with patch("hexswitch.adapters.websocket.outbound_adapter.websockets.connect") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            with pytest.raises(AdapterConnectionError):
                adapter.connect()

    def test_disconnect_success(self) -> None:
        """Test successful disconnection."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()
        adapter._receive_task = Mock()

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.return_value = None
            mock_run.return_value = mock_future

            adapter.disconnect()
            assert not adapter._connected

    def test_disconnect_not_connected(self) -> None:
        """Test disconnecting when not connected."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
            adapter.disconnect()
            mock_logger.warning.assert_called_once()

    def test_disconnect_error(self) -> None:
        """Test disconnection error handling."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()
        adapter._receive_task = Mock()

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.side_effect = Exception("Close error")
            mock_run.return_value = mock_future

            with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
                adapter.disconnect()
                mock_logger.error.assert_called()

    def test_from_envelope(self) -> None:
        """Test converting envelope to WebSocket message."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        envelope = Envelope(path="/test", method="POST", body={"key": "value"})

        result = adapter.from_envelope(envelope)
        assert isinstance(result, str)
        data = json.loads(result)
        assert data == {"key": "value"}

    def test_to_envelope(self) -> None:
        """Test converting WebSocket message to envelope."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        original_envelope = Envelope(path="/test", method="POST")
        message = json.dumps({"result": "success"})

        result = adapter.to_envelope(message, original_envelope)
        assert result.status_code == 200
        assert result.data == {"result": "success"}

    def test_to_envelope_with_bytes(self) -> None:
        """Test converting bytes message to envelope."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        message = b'{"result": "success"}'

        result = adapter.to_envelope(message, None)
        assert result.status_code == 200

    def test_request_success(self) -> None:
        """Test successful request."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()

        envelope = Envelope(path="/test", method="POST", body={"key": "value"})

        # Mock message queue with response
        async def mock_get():
            return {"result": "success"}

        with patch.object(adapter._message_queue, "get_nowait", side_effect=[{"result": "success"}]):
            with patch("asyncio.run_coroutine_threadsafe") as mock_run:
                mock_future = Mock()
                mock_future.result.return_value = None
                mock_run.return_value = mock_future

                result = adapter.request(envelope)
                assert result.status_code == 200
                assert result.data == {"result": "success"}

    def test_request_not_connected(self) -> None:
        """Test request when not connected."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        envelope = Envelope(path="/test", method="POST")

        with pytest.raises(RuntimeError) as exc_info:
            adapter.request(envelope)
        assert "not connected" in str(exc_info.value)

    def test_request_timeout(self) -> None:
        """Test request timeout."""
        config = {"url": "ws://localhost:9000", "timeout": 1}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()

        envelope = Envelope(path="/test", method="POST", body={"key": "value"})

        # Mock _send_async using AsyncMock to avoid coroutine warnings
        adapter._send_async = AsyncMock(return_value=None)

        with patch.object(adapter._message_queue, "get_nowait", side_effect=asyncio.QueueEmpty()):
            with patch("asyncio.run_coroutine_threadsafe") as mock_run:
                mock_future = Mock()
                mock_future.result.return_value = None
                mock_run.return_value = mock_future

                result = adapter.request(envelope)
                assert result.status_code == 504
                assert "timeout" in result.error_message.lower()

    def test_request_error(self) -> None:
        """Test request error handling."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()

        envelope = Envelope(path="/test", method="POST", body={"key": "value"})

        # Mock _send_async using AsyncMock to avoid coroutine warnings
        adapter._send_async = AsyncMock(return_value=None)

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.side_effect = Exception("Send error")
            mock_run.return_value = mock_future

            result = adapter.request(envelope)
            assert result.status_code == 500

    def test_send_async_dict(self) -> None:
        """Test async send with dict message."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        async def test_send():
            await adapter._send_async({"key": "value"})
            adapter.websocket.send.assert_called_once()
            call_args = adapter.websocket.send.call_args[0][0]
            assert json.loads(call_args) == {"key": "value"}

        asyncio.run(test_send())

    def test_send_async_list(self) -> None:
        """Test async send with list message."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        async def test_send():
            await adapter._send_async([1, 2, 3])
            adapter.websocket.send.assert_called_once()

        asyncio.run(test_send())

    def test_send_async_bytes(self) -> None:
        """Test async send with bytes message."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        async def test_send():
            message = b"raw bytes"
            await adapter._send_async(message)
            adapter.websocket.send.assert_called_once_with(message)

        asyncio.run(test_send())

    def test_send_async_string(self) -> None:
        """Test async send with string message."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        async def test_send():
            await adapter._send_async("test message")
            adapter.websocket.send.assert_called_once_with("test message")

        asyncio.run(test_send())

    def test_send_async_not_connected(self) -> None:
        """Test async send when not connected."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = None

        async def test_send():
            with pytest.raises(RuntimeError) as exc_info:
                await adapter._send_async("test")
            assert "not connected" in str(exc_info.value)

        asyncio.run(test_send())

    def test_send_success(self) -> None:
        """Test send method."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.return_value = None
            mock_run.return_value = mock_future

            adapter.send({"key": "value"})
            mock_run.assert_called()

    def test_send_not_connected(self) -> None:
        """Test send when not connected."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        with pytest.raises(RuntimeError) as exc_info:
            adapter.send("test")
        assert "not connected" in str(exc_info.value)

    def test_send_error(self) -> None:
        """Test send error handling."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter.websocket = AsyncMock()
        adapter._loop = asyncio.new_event_loop()

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.side_effect = Exception("Send error")
            mock_run.return_value = mock_future

            with pytest.raises(Exception):
                adapter.send("test")

    def test_receive_success(self) -> None:
        """Test receive method."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter._loop = asyncio.new_event_loop()

        # Mock _send_async to avoid coroutine warnings during garbage collection
        adapter._send_async = AsyncMock(return_value=None)

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.return_value = {"result": "success"}
            mock_run.return_value = mock_future

            result = adapter.receive()
            assert result == {"result": "success"}

        # Clean up loop
        if adapter._loop and not adapter._loop.is_closed():
            adapter._loop.close()

    def test_receive_with_timeout(self) -> None:
        """Test receive with custom timeout."""
        config = {"url": "ws://localhost:9000", "timeout": 10}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter._loop = asyncio.new_event_loop()

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.return_value = {"result": "success"}
            mock_run.return_value = mock_future

            result = adapter.receive(timeout=2.0)
            assert result == {"result": "success"}

    def test_receive_not_connected(self) -> None:
        """Test receive when not connected."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        # Ensure no coroutines are created by checking connection status first
        assert not adapter._connected
        assert adapter._loop is None

        with pytest.raises(RuntimeError) as exc_info:
            adapter.receive()
        assert "not connected" in str(exc_info.value)

    def test_receive_timeout_error(self) -> None:
        """Test receive timeout error."""
        config = {"url": "ws://localhost:9000", "timeout": 1}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter._loop = asyncio.new_event_loop()

        # Mock _message_queue.get using AsyncMock to avoid coroutine warnings
        mock_queue = AsyncMock()
        mock_queue.get = AsyncMock(side_effect=asyncio.TimeoutError())
        adapter._message_queue = mock_queue

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.side_effect = asyncio.TimeoutError()
            mock_run.return_value = mock_future

            with pytest.raises(TimeoutError) as exc_info:
                adapter.receive()
            assert "No message received" in str(exc_info.value)

    def test_receive_error(self) -> None:
        """Test receive error handling."""
        config = {"url": "ws://localhost:9000", "timeout": 5}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter._connected = True
        adapter._loop = asyncio.new_event_loop()

        # Mock _message_queue.get using AsyncMock to avoid coroutine warnings
        mock_queue = AsyncMock()
        mock_queue.get = AsyncMock(side_effect=Exception("Receive error"))
        adapter._message_queue = mock_queue

        with patch("asyncio.run_coroutine_threadsafe") as mock_run:
            mock_future = Mock()
            mock_future.result.side_effect = Exception("Receive error")
            mock_run.return_value = mock_future

            with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
                with pytest.raises(Exception):
                    adapter.receive()
                mock_logger.error.assert_called()

    def test_receive_messages_connection_closed_with_reconnect(self) -> None:
        """Test receive messages with connection closed and reconnect."""
        config = {"url": "ws://localhost:9000", "reconnect": True, "reconnect_interval": 0.1}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        # Mock websocket iteration to raise ConnectionClosed
        async def mock_iter():
            raise websockets.exceptions.ConnectionClosed(None, None)

        adapter.websocket.__aiter__ = lambda self: self
        adapter.websocket.__anext__ = mock_iter

        async def test_receive():
            try:
                await adapter._receive_messages()
            except Exception:
                pass

        # Run with timeout to avoid hanging
        try:
            asyncio.run(asyncio.wait_for(test_receive(), timeout=0.5))
        except asyncio.TimeoutError:
            pass

    def test_receive_messages_error_handling(self) -> None:
        """Test receive messages error handling."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        # Mock websocket iteration to raise generic exception - create iterator properly
        async def mock_iter():
            raise Exception("Receive error")
            yield  # Never reached, but makes it a generator

        mock_iter_instance = mock_iter()
        adapter.websocket.__aiter__ = lambda: mock_iter_instance

        async def test_receive():
            try:
                await adapter._receive_messages()
            except Exception:
                pass

        with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
            try:
                asyncio.run(asyncio.wait_for(test_receive(), timeout=0.5))
            except asyncio.TimeoutError:
                pass
            finally:
                # Clean up: try to exhaust the iterator
                async def cleanup():
                    try:
                        async for _ in mock_iter_instance:
                            pass
                    except Exception:
                        pass
                try:
                    asyncio.run(cleanup())
                except Exception:
                    pass

    @pytest.mark.asyncio
    async def test_receive_messages_json_decode_error(self) -> None:
        """Test receive messages with JSON decode error."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        # Mock websocket to return invalid JSON - create iterator properly
        async def mock_iter():
            yield "invalid json {"
            return

        mock_iter_instance = mock_iter()
        adapter.websocket.__aiter__ = lambda: mock_iter_instance

        try:
            await asyncio.wait_for(adapter._receive_messages(), timeout=0.5)
        except (asyncio.TimeoutError, Exception):
            pass
        finally:
            # Clean up: try to exhaust the iterator
            try:
                async for _ in mock_iter_instance:
                    pass
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_receive_messages_processing_error(self) -> None:
        """Test receive messages with processing error."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)
        adapter.websocket = AsyncMock()

        # Mock message queue to raise error
        async def mock_put(item):
            raise Exception("Queue error")

        adapter._message_queue.put = mock_put

        # Create async iterator properly to avoid coroutine warnings
        async def mock_iter():
            yield '{"key": "value"}'
            # Ensure iterator is exhausted
            return

        mock_iter_instance = mock_iter()
        adapter.websocket.__aiter__ = lambda: mock_iter_instance

        with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
            try:
                await asyncio.wait_for(adapter._receive_messages(), timeout=0.5)
            except (asyncio.TimeoutError, Exception):
                pass
            finally:
                # Clean up: try to exhaust the iterator
                try:
                    async for _ in mock_iter_instance:
                        pass
                except Exception:
                    pass

    def test_run_event_loop_error(self) -> None:
        """Test event loop error handling."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        # Create a real event loop and patch run_forever to raise an error
        loop = asyncio.new_event_loop()
        original_run_forever = loop.run_forever

        def failing_run_forever():
            raise Exception("Loop error")

        with patch.object(loop, "run_forever", side_effect=failing_run_forever):
            with patch("asyncio.new_event_loop", return_value=loop):
                with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
                    adapter._run_event_loop()
                    mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_connect_async_logging(self) -> None:
        """Test connect async logging."""
        config = {"url": "ws://localhost:9000"}
        adapter = WebSocketAdapterClient("test_ws", config)

        mock_ws = AsyncMock()
        async def mock_connect(*args, **kwargs):
            return mock_ws

        with patch.object(websockets, "connect", side_effect=mock_connect):
            with patch("hexswitch.adapters.websocket.outbound_adapter.logger") as mock_logger:
                await adapter._connect_async()
                assert adapter.websocket == mock_ws
                mock_logger.info.assert_called()

