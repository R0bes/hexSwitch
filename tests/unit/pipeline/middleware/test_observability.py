"""Unit tests for ObservabilityMiddleware."""

from unittest.mock import MagicMock, patch

import pytest

from hexswitch.pipeline.middleware.observability import ObservabilityMiddleware
from hexswitch.pipeline.pipeline import PipelineContext
from hexswitch.shared.envelope import Envelope


@pytest.mark.asyncio
async def test_observability_middleware_creates_spans():
    """Test observability middleware creates spans."""
    middleware = ObservabilityMiddleware()

    # Create mock context
    ctx = PipelineContext(
        envelope=Envelope(path="/test", method="GET"),
        port_name="test_port",
        stage="test",
    )

    # Create mock next function
    async def next_func(ctx: PipelineContext) -> PipelineContext:
        return ctx

    # Mock tracer
    with patch("hexswitch.pipeline.middleware.observability.start_span") as mock_start_span:
        mock_span = MagicMock()
        mock_start_span.return_value = mock_span

        # Execute middleware
        result_ctx = await middleware(ctx, next_func)

        # Verify span was created
        mock_start_span.assert_called_once()
        assert "span" in result_ctx.metadata
        mock_span.finish.assert_called_once()


@pytest.mark.asyncio
async def test_observability_middleware_records_metrics():
    """Test observability middleware records metrics."""
    middleware = ObservabilityMiddleware()

    # Create mock context
    ctx = PipelineContext(
        envelope=Envelope(path="/test", method="GET"),
        port_name="test_port",
        stage="test",
    )

    # Create mock next function
    async def next_func(ctx: PipelineContext) -> PipelineContext:
        return ctx

    # Mock metrics
    with patch.object(middleware._metrics, "counter") as mock_counter:
        mock_counter_instance = MagicMock()
        mock_counter.return_value = mock_counter_instance

        # Execute middleware
        await middleware(ctx, next_func)

        # Verify metrics were recorded
        assert mock_counter.call_count >= 2  # Start and success metrics


@pytest.mark.asyncio
async def test_observability_middleware_handles_errors():
    """Test observability middleware handles errors."""
    middleware = ObservabilityMiddleware()

    # Create mock context
    ctx = PipelineContext(
        envelope=Envelope(path="/test", method="GET"),
        port_name="test_port",
        stage="test",
    )

    # Create mock next function that raises error
    async def next_func(ctx: PipelineContext) -> PipelineContext:
        raise Exception("Test error")

    # Mock tracer
    with patch("hexswitch.pipeline.middleware.observability.start_span") as mock_start_span:
        mock_span = MagicMock()
        mock_start_span.return_value = mock_span

        # Execute middleware and expect error
        with pytest.raises(Exception, match="Test error"):
            await middleware(ctx, next_func)

        # Verify span was finished even on error
        mock_span.finish.assert_called_once()

