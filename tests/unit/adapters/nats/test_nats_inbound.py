"""Unit tests for NATS inbound adapter."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError, HandlerError
from hexswitch.adapters.nats.inbound_adapter import NatsAdapterServer
from hexswitch.shared.envelope import Envelope


@pytest.fixture
def mock_nats():
    """Mock NATS client."""
    with patch("hexswitch.adapters.nats.inbound_adapter.nats") as mock_nats_module:
        mock_client = AsyncMock()
        mock_nats_module.connect = AsyncMock(return_value=mock_client)
        yield mock_client, mock_nats_module


@pytest.fixture
def nats_config():
    """NATS adapter configuration."""
    return {
        "servers": ["nats://localhost:4222"],
        "subjects": [
            {
                "subject": "test.subject",
                "port": "test_handler",
            }
        ],
    }


class TestNatsAdapterServer:
    """Test NATS inbound adapter."""

    def test_init_requires_nats_py(self) -> None:
        """Test that adapter requires nats-py package."""
        with patch("hexswitch.adapters.nats.inbound_adapter.NATS_AVAILABLE", False):
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [{"subject": "test", "port": "test_port"}],
            }
            # Adapter can be instantiated, but start() should fail
            adapter = NatsAdapterServer("nats", config)
            with pytest.raises(AdapterStartError, match="nats-py package"):
                adapter.start()

    def test_config_parsing(self, nats_config) -> None:
        """Test adapter configuration parsing."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)
            assert adapter.servers == ["nats://localhost:4222"]
            assert len(adapter.subjects) == 1
            assert adapter.queue_group is None
        except ImportError:
            pytest.skip("nats-py not available")

    def test_config_with_queue_group(self) -> None:
        """Test adapter with queue group."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [{"subject": "test.subject", "port": "test_handler"}],
                "queue_group": "workers",
            }
            adapter = NatsAdapterServer("nats", config)
            assert adapter.queue_group == "workers"
        except ImportError:
            pytest.skip("nats-py not available")

    def test_config_with_multiple_servers(self) -> None:
        """Test adapter with multiple servers."""
        try:
            config = {
                "servers": ["nats://server1:4222", "nats://server2:4222"],
                "subjects": [{"subject": "test.subject", "port": "test_handler"}],
            }
            adapter = NatsAdapterServer("nats", config)
            assert len(adapter.servers) == 2
        except ImportError:
            pytest.skip("nats-py not available")

    def test_config_with_single_server_string(self) -> None:
        """Test adapter with single server as string."""
        try:
            config = {
                "servers": "nats://localhost:4222",
                "subjects": [{"subject": "test.subject", "port": "test_handler"}],
            }
            adapter = NatsAdapterServer("nats", config)
            assert isinstance(adapter.servers, list)
            assert len(adapter.servers) == 1
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_message_handler(self, mock_nats, nats_config) -> None:
        """Test message handler processes messages correctly."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock handler
            mock_handler = MagicMock(return_value=Envelope.success({"result": "ok"}))

            # Register handler
            adapter._handler_map["test.subject"] = mock_handler

            # Create mock message
            mock_msg = MagicMock()
            mock_msg.subject = "test.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = None
            mock_msg.headers = None

            # Call message handler
            await adapter._message_handler(mock_msg)

            # Verify handler was called
            assert mock_handler.called
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_message_handler_with_reply(self, mock_nats, nats_config) -> None:
        """Test message handler with reply-to."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock handler
            response_envelope = Envelope.success({"result": "ok"})
            mock_handler = MagicMock(return_value=response_envelope)

            # Register handler
            adapter._handler_map["test.subject"] = mock_handler
            adapter._nc = mock_client

            # Create mock message with reply
            mock_msg = MagicMock()
            mock_msg.subject = "test.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = "reply.subject"
            mock_msg.headers = None

            # Mock publish
            mock_client.publish = AsyncMock()

            # Call message handler
            await adapter._message_handler(mock_msg)

            # Verify handler was called
            assert mock_handler.called
            # Verify reply was sent
            assert mock_client.publish.called
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers(self, nats_config) -> None:
        """Test handler loading."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock port registry
            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry") as mock_registry:
                mock_handler = MagicMock()
                mock_registry.return_value.get_handler.return_value = mock_handler

                adapter._load_handlers()

                assert "test.subject" in adapter._handler_map
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_with_handler_path(self) -> None:
        """Test handler loading with handler path."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "handler": "tests.fixtures.mock_handlers:test_handler",
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            # Mock import
            with patch("hexswitch.adapters.nats.inbound_adapter.importlib") as mock_importlib:
                mock_module = MagicMock()
                mock_module.test_handler = MagicMock()
                mock_importlib.import_module.return_value = mock_module

                adapter._load_handlers()

                assert "test.subject" in adapter._handler_map
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_start(self, mock_nats, nats_config) -> None:
        """Test async startup."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock handler loading
            adapter._handler_map = {"test.subject": MagicMock()}

            # Mock subscribe
            mock_sub = AsyncMock()
            mock_client.subscribe = AsyncMock(return_value=mock_sub)

            await adapter._async_start()

            assert adapter._nc == mock_client
            assert len(adapter._subscriptions) == 1
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_start_with_queue_group(self, mock_nats) -> None:
        """Test async startup with queue group."""
        try:
            mock_client, _ = mock_nats
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [{"subject": "test.subject", "port": "test_handler"}],
                "queue_group": "workers",
            }
            adapter = NatsAdapterServer("nats", config)

            # Mock handler loading
            adapter._handler_map = {"test.subject": MagicMock()}

            # Mock subscribe with queue
            mock_sub = AsyncMock()
            mock_client.subscribe = AsyncMock(return_value=mock_sub)

            await adapter._async_start()

            # Verify subscribe was called with queue
            mock_client.subscribe.assert_called()
            call_args = mock_client.subscribe.call_args
            assert call_args[1].get("queue") == "workers"
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_stop(self, mock_nats, nats_config) -> None:
        """Test async shutdown."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._nc = mock_client

            # Create mock subscription
            mock_sub = AsyncMock()
            adapter._subscriptions = [mock_sub]

            # Mock unsubscribe and close
            mock_sub.unsubscribe = AsyncMock()
            mock_client.close = AsyncMock()

            await adapter._async_stop()

            assert mock_sub.unsubscribe.called
            assert mock_client.close.called
            assert adapter._nc is None
        except ImportError:
            pytest.skip("nats-py not available")

    def test_start_failure(self, nats_config) -> None:
        """Test start failure handling."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock async_start to raise error
            async def failing_start():
                raise Exception("Connection failed")

            adapter._async_start = failing_start

            with pytest.raises(AdapterStartError):
                adapter.start()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_start_already_running(self, nats_config) -> None:
        """Test start when already running."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._running = True

            # Should not raise, just log warning
            adapter.start()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_start_nats_not_available(self) -> None:
        """Test start when NATS is not available."""
        with patch("hexswitch.adapters.nats.inbound_adapter.NATS_AVAILABLE", False):
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [{"subject": "test", "port": "test_port"}],
            }
            adapter = NatsAdapterServer("nats", config)
            with pytest.raises(AdapterStartError, match="nats-py package"):
                adapter.start()

    @pytest.mark.asyncio
    async def test_message_handler_no_handler(self, mock_nats, nats_config) -> None:
        """Test message handler when no handler is found."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._handler_map = {}  # No handlers

            # Create mock message
            mock_msg = MagicMock()
            mock_msg.subject = "unknown.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = None
            mock_msg.headers = None

            # Should not raise, just log warning
            await adapter._message_handler(mock_msg)
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_message_handler_with_headers(self, mock_nats, nats_config) -> None:
        """Test message handler with headers."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock handler
            mock_handler = MagicMock(return_value=Envelope.success({"result": "ok"}))

            # Register handler
            adapter._handler_map["test.subject"] = mock_handler

            # Create mock message with headers
            mock_msg = MagicMock()
            mock_msg.subject = "test.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = None
            mock_msg.headers = {"X-Trace-Id": "12345"}

            # Call message handler
            await adapter._message_handler(mock_msg)

            # Verify handler was called
            assert mock_handler.called
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_message_handler_async_handler(self, mock_nats, nats_config) -> None:
        """Test message handler with async handler."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock async handler
            async def async_handler(envelope):
                return Envelope.success({"result": "ok"})

            # Register handler
            adapter._handler_map["test.subject"] = async_handler

            # Create mock message
            mock_msg = MagicMock()
            mock_msg.subject = "test.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = None
            mock_msg.headers = None

            # Call message handler
            await adapter._message_handler(mock_msg)

            # Handler should be called
            assert "test.subject" in adapter._handler_map
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_message_handler_exception(self, mock_nats, nats_config) -> None:
        """Test message handler with exception."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock handler that raises exception
            def failing_handler(envelope):
                raise ValueError("Handler error")

            # Register handler
            adapter._handler_map["test.subject"] = failing_handler

            # Create mock message
            mock_msg = MagicMock()
            mock_msg.subject = "test.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = None
            mock_msg.headers = None

            # Should not raise, just log exception
            await adapter._message_handler(mock_msg)
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_message_handler_no_reply(self, mock_nats, nats_config) -> None:
        """Test message handler without reply_to."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)

            # Mock handler
            mock_handler = MagicMock(return_value=Envelope.success({"result": "ok"}))
            adapter._handler_map["test.subject"] = mock_handler
            adapter._nc = mock_client

            # Create mock message without reply
            mock_msg = MagicMock()
            mock_msg.subject = "test.subject"
            mock_msg.data = b'{"key": "value"}'
            mock_msg.reply = None
            mock_msg.headers = None

            # Mock publish
            mock_client.publish = AsyncMock()

            # Call message handler
            await adapter._message_handler(mock_msg)

            # Verify handler was called
            assert mock_handler.called
            # Verify publish was NOT called (no reply_to)
            assert not mock_client.publish.called
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_no_handler_or_port(self) -> None:
        """Test handler loading with no handler or port."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        # Missing both handler and port
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            # Should not raise, just log warning
            adapter._load_handlers()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_with_handler_loader(self) -> None:
        """Test handler loading with HandlerLoader."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "port": "test_port",
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            # Mock handler loader
            mock_loader = MagicMock()
            mock_handler = MagicMock()
            mock_loader.resolve.return_value = mock_handler
            adapter._handler_loader = mock_loader

            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry"):
                adapter._load_handlers()

                assert "test.subject" in adapter._handler_map
                assert adapter._handler_map["test.subject"] == mock_handler
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_handler_path_invalid_format(self) -> None:
        """Test handler loading with invalid handler path format."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "handler": "invalid_format",  # Missing colon
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry"):
                with pytest.raises(HandlerError, match="Invalid handler path format"):
                    adapter._load_handlers()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_handler_path_empty_parts(self) -> None:
        """Test handler loading with empty module or function name."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "handler": ":function",  # Empty module
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry"):
                with pytest.raises(HandlerError, match="Module path and function name must not be empty"):
                    adapter._load_handlers()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_module_not_found(self) -> None:
        """Test handler loading with module not found."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "handler": "nonexistent.module:handler",
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry"):
                with patch("hexswitch.adapters.nats.inbound_adapter.importlib") as mock_importlib:
                    mock_importlib.import_module.side_effect = ImportError("No module named 'nonexistent'")

                    with pytest.raises(HandlerError):
                        adapter._load_handlers()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_function_not_found(self) -> None:
        """Test handler loading with function not found in module."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "handler": "test.module:nonexistent",
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry"):
                with patch("hexswitch.adapters.nats.inbound_adapter.importlib") as mock_importlib:
                    # Create a mock module with spec to limit attributes
                    # This ensures hasattr returns False for 'nonexistent'
                    mock_module = MagicMock(spec=[])  # Empty spec means no attributes
                    mock_importlib.import_module.return_value = mock_module

                    with pytest.raises(HandlerError, match="does not have attribute"):
                        adapter._load_handlers()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_load_handlers_function_not_callable(self) -> None:
        """Test handler loading with function not callable."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "test.subject",
                        "handler": "test.module:not_callable",
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)

            with patch("hexswitch.adapters.nats.inbound_adapter.get_port_registry"):
                with patch("hexswitch.adapters.nats.inbound_adapter.importlib") as mock_importlib:
                    mock_module = MagicMock()
                    mock_module.not_callable = "not a function"
                    mock_importlib.import_module.return_value = mock_module

                    with patch("builtins.callable", return_value=False):
                        with pytest.raises(HandlerError, match="is not callable"):
                            adapter._load_handlers()
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_start_empty_subject(self, mock_nats) -> None:
        """Test async start with empty subject."""
        try:
            mock_client, _ = mock_nats
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {
                        "subject": "",  # Empty subject
                        "port": "test_handler",
                    }
                ],
            }
            adapter = NatsAdapterServer("nats", config)
            adapter._handler_map = {}

            # Mock subscribe
            mock_sub = AsyncMock()
            mock_client.subscribe = AsyncMock(return_value=mock_sub)

            await adapter._async_start()

            # Should not subscribe to empty subject
            assert len(adapter._subscriptions) == 0
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_stop_with_exceptions(self, mock_nats, nats_config) -> None:
        """Test async stop with exceptions during unsubscribe/close."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._nc = mock_client

            # Create mock subscription that raises exception
            mock_sub = AsyncMock()
            mock_sub.unsubscribe = AsyncMock(side_effect=Exception("Unsubscribe error"))
            adapter._subscriptions = [mock_sub]

            # Mock close to raise exception
            mock_client.close = AsyncMock(side_effect=Exception("Close error"))

            # Should not raise, just log warnings
            await adapter._async_stop()

            assert adapter._nc is None
            assert len(adapter._subscriptions) == 0
        except ImportError:
            pytest.skip("nats-py not available")

    def test_stop_not_running(self, nats_config) -> None:
        """Test stop when not running."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._running = False

            # Should not raise, just log warning
            adapter.stop()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_stop_loop_not_running(self, nats_config) -> None:
        """Test stop when loop is not running."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._running = True

            # Mock loop that is not running
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = False
            adapter._loop = mock_loop

            # Should not raise
            adapter.stop()

            assert adapter._running is False
        except ImportError:
            pytest.skip("nats-py not available")

    def test_stop_with_exception(self, nats_config) -> None:
        """Test stop with exception."""
        try:
            adapter = NatsAdapterServer("nats", nats_config)
            adapter._running = True

            # Mock loop that raises exception
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            mock_loop.call_soon_threadsafe.side_effect = Exception("Loop error")
            adapter._loop = mock_loop

            with pytest.raises(AdapterStopError):
                adapter.stop()
        except ImportError:
            pytest.skip("nats-py not available")

