---
layout: default
title: HexSwitch Documentation
---

<div align="center">
  <img src="../assets/logo.png" alt="HexSwitch Logo" width="200" />
</div>

# HexSwitch

**Hexagonal runtime switchboard for config-driven microservices.**

HexSwitch is a runtime system designed to orchestrate microservices using a hexagonal architecture pattern. It provides a configuration-driven approach to wiring together inbound and outbound adapters, enabling flexible and maintainable service communication.

## Quick Start

### Installation

```bash
pip install hexswitch
```

### Basic Usage

```python
from hexswitch.runtime import Runtime

config = {
    "service": {"name": "my-service"},
    "adapters": {
        "inbound": [
            {
                "name": "http",
                "enabled": True,
                "port": 8000,
                "routes": [
                    {
                        "path": "/hello",
                        "method": "GET",
                        "handler": "my_module:handler"
                    }
                ]
            }
        ]
    }
}

runtime = Runtime(config)
runtime.start()
```

## Features

- ✅ **Protocol-agnostic**: Business logic is completely independent of communication protocols
- ✅ **Configuration-driven**: Adapters are wired together via YAML configuration files
- ✅ **Separation of concerns**: Clear boundaries between adapters, ports, and business logic
- ✅ **Extensible**: Easy to add new adapters without changing core logic
- ✅ **Observability**: Integrated metrics, tracing, and logging
- ✅ **Multi-protocol**: Support for HTTP, WebSocket, gRPC, and MCP

## Documentation

- [Architecture Overview](architecture_overview.md)
- [Development Guide](development_guide.md)
- [PyPI Upload Guide](PYPI_UPLOAD.md)
- [Project Documentation](PROJECT_DOCUMENTATION.md)

## Links

- **GitHub Repository**: [https://github.com/R0bes/hexSwitch](https://github.com/R0bes/hexSwitch)
- **PyPI Package**: [https://pypi.org/project/hexswitch/](https://pypi.org/project/hexswitch/)
- **Issues**: [https://github.com/R0bes/hexSwitch/issues](https://github.com/R0bes/hexSwitch/issues)

## License

MIT License - see [LICENSE](../LICENSE) file for details.

