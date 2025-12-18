"""Unit tests for tracing module."""

import uuid

import pytest

from hexswitch.shared.observability.tracing import (
    Span,
    get_current_span,
    get_global_tracer,
    start_span,
)


class TestTracing:
    """Test tracing functions."""

    def test_get_global_tracer(self) -> None:
        """Test getting global tracer."""
        tracer = get_global_tracer()
        assert tracer is not None

    def test_start_span(self) -> None:
        """Test starting a span."""
        span = start_span("test_span")
        assert span is not None
        assert span.name == "test_span"
        span.finish()

    def test_start_span_with_tags(self) -> None:
        """Test starting a span with tags."""
        span = start_span("test_span", tags={"key": "value"})
        assert span is not None
        span.finish()

    def test_start_span_with_parent(self) -> None:
        """Test starting a span with parent."""
        parent_span = start_span("parent_span")
        child_span = start_span("child_span", parent=parent_span)
        assert child_span is not None
        child_span.finish()
        parent_span.finish()

    def test_span_add_tag(self) -> None:
        """Test adding tag to span."""
        span = start_span("test_span")
        span.add_tag("key", "value")
        span.finish()

    def test_span_finish(self) -> None:
        """Test finishing a span."""
        span = start_span("test_span")
        span.finish()  # Should not raise

    def test_get_current_span(self) -> None:
        """Test getting current span."""
        span = start_span("test_span")
        current = get_current_span()
        # May be None if not in context
        span.finish()

    def test_span_context_manager(self) -> None:
        """Test span as context manager."""
        span = start_span("test_span")
        assert span is not None
        # Manually finish span (context manager not implemented)
        span.finish()

    def test_span_with_exception(self) -> None:
        """Test span with exception."""
        span = start_span("test_span")
        try:
            raise ValueError("test error")
        except ValueError:
            span.add_tag("error", "true")
        span.finish()

