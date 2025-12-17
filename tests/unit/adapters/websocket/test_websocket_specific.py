"""WebSocket adapter specific tests."""

import asyncio
import json
import time
from types import ModuleType

import pytest
import websockets

from hexswitch.adapters.exceptions import AdapterStartError
from hexswitch.adapters.websocket import WebSocketAdapterServer
from tests.unit.adapters.base.adapter_tester import AdapterTester
from tests.unit.adapters.base.security_test_base import SecurityTestBase


@pytest.mark.fast
def test_websocket_adapter_default_config() -> None:
    """Test WebSocket adapter with default configuration."""
    config = {"enabled": True, "routes": []}
    adapter = WebSocketAdapterServer("websocket", config)
    assert adapter.port == 8080
    assert adapter.path == "/ws"


@pytest.mark.fast
def test_websocket_adapter_with_routes(handler_module: ModuleType) -> None:
    """Test WebSocket adapter with route configuration."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [
            {
                "path": "/test",
                "handler": "test_handler_module:test_handler",
            }
        ],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port
    adapter = WebSocketAdapterServer("websocket", config)

    try:
        adapter.start()
        time.sleep(0.5)
        assert adapter.is_running() is True
    finally:
        adapter.stop()


@pytest.mark.fast
def test_websocket_adapter_invalid_handler() -> None:
    """Test WebSocket adapter with invalid handler."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [
            {
                "path": "/test",
                "handler": "nonexistent.module:handler",
            }
        ],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port
    adapter = WebSocketAdapterServer("websocket", config)

    with pytest.raises(AdapterStartError):
        adapter.start()


@pytest.mark.security
class TestWebSocketAdapterSecurity(SecurityTestBase):
    """Test WebSocket adapter security features."""

    def test_message_flooding_protection(self, handler_module: ModuleType) -> None:
        """Test protection against message flooding."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = WebSocketAdapterServer("websocket", config)

        try:
            adapter.start()
            time.sleep(0.5)

            async def flood_messages():
                uri = f"ws://localhost:{free_port}/ws/test"
                try:
                    async with websockets.connect(uri) as ws:
                        # Send 100 messages rapidly
                        for _ in range(100):
                            await ws.send(json.dumps({"message": "flood"}))
                            await asyncio.sleep(0.001)
                except Exception:
                    pass

            # Run flood test
            asyncio.run(flood_messages())
            time.sleep(0.5)

            # Adapter should still be running
            assert adapter.is_running() is True
        finally:
            adapter.stop()

    def test_oversized_message_handling(self, handler_module: ModuleType) -> None:
        """Test handling of oversized messages."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = WebSocketAdapterServer("websocket", config)

        try:
            adapter.start()
            time.sleep(0.5)

            async def send_large_message():
                uri = f"ws://localhost:{free_port}/ws/test"
                try:
                    async with websockets.connect(uri) as ws:
                        # Send 1MB message
                        large_message = "A" * (1024 * 1024)
                        await ws.send(json.dumps({"data": large_message}))
                except Exception:
                    # Error is acceptable for oversized messages
                    pass

            asyncio.run(send_large_message())
        finally:
            adapter.stop()

    def test_malformed_json_handling(self, handler_module: ModuleType) -> None:
        """Test handling of malformed JSON messages."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = WebSocketAdapterServer("websocket", config)

        try:
            adapter.start()
            time.sleep(0.5)

            async def send_malformed():
                uri = f"ws://localhost:{free_port}/ws/test"
                try:
                    async with websockets.connect(uri) as ws:
                        await ws.send("{invalid json}")
                        # Should handle gracefully
                except Exception:
                    pass

            asyncio.run(send_malformed())
        finally:
            adapter.stop()

