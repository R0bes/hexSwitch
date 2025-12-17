"""Tests for Envelope class."""

import pytest

from hexswitch.shared.envelope import Envelope


class TestEnvelope:
    """Test cases for Envelope class."""

    def test_envelope_creation_with_minimal_fields(self) -> None:
        """Test creating Envelope with minimal required fields."""
        envelope = Envelope(path="/orders")
        assert envelope.path == "/orders"
        assert envelope.method is None
        assert envelope.path_params == {}
        assert envelope.query_params == {}
        assert envelope.headers == {}
        assert envelope.body is None
        assert envelope.status_code == 200
        assert envelope.data is None
        assert envelope.error_message is None
        assert envelope.metadata == {}

    def test_envelope_creation_with_all_fields(self) -> None:
        """Test creating Envelope with all fields."""
        envelope = Envelope(
            path="/orders/123",
            method="GET",
            path_params={"id": "123"},
            query_params={"page": "1"},
            headers={"Authorization": "Bearer token"},
            body={"customer_id": "456"},
            status_code=200,
            data={"order_id": "123"},
            metadata={
                "session_id": "session_123",
                "cookies": {"session": "abc"},
                "trace_id": "trace_123",
            },
        )
        assert envelope.path == "/orders/123"
        assert envelope.method == "GET"
        assert envelope.path_params == {"id": "123"}
        assert envelope.query_params == {"page": "1"}
        assert envelope.headers == {"Authorization": "Bearer token"}
        assert envelope.body == {"customer_id": "456"}
        assert envelope.status_code == 200
        assert envelope.data == {"order_id": "123"}
        assert envelope.metadata == {
            "session_id": "session_123",
            "cookies": {"session": "abc"},
            "trace_id": "trace_123",
        }

    def test_envelope_success_factory(self) -> None:
        """Test Envelope.success() factory method."""
        envelope = Envelope.success({"order_id": "123", "status": "created"})
        assert envelope.path == ""
        assert envelope.status_code == 200
        assert envelope.data == {"order_id": "123", "status": "created"}
        assert envelope.error_message is None

    def test_envelope_success_with_custom_status_code(self) -> None:
        """Test Envelope.success() with custom status code."""
        envelope = Envelope.success({"order_id": "123"}, status_code=201)
        assert envelope.status_code == 201
        assert envelope.data == {"order_id": "123"}

    def test_envelope_error_factory(self) -> None:
        """Test Envelope.error() factory method."""
        envelope = Envelope.error(400, "customer_id is required")
        assert envelope.path == ""
        assert envelope.status_code == 400
        assert envelope.error_message == "customer_id is required"
        assert envelope.data is None

    def test_envelope_error_with_different_status_codes(self) -> None:
        """Test Envelope.error() with different status codes."""
        envelope_404 = Envelope.error(404, "Order not found")
        assert envelope_404.status_code == 404
        assert envelope_404.error_message == "Order not found"

        envelope_500 = Envelope.error(500, "Internal server error")
        assert envelope_500.status_code == 500
        assert envelope_500.error_message == "Internal server error"

    def test_envelope_default_factories(self) -> None:
        """Test that default factories create empty collections."""
        envelope = Envelope(path="/test")
        assert envelope.path_params == {}
        assert envelope.query_params == {}
        assert envelope.headers == {}
        assert envelope.metadata == {}

    def test_envelope_metadata(self) -> None:
        """Test metadata field can store protocol-agnostic data."""
        envelope = Envelope(
            path="/test",
            metadata={
                "session_id": "session_123",
                "cookies": {"session": "abc"},
                "trace_id": "trace_123",
            },
        )
        assert envelope.metadata["session_id"] == "session_123"
        assert envelope.metadata["cookies"] == {"session": "abc"}
        assert envelope.metadata["trace_id"] == "trace_123"

