"""Unit tests for RetryMiddleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from hexswitch.pipeline.middleware.retry import RetryMiddleware
from hexswitch.pipeline.pipeline import PipelineContext
from hexswitch.shared.envelope import Envelope


@pytest.mark.asyncio
async def test_retry_middleware_disabled():
    """Test retry middleware when disabled."""
    middleware = RetryMiddleware({"enabled": False})

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    next_func = AsyncMock(return_value=ctx)

    result = await middleware(ctx, next_func)

    assert result == ctx
    next_func.assert_called_once()


@pytest.mark.asyncio
async def test_retry_middleware_success_first_attempt():
    """Test retry middleware with successful first attempt."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 3,
            "initial_delay": 0.1,
            "retryable_errors": ["500"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    next_func = AsyncMock(return_value=ctx)

    result = await middleware(ctx, next_func)

    assert result == ctx
    next_func.assert_called_once()


@pytest.mark.asyncio
async def test_retry_middleware_retries_on_retryable_error():
    """Test retry middleware retries on retryable error."""
    import asyncio

    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 3,
            "initial_delay": 0.01,
            "retryable_errors": ["500"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    error_ctx = PipelineContext(
        envelope=Envelope.error(500, "Internal Server Error")
    )
    success_ctx = PipelineContext(envelope=Envelope.success({"result": "ok"}))

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return error_ctx
        return success_ctx

    result = await middleware(ctx, next_func)

    assert call_count == 2
    assert result.envelope.data == {"result": "ok"}


@pytest.mark.asyncio
async def test_retry_middleware_max_attempts():
    """Test retry middleware respects max attempts."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 2,
            "initial_delay": 0.01,
            "retryable_errors": ["500"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    error_ctx = PipelineContext(
        envelope=Envelope.error(500, "Internal Server Error")
    )

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        return error_ctx

    result = await middleware(ctx, next_func)

    assert call_count == 2
    assert result.envelope.error_message is not None


@pytest.mark.asyncio
async def test_retry_middleware_non_retryable_error():
    """Test retry middleware doesn't retry non-retryable errors."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 3,
            "initial_delay": 0.01,
            "retryable_errors": ["500", "503"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    error_ctx = PipelineContext(
        envelope=Envelope.error(400, "Bad Request")
    )

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        return error_ctx

    result = await middleware(ctx, next_func)

    assert call_count == 1  # Should not retry
    assert result.envelope.error_message is not None


@pytest.mark.asyncio
async def test_retry_middleware_error_message_match():
    """Test retry middleware retries based on error message."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 2,
            "initial_delay": 0.01,
            "retryable_errors": ["timeout", "503"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"))
    error_ctx = PipelineContext(
        envelope=Envelope(path="/test", method="GET", status_code=200)
    )
    error_ctx.envelope.error_message = "Connection timeout occurred"

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return error_ctx
        return PipelineContext(envelope=Envelope.success({"result": "ok"}))

    result = await middleware(ctx, next_func)

    assert call_count == 2
    assert result.envelope.data == {"result": "ok"}


@pytest.mark.asyncio
async def test_retry_middleware_exception_retryable():
    """Test retry middleware retries on retryable exceptions."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 2,
            "initial_delay": 0.01,
            "retryable_errors": ["timeout", "connection"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"), port_name="test_port")

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("Connection timeout")
        return PipelineContext(envelope=Envelope.success({"result": "ok"}))

    result = await middleware(ctx, next_func)

    assert call_count == 2
    assert result.envelope.data == {"result": "ok"}


@pytest.mark.asyncio
async def test_retry_middleware_exception_non_retryable():
    """Test retry middleware doesn't retry non-retryable exceptions."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 3,
            "initial_delay": 0.01,
            "retryable_errors": ["timeout", "503"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"), port_name="test_port")

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        raise ValueError("Invalid input")

    with pytest.raises(ValueError):
        await middleware(ctx, next_func)

    assert call_count == 1  # Should not retry


@pytest.mark.asyncio
async def test_retry_middleware_exception_max_attempts():
    """Test retry middleware respects max attempts for exceptions."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 2,
            "initial_delay": 0.01,
            "retryable_errors": ["timeout"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"), port_name="test_port")

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        raise TimeoutError("Connection timeout")

    with pytest.raises(TimeoutError):
        await middleware(ctx, next_func)

    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_middleware_exponential_backoff():
    """Test retry middleware uses exponential backoff."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 3,
            "initial_delay": 0.05,
            "backoff_multiplier": 2.0,
            "max_delay": 1.0,
            "retryable_errors": ["500"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"), port_name="test_port")
    error_ctx = PipelineContext(
        envelope=Envelope.error(500, "Internal Server Error")
    )

    call_count = 0
    delays = []

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return error_ctx
        return PipelineContext(envelope=Envelope.success({"result": "ok"}))

    import time
    start = time.time()
    result = await middleware(ctx, next_func)
    elapsed = time.time() - start

    assert call_count == 3
    # Should have waited: 0.05 + 0.1 = 0.15 seconds (approximately)
    assert elapsed >= 0.14  # Allow some margin
    assert result.envelope.data == {"result": "ok"}


@pytest.mark.asyncio
async def test_retry_middleware_max_delay_cap():
    """Test retry middleware respects max_delay cap."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "max_attempts": 3,
            "initial_delay": 0.1,
            "backoff_multiplier": 10.0,  # Large multiplier
            "max_delay": 0.2,  # But capped at 0.2
            "retryable_errors": ["500"],
        }
    )

    ctx = PipelineContext(envelope=Envelope(path="/test", method="GET"), port_name="test_port")
    error_ctx = PipelineContext(
        envelope=Envelope.error(500, "Internal Server Error")
    )

    call_count = 0

    async def next_func(ctx: PipelineContext) -> PipelineContext:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            return error_ctx
        return PipelineContext(envelope=Envelope.success({"result": "ok"}))

    import time
    start = time.time()
    result = await middleware(ctx, next_func)
    elapsed = time.time() - start

    assert call_count == 3
    # Should have waited: 0.1 + 0.2 (capped) = 0.3 seconds (approximately)
    assert 0.25 <= elapsed <= 0.5  # Allow margin
    assert result.envelope.data == {"result": "ok"}


@pytest.mark.asyncio
async def test_retry_middleware_is_retryable_status_code():
    """Test _is_retryable method with status code."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "retryable_errors": ["500", "502", "503"],
        }
    )

    ctx1 = PipelineContext(envelope=Envelope.error(500, "Error"))
    assert middleware._is_retryable(ctx1) is True

    ctx2 = PipelineContext(envelope=Envelope.error(400, "Bad Request"))
    assert middleware._is_retryable(ctx2) is False

    ctx3 = PipelineContext(envelope=Envelope.error(503, "Service Unavailable"))
    assert middleware._is_retryable(ctx3) is True


@pytest.mark.asyncio
async def test_retry_middleware_is_retryable_error_message():
    """Test _is_retryable method with error message."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "retryable_errors": ["timeout", "connection"],
        }
    )

    ctx1 = PipelineContext(envelope=Envelope(path="/test", method="GET", status_code=200))
    ctx1.envelope.error_message = "Connection timeout occurred"
    assert middleware._is_retryable(ctx1) is True

    ctx2 = PipelineContext(envelope=Envelope(path="/test", method="GET", status_code=200))
    ctx2.envelope.error_message = "Invalid input"
    assert middleware._is_retryable(ctx2) is False

    ctx3 = PipelineContext(envelope=Envelope(path="/test", method="GET", status_code=200))
    ctx3.envelope.error_message = "Connection refused"
    assert middleware._is_retryable(ctx3) is True


@pytest.mark.asyncio
async def test_retry_middleware_is_retryable_no_error():
    """Test _is_retryable method when no error."""
    middleware = RetryMiddleware(
        {
            "enabled": True,
            "retryable_errors": ["500"],
        }
    )

    ctx = PipelineContext(envelope=Envelope.success({"result": "ok"}))
    assert middleware._is_retryable(ctx) is False


