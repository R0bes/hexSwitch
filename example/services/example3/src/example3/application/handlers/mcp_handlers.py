"""MCP handlers for example3 service."""

import json
import logging

from example3_service.application.services.example3_service import get_example3_service

from hexswitch.shared.envelope import Envelope

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
    {
        "name": "call_example1",
        "description": "Call example1 service via HTTP",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "HTTP path"},
                "method": {"type": "string", "description": "HTTP method"},
                "data": {"type": "object", "description": "Request data"},
            },
        },
    },
    {
        "name": "call_example2",
        "description": "Call example2 service via gRPC",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "description": "gRPC method name"},
                "data": {"type": "object", "description": "Request data"},
            },
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
]


def mcp_initialize_handler(envelope: Envelope) -> Envelope:
    """Handle MCP initialize request.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with initialization data.
    """
    try:
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
                    "name": "example3-mcp",
                    "version": "1.0.0",
                },
            },
        )
    except Exception as e:
        logger.exception(f"Error in mcp_initialize_handler: {e}")
        return Envelope.error(500, "Internal server error")


def mcp_tools_list_handler(envelope: Envelope) -> Envelope:
    """Handle MCP tools/list request.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with list of tools.
    """
    try:
        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={"tools": _example_tools},
        )
    except Exception as e:
        logger.exception(f"Error in mcp_tools_list_handler: {e}")
        return Envelope.error(500, "Internal server error")


def mcp_tools_call_handler(envelope: Envelope) -> Envelope:
    """Handle MCP tools/call request.

    Args:
        envelope: Request envelope with body containing tool name and arguments.

    Returns:
        Response envelope with tool result.
    """
    try:
        body = envelope.body or {}
        tool_name = body.get("name")
        arguments = body.get("arguments", {})

        service = get_example3_service()

        if tool_name == "get_example":
            item_id = arguments.get("id")
            if not item_id:
                return Envelope.error(400, "id is required")
            entity = service.get_example(item_id)
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"content": [{"type": "text", "text": json.dumps(entity.to_dict())}]},
            )

        elif tool_name == "create_example":
            name = arguments.get("name")
            if not name:
                return Envelope.error(400, "name is required")
            entity = service.create_example(
                name=name,
                description=arguments.get("description"),
                data=arguments.get("data"),
                entity_id=arguments.get("id"),
            )
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"content": [{"type": "text", "text": json.dumps(entity.to_dict())}]},
            )

        elif tool_name == "list_examples":
            entities = service.list_examples()
            items = [entity.to_dict() for entity in entities]
            return Envelope(
                path=envelope.path,
                method=envelope.method,
                status_code=200,
                data={"content": [{"type": "text", "text": json.dumps({"items": items, "count": len(items)})}]},
            )

        elif tool_name == "call_example1":
            from hexswitch.ports import get_port_registry
            path = arguments.get("path", "/api/examples")
            method = arguments.get("method", "GET")
            data = arguments.get("data", {})
            http_envelope = Envelope(path=path, method=method, body=data)
            registry = get_port_registry()
            results = registry.route("example1_http_port", http_envelope)
            if results:
                return Envelope(
                    path=envelope.path,
                    method=envelope.method,
                    status_code=200,
                    data={"content": [{"type": "text", "text": json.dumps(results[0].data)}]},
                )
            return Envelope.error(500, "No response from example1")

        elif tool_name == "call_example2":
            from hexswitch.ports import get_port_registry
            method = arguments.get("method", "ListExamples")
            data = arguments.get("data", {})
            grpc_envelope = Envelope(path=f"/{method}", method="POST", body=data)
            registry = get_port_registry()
            results = registry.route("example2_grpc_port", grpc_envelope)
            if results:
                return Envelope(
                    path=envelope.path,
                    method=envelope.method,
                    status_code=200,
                    data={"content": [{"type": "text", "text": json.dumps(results[0].data)}]},
                )
            return Envelope.error(500, "No response from example2")

        else:
            return Envelope.error(400, f"Unknown tool: {tool_name}")

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return Envelope.error(400, str(e))
    except Exception as e:
        logger.exception(f"Error in mcp_tools_call_handler: {e}")
        return Envelope.error(500, "Internal server error")


def mcp_resources_list_handler(envelope: Envelope) -> Envelope:
    """Handle MCP resources/list request.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with list of resources.
    """
    try:
        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={"resources": _example_resources},
        )
    except Exception as e:
        logger.exception(f"Error in mcp_resources_list_handler: {e}")
        return Envelope.error(500, "Internal server error")


def mcp_resources_read_handler(envelope: Envelope) -> Envelope:
    """Handle MCP resources/read request.

    Args:
        envelope: Request envelope with body containing URI.

    Returns:
        Response envelope with resource data.
    """
    try:
        body = envelope.body or {}
        uri = body.get("uri", "")

        if uri == "example://items":
            service = get_example3_service()
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
                            "text": json.dumps({"items": items, "count": len(items)}, indent=2),
                        }
                    ]
                },
            )
        else:
            return Envelope.error(404, f"Resource not found: {uri}")

    except Exception as e:
        logger.exception(f"Error in mcp_resources_read_handler: {e}")
        return Envelope.error(500, "Internal server error")

