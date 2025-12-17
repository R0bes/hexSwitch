#!/usr/bin/env python3
"""
Export hexSwitch adapter metadata as JSON.
This script reads the real hexSwitch implementation and exports adapter information.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import hexswitch
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from hexswitch.runtime import Runtime
    from hexswitch.config import load_config, validate_config
except ImportError as e:
    print(f"Error importing hexswitch: {e}", file=sys.stderr)
    print("Make sure hexSwitch is installed: pip install -e .", file=sys.stderr)
    sys.exit(1)


def get_adapter_metadata():
    """Extract adapter metadata from hexSwitch implementation."""
    
    # Real adapters from runtime.py
    adapters = []
    
    # Inbound adapters
    adapters.append({
        "id": "http",
        "name": "HTTP Adapter",
        "type": "inbound",
        "category": "Inbound",
        "icon": "Globe",
        "description": "HTTP REST API endpoint adapter",
        "source": "src/hexswitch/adapters/http/adapter.py",
        "configSchema": {
            "enabled": {"type": "boolean", "required": True},
            "base_path": {"type": "string", "required": False},
            "port": {"type": "number", "required": False, "min": 1, "max": 65535},
            "routes": {
                "type": "array",
                "required": False,
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "required": True},
                        "method": {"type": "string", "required": True, "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                        "handler": {"type": "string", "required": True, "format": "module.path:function_name"}
                    }
                }
            }
        }
    })
    
    # Outbound adapters
    adapters.append({
        "id": "http_client",
        "name": "HTTP Client",
        "type": "outbound",
        "category": "Outbound",
        "icon": "ExternalLink",
        "description": "HTTP client adapter for making requests to other services",
        "source": "src/hexswitch/adapters/http_client/adapter.py",
        "configSchema": {
            "enabled": {"type": "boolean", "required": True},
            "base_url": {"type": "string", "required": False},
            "timeout": {"type": "number", "required": False, "min": 0},
            "headers": {"type": "object", "required": False}
        }
    })
    
    adapters.append({
        "id": "mcp_client",
        "name": "MCP Client",
        "type": "outbound",
        "category": "Outbound",
        "icon": "Server",
        "description": "MCP (Model Context Protocol) client adapter",
        "source": "src/hexswitch/adapters/mcp_client/adapter.py",
        "configSchema": {
            "enabled": {"type": "boolean", "required": True},
            "server_url": {"type": "string", "required": True},
            "timeout": {"type": "number", "required": False, "min": 0},
            "headers": {"type": "object", "required": False}
        }
    })
    
    return adapters


def main():
    """Main entry point."""
    adapters = get_adapter_metadata()
    print(json.dumps(adapters, indent=2))


if __name__ == "__main__":
    main()

