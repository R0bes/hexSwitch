"""gRPC handlers for example service."""

import logging

from hexswitch.shared.envelope import Envelope

from example_service.application.services.example_service import get_example_service

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

        service = get_example_service()
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

        service = get_example_service()
        entity = service.create_from_dict(body)

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
        service = get_example_service()
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
        envelope: Request envelope with body containing id and update fields.

    Returns:
        Response envelope with updated data.
    """
    try:
        body = envelope.body or {}
        item_id = body.get("id")

        if not item_id:
            return Envelope.error(400, "Field 'id' is required")

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
        logger.exception(f"Error in grpc_delete_example_handler: {e}")
        return Envelope.error(500, "Internal server error")
