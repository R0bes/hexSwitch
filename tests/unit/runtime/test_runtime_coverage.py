"""Additional unit tests for runtime to improve coverage."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from hexswitch.adapters.base import OutboundAdapter
from hexswitch.runtime import Runtime
from hexswitch.shared.envelope import Envelope


class TestRuntimeDeliver:
    """Test Runtime.deliver() error cases."""

    def test_deliver_adapter_not_found(self) -> None:
        """Test deliver() when adapter is not found."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        envelope = Envelope(path="/test", method="POST")
        response = runtime.deliver(envelope, "nonexistent_adapter")

        assert response.status_code == 404
        assert "not found" in response.error_message.lower()

    def test_deliver_adapter_not_outbound_adapter(self) -> None:
        """Test deliver() when adapter is not an OutboundAdapter."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        # Add a mock that is not an OutboundAdapter
        mock_adapter = MagicMock()
        mock_adapter.name = "invalid_adapter"
        runtime.outbound_adapters.append(mock_adapter)

        envelope = Envelope(path="/test", method="POST")
        with pytest.raises(ValueError, match="not an OutboundAdapter"):
            runtime.deliver(envelope, "invalid_adapter")

    def test_deliver_adapter_request_exception(self) -> None:
        """Test deliver() when adapter.request() raises exception."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        mock_adapter = MagicMock(spec=OutboundAdapter)
        mock_adapter.name = "http_client"
        mock_adapter.request.side_effect = Exception("Connection failed")
        runtime.outbound_adapters.append(mock_adapter)

        envelope = Envelope(path="/test", method="POST")
        response = runtime.deliver(envelope, "http_client")

        assert response.status_code == 500
        assert "Failed to deliver" in response.error_message


class TestRuntimeDispatch:
    """Test Runtime.dispatch() with port policies."""

    @pytest.mark.asyncio
    async def test_dispatch_without_port_policy(self) -> None:
        """Test dispatch() without port policy."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        envelope = Envelope(path="/test", method="GET", metadata={})
        
        # Mock pipeline.process
        with patch.object(runtime.pipeline, "process") as mock_process:
            mock_process.return_value = Envelope.success({"result": "ok"})
            result = await runtime.dispatch(envelope)

            assert result.status_code == 200
            mock_process.assert_called_once_with(envelope)

    @pytest.mark.asyncio
    async def test_dispatch_with_port_policy_retry(self) -> None:
        """Test dispatch() with retry policy."""
        config = {
            "service": {"name": "test-service"},
            "ports": {
                "test_port": {
                    "policies": {
                        "retry": {"max_attempts": 3, "backoff": "exponential"}
                    }
                }
            }
        }
        runtime = Runtime(config)

        envelope = Envelope(path="/test", method="GET", metadata={"port_name": "test_port"})
        
        # Mock pipeline.process
        with patch.object(runtime.pipeline, "process") as mock_process:
            mock_process.return_value = Envelope.success({"result": "ok"})
            result = await runtime.dispatch(envelope)

            assert result.status_code == 200
            mock_process.assert_called_once_with(envelope)

    @pytest.mark.asyncio
    async def test_dispatch_with_port_policy_timeout(self) -> None:
        """Test dispatch() with timeout policy."""
        config = {
            "service": {"name": "test-service"},
            "ports": {
                "test_port": {
                    "policies": {
                        "timeout": {"seconds": 5}
                    }
                }
            }
        }
        runtime = Runtime(config)

        envelope = Envelope(path="/test", method="GET", metadata={"port_name": "test_port"})
        
        # Mock pipeline.process
        with patch.object(runtime.pipeline, "process") as mock_process:
            mock_process.return_value = Envelope.success({"result": "ok"})
            result = await runtime.dispatch(envelope)

            assert result.status_code == 200
            mock_process.assert_called_once_with(envelope)

    @pytest.mark.asyncio
    async def test_dispatch_with_port_policy_backpressure(self) -> None:
        """Test dispatch() with backpressure policy."""
        config = {
            "service": {"name": "test-service"},
            "ports": {
                "test_port": {
                    "policies": {
                        "backpressure": {"max_concurrent": 10}
                    }
                }
            }
        }
        runtime = Runtime(config)

        envelope = Envelope(path="/test", method="GET", metadata={"port_name": "test_port"})
        
        # Mock pipeline.process
        with patch.object(runtime.pipeline, "process") as mock_process:
            mock_process.return_value = Envelope.success({"result": "ok"})
            result = await runtime.dispatch(envelope)

            assert result.status_code == 200
            mock_process.assert_called_once_with(envelope)


class TestRuntimePortPolicies:
    """Test Runtime._load_port_policies()."""

    def test_load_port_policies_empty_config(self) -> None:
        """Test loading port policies with empty config."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)
        
        # Should not raise
        assert runtime.pipeline is not None

    def test_load_port_policies_no_ports(self) -> None:
        """Test loading port policies when no ports config."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)
        
        # Should not raise
        assert runtime.pipeline is not None

    def test_load_port_policies_with_policies(self) -> None:
        """Test loading port policies with all policy types."""
        config = {
            "service": {"name": "test-service"},
            "ports": {
                "test_port": {
                    "policies": {
                        "retry": {"max_attempts": 3},
                        "timeout": {"seconds": 5},
                        "backpressure": {"max_concurrent": 10}
                    }
                }
            }
        }
        runtime = Runtime(config)
        
        # Verify policy was set
        policy = runtime.pipeline.get_port_policy("test_port")
        assert policy is not None
        assert "retry" in policy
        assert "timeout" in policy
        assert "backpressure" in policy

    def test_load_port_policies_non_dict_config(self) -> None:
        """Test loading port policies with non-dict port config."""
        config = {
            "service": {"name": "test-service"},
            "ports": {
                "test_port": "not a dict"
            }
        }
        runtime = Runtime(config)
        
        # Should not raise, just skip
        assert runtime.pipeline is not None


class TestRuntimeRun:
    """Test Runtime.run() and run_sync()."""

    def test_run_without_start(self) -> None:
        """Test run() without calling start() first."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        with pytest.raises(RuntimeError, match="not started"):
            asyncio.run(runtime.run())

    def test_run_sync_without_start(self) -> None:
        """Test run_sync() without calling start() first."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        with pytest.raises(RuntimeError, match="not started"):
            runtime.run_sync()

    # Note: test_run_sync_with_shutdown removed due to event loop issues in test environment
    # This functionality is tested in integration tests


class TestRuntimeErrorHandling:
    """Test Runtime error handling in start/stop."""

    @pytest.mark.timeout(10)
    def test_async_start_adapter_error(self) -> None:
        """Test _async_start() when adapter creation fails."""
        config = {
            "service": {"name": "test-service"},
            "inbound": {
                "http": {
                    "enabled": True,
                    "port": 0,  # Invalid port
                    "routes": [],
                }
            }
        }
        runtime = Runtime(config)

        # Mock adapter factory to raise error
        with patch.object(runtime.adapter_factory, "create_inbound_adapter") as mock_create:
            mock_create.side_effect = Exception("Adapter creation failed")
            
            with pytest.raises(RuntimeError, match="Failed to start adapter"):
                asyncio.run(runtime._async_start())

    @pytest.mark.timeout(10)
    def test_async_stop_with_exception(self) -> None:
        """Test _async_stop() when adapter stop raises exception."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)

        # Create a mock adapter that raises on stop
        mock_adapter = MagicMock()
        mock_adapter.name = "test_adapter"
        mock_adapter.stop.side_effect = Exception("Stop failed")
        runtime.inbound_adapters.append(mock_adapter)

        # Should not raise, just log error
        asyncio.run(runtime._async_stop())
        
        # Adapters should be cleared
        assert len(runtime.inbound_adapters) == 0

    @pytest.mark.timeout(10)
    def test_async_stop_already_stopped(self) -> None:
        """Test _async_stop() when already stopped."""
        config = {"service": {"name": "test-service"}}
        runtime = Runtime(config)
        runtime._shutdown_requested = True
        runtime.inbound_adapters.clear()
        runtime.outbound_adapters.clear()

        # Should return early
        asyncio.run(runtime._async_stop())
        
        assert runtime._shutdown_requested is True

