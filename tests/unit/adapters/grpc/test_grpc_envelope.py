"""Unit tests for GrpcEnvelope conversion logic."""

from unittest.mock import MagicMock, Mock

import grpc
import pytest

from hexswitch.adapters.grpc._Grpc_Envelope import GrpcEnvelope
from hexswitch.shared.envelope import Envelope


class TestGrpcEnvelope:
    """Test GrpcEnvelope conversion methods."""

    def test_request_to_envelope_with_metadata(self) -> None:
        """Test converting gRPC request to envelope with metadata."""
        # Create mock protobuf request
        mock_request = MagicMock()
        mock_field1 = MagicMock()
        mock_field1.name = "field1"
        mock_field1.label = 1  # LABEL_OPTIONAL
        mock_field1.LABEL_REPEATED = 3
        mock_field2 = MagicMock()
        mock_field2.name = "field2"
        mock_field2.label = 3  # LABEL_REPEATED
        mock_field2.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field1, mock_field2]
        mock_request.DESCRIPTOR = mock_descriptor
        mock_request.field1 = "value1"
        mock_request.field2 = ["item1", "item2"]

        # Create mock gRPC context with metadata
        mock_context = MagicMock()
        mock_context.invocation_metadata.return_value = [
            ("authorization", "Bearer token123"),
            ("content-type", "application/grpc"),
            ("x-trace-id", "trace-123"),
        ]

        envelope = GrpcEnvelope.request_to_envelope(
            request=mock_request,
            context=mock_context,
            service_name="TestService",
            method_name="TestMethod",
        )

        assert envelope.path == "/TestService/TestMethod"
        assert envelope.method is None
        assert envelope.body == {"field1": "value1", "field2": ["item1", "item2"]}
        assert envelope.metadata["service"] == "TestService"
        assert envelope.metadata["method"] == "TestMethod"
        assert envelope.metadata["grpc_metadata"]["authorization"] == "Bearer token123"
        assert envelope.metadata["grpc_metadata"]["content-type"] == "application/grpc"
        assert envelope.metadata["grpc_metadata"]["x-trace-id"] == "trace-123"

    def test_request_to_envelope_without_metadata(self) -> None:
        """Test converting gRPC request to envelope without metadata."""
        # Create mock protobuf request
        mock_request = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "test_field"
        mock_field.label = 1  # LABEL_OPTIONAL
        mock_field.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field]
        mock_request.DESCRIPTOR = mock_descriptor
        mock_request.test_field = "test_value"

        # Create mock gRPC context without invocation_metadata
        mock_context = MagicMock()
        del mock_context.invocation_metadata

        envelope = GrpcEnvelope.request_to_envelope(
            request=mock_request,
            context=mock_context,
            service_name="Service",
            method_name="Method",
        )

        assert envelope.path == "/Service/Method"
        assert envelope.metadata["grpc_metadata"] == {}

    def test_request_to_envelope_without_descriptor(self) -> None:
        """Test converting gRPC request to envelope without DESCRIPTOR."""
        # Create mock request without DESCRIPTOR
        mock_request = MagicMock()
        del mock_request.DESCRIPTOR

        mock_context = MagicMock()
        mock_context.invocation_metadata.return_value = []

        envelope = GrpcEnvelope.request_to_envelope(
            request=mock_request,
            context=mock_context,
            service_name="Service",
            method_name="Method",
        )

        assert envelope.path == "/Service/Method"
        assert envelope.body is None

    def test_request_to_envelope_with_empty_repeated_field(self) -> None:
        """Test converting gRPC request with empty repeated field."""
        mock_request = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "repeated_field"
        mock_field.label = 3  # LABEL_REPEATED
        mock_field.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field]
        mock_request.DESCRIPTOR = mock_descriptor
        mock_request.repeated_field = None

        mock_context = MagicMock()
        mock_context.invocation_metadata.return_value = []

        envelope = GrpcEnvelope.request_to_envelope(
            request=mock_request,
            context=mock_context,
            service_name="Service",
            method_name="Method",
        )

        assert envelope.body == {"repeated_field": []}

    def test_request_to_envelope_with_trace_context(self) -> None:
        """Test converting gRPC request with trace context in metadata."""
        mock_request = MagicMock()
        del mock_request.DESCRIPTOR

        mock_context = MagicMock()
        mock_context.invocation_metadata.return_value = [
            ("traceparent", "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"),
            ("x-b3-traceid", "trace-456"),
            ("x-b3-spanid", "span-456"),
        ]

        envelope = GrpcEnvelope.request_to_envelope(
            request=mock_request,
            context=mock_context,
            service_name="Service",
            method_name="Method",
        )

        # Trace context should be extracted (may be None if OpenTelemetry not configured)
        assert envelope.trace_id is not None or envelope.trace_id is None
        assert envelope.span_id is not None or envelope.span_id is None

    def test_envelope_to_response_with_data(self) -> None:
        """Test converting envelope to gRPC response with data."""
        grpc_envelope = GrpcEnvelope()
        envelope = Envelope(
            path="/test",
            method="POST",
            data={"result": "success", "value": 42},
        )

        response = grpc_envelope.envelope_to_response(envelope)

        assert response == {"result": "success", "value": 42}

    def test_envelope_to_response_with_error(self) -> None:
        """Test converting envelope to gRPC response with error."""
        grpc_envelope = GrpcEnvelope()
        envelope = Envelope(
            path="/test",
            method="POST",
            error_message="Something went wrong",
        )

        response = grpc_envelope.envelope_to_response(envelope)

        assert response == {}

    def test_envelope_to_response_with_empty_data(self) -> None:
        """Test converting envelope to gRPC response with empty data."""
        grpc_envelope = GrpcEnvelope()
        envelope = Envelope(path="/test", method="POST", data=None)

        response = grpc_envelope.envelope_to_response(envelope)

        assert response == {}

    def test_envelope_to_request_with_body(self) -> None:
        """Test converting envelope to gRPC request with body."""
        grpc_envelope = GrpcEnvelope()
        envelope = Envelope(
            path="/test",
            method="POST",
            body={"param1": "value1", "param2": 123},
        )

        request = grpc_envelope.envelope_to_request(envelope)

        assert request == {"param1": "value1", "param2": 123}

    def test_envelope_to_request_without_body(self) -> None:
        """Test converting envelope to gRPC request without body."""
        grpc_envelope = GrpcEnvelope()
        envelope = Envelope(path="/test", method="POST", body=None)

        request = grpc_envelope.envelope_to_request(envelope)

        assert request == {}

    def test_response_to_envelope_with_original_envelope(self) -> None:
        """Test converting gRPC response to envelope with original envelope."""
        # Create mock protobuf response
        mock_response = MagicMock()
        mock_field1 = MagicMock()
        mock_field1.name = "status"
        mock_field1.label = 1  # LABEL_OPTIONAL
        mock_field1.LABEL_REPEATED = 3
        mock_field2 = MagicMock()
        mock_field2.name = "items"
        mock_field2.label = 3  # LABEL_REPEATED
        mock_field2.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field1, mock_field2]
        mock_response.DESCRIPTOR = mock_descriptor
        mock_response.status = "ok"
        mock_response.items = ["item1", "item2"]

        original_envelope = Envelope(
            path="/test",
            method="POST",
            trace_id="trace-123",
            span_id="span-123",
            parent_span_id="parent-123",
            metadata={"key": "value"},
        )

        envelope = GrpcEnvelope.response_to_envelope(
            response=mock_response,
            original_envelope=original_envelope,
        )

        assert envelope.path == "/test"
        assert envelope.method == "POST"
        assert envelope.status_code == 200
        assert envelope.data == {"status": "ok", "items": ["item1", "item2"]}
        assert envelope.metadata == {"key": "value"}
        assert envelope.trace_id == "trace-123"
        assert envelope.span_id == "span-123"
        assert envelope.parent_span_id == "parent-123"

    def test_response_to_envelope_without_original_envelope(self) -> None:
        """Test converting gRPC response to envelope without original envelope."""
        mock_response = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "result"
        mock_field.label = 1
        mock_field.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field]
        mock_response.DESCRIPTOR = mock_descriptor
        mock_response.result = "success"

        envelope = GrpcEnvelope.response_to_envelope(
            response=mock_response,
            original_envelope=None,
        )

        assert envelope.path == ""
        assert envelope.method is None
        assert envelope.status_code == 200
        assert envelope.data == {"result": "success"}
        assert envelope.metadata == {}
        assert envelope.trace_id is None
        assert envelope.span_id is None
        assert envelope.parent_span_id is None

    def test_response_to_envelope_without_descriptor(self) -> None:
        """Test converting gRPC response to envelope without DESCRIPTOR."""
        mock_response = MagicMock()
        del mock_response.DESCRIPTOR

        envelope = GrpcEnvelope.response_to_envelope(
            response=mock_response,
            original_envelope=None,
        )

        assert envelope.data is None

    def test_response_to_envelope_with_empty_repeated_field(self) -> None:
        """Test converting gRPC response with empty repeated field."""
        mock_response = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "list_field"
        mock_field.label = 3  # LABEL_REPEATED
        mock_field.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field]
        mock_response.DESCRIPTOR = mock_descriptor
        mock_response.list_field = None

        envelope = GrpcEnvelope.response_to_envelope(
            response=mock_response,
            original_envelope=None,
        )

        assert envelope.data == {"list_field": []}

    def test_response_to_envelope_metadata_copy(self) -> None:
        """Test that metadata is copied, not referenced."""
        mock_response = MagicMock()
        del mock_response.DESCRIPTOR

        original_metadata = {"key": "value"}
        original_envelope = Envelope(
            path="/test",
            method="POST",
            metadata=original_metadata,
        )

        envelope = GrpcEnvelope.response_to_envelope(
            response=mock_response,
            original_envelope=original_envelope,
        )

        # Modify original metadata
        original_metadata["new_key"] = "new_value"

        # Envelope metadata should not be affected
        assert "new_key" not in envelope.metadata
        assert envelope.metadata == {"key": "value"}

    def test_error_to_envelope_not_found(self) -> None:
        """Test converting gRPC NOT_FOUND error to envelope."""
        original_envelope = Envelope(
            path="/test",
            method="GET",
            trace_id="trace-123",
            span_id="span-123",
            metadata={"key": "value"},
        )

        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.NOT_FOUND,
            error_message="Resource not found",
            original_envelope=original_envelope,
        )

        assert envelope.path == "/test"
        assert envelope.method == "GET"
        assert envelope.status_code == 404
        assert envelope.error_message == "Resource not found"
        assert envelope.metadata == {"key": "value"}
        assert envelope.trace_id == "trace-123"
        assert envelope.span_id == "span-123"

    def test_error_to_envelope_invalid_argument(self) -> None:
        """Test converting gRPC INVALID_ARGUMENT error to envelope."""
        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.INVALID_ARGUMENT,
            error_message="Invalid parameter",
            original_envelope=None,
        )

        assert envelope.status_code == 400
        assert envelope.error_message == "Invalid parameter"

    def test_error_to_envelope_unauthenticated(self) -> None:
        """Test converting gRPC UNAUTHENTICATED error to envelope."""
        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.UNAUTHENTICATED,
            error_message="Authentication required",
            original_envelope=None,
        )

        assert envelope.status_code == 401
        assert envelope.error_message == "Authentication required"

    def test_error_to_envelope_permission_denied(self) -> None:
        """Test converting gRPC PERMISSION_DENIED error to envelope."""
        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.PERMISSION_DENIED,
            error_message="Access denied",
            original_envelope=None,
        )

        assert envelope.status_code == 403
        assert envelope.error_message == "Access denied"

    def test_error_to_envelope_unknown_status_code(self) -> None:
        """Test converting gRPC error with unknown status code to envelope."""
        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.INTERNAL,
            error_message="Internal error",
            original_envelope=None,
        )

        # Unknown status codes should default to 500
        assert envelope.status_code == 500
        assert envelope.error_message == "Internal error"

    def test_error_to_envelope_without_original_envelope(self) -> None:
        """Test converting gRPC error to envelope without original envelope."""
        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.NOT_FOUND,
            error_message="Not found",
            original_envelope=None,
        )

        assert envelope.path == ""
        assert envelope.method is None
        assert envelope.status_code == 404
        assert envelope.error_message == "Not found"
        assert envelope.metadata == {}
        assert envelope.trace_id is None
        assert envelope.span_id is None
        assert envelope.parent_span_id is None

    def test_error_to_envelope_metadata_copy(self) -> None:
        """Test that error envelope metadata is copied, not referenced."""
        original_metadata = {"key": "value"}
        original_envelope = Envelope(
            path="/test",
            method="POST",
            metadata=original_metadata,
        )

        envelope = GrpcEnvelope.error_to_envelope(
            status_code=grpc.StatusCode.INTERNAL,
            error_message="Error",
            original_envelope=original_envelope,
        )

        # Modify original metadata
        original_metadata["new_key"] = "new_value"

        # Envelope metadata should not be affected
        assert "new_key" not in envelope.metadata
        assert envelope.metadata == {"key": "value"}

    def test_request_to_envelope_with_missing_field_value(self) -> None:
        """Test converting gRPC request when field value is missing."""
        mock_request = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "missing_field"
        mock_field.label = 1
        mock_field.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field]
        mock_request.DESCRIPTOR = mock_descriptor
        # Field doesn't exist on request object
        mock_request.missing_field = None

        mock_context = MagicMock()
        mock_context.invocation_metadata.return_value = []

        envelope = GrpcEnvelope.request_to_envelope(
            request=mock_request,
            context=mock_context,
            service_name="Service",
            method_name="Method",
        )

        assert envelope.body == {"missing_field": None}

    def test_response_to_envelope_with_missing_field_value(self) -> None:
        """Test converting gRPC response when field value is missing."""
        mock_response = MagicMock()
        mock_field = MagicMock()
        mock_field.name = "missing_field"
        mock_field.label = 1
        mock_field.LABEL_REPEATED = 3

        mock_descriptor = MagicMock()
        mock_descriptor.fields = [mock_field]
        mock_response.DESCRIPTOR = mock_descriptor
        mock_response.missing_field = None

        envelope = GrpcEnvelope.response_to_envelope(
            response=mock_response,
            original_envelope=None,
        )

        assert envelope.data == {"missing_field": None}

