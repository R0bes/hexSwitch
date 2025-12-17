"""WebSocket handlers for example3 service."""

import json
import logging

from example3_service.application.services.example3_service import get_example3_service

from hexswitch.shared.envelope import Envelope

logger = logging.getLogger(__name__)


def websocket_message_handler(envelope: Envelope) -> Envelope:
    """Handle WebSocket message.

    Args:
        envelope: Request envelope with WebSocket message.

    Returns:
        Response envelope with processed message.
    """
    try:
        body = envelope.body or {}
        message = body.get("message", "")

        # Parse message if it's JSON
        try:
            message_data = json.loads(message) if isinstance(message, str) else message
        except json.JSONDecodeError:
            message_data = {"text": message}

        # Process message
        service = get_example3_service()

        # Echo back with service info
        response_data = {
            "service": "example3",
            "received": message_data,
            "examples_count": len(service.list_examples())
        }

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data=response_data,
        )
    except Exception as e:
        logger.exception(f"Error in websocket_message_handler: {e}")
        return Envelope.error(500, "Internal server error")


def call_example1_handler(envelope: Envelope) -> Envelope:
    """Call example1 service via HTTP from WebSocket.

    Args:
        envelope: Request envelope with body containing path and data.

    Returns:
        Response envelope from example1.
    """
    try:
        from hexswitch.ports import get_port_registry

        body = envelope.body or {}
        path = body.get("path", "/api/examples")
        method = body.get("method", "GET")
        data = body.get("data", {})

        # Create envelope for HTTP call
        http_envelope = Envelope(
            path=path,
            method=method,
            body=data
        )

        # Route through HTTP client port
        registry = get_port_registry()
        results = registry.route("example1_http_port", http_envelope)

        if results:
            return results[0]
        else:
            return Envelope.error(500, "No response from example1")
    except Exception as e:
        logger.exception(f"Error calling example1: {e}")
        return Envelope.error(500, f"Error calling example1: {str(e)}")


def call_example2_handler(envelope: Envelope) -> Envelope:
    """Call example2 service via gRPC from WebSocket.

    Args:
        envelope: Request envelope with body containing method and data.

    Returns:
        Response envelope from example2.
    """
    try:
        from hexswitch.ports import get_port_registry

        body = envelope.body or {}
        method = body.get("method", "ListExamples")
        data = body.get("data", {})

        # Create envelope for gRPC call
        grpc_envelope = Envelope(
            path=f"/{method}",
            method="POST",
            body=data
        )

        # Route through gRPC client port
        registry = get_port_registry()
        results = registry.route("example2_grpc_port", grpc_envelope)

        if results:
            return results[0]
        else:
            return Envelope.error(500, "No response from example2")
    except Exception as e:
        logger.exception(f"Error calling example2: {e}")
        return Envelope.error(500, f"Error calling example2: {str(e)}")

