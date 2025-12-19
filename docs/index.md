---
layout: default
title: HexSwitch Documentation
---

<div class="hexswitch-header">
  <div class="hexswitch-header-content">
    <div class="hexswitch-logo-container">
      <img src="{{ '/assets/logo.png' | relative_url }}" alt="HexSwitch Logo" class="hexswitch-logo" />
      <div class="hexswitch-title-group">
        <h1 class="hexswitch-title">HexSwitch</h1>
        <p class="hexswitch-tagline">Hexagonal runtime switchboard for config-driven microservices</p>
      </div>
    </div>
  </div>
</div>

<div class="hexswitch-content">

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
    "inbound": [
        {
            "name": "http",
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/hello",
                    "method": "GET",
                    "port": "hello_handler"
                }
            ]
        }
    ]
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
- **Website**: [https://r0bes.github.io/hexSwitch/](https://r0bes.github.io/hexSwitch/)
- **Issues**: [https://github.com/R0bes/hexSwitch/issues](https://github.com/R0bes/hexSwitch/issues)

## License

MIT License - see [LICENSE](../LICENSE) file for details.

</div>

<div class="hexswitch-footer">
  <p>© 2025 HexSwitch | MIT License</p>
</div>
