"""Unit tests for MCP outbound adapter."""

from unittest.mock import Mock, patch

import pytest

from hexswitch.adapters.exceptions import AdapterConnectionError
from hexswitch.adapters.mcp.outbound_adapter import McpAdapterClient
from hexswitch.shared.envelope import Envelope


@pytest.mark.fast
def test_mcp_adapter_initialization():
    """Test MCP adapter initialization."""
    config = {"server_url": "https://mcp.example.com", "timeout": 60}
    adapter = McpAdapterClient("mcp_client", config)

    assert adapter.name == "mcp_client"
    assert adapter.server_url == "https://mcp.example.com"
    assert adapter._request_id == 0
    assert not adapter._connected


@pytest.mark.fast
def test_mcp_adapter_initialization_missing_server_url():
    """Test MCP adapter initialization without server_url."""
    config = {}

    with pytest.raises(ValueError, match="requires 'server_url'"):
        McpAdapterClient("mcp_client", config)


@pytest.mark.fast
def test_mcp_adapter_initialization_default_timeout():
    """Test MCP adapter initialization with default timeout."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    assert adapter._http_client.timeout == 30


@pytest.mark.fast
def test_mcp_adapter_connect_success():
    """Test successful connection to MCP server."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    # Mock HTTP client
    adapter._http_client = Mock()
    adapter._http_client.connect = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)

    # Mock _send_request to avoid actual HTTP call
    adapter._send_request = Mock(return_value={"result": "ok"})

    adapter.connect()

    assert adapter._connected is True
    adapter._http_client.connect.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_connect_already_connected():
    """Test connecting when already connected."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)
    adapter._connected = True

    adapter._http_client = Mock()
    adapter._http_client.connect = Mock()

    with patch("hexswitch.adapters.mcp.outbound_adapter.logger") as mock_logger:
        adapter.connect()
        mock_logger.warning.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_connect_failure():
    """Test connection failure."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.connect = Mock(side_effect=Exception("Connection failed"))
    adapter._http_client.disconnect = Mock()

    with pytest.raises(AdapterConnectionError):
        adapter.connect()

    adapter._http_client.disconnect.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_connect_initialize_failure():
    """Test connection failure during initialize."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.connect = Mock()
    adapter._http_client.disconnect = Mock()

    # Mock _send_request to raise error
    adapter._send_request = Mock(side_effect=Exception("Initialize failed"))

    with pytest.raises(AdapterConnectionError):
        adapter.connect()

    adapter._http_client.disconnect.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_disconnect_success():
    """Test successful disconnection."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)
    adapter._connected = True

    adapter._http_client = Mock()
    adapter._http_client.disconnect = Mock()

    adapter.disconnect()

    assert adapter._connected is False
    adapter._http_client.disconnect.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_disconnect_not_connected():
    """Test disconnecting when not connected."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()

    with patch("hexswitch.adapters.mcp.outbound_adapter.logger") as mock_logger:
        adapter.disconnect()
        mock_logger.warning.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_disconnect_error():
    """Test disconnection error handling."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)
    adapter._connected = True

    adapter._http_client = Mock()
    adapter._http_client.disconnect = Mock(side_effect=Exception("Disconnect error"))

    with patch("hexswitch.adapters.mcp.outbound_adapter.logger") as mock_logger:
        adapter.disconnect()
        mock_logger.error.assert_called_once()

    # Note: In the actual implementation, _connected is only set to False if disconnect succeeds
    # This test verifies that errors are logged but the state may remain True
    # This is the current behavior of the code


@pytest.mark.fast
def test_mcp_adapter_get_next_request_id():
    """Test getting next request ID."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    assert adapter._get_next_request_id() == 1
    assert adapter._get_next_request_id() == 2
    assert adapter._get_next_request_id() == 3


@pytest.mark.fast
def test_mcp_adapter_get_next_request_id_thread_safe():
    """Test request ID generation is thread-safe."""
    import threading

    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    ids = []

    def get_id():
        ids.append(adapter._get_next_request_id())

    threads = [threading.Thread(target=get_id) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All IDs should be unique
    assert len(set(ids)) == 10


@pytest.mark.fast
def test_mcp_adapter_request_not_connected():
    """Test request when not connected."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=False)

    envelope = Envelope(path="/test", method="POST", body={"param": "value"})

    with pytest.raises(RuntimeError, match="not connected"):
        adapter.request(envelope)


@pytest.mark.fast
def test_mcp_adapter_request_success():
    """Test successful request."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)

    response_envelope = Envelope.success({"result": "ok"})
    response_envelope.data = {"jsonrpc": "2.0", "id": 1, "result": {"result": "ok"}}

    adapter._http_client.request = Mock(return_value=response_envelope)

    request_envelope = Envelope(path="/test", method="POST", body={"param": "value"})
    result = adapter.request(request_envelope)

    assert isinstance(result, Envelope)
    adapter._http_client.request.assert_called_once()


@pytest.mark.fast
def test_mcp_adapter_request_no_data():
    """Test request when response has no data."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)

    response_envelope = Envelope.success({})
    response_envelope.data = None

    adapter._http_client.request = Mock(return_value=response_envelope)

    request_envelope = Envelope(path="/test", method="POST", body={"param": "value"})
    result = adapter.request(request_envelope)

    assert result == response_envelope


@pytest.mark.fast
def test_mcp_adapter_request_exception():
    """Test request when exception occurs."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)
    adapter._http_client.request = Mock(side_effect=Exception("Request failed"))

    request_envelope = Envelope(path="/test", method="POST", body={"param": "value"})
    result = adapter.request(request_envelope)

    assert result.error_message is not None
    assert result.status_code == 500


@pytest.mark.fast
def test_mcp_adapter_from_envelope():
    """Test converting envelope to JSON-RPC request."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    envelope = Envelope(path="/test_method", method="POST", body={"param1": "value1"})
    request = adapter.from_envelope(envelope)

    assert request["jsonrpc"] == "2.0"
    assert request["method"] == "test_method"
    assert request["params"] == {"param1": "value1"}
    assert "id" in request


@pytest.mark.fast
def test_mcp_adapter_from_envelope_empty_path():
    """Test converting envelope with empty path."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    envelope = Envelope(path="", method="POST", body={"param": "value"})
    envelope.metadata["method"] = "custom_method"

    request = adapter.from_envelope(envelope)

    assert request["method"] == "custom_method"


@pytest.mark.fast
def test_mcp_adapter_from_envelope_stripped_path():
    """Test converting envelope with path starting with /."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    envelope = Envelope(path="/test_method", method="POST", body={})
    request = adapter.from_envelope(envelope)

    assert request["method"] == "test_method"


@pytest.mark.fast
def test_mcp_adapter_to_envelope_success():
    """Test converting JSON-RPC response to envelope (success)."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    original_envelope = Envelope(path="/test", method="POST", body={})
    jsonrpc_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"data": "value"},
    }

    envelope = adapter.to_envelope(jsonrpc_response, original_envelope)

    assert envelope.status_code == 200
    assert envelope.data == {"data": "value"}
    assert envelope.path == "/test"


@pytest.mark.fast
def test_mcp_adapter_to_envelope_error():
    """Test converting JSON-RPC response to envelope (error)."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    original_envelope = Envelope(path="/test", method="POST", body={})
    jsonrpc_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"code": -32603, "message": "Internal error"},
    }

    envelope = adapter.to_envelope(jsonrpc_response, original_envelope)

    assert envelope.error_message is not None
    assert "MCP RPC error" in envelope.error_message
    assert envelope.status_code == -32603


@pytest.mark.fast
def test_mcp_adapter_to_envelope_error_no_code():
    """Test converting JSON-RPC response with error but no code."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    original_envelope = Envelope(path="/test", method="POST", body={})
    jsonrpc_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {"message": "Error message"},
    }

    envelope = adapter.to_envelope(jsonrpc_response, original_envelope)

    assert envelope.error_message is not None
    assert envelope.status_code == 500


@pytest.mark.fast
def test_mcp_adapter_to_envelope_no_original():
    """Test converting JSON-RPC response without original envelope."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    jsonrpc_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"data": "value"},
    }

    envelope = adapter.to_envelope(jsonrpc_response, None)

    assert envelope.status_code == 200
    assert envelope.data == {"data": "value"}
    assert envelope.path == ""


@pytest.mark.fast
def test_mcp_adapter_send_request_success():
    """Test _send_request method (legacy)."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)

    response_envelope = Envelope.success({"result": "ok"})
    response_envelope.data = {"jsonrpc": "2.0", "id": 1, "result": {"result": "ok"}}

    adapter._http_client.request = Mock(return_value=response_envelope)

    result = adapter._send_request("test_method", {"param": "value"})

    assert result == {"result": "ok"}


@pytest.mark.fast
def test_mcp_adapter_send_request_error():
    """Test _send_request method with error response."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)

    response_envelope = Envelope.error(500, "Server error")
    response_envelope.data = {"jsonrpc": "2.0", "id": 1, "error": {"code": 500, "message": "Server error"}}

    adapter._http_client.request = Mock(return_value=response_envelope)

    with pytest.raises(ValueError, match="Server error"):
        adapter._send_request("test_method", {})


@pytest.mark.fast
def test_mcp_adapter_send_request_not_connected():
    """Test _send_request when not connected."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=False)

    with pytest.raises(RuntimeError):
        adapter._send_request("test_method", {})


@pytest.mark.fast
def test_mcp_adapter_call_tool():
    """Test call_tool method."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={"result": "tool_result"})

    result = adapter.call_tool("test_tool", {"arg1": "value1"})

    assert result == {"result": "tool_result"}
    adapter._send_request.assert_called_once_with(
        "tools/call",
        {"name": "test_tool", "arguments": {"arg1": "value1"}},
    )


@pytest.mark.fast
def test_mcp_adapter_call_tool_no_arguments():
    """Test call_tool method without arguments."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={"result": "tool_result"})

    result = adapter.call_tool("test_tool")

    assert result == {"result": "tool_result"}
    adapter._send_request.assert_called_once_with(
        "tools/call",
        {"name": "test_tool", "arguments": {}},
    )


@pytest.mark.fast
def test_mcp_adapter_list_tools():
    """Test list_tools method."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={"tools": [{"name": "tool1"}, {"name": "tool2"}]})

    result = adapter.list_tools()

    assert result == [{"name": "tool1"}, {"name": "tool2"}]
    adapter._send_request.assert_called_once_with("tools/list")


@pytest.mark.fast
def test_mcp_adapter_list_tools_empty():
    """Test list_tools method with empty result."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={})

    result = adapter.list_tools()

    assert result == []


@pytest.mark.fast
def test_mcp_adapter_list_resources():
    """Test list_resources method."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={"resources": [{"uri": "res1"}, {"uri": "res2"}]})

    result = adapter.list_resources()

    assert result == [{"uri": "res1"}, {"uri": "res2"}]
    adapter._send_request.assert_called_once_with("resources/list")


@pytest.mark.fast
def test_mcp_adapter_list_resources_empty():
    """Test list_resources method with empty result."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={})

    result = adapter.list_resources()

    assert result == []


@pytest.mark.fast
def test_mcp_adapter_get_resource():
    """Test get_resource method."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._send_request = Mock(return_value={"content": "resource_data"})

    result = adapter.get_resource("resource://test/resource")

    assert result == {"content": "resource_data"}
    adapter._send_request.assert_called_once_with(
        "resources/read",
        {"uri": "resource://test/resource"},
    )


@pytest.mark.fast
def test_mcp_adapter_request_metadata_preserved():
    """Test that request metadata is preserved in HTTP envelope."""
    config = {"server_url": "https://mcp.example.com"}
    adapter = McpAdapterClient("mcp_client", config)

    adapter._http_client = Mock()
    adapter._http_client.is_connected = Mock(return_value=True)

    response_envelope = Envelope.success({"result": "ok"})
    response_envelope.data = {"jsonrpc": "2.0", "id": 1, "result": {"result": "ok"}}

    adapter._http_client.request = Mock(return_value=response_envelope)

    request_envelope = Envelope(
        path="/test",
        method="POST",
        body={"param": "value"},
        metadata={"custom": "metadata"},
    )

    adapter.request(request_envelope)

    # Check that HTTP request was called with metadata
    call_args = adapter._http_client.request.call_args[0][0]
    assert call_args.metadata.get("custom") == "metadata"
    assert "mcp_method" in call_args.metadata
    assert "mcp_request_id" in call_args.metadata

