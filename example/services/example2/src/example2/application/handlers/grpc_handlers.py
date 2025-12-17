"""gRPC handlers for example2 service."""

import logging

from example2_service.application.services.example2_service import get_example2_service

from hexswitch.shared.envelope import Envelope

logger = logging.getLogger(__name__)


def grpc_get_example_handler(envelope: Envelope) -> Envelope:
    """Handle gRPC GetExample request.

    Args:
        envelope: Request envelope with body containing id.

    Returns:
        Response envelope with example data.
    """
    try:
        body = envelope.body or {}
        item_id = body.get("id")

        if not item_id:
            return Envelope.error(400, "Field 'id' is required")

        service = get_example2_service()
        entity = service.get_example(item_id)

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data=entity.to_dict(),
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(404, str(e))
    except Exception as e:
        logger.exception(f"Error in grpc_get_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def grpc_create_example_handler(envelope: Envelope) -> Envelope:
    """Handle gRPC CreateExample request.

    Args:
        envelope: Request envelope with body containing name, description, data.

    Returns:
        Response envelope with created data.
    """
    try:
        body = envelope.body or {}
        name = body.get("name")
        description = body.get("description")
        data = body.get("data")

        if not name:
            return Envelope.error(400, "Field 'name' is required")

        service = get_example2_service()
        entity = service.create_example(name=name, description=description, data=data)

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data=entity.to_dict(),
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(400, str(e))
    except Exception as e:
        logger.exception(f"Error in grpc_create_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def grpc_list_examples_handler(envelope: Envelope) -> Envelope:
    """Handle gRPC ListExamples request.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with list of examples.
    """
    try:
        service = get_example2_service()
        entities = service.list_examples()
        items = [entity.to_dict() for entity in entities]

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={"items": items, "count": len(items)},
        )
    except Exception as e:
        logger.exception(f"Error in grpc_list_examples_handler: {e}")
        return Envelope.error(500, "Internal server error")


def grpc_update_example_handler(envelope: Envelope) -> Envelope:
    """Handle gRPC UpdateExample request.

    Args:
        envelope: Request envelope with body containing id, name, description, data.

    Returns:
        Response envelope with updated data.
    """
    try:
        body = envelope.body or {}
        item_id = body.get("id")
        name = body.get("name")
        description = body.get("description")
        data = body.get("data")

        if not item_id:
            return Envelope.error(400, "Field 'id' is required")

        service = get_example2_service()
        entity = service.update_example(
            entity_id=item_id, name=name, description=description, data=data
        )

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data=entity.to_dict(),
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(404, str(e))
    except Exception as e:
        logger.exception(f"Error in grpc_update_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def grpc_delete_example_handler(envelope: Envelope) -> Envelope:
    """Handle gRPC DeleteExample request.

    Args:
        envelope: Request envelope with body containing id.

    Returns:
        Response envelope with deletion confirmation.
    """
    try:
        body = envelope.body or {}
        item_id = body.get("id")

        if not item_id:
            return Envelope.error(400, "Field 'id' is required")

        service = get_example2_service()
        deleted = service.delete_example(item_id)

        if not deleted:
            return Envelope.error(404, f"Item with id '{item_id}' not found")

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={"message": f"Item '{item_id}' deleted successfully"},
        )
    except Exception as e:
        logger.exception(f"Error in grpc_delete_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def call_example1_handler(envelope: Envelope) -> Envelope:
    """Call example1 service via HTTP.

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


def call_example3_handler(envelope: Envelope) -> Envelope:
    """Call example3 service via WebSocket.

    Args:
        envelope: Request envelope with body containing message.

    Returns:
        Response envelope from example3.
    """
    try:
        from hexswitch.ports import get_port_registry

        body = envelope.body or {}
        message = body.get("message", "ping")

        # Create envelope for WebSocket call
        ws_envelope = Envelope(
            path="/ws",
            method="POST",
            body={"message": message}
        )

        # Route through WebSocket client port
        registry = get_port_registry()
        results = registry.route("example3_ws_port", ws_envelope)

        if results:
            return results[0]
        else:
            return Envelope.error(500, "No response from example3")
    except Exception as e:
        logger.exception(f"Error calling example3: {e}")
        return Envelope.error(500, f"Error calling example3: {str(e)}")

