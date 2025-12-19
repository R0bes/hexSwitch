"""Unit tests for trace middleware."""

from unittest.mock import patch

import pytest

from hexswitch.pipeline.middleware.trace import (
    TraceExtractionMiddleware,
    TraceInjectionMiddleware,
    format_traceparent,
    parse_traceparent,
)
from hexswitch.pipeline.pipeline import PipelineContext
from hexswitch.shared.envelope import Envelope


@pytest.mark.fast
class TestParseTraceparent:
    """Test parse_traceparent function."""

    def test_parse_traceparent_valid(self):
        """Test parsing valid traceparent header."""
        traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
        trace_id, span_id, parent_span_id = parse_traceparent(traceparent)

        assert trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
        assert span_id == "00f067aa0ba902b7"
        assert parent_span_id is None

    def test_parse_traceparent_invalid_format(self):
        """Test parsing invalid traceparent format."""
        traceparent = "invalid-format"

        with pytest.raises(ValueError, match="Invalid traceparent format"):
            parse_traceparent(traceparent)

    def test_parse_traceparent_wrong_version(self):
        """Test parsing traceparent with unsupported version."""
        traceparent = "01-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

        with patch("hexswitch.pipeline.middleware.trace.logger") as mock_logger:
            trace_id, span_id, parent_span_id = parse_traceparent(traceparent)

            assert trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
            assert span_id == "00f067aa0ba902b7"
            assert parent_span_id is None
            mock_logger.warning.assert_called_once()
            assert "Unsupported traceparent version" in str(mock_logger.warning.call_args)

    def test_parse_traceparent_wrong_parts_count(self):
        """Test parsing traceparent with wrong number of parts."""
        traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7"

        with pytest.raises(ValueError, match="Invalid traceparent format"):
            parse_traceparent(traceparent)


@pytest.mark.fast
class TestFormatTraceparent:
    """Test format_traceparent function."""

    def test_format_traceparent_basic(self):
        """Test formatting traceparent header."""
        trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
        span_id = "00f067aa0ba902b7"

        result = format_traceparent(trace_id, span_id)

        assert result == f"00-{trace_id}-{span_id}-01"

    def test_format_traceparent_with_parent_span_id(self):
        """Test formatting traceparent with parent_span_id (should be ignored)."""
        trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
        span_id = "00f067aa0ba902b7"
        parent_span_id = "parent123"

        result = format_traceparent(trace_id, span_id, parent_span_id)

        # parent_span_id is currently not used in format
        assert result == f"00-{trace_id}-{span_id}-01"


@pytest.mark.asyncio
@pytest.mark.fast
class TestTraceExtractionMiddleware:
    """Test TraceExtractionMiddleware."""

    async def test_extract_traceparent_from_headers(self):
        """Test extracting trace context from traceparent header."""
        middleware = TraceExtractionMiddleware()
        envelope = Envelope(
            path="/test",
            headers={"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert result_ctx.envelope.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
        assert result_ctx.envelope.span_id == "00f067aa0ba902b7"
        assert result_ctx.envelope.parent_span_id is None

    async def test_extract_traceparent_invalid_handled_gracefully(self):
        """Test that invalid traceparent is handled gracefully."""
        middleware = TraceExtractionMiddleware()
        envelope = Envelope(
            path="/test",
            headers={"traceparent": "invalid-format"}
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        with patch("hexswitch.pipeline.middleware.trace.logger") as mock_logger:
            result_ctx = await middleware(ctx, next_func)

            # Should continue without setting trace context
            assert result_ctx.envelope.trace_id is None
            mock_logger.warning.assert_called_once()
            assert "Failed to parse traceparent header" in str(mock_logger.warning.call_args)

    async def test_extract_trace_from_metadata(self):
        """Test extracting trace context from metadata."""
        middleware = TraceExtractionMiddleware()
        envelope = Envelope(
            path="/test",
            metadata={"trace_id": "trace123", "span_id": "span456", "parent_span_id": "parent789"}
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert result_ctx.envelope.trace_id == "trace123"
        assert result_ctx.envelope.span_id == "span456"
        assert result_ctx.envelope.parent_span_id == "parent789"

    async def test_extract_trace_from_metadata_partial(self):
        """Test extracting trace context from metadata with partial data."""
        middleware = TraceExtractionMiddleware()
        envelope = Envelope(
            path="/test",
            metadata={"trace_id": "trace123"}
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert result_ctx.envelope.trace_id == "trace123"
        # span_id and parent_span_id should be None if not in metadata
        assert result_ctx.envelope.span_id is None
        assert result_ctx.envelope.parent_span_id is None

    async def test_extract_trace_metadata_only_when_no_header(self):
        """Test that metadata is only used when no traceparent header exists."""
        middleware = TraceExtractionMiddleware()
        envelope = Envelope(
            path="/test",
            headers={"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"},
            metadata={"trace_id": "metadata_trace", "span_id": "metadata_span"}
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        # Should use header, not metadata
        assert result_ctx.envelope.trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
        assert result_ctx.envelope.span_id == "00f067aa0ba902b7"


@pytest.mark.asyncio
@pytest.mark.fast
class TestTraceInjectionMiddleware:
    """Test TraceInjectionMiddleware."""

    async def test_inject_traceparent_into_headers(self):
        """Test injecting trace context into headers."""
        middleware = TraceInjectionMiddleware()
        envelope = Envelope(
            path="/test",
            trace_id="4bf92f3577b34da6a3ce929d0e0e4736",
            span_id="00f067aa0ba902b7"
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert "traceparent" in result_ctx.envelope.headers
        assert result_ctx.envelope.headers["traceparent"] == "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
        assert result_ctx.envelope.metadata["trace_id"] == "4bf92f3577b34da6a3ce929d0e0e4736"
        assert result_ctx.envelope.metadata["span_id"] == "00f067aa0ba902b7"

    async def test_inject_trace_with_parent_span_id(self):
        """Test injecting trace context with parent_span_id."""
        middleware = TraceInjectionMiddleware()
        envelope = Envelope(
            path="/test",
            trace_id="trace123",
            span_id="span456",
            parent_span_id="parent789"
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert result_ctx.envelope.metadata["trace_id"] == "trace123"
        assert result_ctx.envelope.metadata["span_id"] == "span456"
        assert result_ctx.envelope.metadata["parent_span_id"] == "parent789"

    async def test_inject_trace_without_parent_span_id(self):
        """Test injecting trace context without parent_span_id."""
        middleware = TraceInjectionMiddleware()
        envelope = Envelope(
            path="/test",
            trace_id="trace123",
            span_id="span456",
            parent_span_id=None
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert result_ctx.envelope.metadata["trace_id"] == "trace123"
        assert result_ctx.envelope.metadata["span_id"] == "span456"
        assert "parent_span_id" not in result_ctx.envelope.metadata

    async def test_inject_trace_only_when_trace_id_and_span_id_exist(self):
        """Test that trace is only injected when both trace_id and span_id exist."""
        middleware = TraceInjectionMiddleware()
        envelope = Envelope(
            path="/test",
            trace_id="trace123"
            # span_id is missing
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            return ctx

        result_ctx = await middleware(ctx, next_func)

        # Should not inject trace context
        assert "traceparent" not in result_ctx.envelope.headers
        assert "trace_id" not in result_ctx.envelope.metadata

    async def test_inject_trace_calls_next_first(self):
        """Test that next middleware is called before injection."""
        middleware = TraceInjectionMiddleware()
        envelope = Envelope(
            path="/test",
            trace_id="trace123",
            span_id="span456"
        )
        ctx = PipelineContext(envelope=envelope, port_name="test", stage="test")

        call_order = []

        async def next_func(ctx: PipelineContext) -> PipelineContext:
            call_order.append("next")
            # Modify envelope to verify it's called first
            ctx.envelope.metadata["modified"] = True
            return ctx

        result_ctx = await middleware(ctx, next_func)

        assert call_order == ["next"]
        assert result_ctx.envelope.metadata["modified"] is True
        # Trace should still be injected after next
        assert "traceparent" in result_ctx.envelope.headers

