"""Unit tests for BackpressureMiddleware."""

import asyncio

import pytest

from hexswitch.pipeline.middleware.backpressure import BackpressureMiddleware
from hexswitch.pipeline.pipeline import PipelineContext
from hexswitch.shared.envelope import Envelope


@pytest.mark.asyncio
async def test_backpressure_middleware_disabled():
    """Test backpressure middleware when disabled."""
    middleware = BackpressureMiddleware({"enabled": False})

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        return ctx

    result = await middleware(ctx, next_func)

    assert result == ctx


@pytest.mark.asyncio
async def test_backpressure_middleware_fail_fast():
    """Test backpressure middleware with fail_fast strategy."""
    middleware = BackpressureMiddleware(
        {
            "enabled": True,
            "max_concurrent": 1,
            "rejection_strategy": "fail_fast",
        }
    )

    ctx1 = PipelineContext(envelope=Envelope(path="/test1", method="GET"))
    ctx2 = PipelineContext(envelope=Envelope(path="/test2", method="GET"))

    async def slow_next(ctx: PipelineContext) -> PipelineContext:
        await asyncio.sleep(0.1)
        return ctx

    # First request should succeed
    result1 = await middleware(ctx1, slow_next)
    assert result1.envelope.error_message is None

    # Second request should be rejected if semaphore is locked
    # (This test is simplified - in practice, we'd need to test concurrent access)


@pytest.mark.asyncio
async def test_backpressure_middleware_queue():
    """Test backpressure middleware with queue strategy."""
    middleware = BackpressureMiddleware(
        {
            "enabled": True,
            "max_concurrent": 1,
            "queue_size": 2,
            "rejection_strategy": "queue",
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        return ctx

    result = await middleware(ctx, next_func)

    assert result == ctx


@pytest.mark.asyncio
async def test_backpressure_middleware_fail_fast_rejection():
    """Test backpressure middleware with fail_fast strategy when semaphore is full."""
    middleware = BackpressureMiddleware(
        {
            "enabled": True,
            "max_concurrent": 1,
            "rejection_strategy": "fail_fast",
        }
    )

    ctx1 = PipelineContext(envelope=Envelope(path="/test1", method="GET"), port_name="test_port")
    ctx2 = PipelineContext(envelope=Envelope(path="/test2", method="GET"), port_name="test_port")

    async def slow_next(ctx: PipelineContext) -> PipelineContext:
        await asyncio.sleep(0.1)
        return ctx

    # Start first request (will hold semaphore)
    task1 = asyncio.create_task(middleware(ctx1, slow_next))

    # Wait a bit to ensure first request acquires semaphore
    await asyncio.sleep(0.01)

    # Second request should be rejected immediately
    result2 = await middleware(ctx2, slow_next)

    assert result2.envelope.error_message is not None
    assert "503" in str(result2.envelope.status_code) or result2.envelope.status_code == 503
    assert result2.metadata.get("backpressure_rejected") is True

    # Wait for first request to complete
    await task1


@pytest.mark.asyncio
async def test_backpressure_middleware_queue_full():
    """Test backpressure middleware with queue strategy when queue is full."""
    middleware = BackpressureMiddleware(
        {
            "enabled": True,
            "max_concurrent": 1,
            "queue_size": 1,
            "rejection_strategy": "queue",
        }
    )

    # Fill the queue by starting a slow request
    ctx1 = PipelineContext(envelope=Envelope(path="/test1", method="GET"), port_name="test_port")
    ctx2 = PipelineContext(envelope=Envelope(path="/test2", method="GET"), port_name="test_port")
    ctx3 = PipelineContext(envelope=Envelope(path="/test3", method="GET"), port_name="test_port")

    async def slow_next(ctx: PipelineContext) -> PipelineContext:
        await asyncio.sleep(0.1)
        return ctx

    # Start first request (will hold semaphore)
    task1 = asyncio.create_task(middleware(ctx1, slow_next))
    await asyncio.sleep(0.01)

    # Second request should be queued
    task2 = asyncio.create_task(middleware(ctx2, slow_next))
    await asyncio.sleep(0.01)

    # Third request should be rejected (queue full)
    result3 = await middleware(ctx3, slow_next)

    assert result3.envelope.error_message is not None
    assert "503" in str(result3.envelope.status_code) or result3.envelope.status_code == 503
    assert result3.metadata.get("backpressure_rejected") is True

    # Wait for requests to complete
    await task1
    await task2


@pytest.mark.asyncio
async def test_backpressure_middleware_drop_strategy():
    """Test backpressure middleware with drop strategy."""
    middleware = BackpressureMiddleware(
        {
            "enabled": True,
            "max_concurrent": 1,
            "rejection_strategy": "drop",
        }
    )

    ctx1 = PipelineContext(envelope=Envelope(path="/test1", method="GET"), port_name="test_port")
    ctx2 = PipelineContext(envelope=Envelope(path="/test2", method="GET"), port_name="test_port")

    async def slow_next(ctx: PipelineContext) -> PipelineContext:
        await asyncio.sleep(0.1)
        return ctx

    # Start first request (will hold semaphore)
    task1 = asyncio.create_task(middleware(ctx1, slow_next))
    await asyncio.sleep(0.01)

    # Second request should be dropped when semaphore is full
    result2 = await middleware(ctx2, slow_next)

    assert result2.envelope.error_message is not None
    assert result2.metadata.get("backpressure_dropped") is True

    # Wait for first request to complete
    await task1


@pytest.mark.asyncio
async def test_backpressure_middleware_unknown_strategy():
    """Test backpressure middleware with unknown strategy."""
    middleware = BackpressureMiddleware(
        {
            "enabled": True,
            "max_concurrent": 1,
            "rejection_strategy": "unknown_strategy",
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        return ctx

    # Should just execute without backpressure control
    result = await middleware(ctx, next_func)
    assert result == ctx


@pytest.mark.asyncio
async def test_backpressure_middleware_no_semaphore():
    """Test backpressure middleware when semaphore is not initialized."""
    middleware = BackpressureMiddleware({"enabled": False})
    middleware._semaphore = None  # Simulate no semaphore

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        return ctx

    result = await middleware(ctx, next_func)
    assert result == ctx


