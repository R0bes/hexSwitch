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

**Einfache Verwendung mit HexSwitchService (Empfohlen):**

```python
from hexswitch.service import HexSwitchService

class MyService(HexSwitchService):
    def on_ready(self):
        print("Service is ready!")

if __name__ == "__main__":
    service = MyService()  # Lädt automatisch hex-config.toml
    service.run()  # Läuft bis unterbrochen
```

**Environment-Variable-Overrides:**

```bash
# Setzen von Umgebungsvariablen
export HEX_SERVICE_NAME="my-service"
export HEX_INBOUND_HTTP_PORT="9000"
export HEX_LOGGING_LEVEL="DEBUG"

# Service starten - Variablen überschreiben automatisch Config-Werte
python my_service.py
```

**Erweiterte Verwendung mit Runtime:**

```python
from hexswitch.runtime import Runtime
from hexswitch.shared.config import load_config

config = load_config("hex-config.toml")
runtime = Runtime(config)
runtime.start()
```

## Features

- ✅ **Simple Entry Point**: `HexSwitchService` class for easy framework usage
- ✅ **Environment Variable Overrides**: Automatic config overrides via `HEX_` prefixed environment variables
- ✅ **Protocol-agnostic**: Business logic is completely independent of communication protocols
- ✅ **Configuration-driven**: Adapters are wired together via TOML configuration files
- ✅ **Separation of concerns**: Clear boundaries between adapters, ports, and business logic
- ✅ **Extensible**: Easy to add new adapters without changing core logic
- ✅ **Observability**: Integrated metrics, tracing, and logging
- ✅ **Multi-protocol**: Support for HTTP, WebSocket, gRPC, and MCP
- ✅ **Lifecycle Management**: Automatic runtime integration with hooks for customization

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
