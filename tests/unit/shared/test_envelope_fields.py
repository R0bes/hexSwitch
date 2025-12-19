"""Golden tests for critical Envelope fields: trace_id, span_id, parent_span_id."""

import re

from hexswitch.shared.envelope import Envelope


def test_envelope_trace_fields() -> None:
    """Test trace context fields in envelope."""
    # Create envelope with trace context
    trace_id = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    span_id = "00f067aa0ba902b7"
    parent_span_id = "00f067aa0ba902b6"

    envelope = Envelope(
        path="/test",
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
    )

    # Verify trace fields are set
    assert envelope.trace_id == trace_id
    assert envelope.span_id == span_id
    assert envelope.parent_span_id == parent_span_id


def test_envelope_trace_fields_format_w3c() -> None:
    """Test that trace fields follow W3C Trace Context format."""
    # W3C Trace Context format:
    # trace_id: 32 hex characters (16 bytes)
    # span_id: 16 hex characters (8 bytes)
    # parent_span_id: 16 hex characters (8 bytes)

    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"  # 32 hex chars
    span_id = "00f067aa0ba902b7"  # 16 hex chars
    parent_span_id = "00f067aa0ba902b6"  # 16 hex chars

    envelope = Envelope(
        path="/test",
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
    )

    # Verify format
    assert len(envelope.trace_id) == 32
    assert all(c in "0123456789abcdef" for c in envelope.trace_id.lower())
    assert len(envelope.span_id) == 16
    assert all(c in "0123456789abcdef" for c in envelope.span_id.lower())
    assert len(envelope.parent_span_id) == 16
    assert all(c in "0123456789abcdef" for c in envelope.parent_span_id.lower())


def test_envelope_trace_fields_optional() -> None:
    """Test that trace fields are optional."""
    envelope = Envelope(path="/test")

    # Verify trace fields can be None
    assert envelope.trace_id is None
    assert envelope.span_id is None
    assert envelope.parent_span_id is None


def test_envelope_trace_fields_propagation() -> None:
    """Test that trace fields are correctly propagated."""
    # Create parent envelope with trace context
    parent_trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    parent_span_id = "00f067aa0ba902b7"

    parent_envelope = Envelope(
        path="/parent",
        trace_id=parent_trace_id,
        span_id=parent_span_id,
    )

    # Create child envelope (simulating span hierarchy)
    child_span_id = "00f067aa0ba902b8"
    child_envelope = Envelope(
        path="/child",
        trace_id=parent_trace_id,  # Same trace_id
        span_id=child_span_id,  # New span_id
        parent_span_id=parent_span_id,  # Parent's span_id becomes parent_span_id
    )

    # Verify propagation
    assert child_envelope.trace_id == parent_envelope.trace_id
    assert child_envelope.parent_span_id == parent_envelope.span_id
    assert child_envelope.span_id != parent_envelope.span_id


def test_envelope_trace_fields_from_headers() -> None:
    """Test that trace fields can be extracted from headers (W3C Trace Context)."""
    # W3C traceparent header format: 00-{trace_id}-{span_id}-{flags}
    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

    # Parse traceparent (simulating adapter extraction)
    parts = traceparent.split("-")
    trace_id = parts[1]  # 32 hex chars
    span_id = parts[2]  # 16 hex chars

    envelope = Envelope(
        path="/test",
        headers={"traceparent": traceparent},
        trace_id=trace_id,
        span_id=span_id,
    )

    # Verify extraction
    assert envelope.trace_id == trace_id
    assert envelope.span_id == span_id
    assert len(envelope.trace_id) == 32
    assert len(envelope.span_id) == 16


def test_envelope_trace_fields_required_fields() -> None:
    """Test that required Envelope fields are present."""
    envelope = Envelope(path="/test")

    # Verify required fields
    assert envelope.path == "/test"
    assert envelope.status_code == 200  # Default
    assert isinstance(envelope.path_params, dict)
    assert isinstance(envelope.query_params, dict)
    assert isinstance(envelope.headers, dict)
    assert isinstance(envelope.metadata, dict)


def test_envelope_trace_fields_golden_examples() -> None:
    """Golden test with specific trace context examples."""
    # Example 1: Root span
    root_envelope = Envelope(
        path="/api/orders",
        trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
        span_id="00f067aa0ba902b7",
        parent_span_id=None,  # Root span has no parent
    )

    assert root_envelope.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert root_envelope.span_id == "00f067aa0ba902b7"
    assert root_envelope.parent_span_id is None

    # Example 2: Child span
    child_envelope = Envelope(
        path="/api/orders/123",
        trace_id="4bf92f3577b34da6a3ce929d0e0e4736",  # Same trace
        span_id="00f067aa0ba902b8",  # New span
        parent_span_id="00f067aa0ba902b7",  # Parent's span_id
    )

    assert child_envelope.trace_id == root_envelope.trace_id
    assert child_envelope.parent_span_id == root_envelope.span_id
    assert child_envelope.span_id != root_envelope.span_id

    # Example 3: Grandchild span
    grandchild_envelope = Envelope(
        path="/api/orders/123/items",
        trace_id="4bf92f3577b34da6a3ce929d0e0e4736",  # Same trace
        span_id="00f067aa0ba902b9",  # New span
        parent_span_id="00f067aa0ba902b8",  # Parent's span_id
    )

    assert grandchild_envelope.trace_id == root_envelope.trace_id
    assert grandchild_envelope.parent_span_id == child_envelope.span_id
    assert grandchild_envelope.span_id != child_envelope.span_id


def test_envelope_trace_fields_validation() -> None:
    """Test validation of trace field formats."""
    # Valid trace_id (32 hex chars)
    valid_trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    assert len(valid_trace_id) == 32
    assert re.match(r"^[0-9a-f]{32}$", valid_trace_id.lower())

    # Valid span_id (16 hex chars)
    valid_span_id = "00f067aa0ba902b7"
    assert len(valid_span_id) == 16
    assert re.match(r"^[0-9a-f]{16}$", valid_span_id.lower())

    # Create envelope with valid fields
    envelope = Envelope(
        path="/test",
        trace_id=valid_trace_id,
        span_id=valid_span_id,
        parent_span_id=valid_span_id,
    )

    assert envelope.trace_id == valid_trace_id
    assert envelope.span_id == valid_span_id

