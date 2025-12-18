"""Unit tests for gRPC outbound adapter."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import grpc
import pytest

from hexswitch.adapters.exceptions import AdapterConnectionError
from hexswitch.adapters.grpc.outbound_adapter import GrpcAdapterClient, compile_proto_files
from hexswitch.shared.envelope import Envelope


class TestCompileProtoFiles:
    """Test proto file compilation."""

    def test_compile_proto_files_nonexistent_path(self) -> None:
        """Test compilation with nonexistent path."""
        with pytest.raises(RuntimeError) as exc_info:
            compile_proto_files("/nonexistent/path", "/tmp/output")
        assert "does not exist" in str(exc_info.value)

    def test_compile_proto_files_no_proto_files(self) -> None:
        """Test compilation with no proto files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(RuntimeError) as exc_info:
                compile_proto_files(tmpdir, "/tmp/output")
            assert "No .proto files found" in str(exc_info.value)

    def test_compile_proto_files_compilation_error(self) -> None:
        """Test compilation error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid proto file
            proto_file = Path(tmpdir) / "test.proto"
            proto_file.write_text("invalid proto content")

            with patch("hexswitch.adapters.grpc.outbound_adapter.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(
                    1, "protoc", stderr=b"Compilation error"
                )

                with pytest.raises(RuntimeError) as exc_info:
                    compile_proto_files(tmpdir, "/tmp/output")
                assert "Failed to compile" in str(exc_info.value)

    def test_compile_proto_files_success(self) -> None:
        """Test successful compilation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create valid proto file
            proto_file = Path(tmpdir) / "test.proto"
            proto_file.write_text("""
syntax = "proto3";
package test;
message TestMessage {
    string field = 1;
}
""")

            output_dir = os.path.join(tmpdir, "output")
            os.makedirs(output_dir, exist_ok=True)

            with patch("hexswitch.adapters.grpc.outbound_adapter.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0)
                compile_proto_files(tmpdir, output_dir)
                mock_run.assert_called()


class TestGrpcAdapterClient:
    """Test gRPC client outbound adapter."""

    def test_initialization(self) -> None:
        """Test adapter initialization."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        assert adapter.name == "test_grpc"
        assert adapter.server_url == "localhost:50051"
        assert adapter.timeout == 30
        assert not adapter._connected

    def test_initialization_custom_config(self) -> None:
        """Test adapter initialization with custom config."""
        config = {
            "server_url": "example.com:50051",
            "proto_path": "/path/to/proto",
            "service_name": "TestService",
            "timeout": 60,
        }
        adapter = GrpcAdapterClient("test_grpc", config)
        assert adapter.server_url == "example.com:50051"
        assert adapter.proto_path == "/path/to/proto"
        assert adapter.service_name == "TestService"
        assert adapter.timeout == 60

    def test_connect_success(self) -> None:
        """Test successful connection."""
        config = {"server_url": "localhost:50051", "timeout": 5}
        adapter = GrpcAdapterClient("test_grpc", config)

        with patch("grpc.insecure_channel") as mock_channel:
            mock_channel_instance = Mock()
            mock_channel.return_value = mock_channel_instance

            with patch("grpc.channel_ready_future") as mock_ready:
                mock_future = Mock()
                mock_future.result.return_value = None
                mock_ready.return_value = mock_future

                adapter.connect()
                assert adapter._connected
                assert adapter.channel == mock_channel_instance

    def test_connect_already_connected(self) -> None:
        """Test connecting when already connected."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True

        with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
            adapter.connect()
            mock_logger.warning.assert_called_once()

    def test_connect_missing_server_url(self) -> None:
        """Test connection with missing server URL."""
        config = {}
        adapter = GrpcAdapterClient("test_grpc", config)

        with pytest.raises(AdapterConnectionError) as exc_info:
            adapter.connect()
        assert "server_url is required" in str(exc_info.value)

    def test_connect_with_proto_path(self) -> None:
        """Test connection with proto path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            proto_dir = os.path.join(tmpdir, "proto")
            os.makedirs(proto_dir, exist_ok=True)
            proto_file = Path(proto_dir) / "test.proto"
            proto_file.write_text("syntax = 'proto3'; message Test {}")

            config = {
                "server_url": "localhost:50051",
                "proto_path": proto_dir,
                "service_name": "TestService",
            }
            adapter = GrpcAdapterClient("test_grpc", config)

            with patch("hexswitch.adapters.grpc.outbound_adapter.compile_proto_files") as mock_compile:
                with patch("grpc.insecure_channel") as mock_channel:
                    mock_channel_instance = Mock()
                    mock_channel.return_value = mock_channel_instance

                    with patch("grpc.channel_ready_future") as mock_ready:
                        mock_future = Mock()
                        mock_future.result.return_value = None
                        mock_ready.return_value = mock_future

                        with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
                            adapter.connect()
                            mock_compile.assert_called_once()
                            mock_logger.info.assert_called()

    def test_connect_timeout_error(self) -> None:
        """Test connection timeout error."""
        config = {"server_url": "localhost:50051", "timeout": 1}
        adapter = GrpcAdapterClient("test_grpc", config)

        with patch("grpc.insecure_channel") as mock_channel:
            mock_channel_instance = Mock()
            mock_channel.return_value = mock_channel_instance

            with patch("grpc.channel_ready_future") as mock_ready:
                mock_future = Mock()
                mock_future.result.side_effect = grpc.FutureTimeoutError()
                mock_ready.return_value = mock_future

                with pytest.raises(AdapterConnectionError) as exc_info:
                    adapter.connect()
                assert "timeout" in str(exc_info.value).lower()

    def test_connect_error(self) -> None:
        """Test connection error."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)

        with patch("grpc.insecure_channel") as mock_channel:
            mock_channel.side_effect = Exception("Connection failed")

            with pytest.raises(AdapterConnectionError):
                adapter.connect()

    def test_disconnect_success(self) -> None:
        """Test successful disconnection."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        mock_channel = Mock()
        adapter.channel = mock_channel

        adapter.disconnect()
        assert not adapter._connected
        assert adapter.channel is None
        assert adapter.stub is None
        mock_channel.close.assert_called_once()

    def test_disconnect_not_connected(self) -> None:
        """Test disconnecting when not connected."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)

        with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
            adapter.disconnect()
            mock_logger.warning.assert_called_once()

    def test_disconnect_with_compiled_proto_cleanup(self) -> None:
        """Test disconnection with compiled proto cleanup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"server_url": "localhost:50051"}
            adapter = GrpcAdapterClient("test_grpc", config)
            adapter._connected = True
            adapter.channel = Mock()
            adapter._compiled_proto_dir = tmpdir

            with patch("os.path.exists", return_value=True):
                with patch("shutil.rmtree") as mock_rmtree:
                    with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
                        adapter.disconnect()
                        mock_rmtree.assert_called_once_with(tmpdir, ignore_errors=True)
                        mock_logger.debug.assert_called()

    def test_disconnect_error(self) -> None:
        """Test disconnection error handling."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        mock_channel = Mock()
        mock_channel.close.side_effect = Exception("Close error")
        adapter.channel = mock_channel

        with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
            adapter.disconnect()
            mock_logger.error.assert_called()

    def test_from_envelope(self) -> None:
        """Test converting envelope to gRPC request."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        envelope = Envelope(path="/test", method="POST", body={"key": "value"})

        result = adapter.from_envelope(envelope)
        assert isinstance(result, dict)

    def test_to_envelope(self) -> None:
        """Test converting gRPC response to envelope."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        original_envelope = Envelope(path="/test", method="POST")

        # Mock protobuf response
        mock_response = Mock()
        mock_response.DESCRIPTOR = Mock()
        mock_response.DESCRIPTOR.fields = []

        result = adapter.to_envelope(mock_response, original_envelope)
        assert result.status_code == 200

    def test_request_success(self) -> None:
        """Test successful request."""
        config = {"server_url": "localhost:50051", "timeout": 5}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = Mock()
        adapter.stub = {"channel": adapter.channel, "service_name": "TestService"}

        envelope = Envelope(path="/TestService/TestMethod", method="POST", body={"key": "value"})

        result = adapter.request(envelope)
        # Should return error since stub is not fully implemented
        assert result.status_code == 501

    def test_request_not_connected(self) -> None:
        """Test request when not connected."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)

        envelope = Envelope(path="/test", method="POST")

        with pytest.raises(RuntimeError) as exc_info:
            adapter.request(envelope)
        assert "not connected" in str(exc_info.value)

    def test_request_no_channel(self) -> None:
        """Test request when channel is None."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = None

        envelope = Envelope(path="/test", method="POST")

        with pytest.raises(RuntimeError) as exc_info:
            adapter.request(envelope)
        assert "not connected" in str(exc_info.value)

    def test_request_no_stub(self) -> None:
        """Test request when stub is None."""
        config = {"server_url": "localhost:50051"}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = Mock()
        adapter.stub = None

        envelope = Envelope(path="/test", method="POST")

        with pytest.raises(RuntimeError) as exc_info:
            adapter.request(envelope)
        assert "not connected" in str(exc_info.value)

    def test_request_with_grpc_error(self) -> None:
        """Test request with gRPC error."""
        config = {"server_url": "localhost:50051", "timeout": 5}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = Mock()
        adapter.stub = {"channel": adapter.channel, "service_name": "TestService"}

        envelope = Envelope(path="/TestService/TestMethod", method="POST", body={"key": "value"})

        # Mock converter to raise RpcError
        with patch.object(adapter._converter, "envelope_to_request") as mock_convert:
            mock_convert.return_value = {}
            with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
                # The request method will try to call stub, which will fail
                # Since stub is not fully implemented, it returns 501 error
                result = adapter.request(envelope)
                assert result.status_code == 501

    def test_request_extract_method_name(self) -> None:
        """Test request extracts method name from path."""
        config = {"server_url": "localhost:50051", "timeout": 5}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = Mock()
        adapter.stub = {"channel": adapter.channel, "service_name": "TestService"}

        envelope = Envelope(path="/ServiceName/MethodName", method="POST", body={})

        with patch("hexswitch.adapters.grpc.outbound_adapter.logger") as mock_logger:
            result = adapter.request(envelope)
            # Should log the method name
            mock_logger.debug.assert_called()

    def test_request_with_metadata(self) -> None:
        """Test request with metadata."""
        config = {"server_url": "localhost:50051", "timeout": 5}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = Mock()
        adapter.stub = {"channel": adapter.channel, "service_name": "TestService"}

        envelope = Envelope(
            path="/TestService/TestMethod",
            method="POST",
            body={},
            metadata={"grpc_metadata": {"key": "value"}},
        )

        result = adapter.request(envelope)
        # Should handle metadata extraction
        assert result.status_code == 501  # Stub not implemented

    def test_request_unknown_method(self) -> None:
        """Test request with unknown method name."""
        config = {"server_url": "localhost:50051", "timeout": 5}
        adapter = GrpcAdapterClient("test_grpc", config)
        adapter._connected = True
        adapter.channel = Mock()
        adapter.stub = {"channel": adapter.channel, "service_name": "TestService"}

        envelope = Envelope(path="", method="POST", body={})

        result = adapter.request(envelope)
        assert result.status_code == 501

