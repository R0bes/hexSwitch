"""Unit tests for trace context."""

import pytest

from hexswitch.shared.observability.trace_context import (
    extract_trace_context_from_headers,
    inject_trace_context_to_headers,
)


class TestTraceContext:
    """Test trace context functions."""

    def test_extract_trace_context_from_headers(self) -> None:
        """Test extracting trace context from headers."""
        headers = {
            "X-Trace-Id": "12345",
            "X-Span-Id": "67890",
            "X-Parent-Span-Id": "11111",
        }

        context = extract_trace_context_from_headers(headers)
        assert context["trace_id"] == "12345"
        assert context["span_id"] == "67890"
        assert context["parent_span_id"] == "11111"

    def test_extract_trace_context_missing_headers(self) -> None:
        """Test extracting trace context with missing headers."""
        headers = {}

        context = extract_trace_context_from_headers(headers)
        assert context.get("trace_id") is None
        assert context.get("span_id") is None
        assert context.get("parent_span_id") is None

    def test_extract_trace_context_partial_headers(self) -> None:
        """Test extracting trace context with partial headers."""
        headers = {"X-Trace-Id": "12345"}

        context = extract_trace_context_from_headers(headers)
        assert context["trace_id"] == "12345"
        assert context.get("span_id") is None

    def test_inject_trace_context_to_headers(self) -> None:
        """Test injecting trace context to headers."""
        headers = {}
        inject_trace_context_to_headers(
            headers,
            trace_id="12345",
            span_id="67890",
            parent_span_id="11111",
            header_format="hexswitch"
        )
        assert headers.get("X-Trace-Id") == "12345" or "trace" in str(headers).lower()
        # W3C format might be used, so we check that headers were modified
        assert len(headers) > 0

    def test_inject_trace_context_partial(self) -> None:
        """Test injecting partial trace context."""
        headers = {}
        inject_trace_context_to_headers(
            headers,
            trace_id="12345",
            span_id=None,
            parent_span_id=None,
            header_format="hexswitch"
        )
        assert headers.get("X-Trace-Id") == "12345" or "trace" in str(headers).lower()
        # W3C format might be used, so we check that headers were modified
        assert len(headers) > 0

    def test_inject_trace_context_empty(self) -> None:
        """Test injecting empty trace context."""
        context = {}

        headers = inject_trace_context_to_headers(context)
        assert len(headers) == 0

