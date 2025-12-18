"""Unit tests for Pipeline."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hexswitch.pipeline.pipeline import Pipeline, PipelineContext
from hexswitch.shared.envelope import Envelope


@pytest.mark.asyncio
async def test_pipeline_processes_envelope():
    """Test pipeline processes envelope through all stages."""
    # Create mock runtime
    mock_runtime = MagicMock()
    mock_handler = AsyncMock(return_value=Envelope.success({"result": "ok"}))
    mock_runtime.handler_loader.resolve.return_value = mock_handler
    mock_runtime.config = {"ports": {}}

    # Create pipeline
    pipeline = Pipeline(mock_runtime)

    # Create input envelope
    input_envelope = Envelope(
        path="/test",
        method="GET",
        metadata={"port_name": "test_port"},
    )

    # Process envelope
    output_envelope = await pipeline.process(input_envelope)

    # Verify handler was called
    assert output_envelope is not None
    assert output_envelope.data == {"result": "ok"}
    mock_handler.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Test pipeline error handling."""
    # Create mock runtime
    mock_runtime = MagicMock()
    mock_handler = AsyncMock(side_effect=Exception("Handler error"))
    mock_runtime.handler_loader.resolve.return_value = mock_handler
    mock_runtime.config = {"ports": {}}

    # Create pipeline
    pipeline = Pipeline(mock_runtime)

    # Create input envelope
    input_envelope = Envelope(
        path="/test",
        method="GET",
        metadata={"port_name": "test_port"},
    )

    # Process envelope
    output_envelope = await pipeline.process(input_envelope)

    # Verify error envelope was created
    assert output_envelope is not None
    assert output_envelope.error_message is not None
    assert "Handler error" in output_envelope.error_message


@pytest.mark.asyncio
async def test_pipeline_no_port_name():
    """Test pipeline handles missing port_name."""
    # Create mock runtime
    mock_runtime = MagicMock()
    mock_runtime.config = {"ports": {}}

    # Create pipeline
    pipeline = Pipeline(mock_runtime)

    # Create input envelope without port_name
    input_envelope = Envelope(path="/test", method="GET")

    # Process envelope
    output_envelope = await pipeline.process(input_envelope)

    # Verify error envelope was created
    assert output_envelope is not None
    assert output_envelope.error_message is not None
    assert output_envelope.status_code == 400


@pytest.mark.asyncio
async def test_pipeline_concurrency_gates():
    """Test pipeline concurrency gates."""
    # Create mock runtime
    mock_runtime = MagicMock()
    call_count = 0

    async def slow_handler(envelope: Envelope) -> Envelope:
        nonlocal call_count
        call_count += 1
        import asyncio
        await asyncio.sleep(0.1)
        return Envelope.success({"count": call_count})

    mock_runtime.handler_loader.resolve.return_value = slow_handler
    mock_runtime.config = {"ports": {"test_port": {"max_concurrent": 2}}}

    # Create pipeline
    pipeline = Pipeline(mock_runtime)

    # Create input envelope
    input_envelope = Envelope(
        path="/test",
        method="GET",
        metadata={"port_name": "test_port"},
    )

    # Process multiple envelopes concurrently
    import asyncio

    tasks = [pipeline.process(input_envelope) for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all envelopes were processed
    assert len(results) == 5
    assert all(isinstance(r, Envelope) for r in results)

    # Verify semaphore was created
    assert "test_port" in pipeline._concurrency_gates


@pytest.mark.asyncio
async def test_pipeline_middleware_stack():
    """Test pipeline middleware stack execution."""
    # Create mock runtime
    mock_runtime = MagicMock()
    mock_handler = AsyncMock(return_value=Envelope.success({"result": "ok"}))
    mock_runtime.handler_loader.resolve.return_value = mock_handler
    mock_runtime.config = {"ports": {}}

    # Create pipeline
    pipeline = Pipeline(mock_runtime)

    # Add middleware
    middleware_calls = []

    async def test_middleware(ctx: PipelineContext, next_func):
        middleware_calls.append("before")
        ctx = await next_func(ctx)
        middleware_calls.append("after")
        return ctx

    pipeline.add_middleware(test_middleware)

    # Create input envelope
    input_envelope = Envelope(
        path="/test",
        method="GET",
        metadata={"port_name": "test_port"},
    )

    # Process envelope
    await pipeline.process(input_envelope)

    # Verify middleware was called
    assert "before" in middleware_calls
    assert "after" in middleware_calls

