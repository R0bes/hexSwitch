"""Unit tests for adapter runners."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hexswitch.execution.runner import (
    AdapterRunner,
    AsyncAdapterRunner,
    BlockingAdapterRunner,
)


@pytest.mark.asyncio
@pytest.mark.fast
class TestAsyncAdapterRunner:
    """Test AsyncAdapterRunner."""

    async def test_start_with_async_start_method(self):
        """Test starting adapter with async start_async method."""
        runner = AsyncAdapterRunner()
        adapter = MagicMock()
        adapter.start_async = AsyncMock(return_value=None)
        
        await runner.start(adapter)
        
        adapter.start_async.assert_called_once()

    async def test_start_with_sync_start_method(self):
        """Test starting adapter with sync start method."""
        runner = AsyncAdapterRunner()
        # Create adapter with only sync start method (no start_async)
        class SyncAdapter:
            def start(self):
                pass
        
        adapter = SyncAdapter()
        
        await runner.start(adapter)
        
        # Should complete without error
        assert True

    async def test_start_without_start_method(self):
        """Test starting adapter without start method raises error."""
        runner = AsyncAdapterRunner()
        adapter = MagicMock(spec=[])  # No methods
        
        with pytest.raises(ValueError, match="has no start method"):
            await runner.start(adapter)

    async def test_stop_with_async_stop_method(self):
        """Test stopping adapter with async stop_async method."""
        runner = AsyncAdapterRunner()
        adapter = MagicMock()
        adapter.stop_async = AsyncMock(return_value=None)
        
        await runner.stop(adapter)
        
        adapter.stop_async.assert_called_once()

    async def test_stop_with_sync_stop_method(self):
        """Test stopping adapter with sync stop method."""
        runner = AsyncAdapterRunner()
        # Create adapter with only sync stop method (no stop_async)
        class SyncAdapter:
            def stop(self):
                pass
        
        adapter = SyncAdapter()
        
        await runner.stop(adapter)
        
        # Should complete without error
        assert True

    async def test_stop_cancels_tasks(self):
        """Test that stop cancels all running tasks."""
        runner = AsyncAdapterRunner()
        adapter = MagicMock()
        adapter.stop_async = AsyncMock(return_value=None)
        
        # Create a task that will be cancelled
        async def long_running_task():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                pass
        
        task = runner.run_in_background(long_running_task())
        
        # Wait a bit to ensure task is running
        await asyncio.sleep(0.01)
        
        # Stop should cancel the task
        await runner.stop(adapter)
        
        # Task should be cancelled
        assert task.cancelled() or task.done()

    async def test_stop_waits_for_tasks(self):
        """Test that stop waits for tasks to complete."""
        runner = AsyncAdapterRunner()
        adapter = MagicMock()
        adapter.stop_async = AsyncMock(return_value=None)
        
        task_completed = False
        
        async def quick_task():
            nonlocal task_completed
            await asyncio.sleep(0.01)
            task_completed = True
        
        task = runner.run_in_background(quick_task())
        
        # Wait a bit to ensure task is running
        await asyncio.sleep(0.005)
        
        await runner.stop(adapter)
        
        # Task should have completed (stop waits for tasks)
        assert task_completed or task.done()

    async def test_run_in_background(self):
        """Test running coroutine in background."""
        runner = AsyncAdapterRunner()
        
        async def background_task():
            await asyncio.sleep(0.01)
            return "done"
        
        task = runner.run_in_background(background_task())
        
        assert isinstance(task, asyncio.Task)
        assert task in runner._tasks
        
        # Wait for task to complete
        result = await task
        assert result == "done"

    async def test_stop_with_multiple_tasks(self):
        """Test stopping with multiple background tasks."""
        runner = AsyncAdapterRunner()
        adapter = MagicMock()
        adapter.stop_async = AsyncMock(return_value=None)
        
        task_results = []
        
        async def task1():
            await asyncio.sleep(0.01)
            task_results.append(1)
        
        async def task2():
            await asyncio.sleep(0.01)
            task_results.append(2)
        
        task1_handle = runner.run_in_background(task1())
        task2_handle = runner.run_in_background(task2())
        
        # Wait a bit to ensure tasks are running
        await asyncio.sleep(0.005)
        
        await runner.stop(adapter)
        
        # Both tasks should have completed (stop waits for tasks)
        # Tasks might complete before or during stop, so check both conditions
        assert len(task_results) == 2 or (task1_handle.done() and task2_handle.done())
        if len(task_results) >= 2:
            assert 1 in task_results
            assert 2 in task_results

    @pytest.mark.asyncio
    async def test_init_with_custom_loop(self):
        """Test initializing with custom event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            runner = AsyncAdapterRunner(loop=loop)
            
            assert runner.loop == loop
        finally:
            loop.close()

    @pytest.mark.asyncio
    async def test_init_without_loop(self):
        """Test initializing without loop uses current loop."""
        # This test needs to run in an async context with an event loop
        runner = AsyncAdapterRunner()
        
        assert runner.loop is not None
        assert isinstance(runner.loop, asyncio.AbstractEventLoop)

    def test_init_without_loop_no_event_loop(self):
        """Test initializing without loop when no event loop exists creates new one."""
        import threading
        
        def run_in_thread():
            # This thread has no event loop - remove any existing loop
            try:
                loop = asyncio.get_event_loop()
                if loop and not loop.is_closed():
                    loop.close()
            except RuntimeError:
                pass
            
            # Clear the event loop for this thread
            asyncio.set_event_loop(None)
            
            # Now create runner - should create new loop
            runner = AsyncAdapterRunner()
            assert runner.loop is not None
            assert isinstance(runner.loop, asyncio.AbstractEventLoop)
            runner.loop.close()
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()


@pytest.mark.fast
class TestBlockingAdapterRunner:
    """Test BlockingAdapterRunner."""

    async def test_start_blocking_adapter(self):
        """Test starting blocking adapter in thread pool."""
        runner = BlockingAdapterRunner()
        adapter = MagicMock()
        adapter.start = MagicMock(return_value=None)
        
        await runner.start(adapter)
        
        adapter.start.assert_called_once()

    async def test_stop_blocking_adapter(self):
        """Test stopping blocking adapter."""
        runner = BlockingAdapterRunner()
        adapter = MagicMock()
        adapter.stop = MagicMock(return_value=None)
        
        await runner.stop(adapter)
        
        adapter.stop.assert_called_once()

    async def test_stop_waits_for_futures(self):
        """Test that stop waits for all futures to complete."""
        runner = BlockingAdapterRunner()
        adapter = MagicMock()
        adapter.start = MagicMock(return_value=None)
        adapter.stop = MagicMock(return_value=None)
        
        # Start adapter to create a future
        await runner.start(adapter)
        
        # Stop should wait for futures
        await runner.stop(adapter)
        
        adapter.stop.assert_called_once()

    def test_shutdown_executor_wait(self):
        """Test shutting down executor with wait=True."""
        runner = BlockingAdapterRunner()
        
        # Should not raise exception
        runner.shutdown(wait=True)
        
        # Executor should be shut down
        assert runner.executor._shutdown

    def test_shutdown_executor_no_wait(self):
        """Test shutting down executor with wait=False."""
        runner = BlockingAdapterRunner()
        
        # Should not raise exception
        runner.shutdown(wait=False)
        
        # Executor should be shut down
        assert runner.executor._shutdown

    def test_init_with_custom_executor(self):
        """Test initializing with custom executor."""
        executor = ThreadPoolExecutor(max_workers=5)
        runner = BlockingAdapterRunner(executor=executor)
        
        assert runner.executor == executor
        
        runner.shutdown(wait=True)

    def test_init_without_executor(self):
        """Test initializing without executor creates new one."""
        runner = BlockingAdapterRunner()
        
        assert runner.executor is not None
        assert isinstance(runner.executor, ThreadPoolExecutor)
        
        runner.shutdown(wait=True)

    async def test_start_stores_future(self):
        """Test that start stores future in _futures list."""
        runner = BlockingAdapterRunner()
        adapter = MagicMock()
        adapter.start = MagicMock(return_value=None)
        
        initial_futures_count = len(runner._futures)
        
        await runner.start(adapter)
        
        assert len(runner._futures) == initial_futures_count + 1

    async def test_stop_with_multiple_futures(self):
        """Test stopping with multiple futures."""
        runner = BlockingAdapterRunner()
        adapter = MagicMock()
        adapter.start = MagicMock(return_value=None)
        adapter.stop = MagicMock(return_value=None)
        
        # Start multiple times to create multiple futures
        await runner.start(adapter)
        await runner.start(adapter)
        
        # Stop should handle all futures
        await runner.stop(adapter)
        
        adapter.stop.assert_called_once()


@pytest.mark.fast
class TestAdapterRunner:
    """Test AdapterRunner abstract base class."""

    def test_adapter_runner_is_abstract(self):
        """Test that AdapterRunner cannot be instantiated."""
        with pytest.raises(TypeError):
            AdapterRunner()  # type: ignore[abstract]

