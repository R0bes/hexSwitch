"""Extended unit tests for HTTP envelope conversion."""

import pytest

from hexswitch.adapters.http._Http_Envelope import HttpEnvelope
from hexswitch.shared.envelope import Envelope


class TestHttpEnvelopeExtended:
    """Extended tests for HTTP envelope conversion."""

    def test_request_to_envelope_with_query_params(self) -> None:
        """Test converting HTTP request with query params."""
        converter = HttpEnvelope()
        envelope = converter.request_to_envelope(
            method="GET",
            path="/test",
            headers={},
            query_params={"page": "1", "limit": "10"},
            body=b"",
        )

        assert envelope.method == "GET"
        assert envelope.path == "/test"
        assert envelope.query_params == {"page": "1", "limit": "10"}

    def test_request_to_envelope_with_path_params(self) -> None:
        """Test converting HTTP request with path params."""
        converter = HttpEnvelope()
        envelope = converter.request_to_envelope(
            method="GET",
            path="/users/123",
            headers={},
            query_params={},
            body=b"",
        )
        # Path params need to be extracted from path, not passed directly
        # This test verifies the basic conversion works
        assert envelope.path == "/users/123"

    def test_request_to_envelope_with_json_body(self) -> None:
        """Test converting HTTP request with JSON body."""
        converter = HttpEnvelope()
        body = b'{"name": "test", "value": 42}'
        envelope = converter.request_to_envelope(
            method="POST",
            path="/test",
            headers={"Content-Type": "application/json"},
            query_params={},
            body=body,
        )

        assert envelope.body == {"name": "test", "value": 42}

    def test_envelope_to_response_with_headers(self) -> None:
        """Test converting Envelope to HTTP response with headers."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=200,
            data={"result": "success"},
            headers={"X-Custom": "value"},
        )

        status_code, data, response_headers = converter.envelope_to_response(envelope)

        assert status_code == 200
        assert data == {"result": "success"}
        assert "X-Custom" in response_headers

    def test_envelope_to_response_error(self) -> None:
        """Test converting error Envelope to HTTP response."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=404,
            error_message="Not Found",
        )

        status_code, data, headers = converter.envelope_to_response(envelope)

        assert status_code == 404
        assert "error" in data
        assert data["error"] == "Not Found"

    def test_request_to_envelope_with_trace_context(self) -> None:
        """Test converting HTTP request with trace context."""
        converter = HttpEnvelope()
        headers = {
            "X-Trace-Id": "12345",
            "X-Span-Id": "67890",
        }
        envelope = converter.request_to_envelope(
            method="GET",
            path="/test",
            headers=headers,
            query_params={},
            body=b"",
        )

        assert envelope.trace_id == "12345"
        assert envelope.span_id == "67890"

    def test_request_to_envelope_with_cookies(self) -> None:
        """Test converting HTTP request with cookies."""
        converter = HttpEnvelope()
        headers = {
            "Cookie": "session=abc123; user=john; theme=dark",
        }
        envelope = converter.request_to_envelope(
            method="GET",
            path="/test",
            headers=headers,
            query_params={},
            body=b"",
        )

        assert "cookies" in envelope.metadata
        assert envelope.metadata["cookies"]["session"] == "abc123"
        assert envelope.metadata["cookies"]["user"] == "john"
        assert envelope.metadata["cookies"]["theme"] == "dark"

    def test_request_to_envelope_with_cookies_no_equals(self) -> None:
        """Test converting HTTP request with cookies that have no equals sign."""
        converter = HttpEnvelope()
        headers = {
            "Cookie": "invalid_cookie; valid=value",
        }
        envelope = converter.request_to_envelope(
            method="GET",
            path="/test",
            headers=headers,
            query_params={},
            body=b"",
        )

        assert "cookies" in envelope.metadata
        assert "valid" in envelope.metadata["cookies"]
        assert envelope.metadata["cookies"]["valid"] == "value"

    def test_request_to_envelope_with_session_id(self) -> None:
        """Test converting HTTP request with session ID."""
        converter = HttpEnvelope()
        headers = {
            "X-Session-ID": "session_abc123",
        }
        envelope = converter.request_to_envelope(
            method="GET",
            path="/test",
            headers=headers,
            query_params={},
            body=b"",
        )

        assert envelope.metadata["session_id"] == "session_abc123"

    def test_request_to_envelope_with_path_params(self) -> None:
        """Test converting HTTP request with path parameters."""
        converter = HttpEnvelope()
        envelope = converter.request_to_envelope(
            method="GET",
            path="/users/123",
            headers={},
            query_params={},
            body=b"",
            path_params={"id": "123"},
        )

        assert envelope.path_params == {"id": "123"}

    def test_request_to_envelope_with_empty_body(self) -> None:
        """Test converting HTTP request with empty body."""
        converter = HttpEnvelope()
        envelope = converter.request_to_envelope(
            method="GET",
            path="/test",
            headers={},
            query_params={},
            body=None,
        )

        assert envelope.body is None or envelope.body == {}

    def test_envelope_to_response_with_cookies(self) -> None:
        """Test converting Envelope to HTTP response with cookies."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=200,
            data={"result": "success"},
            metadata={"cookies": {"session": "abc123", "theme": "dark"}},
        )

        status_code, data, headers = converter.envelope_to_response(envelope)

        assert status_code == 200
        assert "Set-Cookie" in headers
        assert "session=abc123" in headers["Set-Cookie"]
        assert "theme=dark" in headers["Set-Cookie"]

    def test_envelope_to_response_with_session_id(self) -> None:
        """Test converting Envelope to HTTP response with session ID."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=200,
            data={"result": "success"},
            metadata={"session_id": "session_123"},
        )

        status_code, data, headers = converter.envelope_to_response(envelope)

        assert status_code == 200
        assert headers["X-Session-ID"] == "session_123"

    def test_envelope_to_response_with_trace_context(self) -> None:
        """Test converting Envelope to HTTP response with trace context."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=200,
            data={"result": "success"},
            trace_id="trace_123",
            span_id="span_456",
        )

        status_code, data, headers = converter.envelope_to_response(envelope)

        assert status_code == 200
        # Trace context should be injected into headers
        assert "X-Trace-Id" in headers or "traceparent" in headers

    def test_envelope_to_response_empty_data(self) -> None:
        """Test converting Envelope to HTTP response with empty data."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=200,
            data=None,
        )

        status_code, data, headers = converter.envelope_to_response(envelope)

        assert status_code == 200
        assert data == {}

    def test_envelope_to_response_cookies_not_dict(self) -> None:
        """Test converting Envelope to HTTP response with non-dict cookies."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            status_code=200,
            data={"result": "success"},
            metadata={"cookies": "not_a_dict"},
        )

        status_code, data, headers = converter.envelope_to_response(envelope)

        assert status_code == 200
        assert "Set-Cookie" not in headers

    def test_envelope_to_request_basic(self) -> None:
        """Test converting Envelope to HTTP request."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method="POST",
            headers={"Content-Type": "application/json"},
            body={"key": "value"},
        )

        method, url, headers, body = converter.envelope_to_request(envelope)

        assert method == "POST"
        assert url == "/test"
        assert headers["Content-Type"] == "application/json"
        assert body == {"key": "value"}

    def test_envelope_to_request_with_base_url(self) -> None:
        """Test converting Envelope to HTTP request with base URL."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method="GET",
        )

        method, url, headers, body = converter.envelope_to_request(envelope, base_url="https://api.example.com")

        assert method == "GET"
        assert url == "https://api.example.com/test"

    def test_envelope_to_request_with_cookies(self) -> None:
        """Test converting Envelope to HTTP request with cookies."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method="GET",
            metadata={"cookies": {"session": "abc123", "user": "john"}},
        )

        method, url, headers, body = converter.envelope_to_request(envelope)

        assert "Cookie" in headers
        assert "session=abc123" in headers["Cookie"]
        assert "user=john" in headers["Cookie"]

    def test_envelope_to_request_with_session_id(self) -> None:
        """Test converting Envelope to HTTP request with session ID."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method="GET",
            metadata={"session_id": "session_123"},
        )

        method, url, headers, body = converter.envelope_to_request(envelope)

        assert headers["X-Session-ID"] == "session_123"

    def test_envelope_to_request_with_trace_context(self) -> None:
        """Test converting Envelope to HTTP request with trace context."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method="GET",
            trace_id="trace_123",
            span_id="span_456",
        )

        method, url, headers, body = converter.envelope_to_request(envelope)

        # Trace context should be injected into headers
        assert "X-Trace-Id" in headers or "traceparent" in headers

    def test_envelope_to_request_default_method(self) -> None:
        """Test converting Envelope to HTTP request with default method."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method=None,
        )

        method, url, headers, body = converter.envelope_to_request(envelope)

        assert method == "GET"

    def test_envelope_to_request_cookies_not_dict(self) -> None:
        """Test converting Envelope to HTTP request with non-dict cookies."""
        converter = HttpEnvelope()
        envelope = Envelope(
            path="/test",
            method="GET",
            metadata={"cookies": "not_a_dict"},
        )

        method, url, headers, body = converter.envelope_to_request(envelope)

        assert "Cookie" not in headers

    def test_response_to_envelope_success(self) -> None:
        """Test converting HTTP response to Envelope (success)."""
        converter = HttpEnvelope()
        original_envelope = Envelope(path="/test", method="GET")

        envelope = converter.response_to_envelope(
            status_code=200,
            data={"result": "success"},
            headers={"Content-Type": "application/json"},
            original_envelope=original_envelope,
        )

        assert envelope.status_code == 200
        assert envelope.data == {"result": "success"}
        assert envelope.path == "/test"
        assert envelope.method == "GET"

    def test_response_to_envelope_error(self) -> None:
        """Test converting HTTP response to Envelope (error)."""
        converter = HttpEnvelope()
        original_envelope = Envelope(path="/test", method="POST")

        envelope = converter.response_to_envelope(
            status_code=404,
            data={"error": "Not Found"},
            headers={},
            original_envelope=original_envelope,
        )

        assert envelope.status_code == 404
        assert envelope.error_message == "Not Found"
        assert envelope.path == "/test"
        assert envelope.method == "POST"

    def test_response_to_envelope_error_with_string_data(self) -> None:
        """Test converting HTTP error response with string data."""
        converter = HttpEnvelope()

        envelope = converter.response_to_envelope(
            status_code=500,
            data="Internal Server Error",
            headers={},
        )

        assert envelope.status_code == 500
        assert envelope.error_message == "Internal Server Error"

    def test_response_to_envelope_error_default_message(self) -> None:
        """Test converting HTTP error response with default error message."""
        converter = HttpEnvelope()

        envelope = converter.response_to_envelope(
            status_code=500,
            data={},
            headers={},
        )

        assert envelope.status_code == 500
        assert envelope.error_message == "HTTP 500"

    def test_response_to_envelope_with_set_cookie(self) -> None:
        """Test converting HTTP response to Envelope with Set-Cookie header."""
        converter = HttpEnvelope()

        envelope = converter.response_to_envelope(
            status_code=200,
            data={"result": "success"},
            headers={"Set-Cookie": "session=abc123; Path=/, theme=dark; Path=/"},
        )

        assert "cookies" in envelope.metadata
        assert envelope.metadata["cookies"]["session"] == "abc123"
        assert envelope.metadata["cookies"]["theme"] == "dark"

    def test_response_to_envelope_with_session_id(self) -> None:
        """Test converting HTTP response to Envelope with session ID."""
        converter = HttpEnvelope()

        envelope = converter.response_to_envelope(
            status_code=200,
            data={"result": "success"},
            headers={"X-Session-ID": "session_123"},
        )

        assert envelope.metadata["session_id"] == "session_123"

    def test_response_to_envelope_with_trace_context(self) -> None:
        """Test converting HTTP response to Envelope with trace context."""
        converter = HttpEnvelope()
        original_envelope = Envelope(
            path="/test",
            method="GET",
            trace_id="original_trace",
            span_id="original_span",
        )

        headers = {
            "X-Trace-Id": "new_trace",
            "X-Span-Id": "new_span",
        }

        envelope = converter.response_to_envelope(
            status_code=200,
            data={"result": "success"},
            headers=headers,
            original_envelope=original_envelope,
        )

        assert envelope.trace_id == "new_trace"
        assert envelope.span_id == "new_span"

    def test_response_to_envelope_without_original_envelope(self) -> None:
        """Test converting HTTP response to Envelope without original envelope."""
        converter = HttpEnvelope()

        envelope = converter.response_to_envelope(
            status_code=200,
            data={"result": "success"},
            headers={},
        )

        assert envelope.status_code == 200
        assert envelope.path == ""
        assert envelope.method is None

    def test_response_to_envelope_set_cookie_invalid_format(self) -> None:
        """Test converting HTTP response with invalid Set-Cookie format."""
        converter = HttpEnvelope()

        envelope = converter.response_to_envelope(
            status_code=200,
            data={"result": "success"},
            headers={"Set-Cookie": "invalid_cookie"},
        )

        # Should not crash, cookies may be empty
        assert envelope.status_code == 200

