"""Unit tests for NATS outbound adapter."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hexswitch.adapters.exceptions import AdapterConnectionError
from hexswitch.adapters.nats.outbound_adapter import NatsAdapterClient
from hexswitch.shared.envelope import Envelope


@pytest.fixture
def mock_nats():
    """Mock NATS client."""
    with patch("hexswitch.adapters.nats.outbound_adapter.nats") as mock_nats_module:
        mock_client = AsyncMock()
        mock_nats_module.connect = AsyncMock(return_value=mock_client)
        yield mock_client, mock_nats_module


@pytest.fixture
def nats_client_config():
    """NATS client adapter configuration."""
    return {
        "servers": ["nats://localhost:4222"],
        "timeout": 30.0,
    }


class TestNatsAdapterClient:
    """Test NATS outbound adapter."""

    def test_init_requires_nats_py(self) -> None:
        """Test that adapter requires nats-py package."""
        with patch("hexswitch.adapters.nats.outbound_adapter.NATS_AVAILABLE", False):
            config = {"servers": ["nats://localhost:4222"]}
            # Adapter can be instantiated, but connect() should fail
            adapter = NatsAdapterClient("nats_client", config)
            with pytest.raises(AdapterConnectionError, match="nats-py package"):
                adapter.connect()

    def test_config_parsing(self, nats_client_config) -> None:
        """Test adapter configuration parsing."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            assert adapter.servers == ["nats://localhost:4222"]
            assert adapter.timeout == 30.0
        except ImportError:
            pytest.skip("nats-py not available")

    def test_config_with_single_server_string(self) -> None:
        """Test adapter with single server as string."""
        try:
            config = {
                "servers": "nats://localhost:4222",
                "timeout": 10.0,
            }
            adapter = NatsAdapterClient("nats_client", config)
            assert isinstance(adapter.servers, list)
            assert len(adapter.servers) == 1
            assert adapter.timeout == 10.0
        except ImportError:
            pytest.skip("nats-py not available")

    def test_config_with_multiple_servers(self) -> None:
        """Test adapter with multiple servers."""
        try:
            config = {
                "servers": ["nats://server1:4222", "nats://server2:4222"],
                "timeout": 15.0,
            }
            adapter = NatsAdapterClient("nats_client", config)
            assert len(adapter.servers) == 2
            assert adapter.timeout == 15.0
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_connect(self, mock_nats, nats_client_config) -> None:
        """Test async connection."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)

            await adapter._async_connect()

            assert adapter._nc == mock_client
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_disconnect(self, mock_nats, nats_client_config) -> None:
        """Test async disconnection."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = mock_client

            mock_client.close = AsyncMock()

            await adapter._async_disconnect()

            assert mock_client.close.called
            assert adapter._nc is None
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_publish(self, mock_nats, nats_client_config) -> None:
        """Test async publish."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = mock_client

            mock_client.publish = AsyncMock()

            subject = "test.subject"
            data = b'{"key": "value"}'
            headers = {"X-Trace-Id": "12345"}

            await adapter._async_publish(subject, data, headers)

            mock_client.publish.assert_called_once_with(subject, data, headers=headers)
        except ImportError:
            pytest.skip("nats-py not available")

    def test_connect_failure(self, nats_client_config) -> None:
        """Test connection failure handling."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)

            # Mock async_connect to raise error
            async def failing_connect():
                raise Exception("Connection failed")

            adapter._async_connect = failing_connect

            with pytest.raises(AdapterConnectionError):
                adapter.connect()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_request_not_connected(self, nats_client_config) -> None:
        """Test request when not connected."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = False

            envelope = Envelope(path="test.subject", data={"key": "value"})

            with pytest.raises(AdapterConnectionError, match="not connected"):
                adapter.request(envelope)
        except ImportError:
            pytest.skip("nats-py not available")

    def test_request_success(self, mock_nats, nats_client_config) -> None:
        """Test successful request."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = True
            adapter._nc = mock_client
            adapter._loop = asyncio.new_event_loop()

            # Mock async publish - use AsyncMock to avoid coroutine warnings
            adapter._async_publish = AsyncMock(return_value=None)

            # Create event loop thread
            import threading

            def run_loop():
                asyncio.set_event_loop(adapter._loop)
                adapter._loop.run_forever()

            thread = threading.Thread(target=run_loop, daemon=True)
            thread.start()

            envelope = Envelope(path="test.subject", data={"key": "value"})

            # Mock run_coroutine_threadsafe
            with patch("hexswitch.adapters.nats.outbound_adapter.asyncio.run_coroutine_threadsafe") as mock_run:
                mock_future = MagicMock()
                mock_future.result.return_value = None
                mock_run.return_value = mock_future

                result = adapter.request(envelope)

                assert result.status_code == 200
                assert "published" in result.data.get("status", "")

            adapter._loop.call_soon_threadsafe(adapter._loop.stop)
            thread.join(timeout=2.0)
            # Ensure loop is closed
            if not adapter._loop.is_closed():
                adapter._loop.close()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_connect_already_connected(self, nats_client_config) -> None:
        """Test connect when already connected."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = True

            # Should not raise, just log warning
            adapter.connect()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_connect_nats_not_available(self) -> None:
        """Test connect when NATS is not available."""
        with patch("hexswitch.adapters.nats.outbound_adapter.NATS_AVAILABLE", False):
            config = {"servers": ["nats://localhost:4222"]}
            adapter = NatsAdapterClient("nats_client", config)
            with pytest.raises(AdapterConnectionError, match="nats-py package"):
                adapter.connect()

    @pytest.mark.asyncio
    async def test_async_publish_not_connected(self, nats_client_config) -> None:
        """Test async publish when not connected."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = None

            with pytest.raises(AdapterConnectionError, match="not connected"):
                await adapter._async_publish("test.subject", b"data", {})
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_publish_no_headers(self, mock_nats, nats_client_config) -> None:
        """Test async publish without headers."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = mock_client

            mock_client.publish = AsyncMock()

            await adapter._async_publish("test.subject", b"data", {})

            mock_client.publish.assert_called_once_with("test.subject", b"data", headers=None)
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_request_not_connected(self, nats_client_config) -> None:
        """Test async request when not connected."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = None

            with pytest.raises(AdapterConnectionError, match="not connected"):
                await adapter._async_request("test.subject", b"data", {}, 30.0)
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_request_no_headers(self, mock_nats, nats_client_config) -> None:
        """Test async request without headers."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = mock_client

            mock_response = MagicMock()
            mock_client.request = AsyncMock(return_value=mock_response)

            result = await adapter._async_request("test.subject", b"data", {}, 30.0)

            mock_client.request.assert_called_once_with("test.subject", b"data", timeout=30.0, headers=None)
            assert result == mock_response
        except ImportError:
            pytest.skip("nats-py not available")

    def test_request_timeout(self, mock_nats, nats_client_config) -> None:
        """Test request with timeout."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = True
            adapter._nc = mock_client
            adapter._loop = asyncio.new_event_loop()
            adapter.timeout = 1.0  # Short timeout

            # Mock _async_publish to avoid coroutine warnings during garbage collection
            adapter._async_publish = AsyncMock(return_value=None)

            envelope = Envelope(path="test.subject", data={"key": "value"})

            # Mock run_coroutine_threadsafe to raise TimeoutError
            with patch("hexswitch.adapters.nats.outbound_adapter.asyncio.run_coroutine_threadsafe") as mock_run:
                mock_future = MagicMock()
                mock_future.result.side_effect = asyncio.TimeoutError()
                mock_run.return_value = mock_future

                with pytest.raises(AdapterConnectionError, match="timeout"):
                    adapter.request(envelope)

            if adapter._loop and not adapter._loop.is_closed():
                adapter._loop.close()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_request_exception(self, mock_nats, nats_client_config) -> None:
        """Test request with exception."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = True
            adapter._nc = mock_client
            adapter._loop = asyncio.new_event_loop()

            # Mock _async_publish to avoid coroutine warnings during garbage collection
            adapter._async_publish = AsyncMock(return_value=None)

            envelope = Envelope(path="test.subject", data={"key": "value"})

            # Mock run_coroutine_threadsafe to raise exception
            with patch("hexswitch.adapters.nats.outbound_adapter.asyncio.run_coroutine_threadsafe") as mock_run:
                mock_future = MagicMock()
                mock_future.result.side_effect = Exception("Connection error")
                mock_run.return_value = mock_future

                result = adapter.request(envelope)

                assert result.status_code == 500
                assert "error" in result.error_message.lower()

            if adapter._loop and not adapter._loop.is_closed():
                adapter._loop.close()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_disconnect_not_connected(self, nats_client_config) -> None:
        """Test disconnect when not connected."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = False

            # Should not raise, just log warning
            adapter.disconnect()
        except ImportError:
            pytest.skip("nats-py not available")

    def test_disconnect_loop_not_running(self, nats_client_config) -> None:
        """Test disconnect when loop is not running."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = True

            # Mock loop that is not running
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = False
            adapter._loop = mock_loop

            # Should not raise
            adapter.disconnect()

            assert adapter._connected is False
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_disconnect_no_connection(self, nats_client_config) -> None:
        """Test async disconnect when no connection."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = None

            # Should not raise
            await adapter._async_disconnect()

            assert adapter._nc is None
        except ImportError:
            pytest.skip("nats-py not available")

    @pytest.mark.asyncio
    async def test_async_disconnect_with_exception(self, mock_nats, nats_client_config) -> None:
        """Test async disconnect with exception."""
        try:
            mock_client, _ = mock_nats
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._nc = mock_client

            # Mock close to raise exception
            mock_client.close = AsyncMock(side_effect=Exception("Close error"))

            # Mock _async_publish to avoid coroutine warnings during garbage collection
            adapter._async_publish = AsyncMock(return_value=None)

            # Should not raise, just log warning
            await adapter._async_disconnect()

            assert adapter._nc is None
        except ImportError:
            pytest.skip("nats-py not available")

    def test_request_nc_none(self, nats_client_config) -> None:
        """Test request when _nc is None."""
        try:
            adapter = NatsAdapterClient("nats_client", nats_client_config)
            adapter._connected = True
            adapter._nc = None  # Not connected

            envelope = Envelope(path="test.subject", data={"key": "value"})

            with pytest.raises(AdapterConnectionError, match="not connected"):
                adapter.request(envelope)
        except ImportError:
            pytest.skip("nats-py not available")

