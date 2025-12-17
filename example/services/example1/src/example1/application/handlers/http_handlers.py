"""HTTP handlers for example service."""

import logging

from hexswitch.shared.envelope import Envelope

from example_service.application.services.example_service import get_example_service

logger = logging.getLogger(__name__)


def get_example_handler(envelope: Envelope) -> Envelope:
    """Handle GET request to retrieve example data.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with example data.
    """
    try:
        service = get_example_service()
        item_id = envelope.path_params.get("id") if envelope.path_params else None

        if item_id:
            # Get specific item
            entity = service.get_example(item_id)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data=entity.to_dict(),
            )
        else:
            # List all items
            entities = service.list_examples()
            items = [entity.to_dict() for entity in entities]
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"items": items, "count": len(items)},
            )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(404, str(e))
    except Exception as e:
        logger.exception(f"Error in get_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def create_example_handler(envelope: Envelope) -> Envelope:
    """Handle POST request to create example data.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with created data.
    """
    try:
        if not envelope.body:
            return Envelope.error(400, "Request body is required")

        body = envelope.body if isinstance(envelope.body, dict) else {}

        service = get_example_service()
        entity = service.create_from_dict(body)

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=201,
            data=entity.to_dict(),
        )
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(400, str(e))
    except Exception as e:
        logger.exception(f"Error in create_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def update_example_handler(envelope: Envelope) -> Envelope:
    """Handle PUT request to update example data.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with updated data.
    """
    try:
        item_id = envelope.path_params.get("id") if envelope.path_params else None

        if not item_id:
            return Envelope.error(400, "Item ID is required in path")

        if not envelope.body:
            return Envelope.error(400, "Request body is required")

        body = envelope.body if isinstance(envelope.body, dict) else {}

        service = get_example_service()
        entity = service.update_example(
            entity_id=item_id,
            name=body.get("name"),
            description=body.get("description"),
            data=body.get("data"),
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
        logger.exception(f"Error in update_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def delete_example_handler(envelope: Envelope) -> Envelope:
    """Handle DELETE request to delete example data.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with deletion confirmation.
    """
    try:
        item_id = envelope.path_params.get("id") if envelope.path_params else None

        if not item_id:
            return Envelope.error(400, "Item ID is required in path")

        service = get_example_service()
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
        logger.exception(f"Error in delete_example_handler: {e}")
        return Envelope.error(500, "Internal server error")


def call_example2_handler(envelope: Envelope) -> Envelope:
    """Call example2 service via gRPC.
    
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