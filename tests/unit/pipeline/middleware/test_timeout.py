"""Unit tests for TimeoutMiddleware."""

import asyncio
from unittest.mock import AsyncMock

import pytest

from hexswitch.pipeline.middleware.timeout import TimeoutMiddleware
from hexswitch.pipeline.pipeline import PipelineContext
from hexswitch.shared.envelope import Envelope


@pytest.mark.asyncio
async def test_timeout_middleware_disabled():
    """Test timeout middleware when disabled."""
    middleware = TimeoutMiddleware({"enabled": False})

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    next_func = AsyncMock(return_value=ctx)

    result = await middleware(ctx, next_func)

    assert result == ctx


@pytest.mark.asyncio
async def test_timeout_middleware_success():
    """Test timeout middleware with successful execution."""
    middleware = TimeoutMiddleware(
        {"enabled": True, "timeout_seconds": 1.0}
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        await asyncio.sleep(0.1)
        return ctx

    result = await middleware(ctx, next_func)

    assert result == ctx
    assert result.envelope.error_message is None


@pytest.mark.asyncio
async def test_timeout_middleware_timeout():
    """Test timeout middleware triggers timeout."""
    middleware = TimeoutMiddleware(
        {"enabled": True, "timeout_seconds": 0.1}
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        await asyncio.sleep(1.0)  # Longer than timeout
        return ctx

    result = await middleware(ctx, next_func)

    assert result.envelope.error_message is not None
    assert "timeout" in result.envelope.error_message.lower()
    assert result.envelope.status_code == 504
    assert result.metadata.get("timeout") is True

