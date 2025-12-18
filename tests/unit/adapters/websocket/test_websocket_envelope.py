"""Unit tests for WebSocketEnvelope conversion logic."""


import pytest

from hexswitch.adapters.websocket._WebSocket_Envelope import WebSocketEnvelope
from hexswitch.shared.envelope import Envelope


@pytest.mark.fast
class TestWebSocketEnvelope:
    """Test WebSocketEnvelope conversion methods."""

    def test_request_to_envelope_delegates_to_message_to_envelope(self):
        """Test that request_to_envelope delegates to message_to_envelope."""
        envelope_converter = WebSocketEnvelope()
        message = '{"test": "data"}'
        path = "/test"

        result = envelope_converter.request_to_envelope(message, path)

        assert isinstance(result, Envelope)
        assert result.path == path
        assert result.body == {"test": "data"}

    def test_message_to_envelope_with_string_json(self):
        """Test message_to_envelope with string JSON message."""
        envelope_converter = WebSocketEnvelope()
        message = '{"key": "value", "number": 42}'
        path = "/test"
        remote_address = "127.0.0.1"
        websocket_id = 123

        result = envelope_converter.message_to_envelope(
            message, path, remote_address, websocket_id
        )

        assert isinstance(result, Envelope)
        assert result.path == path
        assert result.method is None
        assert result.body == {"key": "value", "number": 42}
        assert result.metadata["raw_message"] == message
        assert result.metadata["remote_address"] == remote_address
        assert result.metadata["websocket_id"] == websocket_id

    def test_message_to_envelope_with_bytes_json(self):
        """Test message_to_envelope with bytes JSON message."""
        envelope_converter = WebSocketEnvelope()
        message = b'{"key": "value"}'
        path = "/test"

        result = envelope_converter.message_to_envelope(message, path)

        assert isinstance(result, Envelope)
        assert result.path == path
        assert result.body == {"key": "value"}
        assert result.metadata["raw_message"] == str(message)

    def test_message_to_envelope_with_invalid_json_fallback(self):
        """Test message_to_envelope with invalid JSON falls back to raw message."""
        envelope_converter = WebSocketEnvelope()
        message = "not valid json"
        path = "/test"

        result = envelope_converter.message_to_envelope(message, path)

        assert isinstance(result, Envelope)
        assert result.path == path
        assert result.body == {"raw": "not valid json"}
        assert result.metadata["raw_message"] == message

    def test_message_to_envelope_with_bytes_invalid_json(self):
        """Test message_to_envelope with bytes that can't be decoded."""
        envelope_converter = WebSocketEnvelope()
        # Create bytes that can't be decoded as UTF-8
        message = b'\xff\xfe\x00\x01'
        path = "/test"

        result = envelope_converter.message_to_envelope(message, path)

        assert isinstance(result, Envelope)
        assert result.path == path
        # Should fall back to raw message in exception handler
        assert "raw" in result.body or result.body is None

    def test_message_to_envelope_without_optional_params(self):
        """Test message_to_envelope without optional parameters."""
        envelope_converter = WebSocketEnvelope()
        message = '{"test": "data"}'
        path = "/test"

        result = envelope_converter.message_to_envelope(message, path)

        assert isinstance(result, Envelope)
        assert result.path == path
        assert "remote_address" not in result.metadata
        assert "websocket_id" not in result.metadata

    def test_envelope_to_response_delegates_to_envelope_to_message(self):
        """Test that envelope_to_response delegates to envelope_to_message."""
        envelope_converter = WebSocketEnvelope()
        envelope = Envelope(path="/test", data={"result": "success"})

        result = envelope_converter.envelope_to_response(envelope)

        assert result == '{"result": "success"}'

    def test_envelope_to_message_with_error(self):
        """Test envelope_to_message with error_message."""
        envelope_converter = WebSocketEnvelope()
        envelope = Envelope(path="/test", error_message="Something went wrong")

        result = envelope_converter.envelope_to_message(envelope)

        assert result == '{"error": "Something went wrong"}'

    def test_envelope_to_message_with_data(self):
        """Test envelope_to_message with data."""
        envelope_converter = WebSocketEnvelope()
        envelope = Envelope(path="/test", data={"key": "value"})

        result = envelope_converter.envelope_to_message(envelope)

        assert result == '{"key": "value"}'

    def test_envelope_to_message_without_data_or_error(self):
        """Test envelope_to_message without data or error."""
        envelope_converter = WebSocketEnvelope()
        envelope = Envelope(path="/test")

        result = envelope_converter.envelope_to_message(envelope)

        assert result == "{}"

    def test_envelope_to_request_with_body(self):
        """Test envelope_to_request with body."""
        envelope_converter = WebSocketEnvelope()
        envelope = Envelope(path="/test", body={"action": "test"})

        result = envelope_converter.envelope_to_request(envelope)

        assert result == '{"action": "test"}'

    def test_envelope_to_request_without_body(self):
        """Test envelope_to_request without body."""
        envelope_converter = WebSocketEnvelope()
        envelope = Envelope(path="/test")

        result = envelope_converter.envelope_to_request(envelope)

        assert result == "{}"

    def test_response_to_envelope_delegates_to_message_to_envelope_response(self):
        """Test that response_to_envelope delegates to message_to_envelope_response."""
        envelope_converter = WebSocketEnvelope()
        message = '{"result": "ok"}'
        original_envelope = Envelope(path="/test", method="GET")

        result = envelope_converter.response_to_envelope(message, original_envelope)

        assert isinstance(result, Envelope)
        assert result.path == "/test"
        assert result.method == "GET"
        assert result.status_code == 200
        assert result.data == {"result": "ok"}

    def test_message_to_envelope_response_with_string_json(self):
        """Test message_to_envelope_response with string JSON."""
        envelope_converter = WebSocketEnvelope()
        message = '{"result": "success"}'
        original_envelope = Envelope(path="/test", method="POST")

        result = envelope_converter.message_to_envelope_response(message, original_envelope)

        assert isinstance(result, Envelope)
        assert result.path == "/test"
        assert result.method == "POST"
        assert result.status_code == 200
        assert result.data == {"result": "success"}
        assert result.metadata == original_envelope.metadata

    def test_message_to_envelope_response_with_bytes_json(self):
        """Test message_to_envelope_response with bytes JSON."""
        envelope_converter = WebSocketEnvelope()
        message = b'{"result": "ok"}'
        original_envelope = Envelope(path="/test")

        result = envelope_converter.message_to_envelope_response(message, original_envelope)

        assert isinstance(result, Envelope)
        assert result.status_code == 200
        assert result.data == {"result": "ok"}

    def test_message_to_envelope_response_with_error_message(self):
        """Test message_to_envelope_response with error in message."""
        envelope_converter = WebSocketEnvelope()
        message = '{"error": "Something went wrong"}'
        original_envelope = Envelope(path="/test", method="GET")
        original_envelope.metadata["test"] = "value"

        result = envelope_converter.message_to_envelope_response(message, original_envelope)

        assert isinstance(result, Envelope)
        assert result.path == "/test"
        assert result.method == "GET"
        assert result.status_code == 500
        assert result.error_message == "Something went wrong"
        assert result.metadata == original_envelope.metadata

    def test_message_to_envelope_response_with_invalid_json(self):
        """Test message_to_envelope_response with invalid JSON."""
        envelope_converter = WebSocketEnvelope()
        message = "not valid json"
        original_envelope = Envelope(path="/test")

        result = envelope_converter.message_to_envelope_response(message, original_envelope)

        assert isinstance(result, Envelope)
        assert result.status_code == 200
        assert result.data == {"raw": "not valid json"}

    def test_message_to_envelope_response_with_bytes_invalid_json(self):
        """Test message_to_envelope_response with bytes that can't be decoded."""
        envelope_converter = WebSocketEnvelope()
        message = b'\xff\xfe\x00\x01'
        original_envelope = Envelope(path="/test")

        result = envelope_converter.message_to_envelope_response(message, original_envelope)

        assert isinstance(result, Envelope)
        # Should handle exception and fall back to raw message
        assert result.status_code == 200

    def test_message_to_envelope_response_without_original_envelope(self):
        """Test message_to_envelope_response without original envelope."""
        envelope_converter = WebSocketEnvelope()
        message = '{"result": "ok"}'

        result = envelope_converter.message_to_envelope_response(message, None)

        assert isinstance(result, Envelope)
        assert result.path == ""
        assert result.method is None
        assert result.status_code == 200
        assert result.data == {"result": "ok"}
        assert result.metadata == {}

    def test_message_to_envelope_response_with_error_without_original_envelope(self):
        """Test message_to_envelope_response with error without original envelope."""
        envelope_converter = WebSocketEnvelope()
        message = '{"error": "Error occurred"}'

        result = envelope_converter.message_to_envelope_response(message, None)

        assert isinstance(result, Envelope)
        assert result.path == ""
        assert result.method is None
        assert result.status_code == 500
        assert result.error_message == "Error occurred"
        assert result.metadata == {}

    def test_message_to_envelope_response_with_non_dict_data(self):
        """Test message_to_envelope_response with non-dict JSON data."""
        envelope_converter = WebSocketEnvelope()
        message = '"just a string"'
        original_envelope = Envelope(path="/test")

        result = envelope_converter.message_to_envelope_response(message, original_envelope)

        assert isinstance(result, Envelope)
        assert result.status_code == 200
        # Non-dict data should result in None
        assert result.data is None

