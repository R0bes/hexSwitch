"""Unit tests for Envelope class."""

import uuid

import pytest

from hexswitch.shared.envelope import Envelope
from hexswitch.shared.observability.tracing import Span


class TestEnvelope:
    """Test Envelope class."""

    def test_create_basic_envelope(self) -> None:
        """Test creating a basic envelope."""
        envelope = Envelope(path="/test", method="GET")
        assert envelope.path == "/test"
        assert envelope.method == "GET"
        assert envelope.status_code == 200
        assert envelope.data is None
        assert envelope.error_message is None

    def test_envelope_success(self) -> None:
        """Test creating success envelope."""
        envelope = Envelope.success({"key": "value"})
        assert envelope.status_code == 200
        assert envelope.data == {"key": "value"}
        assert envelope.error_message is None

    def test_envelope_error(self) -> None:
        """Test creating error envelope."""
        envelope = Envelope.error(404, "Not Found")
        assert envelope.status_code == 404
        assert envelope.error_message == "Not Found"
        assert envelope.data is None

    def test_envelope_with_path_params(self) -> None:
        """Test envelope with path parameters."""
        envelope = Envelope(
            path="/users/:id",
            method="GET",
            path_params={"id": "123"},
        )
        assert envelope.path_params == {"id": "123"}

    def test_envelope_with_query_params(self) -> None:
        """Test envelope with query parameters."""
        envelope = Envelope(
            path="/search",
            method="GET",
            query_params={"q": "test", "page": "1"},
        )
        assert envelope.query_params == {"q": "test", "page": "1"}

    def test_envelope_with_headers(self) -> None:
        """Test envelope with headers."""
        envelope = Envelope(
            path="/test",
            method="GET",
            headers={"Authorization": "Bearer token"},
        )
        assert envelope.headers == {"Authorization": "Bearer token"}

    def test_envelope_with_body(self) -> None:
        """Test envelope with body."""
        envelope = Envelope(
            path="/test",
            method="POST",
            body={"name": "test"},
        )
        assert envelope.body == {"name": "test"}

    def test_envelope_with_metadata(self) -> None:
        """Test envelope with metadata."""
        envelope = Envelope(
            path="/test",
            method="GET",
            metadata={"session_id": "abc123"},
        )
        assert envelope.metadata == {"session_id": "abc123"}

    def test_envelope_with_trace_context(self) -> None:
        """Test envelope with trace context."""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        parent_span_id = str(uuid.uuid4())

        envelope = Envelope(
            path="/test",
            method="GET",
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )
        assert envelope.trace_id == trace_id
        assert envelope.span_id == span_id
        assert envelope.parent_span_id == parent_span_id

    def test_envelope_to_dict(self) -> None:
        """Test envelope to_dict conversion using dataclass asdict."""
        from dataclasses import asdict

        envelope = Envelope(
            path="/test",
            method="GET",
            data={"result": "success"},
            status_code=200,
        )
        envelope_dict = asdict(envelope)
        assert envelope_dict["path"] == "/test"
        assert envelope_dict["method"] == "GET"
        assert envelope_dict["data"] == {"result": "success"}
        assert envelope_dict["status_code"] == 200

    def test_envelope_from_dict(self) -> None:
        """Test envelope from_dict creation using direct instantiation."""
        envelope = Envelope(
            path="/test",
            method="GET",
            data={"result": "success"},
            status_code=200,
        )
        assert envelope.path == "/test"
        assert envelope.method == "GET"
        assert envelope.data == {"result": "success"}
        assert envelope.status_code == 200

    def test_envelope_with_span(self) -> None:
        """Test envelope with span."""
        from unittest.mock import MagicMock

        envelope = Envelope(path="/test", method="GET")

        # Create a mock span
        mock_span = MagicMock()
        mock_span.name = "test_span"
        mock_span.trace_id = str(uuid.uuid4())
        mock_span.span_id = str(uuid.uuid4())

        # Use start_span to set span
        envelope.start_span("test_span")
        span = envelope.get_span()
        assert span is not None

    def test_envelope_default_values(self) -> None:
        """Test envelope default values."""
        envelope = Envelope(path="/test")
        assert envelope.method is None
        assert envelope.path_params == {}
        assert envelope.query_params == {}
        assert envelope.headers == {}
        assert envelope.body is None
        assert envelope.status_code == 200
        assert envelope.data is None
        assert envelope.error_message is None
        assert envelope.metadata == {}

