"""MCP handlers for example service."""

import json
import logging

from hexswitch.shared.envelope import Envelope

from example_service.application.services.example_service import get_example_service

logger = logging.getLogger(__name__)

# Example tools and resources for MCP
_example_tools = [
    {
        "name": "get_example",
        "description": "Get an example item by ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Item ID"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "create_example",
        "description": "Create a new example item",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Item ID (optional)"},
                "name": {"type": "string", "description": "Item name"},
                "description": {"type": "string", "description": "Item description"},
                "data": {"type": "object", "description": "Additional data"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "list_examples",
        "description": "List all example items",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]

_example_resources = [
    {
        "uri": "example://items",
        "name": "Example Items",
        "description": "List of all example items",
        "mimeType": "application/json",
    },
    {
        "uri": "example://item/:id",
        "name": "Example Item",
        "description": "A specific example item",
        "mimeType": "application/json",
    },
]


def mcp_initialize_handler(envelope: Envelope) -> Envelope:
    """Handle MCP initialize request.

    Args:
        envelope: Request envelope with initialization parameters.

    Returns:
        Response envelope with server capabilities.
    """
    logger.info("MCP initialize request received")

    return Envelope(
        path=envelope.path,
        method=envelope.method,
        status_code=200,
        data={
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
            },
            "serverInfo": {
                "name": "example-service",
                "version": "1.0.0",
            },
        },
    )


def mcp_tools_list_handler(envelope: Envelope) -> Envelope:
    """Handle MCP tools/list request.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with list of available tools.
    """
    logger.info("MCP tools/list request received")

    return Envelope(
        path=envelope.path,
        method=envelope.method,
        status_code=200,
        data={"tools": _example_tools},
    )


def mcp_tools_call_handler(envelope: Envelope) -> Envelope:
    """Handle MCP tools/call request.

    Args:
        envelope: Request envelope with tool name and arguments.

    Returns:
        Response envelope with tool result.
    """
    try:
        body = envelope.body or {}
        tool_name = body.get("name")
        arguments = body.get("arguments", {})

        logger.info(f"MCP tools/call request received: tool={tool_name}, arguments={arguments}")

        service = get_example_service()

        if tool_name == "get_example":
            item_id = arguments.get("id")
            if not item_id:
                return Envelope.error(400, "Field 'id' is required")

            entity = service.get_example(item_id)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"content": [{"type": "text", "text": json.dumps(entity.to_dict())}]},
            )

        elif tool_name == "create_example":
            entity = service.create_from_dict(arguments)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"content": [{"type": "text", "text": f"Created item: {entity.id}"}]},
            )

        elif tool_name == "list_examples":
            entities = service.list_examples()
            items = [entity.to_dict() for entity in entities]
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"content": [{"type": "text", "text": json.dumps(items)}]},
            )

        else:
            return Envelope.error(404, f"Tool '{tool_name}' not found")

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(400, str(e))
    except Exception as e:
        logger.exception(f"Error in mcp_tools_call_handler: {e}")
        return Envelope.error(500, f"Internal error: {str(e)}")


def mcp_resources_list_handler(envelope: Envelope) -> Envelope:
    """Handle MCP resources/list request.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with list of available resources.
    """
    logger.info("MCP resources/list request received")

    return Envelope(
        path=envelope.path,
        method=envelope.method,
        status_code=200,
        data={"resources": _example_resources},
    )


def mcp_resources_read_handler(envelope: Envelope) -> Envelope:
    """Handle MCP resources/read request.

    Args:
        envelope: Request envelope with resource URI.

    Returns:
        Response envelope with resource content.
    """
    try:
        body = envelope.body or {}
        uri = body.get("uri", "")

        logger.info(f"MCP resources/read request received: uri={uri}")

        service = get_example_service()

        if uri == "example://items":
            entities = service.list_examples()
            items = [entity.to_dict() for entity in entities]
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(items),
                        }
                    ]
                },
            )
        elif uri.startswith("example://item/"):
            item_id = uri.split("/")[-1]
            entity = service.get_example(item_id)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(entity.to_dict()),
                        }
                    ]
                },
            )
        else:
            return Envelope.error(404, f"Resource '{uri}' not found")

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(404, str(e))
    except Exception as e:
        logger.exception(f"Error in mcp_resources_read_handler: {e}")
        return Envelope.error(500, f"Internal error: {str(e)}")
