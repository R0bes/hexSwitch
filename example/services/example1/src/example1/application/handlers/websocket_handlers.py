"""WebSocket handlers for example service."""

import json
import logging

from hexswitch.shared.envelope import Envelope

from example_service.application.services.example_service import get_example_service

logger = logging.getLogger(__name__)


def websocket_connection_handler(connection_data: dict) -> None:
    """Handle WebSocket connection.

    Args:
        connection_data: Connection data containing websocket, path, remote_address.
    """
    websocket = connection_data.get("websocket")
    path = connection_data.get("path", "")
    remote_address = connection_data.get("remote_address")

    logger.info(f"WebSocket connection established: {path} from {remote_address}")

    if websocket:
        try:
            # Send welcome message
            welcome_message = {
                "type": "welcome",
                "message": "Connected to example service",
                "path": path,
            }
            # Note: WebSocket adapter handles the actual sending
            # This is just for demonstration
        except Exception as e:
            logger.error(f"Error in WebSocket connection handler: {e}")


def websocket_message_handler(envelope: Envelope) -> Envelope:
    """Handle WebSocket message.

    Args:
        envelope: Request envelope with WebSocket message data.

    Returns:
        Response envelope with response data.
    """
    try:
        # Parse message from envelope body
        message = envelope.body
        if isinstance(message, str):
            message = json.loads(message)
        elif not isinstance(message, dict):
            message = {"raw": message}

        message_type = message.get("type", "unknown")
        action = message.get("action")

        logger.info(f"Received WebSocket message: type={message_type}, action={action}")

        service = get_example_service()

        if action == "get":
            # Get item by ID
            item_id = message.get("id")
            if not item_id:
                return Envelope.error(400, "Field 'id' is required")

            entity = service.get_example(item_id)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"type": "response", "action": "get", "item": entity.to_dict()},
            )

        elif action == "list":
            # List all items
            entities = service.list_examples()
            items = [entity.to_dict() for entity in entities]
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"type": "response", "action": "list", "items": items, "count": len(items)},
            )

        elif action == "create":
            # Create new item
            entity = service.create_from_dict(message)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"type": "response", "action": "create", "item": entity.to_dict()},
            )

        elif action == "update":
            # Update item
            item_id = message.get("id")
            if not item_id:
                return Envelope.error(400, "Field 'id' is required")

            entity = service.update_example(
                entity_id=item_id,
                name=message.get("name"),
                description=message.get("description"),
                data=message.get("data"),
            )

            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"type": "response", "action": "update", "item": entity.to_dict()},
            )

        elif action == "delete":
            # Delete item
            item_id = message.get("id")
            if not item_id:
                return Envelope.error(400, "Field 'id' is required")

            deleted = service.delete_example(item_id)
            if not deleted:
                return Envelope.error(404, f"Item with id '{item_id}' not found")

            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"type": "response", "action": "delete", "message": f"Item '{item_id}' deleted"},
            )

        else:
            return Envelope.error(400, f"Unknown action: {action}")

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(400, str(e))
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in WebSocket message: {e}")
        return Envelope.error(400, "Invalid JSON message")
    except Exception as e:
        logger.exception(f"Error processing WebSocket message: {e}")
        return Envelope.error(500, f"Internal error: {str(e)}")
