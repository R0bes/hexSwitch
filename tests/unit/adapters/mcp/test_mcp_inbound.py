"""Unit tests for MCP inbound adapter."""

import json
import sys
import time
from http.server import HTTPServer
from io import BytesIO
from types import ModuleType
from unittest.mock import MagicMock, Mock, patch

import pytest

from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError, HandlerError
from hexswitch.adapters.mcp.inbound_adapter import McpAdapterServer, McpRequestHandler
from hexswitch.handlers.loader import HandlerLoader
from hexswitch.ports import PortError, get_port_registry
from hexswitch.shared.envelope import Envelope


class TestMcpAdapterServer:
    """Test MCP adapter server."""

    def test_initialization(self) -> None:
        """Test adapter initialization."""
        config = {"port": 3000, "methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        assert adapter.name == "test_mcp"
        assert adapter.port == 3000
        assert adapter.methods == []
        assert not adapter._running

    def test_initialization_default_port(self) -> None:
        """Test adapter initialization with default port."""
        config = {"methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        assert adapter.port == 3000

    def test_start_success(self) -> None:
        """Test successful adapter start."""
        config = {"port": 0, "methods": []}  # Port 0 = random available port
        adapter = McpAdapterServer("test_mcp", config)
        adapter.start()
        assert adapter._running
        assert adapter.server is not None
        adapter.stop()

    def test_start_already_running(self) -> None:
        """Test starting already running adapter."""
        config = {"port": 0, "methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        adapter.start()
        with patch("hexswitch.adapters.mcp.inbound_adapter.logger") as mock_logger:
            adapter.start()
            mock_logger.warning.assert_called_once()
        adapter.stop()

    def test_start_error(self) -> None:
        """Test adapter start error."""
        config = {"port": 0, "methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        with patch("hexswitch.adapters.mcp.inbound_adapter.HTTPServer") as mock_server:
            mock_server.side_effect = Exception("Server error")
            with pytest.raises(AdapterStartError):
                adapter.start()

    def test_stop_success(self) -> None:
        """Test successful adapter stop."""
        config = {"port": 0, "methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        adapter.start()
        time.sleep(0.1)  # Give server time to start
        adapter.stop()
        assert not adapter._running

    def test_stop_not_running(self) -> None:
        """Test stopping non-running adapter."""
        config = {"port": 0, "methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        with patch("hexswitch.adapters.mcp.inbound_adapter.logger") as mock_logger:
            adapter.stop()
            mock_logger.warning.assert_called_once()

    def test_stop_error(self) -> None:
        """Test adapter stop error."""
        config = {"port": 0, "methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        adapter.start()
        time.sleep(0.1)
        with patch.object(adapter.server, "shutdown") as mock_shutdown:
            mock_shutdown.side_effect = Exception("Shutdown error")
            with pytest.raises(AdapterStopError):
                adapter.stop()

    def test_to_envelope(self) -> None:
        """Test converting MCP request to envelope."""
        config = {"methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        envelope = adapter.to_envelope(
            method="test_method",
            params={"param1": "value1"},
            request_id=1,
            headers={"Content-Type": "application/json"},
        )
        assert envelope.path == "/test_method"
        assert envelope.method == "POST"
        assert envelope.body == {"param1": "value1"}
        assert envelope.metadata["mcp_method"] == "test_method"
        assert envelope.metadata["mcp_request_id"] == 1

    def test_from_envelope_success(self) -> None:
        """Test converting envelope to MCP response (success)."""
        config = {"methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        envelope = Envelope(path="/test", method="POST", body={"result": "ok"})
        envelope.data = {"result": "ok"}  # Set data explicitly
        response = adapter.from_envelope(envelope, request_id=1)
        assert response["jsonrpc"] == "2.0"
        assert response["result"] == {"result": "ok"}
        assert response["id"] == 1

    def test_from_envelope_error(self) -> None:
        """Test converting envelope to MCP response (error)."""
        config = {"methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        envelope = Envelope.error(500, "Internal error")
        response = adapter.from_envelope(envelope, request_id=1)
        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == 500
        assert response["error"]["message"] == "Internal error"
        assert response["id"] == 1

    def test_from_envelope_error_no_status_code(self) -> None:
        """Test converting envelope to MCP response (error without status code)."""
        config = {"methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        envelope = Envelope(path="/test", method="POST", body={})
        envelope.error_message = "Error"
        envelope.status_code = None
        response = adapter.from_envelope(envelope, request_id=1)
        assert response["error"]["code"] == -32603

    def test_from_envelope_error_with_data(self) -> None:
        """Test converting envelope to MCP response (error with data)."""
        config = {"methods": []}
        adapter = McpAdapterServer("test_mcp", config)
        envelope = Envelope(path="/test", method="POST", body={})
        envelope.error_message = "Error"
        envelope.status_code = 500
        response = adapter.from_envelope(envelope, request_id=1)
        assert response["error"]["code"] == 500
        assert response["error"]["message"] == "Error"


class TestMcpRequestHandler:
    """Test MCP request handler."""

    def test_handler_initialization(self) -> None:
        """Test handler initialization."""
        methods = [{"method_name": "test_method", "handler": "test:handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        # Create a mock request/response
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)
            assert handler.methods == methods
            assert handler._adapter == adapter
            assert handler._handler_loader is None

    def test_handler_initialization_with_loader(self) -> None:
        """Test handler initialization with handler loader."""
        methods = [{"method_name": "test_method", "handler": "test:handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        loader = HandlerLoader()

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock rfile before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, loader, mock_request, mock_client_address, mock_server)
            assert handler._handler_loader == loader

    def test_log_message(self) -> None:
        """Test log message method."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock rfile before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            with patch("hexswitch.adapters.mcp.inbound_adapter.logger") as mock_logger:
                handler.log_message("Test message %s", "arg1")
                mock_logger.debug.assert_called_once()

    def test_do_post_parse_error(self) -> None:
        """Test POST with parse error."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock rfile before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            # Mock request attributes
            handler.rfile = BytesIO(b"invalid json")
            handler.headers = Mock()
            handler.headers.get.return_value = "12"
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_invalid_request_not_dict(self) -> None:
        """Test POST with invalid request (not a dict)."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            handler.rfile = BytesIO(json.dumps("not a dict").encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps("not a dict")))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_invalid_jsonrpc_version(self) -> None:
        """Test POST with invalid JSON-RPC version."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "1.0", "method": "test", "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_missing_method(self) -> None:
        """Test POST with missing method."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_method_not_found(self) -> None:
        """Test POST with method not found."""
        methods = [{"method_name": "other_method", "handler": "test:handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "unknown_method", "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_with_port_handler_loader(self) -> None:
        """Test POST with port using handler loader."""
        # Create test port
        def test_port(envelope: Envelope) -> Envelope:
            return Envelope(path="/test", data={"result": "success"})

        port_registry = get_port_registry()
        port_registry.register_handler("test_port", test_port)

        methods = [{"method_name": "test_method", "port": "test_port"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        loader = HandlerLoader()

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, loader, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_with_handler_loader(self) -> None:
        """Test POST with handler using handler loader."""
        # Create test handler module
        test_module = ModuleType("test_mcp_handler")
        def test_handler(envelope: Envelope) -> Envelope:
            return Envelope(path="/test", data={"result": "success"})
        test_module.test_handler = test_handler
        sys.modules["test_mcp_handler"] = test_module

        methods = [{"method_name": "test_method", "handler": "test_mcp_handler:test_handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        loader = HandlerLoader()

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, loader, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

        # Cleanup
        if "test_mcp_handler" in sys.modules:
            del sys.modules["test_mcp_handler"]

    def test_do_post_with_port_fallback(self) -> None:
        """Test POST with port using fallback method."""
        def test_port(envelope: Envelope) -> Envelope:
            return Envelope(path="/test", data={"result": "success"})

        port_registry = get_port_registry()
        port_registry.register_handler("test_port_fallback", test_port)

        methods = [{"method_name": "test_method", "port": "test_port_fallback"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_do_post_with_handler_fallback(self) -> None:
        """Test POST with handler using fallback method."""
        test_module = ModuleType("test_mcp_handler_fallback")
        def test_handler(envelope: Envelope) -> Envelope:
            return Envelope(path="/test", data={"result": "success"})
        test_module.test_handler = test_handler
        sys.modules["test_mcp_handler_fallback"] = test_module

        methods = [{"method_name": "test_method", "handler": "test_mcp_handler_fallback:test_handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

        # Cleanup
        if "test_mcp_handler_fallback" in sys.modules:
            del sys.modules["test_mcp_handler_fallback"]

    def test_do_post_handler_error(self) -> None:
        """Test POST with handler error."""
        test_module = ModuleType("test_mcp_handler_error")
        def test_handler(envelope: Envelope) -> Envelope:
            raise Exception("Handler error")
        test_module.test_handler = test_handler
        sys.modules["test_mcp_handler_error"] = test_module

        methods = [{"method_name": "test_method", "handler": "test_mcp_handler_error:test_handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            with patch("hexswitch.adapters.mcp.inbound_adapter.logger") as mock_logger:
                handler.do_POST()
                mock_logger.exception.assert_called()
                handler.send_response.assert_called_with(200)

        # Cleanup
        if "test_mcp_handler_error" in sys.modules:
            del sys.modules["test_mcp_handler_error"]

    def test_do_post_port_error(self) -> None:
        """Test POST with port error."""
        methods = [{"method_name": "test_method", "port": "nonexistent_port"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            with patch("hexswitch.adapters.mcp.inbound_adapter.logger") as mock_logger:
                handler.do_POST()
                mock_logger.error.assert_called()
                handler.send_response.assert_called_with(200)

    def test_do_post_no_handler_or_port(self) -> None:
        """Test POST with method that has neither handler nor port."""
        methods = [{"method_name": "test_method"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            request = {"jsonrpc": "2.0", "method": "test_method", "params": {}, "id": 1}
            handler.rfile = BytesIO(json.dumps(request).encode())
            handler.headers = Mock()
            handler.headers.get.return_value = str(len(json.dumps(request)))
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            with patch("hexswitch.adapters.mcp.inbound_adapter.logger") as mock_logger:
                handler.do_POST()
                mock_logger.error.assert_called()
                handler.send_response.assert_called_with(200)

    def test_send_jsonrpc_response(self) -> None:
        """Test sending JSON-RPC response."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            response = {"jsonrpc": "2.0", "result": {"key": "value"}, "id": 1}
            handler._send_jsonrpc_response(response)

            handler.send_response.assert_called_with(200)
            handler.send_header.assert_any_call("Content-Type", "application/json")
            assert handler.wfile.getvalue() == json.dumps(response).encode()

    def test_send_jsonrpc_error(self) -> None:
        """Test sending JSON-RPC error."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler._send_jsonrpc_error(-32600, "Invalid Request", 1, "Test error data")

            handler.send_response.assert_called_with(200)
            handler.send_header.assert_any_call("Content-Type", "application/json")
            response_data = json.loads(handler.wfile.getvalue().decode())
            assert response_data["error"]["code"] == -32600
            assert response_data["error"]["message"] == "Invalid Request"
            assert response_data["error"]["data"] == "Test error data"
            assert response_data["id"] == 1

    def test_send_jsonrpc_error_no_data(self) -> None:
        """Test sending JSON-RPC error without data."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler._send_jsonrpc_error(-32600, "Invalid Request", 1)

            response_data = json.loads(handler.wfile.getvalue().decode())
            assert "data" not in response_data["error"]

    def test_send_jsonrpc_error_no_request_id(self) -> None:
        """Test sending JSON-RPC error without request ID."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler._send_jsonrpc_error(-32700, "Parse error", None)

            response_data = json.loads(handler.wfile.getvalue().decode())
            assert response_data["id"] is None

    def test_do_post_empty_body(self) -> None:
        """Test POST with empty body."""
        methods = []
        adapter = McpAdapterServer("test_mcp", {"methods": methods})
        mock_request = Mock()
        mock_client_address = ("127.0.0.1", 12345)
        mock_server = Mock()

        # Mock handle_one_request before initialization to prevent BaseHTTPRequestHandler from trying to read
        with patch("hexswitch.adapters.mcp.inbound_adapter.BaseHTTPRequestHandler.handle_one_request"):
            handler = McpRequestHandler(methods, adapter, None, mock_request, mock_client_address, mock_server)

            handler.rfile = BytesIO(b"")
            handler.headers = Mock()
            handler.headers.get.return_value = "0"
            handler.send_response = Mock()
            handler.send_header = Mock()
            handler.end_headers = Mock()
            handler.wfile = BytesIO()

            handler.do_POST()
            handler.send_response.assert_called_with(200)

    def test_start_handler_factory(self) -> None:
        """Test handler factory in start method."""
        methods = [{"method_name": "test_method", "handler": "test:handler"}]
        adapter = McpAdapterServer("test_mcp", {"methods": methods})

        with patch("hexswitch.adapters.mcp.inbound_adapter.HTTPServer") as mock_server_class:
            mock_server_instance = Mock()
            mock_server_class.return_value = mock_server_instance

            adapter.start()
            assert adapter._running

            # Verify handler factory was used
            mock_server_class.assert_called_once()
            call_args = mock_server_class.call_args
            assert call_args[0][1] is not None  # Handler factory function

            adapter.stop()

