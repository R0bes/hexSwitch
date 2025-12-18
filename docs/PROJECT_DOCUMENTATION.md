---
layout: default
title: HexSwitch - Vollständige Projektdokumentation
---

<div class="hexswitch-header">
  <div class="hexswitch-header-content">
    <div class="hexswitch-logo-container">
      <img src="{{ '/assets/logo.png' | relative_url }}" alt="HexSwitch Logo" class="hexswitch-logo" />
      <div class="hexswitch-title-group">
        <h1 class="hexswitch-title">HexSwitch</h1>
        <p class="hexswitch-tagline">Vollständige Projektdokumentation</p>
      </div>
    </div>
  </div>
</div>

<div class="hexswitch-content">

# HexSwitch - Vollständige Projektdokumentation

**Version:** 0.1.0  
**Letzte Aktualisierung:** 2025-12-13  
**Status:** <span class="badge badge-warning">Alpha</span>

---

## 📋 Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [Installation & Setup](#installation--setup)
3. [Architektur](#architektur)
4. [Komponenten](#komponenten)
5. [Adapter-System](#adapter-system)
6. [Konfiguration](#konfiguration)
7. [CLI & Commands](#cli--commands)
8. [Entwicklung](#entwicklung)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [API-Referenz](#api-referenz)
12. [Beispiele](#beispiele)

---

## Projektübersicht

HexSwitch ist ein **konfigurationsgetriebenes Runtime-System** für Microservices, das auf dem **Hexagonal Architecture Pattern** (Ports & Adapters) basiert. Es bietet eine flexible, protokoll-agnostische Möglichkeit, Business-Logik mit verschiedenen Kommunikationsprotokollen zu verbinden.

### Hauptmerkmale

- ✅ **Protokoll-agnostisch**: Business-Logik ist vollständig unabhängig von Kommunikationsprotokollen
- ✅ **Konfigurationsgetrieben**: Adapter werden über YAML-Konfigurationsdateien verbunden
- ✅ **Trennung der Belange**: Klare Grenzen zwischen Adaptern, Ports und Business-Logik
- ✅ **Erweiterbar**: Einfaches Hinzufügen neuer Adapter ohne Änderung der Kern-Logik
- ✅ **Observability**: Integrierte Metriken, Tracing und Logging
- ✅ **Multi-Protokoll**: Unterstützung für HTTP, WebSocket, gRPC und MCP

### Technologie-Stack

- **Sprache**: Python 3.12+
- **Konfiguration**: YAML mit Jinja2-Template-Support
- **Protokolle**: HTTP, WebSocket, gRPC, MCP (Model Context Protocol)
- **Testing**: pytest mit umfassender Coverage
- **Linting**: ruff, mypy
- **Deployment**: Docker

---

## Installation & Setup

### Voraussetzungen

- Python 3.12 oder höher
- pip (Python Package Manager)
- (Optional) Docker für Container-Deployment

### Installation

```bash
# Repository klonen
git clone <repository-url>
cd hexSwitch

# Virtual Environment erstellen
python -m venv .venv

# Virtual Environment aktivieren
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Projekt installieren (mit Dev-Dependencies)
pip install -e ".[dev]"
```

### Verifikation

```bash
# Version prüfen
hexswitch version

# Konfiguration validieren
hexswitch validate
```

---

## Architektur

HexSwitch implementiert das **Hexagonal Architecture Pattern**, das Business-Logik von externen Anliegen durch wohldefinierte Interfaces (Ports) und Implementierungen (Adapters) trennt.

### Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────┐
│                    HexSwitch Runtime                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Inbound    │         │   Outbound    │                 │
│  │   Adapters   │         │   Adapters    │                 │
│  │              │         │               │                 │
│  │  - HTTP      │         │  - HTTP Client│                 │
│  │  - WebSocket │         │  - gRPC Client│                │
│  │  - gRPC      │         │  - WS Client  │                 │
│  │  - MCP       │         │  - MCP Client │                 │
│  └──────┬───────┘         └───────┬───────┘                 │
│         │                         │                          │
│         │  Envelope               │  Envelope                │
│         │  (Protocol-agnostic)    │  (Protocol-agnostic)    │
│         │                         │                          │
│         └───────────┬─────────────┘                         │
│                     │                                        │
│              ┌──────▼──────┐                                │
│              │    Ports     │                                │
│              │  (Handlers)  │                                │
│              └──────┬───────┘                                │
│                     │                                        │
│              ┌──────▼──────┐                                │
│              │   Business   │                                │
│              │    Logic     │                                │
│              │  (Services)  │                                │
│              └──────────────┘                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Datenfluss

1. **Inbound Request**: Externes System sendet Request über Protokoll (HTTP/WS/gRPC)
2. **Adapter Conversion**: Adapter konvertiert Request zu Envelope-Format
3. **Port Handler**: Handler verarbeitet Envelope (protocol-agnostic)
4. **Business Logic**: Service führt Business-Logik aus
5. **Port Response**: Handler erstellt Response-Envelope
6. **Adapter Conversion**: Adapter konvertiert Envelope zurück zu Protokoll-Format
7. **Outbound Response**: Response wird an externes System gesendet

---

## Komponenten

### Core-Module

#### 1. **Runtime** (`src/hexswitch/runtime.py`)
- Orchestriert Adapter-Lifecycle
- Verwaltet Execution Plan
- Startet/Stoppt Adapter basierend auf Konfiguration

#### 2. **Config** (`src/hexswitch/config.py`)
- Lädt und validiert YAML-Konfigurationen
- Unterstützt Jinja2-Templates
- Umfassende Validierung aller Konfigurationsoptionen

#### 3. **Handlers** (`src/hexswitch/handlers/`)
- Port-Registry für Handler-Registrierung
- Handler-Loader für dynamisches Laden
- Decorator-System für Port-Registrierung (`@port`)

#### 4. **Envelope** (`src/hexswitch/envelope/`)
- Protocol-agnostic Datenformat
- Konvertierung zwischen Protokollen und Business-Logik
- Standardisiertes Request/Response-Format

#### 5. **Observability** (`src/hexswitch/observability/`)
- Metriken-Sammlung
- Distributed Tracing
- Logging-Integration

### Business Logic (`src/hexswitch/core/`)

Beispiel-Implementierung eines E-Commerce Order-Service:

- **Domain Models**: `domain/order.py`, `domain/product.py`
- **Services**: `services/order_service.py`, `services/product_service.py`
- **Repositories**: `repositories/order_repository.py`
- **Handlers**: `handlers/` - Port-Implementierungen

---

## Adapter-System

### Inbound Adapters (Server)

Empfangen Requests von externen Systemen:

#### 1. **HTTP Adapter** (`adapters/http/`)
- RESTful API-Support
- Route-basierte Handler-Zuordnung
- Query-Parameter und Path-Parameter Support

**Konfiguration:**
```yaml
inbound:
  http:
    enabled: true
    base_path: /api
    routes:
      - path: /orders
        method: GET
        handler: hexswitch.core.handlers:list_orders_handler
```

#### 2. **WebSocket Adapter** (`adapters/websocket/`)
- Bidirektionale Kommunikation
- Real-time Updates
- Path-basierte Handler-Zuordnung

**Konfiguration:**
```yaml
inbound:
  websocket:
    enabled: true
    path: /ws
    handlers:
      - path: /orders/updates
        handler: hexswitch.core.handlers:subscribe_order_updates
```

#### 3. **gRPC Adapter** (`adapters/grpc/`)
- High-Performance RPC
- Protocol Buffers
- Service-basierte Handler-Zuordnung

#### 4. **MCP Adapter** (`adapters/mcp/`)
- Model Context Protocol Support
- AI/LLM-Integration

### Outbound Adapters (Client)

Senden Requests an externe Systeme:

#### 1. **HTTP Client** (`adapters/http/`)
- RESTful API-Calls
- Request/Response-Handling

#### 2. **WebSocket Client** (`adapters/websocket/`)
- Bidirektionale Client-Kommunikation

#### 3. **gRPC Client** (`adapters/grpc/`)
- gRPC Service-Calls

#### 4. **MCP Client** (`adapters/mcp/`)
- MCP-Protokoll-Client

---

## Konfiguration

### Konfigurationsdatei-Struktur

```yaml
service:
  name: my-service
  version: "1.0.0"
  runtime: python

inbound:
  http:
    enabled: true
    base_path: /api
    routes:
      - path: /hello
        method: GET
        handler: my_module:hello_handler

outbound:
  http_client:
    enabled: true
    base_url: https://api.example.com
```

### Jinja2-Template-Support

Konfigurationen können als Jinja2-Templates erstellt werden (`.j2` Extension):

```yaml
service:
  name: {{ SERVICE_NAME | default("my-service") }}

inbound:
  http:
    enabled: {{ HTTP_ENABLED | default(true) }}
    port: {{ HTTP_PORT | default(8080) }}
```

### Konfigurationsvalidierung

```bash
# Validierung
hexswitch validate

# Mit spezifischer Config-Datei
hexswitch validate --config my-config.yaml
```

---

## CLI & Commands

### Verfügbare Commands

#### `hexswitch version`
Zeigt Version und Projektinformationen.

```bash
hexswitch version
```

#### `hexswitch init`
Erstellt eine Beispiel-Konfigurationsdatei.

```bash
hexswitch init
hexswitch init --template ecommerce
hexswitch init --template http-only
```

#### `hexswitch validate`
Validiert die Konfigurationsdatei.

```bash
hexswitch validate
hexswitch validate --config my-config.yaml
```

#### `hexswitch run`
Startet den Runtime (zukünftig).

```bash
hexswitch run
hexswitch run --dry-run  # Zeigt Execution Plan ohne Start
```


---

## Entwicklung

### Projektstruktur

```
hexSwitch/
├── src/
│   └── hexswitch/          # Haupt-Package
│       ├── adapters/       # Adapter-Implementierungen
│       ├── core/          # Business-Logik (Beispiel)
│       ├── handlers/      # Handler-System
│       ├── observability/ # Observability-Tools
│       └── templates/     # Template-Engine
├── tests/                  # Test-Suite
│   ├── unit/              # Unit-Tests
│   └── integration/       # Integration-Tests
├── docs/                   # Dokumentation
├── templates/              # Konfigurations-Templates
└── pyproject.toml         # Projekt-Konfiguration
```

### Entwicklungssetup

1. **Repository klonen**
2. **Virtual Environment erstellen und aktivieren**
3. **Dependencies installieren**: `pip install -e ".[dev]"`
4. **Tests ausführen**: `pytest`
5. **Linting**: `ruff check .`
6. **Type Checking**: `mypy src/`

### Code-Standards

- **Linting**: ruff (E, W, F, I, B, C4)
- **Formatting**: ruff format
- **Type Checking**: mypy
- **Line Length**: 100 Zeichen
- **Python Version**: 3.12+

### Branch-Strategie

- `feat/...` - Neue Features
- `fix/...` - Bug-Fixes
- `chore/...` - Wartungsaufgaben
- `docs/...` - Dokumentation
- `refactor/...` - Refactoring

Siehe [CONTRIBUTING.md](../CONTRIBUTING.md) für Details.

---

## Testing

### Test-Struktur

```
tests/
├── unit/              # Unit-Tests
│   ├── adapters/      # Adapter-Tests
│   ├── handlers/      # Handler-Tests
│   ├── config/        # Config-Tests
│   └── runtime/       # Runtime-Tests
└── integration/       # Integration-Tests
    └── test_e2e_*.py  # End-to-End-Tests
```

### Tests ausführen

```bash
# Alle Tests
pytest

# Nur Unit-Tests
pytest tests/unit/

# Nur Integration-Tests
pytest tests/integration/

# Mit Coverage
pytest --cov=src/hexswitch --cov-report=html

# Spezifische Test-Datei
pytest tests/unit/adapters/test_http_adapter.py
```

### Test-Marker

- `@pytest.mark.unit` - Unit-Tests
- `@pytest.mark.integration` - Integration-Tests
- `@pytest.mark.docker` - Docker-Tests
- `@pytest.mark.fast` - Schnelle Tests (< 1s)
- `@pytest.mark.slow` - Langsame Tests (< 60s)

### Coverage

Aktueller Coverage-Threshold: **50%** (ziel: schrittweise Erhöhung)

---

## Deployment

### Docker

#### Build

```bash
docker build -t hexswitch:latest .
```

#### Run

```bash
docker run --rm hexswitch:latest hexswitch version
```

### Dockerfile-Struktur

Multi-Stage Build:
1. **Builder Stage**: Installiert Dependencies
2. **Runtime Stage**: Minimale Runtime-Umgebung

### Konfiguration für Production

1. Erstelle Production-Config (`hex-config.prod.yaml`)
2. Setze Environment-Variablen
3. Deploy Container mit Config-Mount

```bash
docker run -v /path/to/config:/app/config hexswitch:latest \
  hexswitch run --config /app/config/hex-config.prod.yaml
```

---

## API-Referenz

### Handler-Registrierung

```python
from hexswitch.handlers.decorators import port

@port("create_order")
def create_order_handler(envelope):
    """Handler für Order-Erstellung."""
    # Business-Logik
    return response_envelope
```

### Adapter-Interfaces

#### InboundInterface

```python
class InboundInterface(ABC):
    def start(self) -> None:
        """Startet den Adapter."""
    
    def stop(self) -> None:
        """Stoppt den Adapter."""
    
    def to_envelope(self, *args, **kwargs) -> Envelope:
        """Konvertiert Request zu Envelope."""
    
    def from_envelope(self, envelope: Envelope) -> Any:
        """Konvertiert Envelope zu Response."""
```

#### OutboundInterface

```python
class OutboundInterface(ABC):
    def call(self, envelope: Envelope) -> Envelope:
        """Sendet Request und gibt Response zurück."""
```

### Envelope-Format

```python
class Envelope:
    port: str              # Port-Name
    data: dict[str, Any]   # Request/Response-Daten
    metadata: dict        # Zusätzliche Metadaten
```

---

## Beispiele

### Beispiel 1: HTTP-Only Service

Siehe `templates/hex-config.http-only.yaml.j2`

### Beispiel 2: E-Commerce Service

Siehe `templates/hex-config.ecommerce.yaml.j2`

### Beispiel 3: MCP-Integration

Siehe `templates/hex-config.with-mcp.yaml.j2`

### Beispiel 4: Custom Handler

```python
# my_module.py
from hexswitch.handlers.decorators import port
from hexswitch.envelope import Envelope

@port("hello")
def hello_handler(envelope: Envelope) -> Envelope:
    name = envelope.data.get("name", "World")
    return Envelope(
        port="hello",
        data={"message": f"Hello, {name}!"},
        metadata={}
    )
```

---

## Weitere Ressourcen

- [Architecture Overview](architecture_overview.md) - Detaillierte Architektur-Beschreibung
- [Contributing Guidelines](../CONTRIBUTING.md) - Wie man beiträgt
- [CLI Specification](../hexswitch_shell_spec.md) - CLI-Dokumentation
- [Core README](../src/hexswitch/core/README.md) - Business-Logik-Beispiele

---

## Support & Kontakt

- **Issues**: GitHub Issues
- **Contributing**: Siehe [CONTRIBUTING.md](../CONTRIBUTING.md)
- **License**: (siehe LICENSE-Datei)

---

**Letzte Aktualisierung:** 2025-12-13  
**Version:** 0.1.0  
**Status:** <span class="badge badge-warning">Alpha</span>

</div>

<div class="hexswitch-footer">
  <p>© 2025 HexSwitch | MIT License</p>
</div>
