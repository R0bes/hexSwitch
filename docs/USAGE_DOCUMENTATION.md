# HexSwitch - Vollständige Nutzungsdokumentation

**Version:** 0.1.2  
**Letzte Aktualisierung:** 2025-12-13  
**Level:** Ultimate++

---

## Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Installation](#installation)
3. [Schnellstart](#schnellstart)
4. [CLI-Befehle](#cli-befehle)
5. [Konfiguration](#konfiguration)
6. [Runtime-Verwendung](#runtime-verwendung)
7. [Adapter-Konfiguration](#adapter-konfiguration)
8. [Handler-Entwicklung](#handler-entwicklung)
9. [Beispiele](#beispiele)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Einführung

HexSwitch ist ein Runtime-System zur Orchestrierung von Microservices basierend auf dem hexagonalen Architekturmuster. Es ermöglicht eine konfigurationsgetriebene Verbindung von Inbound- und Outbound-Adaptern für flexible und wartbare Service-Kommunikation.

### Kernkonzepte

- **Hexagonale Architektur**: Trennung von Business-Logik und Kommunikationsprotokollen
- **Konfigurationsgetrieben**: Adapter werden über TOML-Konfigurationsdateien verbunden
- **Protokoll-agnostisch**: Business-Logik ist unabhängig von Kommunikationsprotokollen
- **Erweiterbar**: Einfaches Hinzufügen neuer Adapter ohne Änderung der Kernlogik

### Unterstützte Protokolle

**Inbound (Server):**
- HTTP/REST
- WebSocket
- gRPC
- MCP (Model Context Protocol)

**Outbound (Client):**
- HTTP Client
- WebSocket Client
- gRPC Client
- MCP Client
- NATS

---

## Installation

### Voraussetzungen

- Python 3.12 oder höher
- pip (Python Package Manager)

### Installation aus PyPI

```bash
pip install hexswitch
```

### Installation im Entwicklungsmodus

```bash
# Repository klonen
git clone https://github.com/R0bes/hexSwitch.git
cd hexSwitch

# Im Entwicklungsmodus installieren (inkl. Dev-Dependencies)
pip install -e ".[dev]"
```

### Docker-Installation

```bash
# Docker Image bauen
docker build -t hexswitch:latest .

# Docker Image testen
docker run --rm hexswitch:latest hexswitch version
```

---

## Schnellstart

### 1. Beispiel-Konfiguration erstellen

```bash
hexswitch init
```

Dies erstellt eine `hex-config.toml` Datei mit einer Beispiel-Konfiguration.

### 2. Konfiguration validieren

```bash
hexswitch validate
```

### 3. Ausführungsplan anzeigen (Dry-Run)

```bash
hexswitch run --dry-run
```

### 4. Runtime starten

```bash
hexswitch run
```

---

## CLI-Befehle

### Übersicht

HexSwitch bietet eine Command-Line-Interface (CLI) mit folgenden Befehlen:

```bash
hexswitch [OPTIONS] COMMAND [ARGS]
```

### Globale Optionen

- `--log-level {DEBUG,INFO,WARNING,ERROR}`: Logging-Level setzen (Standard: INFO)
- `--config PATH`: Pfad zur Konfigurationsdatei (Standard: `hex-config.toml`)
- `--version`: Version anzeigen

### Befehle

#### `version`

Zeigt die Version und den Tagline an.

```bash
hexswitch version
# oder
hexswitch --version  # Rückwärtskompatibel
```

**Ausgabe:**
```
HexSwitch 0.1.2
Hexagonal runtime switchboard for config-driven microservices
```

#### `init`

Erstellt eine Beispiel-Konfigurationsdatei.

```bash
hexswitch init
```

**Optionen:**
- `--force`: Überschreibt vorhandene Konfigurationsdatei

**Beispiel:**
```bash
hexswitch init --force
```

#### `validate`

Validiert die Konfigurationsdatei.

```bash
hexswitch validate
```

**Optionen:**
- `--config PATH`: Pfad zur zu validierenden Konfigurationsdatei

**Beispiel:**
```bash
hexswitch validate --config path/to/config.toml
```

**Ausgabe bei Erfolg:**
```
Configuration is valid: hex-config.toml
```

**Ausgabe bei Fehler:**
```
Validation failed: <Fehlerbeschreibung>
```

#### `run`

Startet die Runtime.

```bash
hexswitch run
```

**Optionen:**
- `--dry-run`: Zeigt den Ausführungsplan an, ohne die Runtime zu starten

**Beispiel:**
```bash
# Dry-Run Modus
hexswitch run --dry-run

# Runtime starten
hexswitch run
```

**Dry-Run Ausgabe:**
```
Execution plan for service 'my-service':
  Inbound adapters: 1
    - http
  Outbound adapters: 2
    - http_client
    - grpc_client
Ready to start runtime
```

### Python-Modul-Verwendung

Alternativ kann HexSwitch auch als Python-Modul ausgeführt werden:

```bash
python -m hexswitch.app version
python -m hexswitch.app init
python -m hexswitch.app validate
python -m hexswitch.app run --dry-run
python -m hexswitch.app run
```

---

## Konfiguration

### Konfigurationsdatei-Struktur

Die Konfigurationsdatei (`hex-config.toml`) folgt einer klaren Struktur:

```toml
service:
  name: my-service
  runtime: python
  version: "1.0.0"  # Optional
  gui:  # Optional
    enabled: false
    port: 8080

inbound:
  <adapter_name>:
    enabled: true
    # Adapter-spezifische Konfiguration

outbound:
  <adapter_name>:
    enabled: true
    # Adapter-spezifische Konfiguration

ports:  # Optional
  <port_name>:
    policies:
      retry: {...}
      timeout: {...}
      backpressure: {...}

logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
```

### Service-Konfiguration

```toml
[service]
name = "my-service"          # Service-Name (erforderlich)
runtime = "python"           # Runtime-Typ (erforderlich)
version = "1.0.0"            # Service-Version (optional)

[service.gui]                # GUI-Server (optional)
enabled = false
port = 8080
```

### Jinja2-Template-Support

Konfigurationen können als Jinja2-Templates erstellt werden (Dateiendung `.j2`):

```toml
# hex-config.toml.j2
[service]
name = "{{ env.SERVICE_NAME | default('my-service') }}"
runtime = "python"

[inbound.http]
enabled = {{ env.ENABLE_HTTP | default(true) }}
port = {{ env.HTTP_PORT | default(8000) | int }}
base_path = "{{ env.BASE_PATH | default('/api') }}"
```

**Verfügbare Template-Variablen:**
- `env.VAR_NAME`: Zugriff auf Umgebungsvariablen
- Jinja2-Filter: `default()`, `int()`, `bool()`, `str()`, etc.

**Verwendung:**
```bash
# Umgebungsvariablen setzen
export SERVICE_NAME=production-service
export HTTP_PORT=9000

# Konfiguration laden (automatische Template-Renderung)
hexswitch run
```

### Environment-Variable-Overrides (HEX_ Präfix)

HexSwitch unterstützt automatisches Überschreiben von Konfigurationswerten durch Umgebungsvariablen mit dem Präfix `HEX_`. Diese Variablen werden automatisch geladen und überschreiben die Werte aus der Config-Datei.

#### Funktionsweise

Umgebungsvariablen mit `HEX_` Präfix werden in verschachtelte Config-Pfade konvertiert:

- `HEX_SERVICE_NAME` → `service.name`
- `HEX_INBOUND_HTTP_PORT` → `inbound.http.port`
- `HEX_INBOUND_HTTP_BASE_PATH` → `inbound.http.base_path`
- `HEX_LOGGING_LEVEL` → `logging.level`

#### Automatische Typkonvertierung

Die Werte werden automatisch in die entsprechenden Datentypen konvertiert:

- **Boolean**: `"true"` / `"false"` → `True` / `False`
- **Integer**: `"8080"` → `8080`
- **Float**: `"30.5"` → `30.5`
- **String**: Bleibt als String

#### Beispiele

**Basis-Konfiguration (`hex-config.toml`):**
```toml
[service]
name = "my-service"
version = "1.0.0"

[inbound.http]
enabled = true
port = 8000
base_path = "/api"

[logging]
level = "INFO"
```

**Umgebungsvariablen setzen:**
```bash
export HEX_SERVICE_NAME="production-service"
export HEX_INBOUND_HTTP_PORT="9000"
export HEX_INBOUND_HTTP_BASE_PATH="/api/v2"
export HEX_LOGGING_LEVEL="DEBUG"
```

**Ergebnis:**
Die Config wird automatisch überschrieben:
- `service.name` = `"production-service"` (überschrieben)
- `service.version` = `"1.0.0"` (unverändert)
- `inbound.http.port` = `9000` (überschrieben, als Integer)
- `inbound.http.base_path` = `"/api/v2"` (überschrieben)
- `inbound.http.enabled` = `true` (unverändert)
- `logging.level` = `"DEBUG"` (überschrieben)
```

#### Verwendung mit HexSwitchService

```python
from hexswitch.service import HexSwitchService

class MyService(HexSwitchService):
    def on_ready(self):
        print("Service ist bereit!")

if __name__ == "__main__":
    # Environment-Variablen werden automatisch geladen
    service = MyService()
    service.run()
```

#### Unterstützte Feldnamen mit Unterstrichen

Folgende Feldnamen mit Unterstrichen werden automatisch erkannt:
- `base_path`
- `server_url`
- `method_name`
- `enable_default`
- `reconnect_interval`

**Beispiel:**
```bash
# Diese Variable wird korrekt zu inbound.http.base_path konvertiert
export HEX_INBOUND_HTTP_BASE_PATH="/api/v2"
```

#### Vorteile gegenüber Jinja2-Templates

- **Einfacher**: Keine Template-Dateien erforderlich
- **Dynamisch**: Werte können zur Laufzeit überschrieben werden
- **Docker-freundlich**: Perfekt für Container-Umgebungen
- **CI/CD-freundlich**: Einfache Integration in Deployment-Pipelines

#### Kombination mit Jinja2-Templates

Environment-Variable-Overrides haben **Vorrang** vor Template-Werten. Die Reihenfolge ist:

1. Config-Datei (Basis-Werte)
2. Jinja2-Template-Renderung (falls `.j2` Datei)
3. **Environment-Variable-Overrides (HEX_)** ← Höchste Priorität

### Konfigurationsvalidierung

Die Validierung prüft:
- Erforderliche Felder
- Datentypen
- Adapter-Konfigurationen
- Handler-Referenzen
- Port-Konfigurationen

---

## Runtime-Verwendung

### Einfache Verwendung mit HexSwitchService (Empfohlen)

Die einfachste Art, HexSwitch zu verwenden, ist die `HexSwitchService`-Klasse. Sie bietet automatische Runtime-Integration, Config-Loading und Lifecycle-Management.

#### Basis-Verwendung

```python
from hexswitch.service import HexSwitchService

class MyService(HexSwitchService):
    def on_start(self):
        """Wird vor Runtime-Start aufgerufen."""
        print("Service wird gestartet...")
    
    def on_ready(self):
        """Wird nach erfolgreichem Start aufgerufen."""
        print("Service ist bereit!")
    
    def on_stop(self):
        """Wird vor Runtime-Stop aufgerufen."""
        print("Service wird gestoppt...")

if __name__ == "__main__":
    # Service erstellen (lädt automatisch hex-config.toml)
    service = MyService()
    
    # Service starten und laufen lassen (bis unterbrochen)
    service.run()  # Behandelt KeyboardInterrupt automatisch
```

#### Config-Pfad angeben

```python
# Mit explizitem Config-Pfad
service = MyService(config_path="custom-config.toml")

# Mit Umgebungsvariable
# export HEXSWITCH_CONFIG_PATH=/path/to/config.toml
service = MyService()  # Lädt automatisch aus Umgebungsvariable

# Mit Config-Dictionary
config = {
    "service": {"name": "my-service"},
    "inbound": {...},
    "outbound": {...}
}
service = MyService(config=config)
```

#### Lifecycle-Hooks

```python
class MyService(HexSwitchService):
    def on_start(self):
        """Wird vor Runtime-Start aufgerufen.
        
        Hier können Sie benutzerdefinierte Initialisierung durchführen,
        z.B. Datenbankverbindungen, Cache-Setup, etc.
        """
        # Benutzerdefinierte Initialisierung
        self.setup_database()
        self.initialize_cache()
    
    def on_ready(self):
        """Wird nach erfolgreichem Start aufgerufen.
        
        Hier können Sie Aktionen durchführen, die ausgeführt werden sollen,
        nachdem alle Adapter gestartet sind.
        """
        print(f"Service '{self.get_runtime().config['service']['name']}' ist bereit!")
    
    def on_stop(self):
        """Wird vor Runtime-Stop aufgerufen.
        
        Hier können Sie Cleanup-Operationen durchführen.
        """
        self.cleanup_database()
        self.close_cache()
    
    def load_config(self):
        """Kann überschrieben werden für benutzerdefinierte Config-Logik.
        
        Returns:
            dict: Konfigurationsdictionary
        """
        # Beispiel: Config aus Datenbank laden
        # config = self.load_config_from_database()
        # return config
        
        # Standard-Implementierung aufrufen
        return super().load_config()
```

#### Runtime-Zugriff

```python
class MyService(HexSwitchService):
    def on_ready(self):
        # Zugriff auf Runtime für erweiterte Nutzung
        runtime = self.get_runtime()
        
        # Beispiel: Manuell Envelope senden
        from hexswitch.shared.envelope import Envelope
        envelope = Envelope(
            path="my_port",
            method="POST",
            body={"data": "test"}
        )
        response = runtime.deliver(envelope, "http_client")
        
        # Prüfen ob Service läuft
        if self.is_running():
            print("Service ist aktiv")
```

### Erweiterte Verwendung mit Runtime (Für fortgeschrittene Nutzung)

Für erweiterte Szenarien können Sie die `Runtime`-Klasse direkt verwenden:

```python
from hexswitch.runtime import Runtime
from hexswitch.shared.config import load_config

# Konfiguration laden
config = load_config("hex-config.toml")

# Runtime erstellen
runtime = Runtime(config)

# Runtime starten
runtime.start()

try:
    # Runtime läuft...
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    runtime.stop()
```

### Async-Verwendung

```python
import asyncio
from hexswitch.runtime import Runtime
from hexswitch.shared.config import load_config

async def main():
    config = load_config("hex-config.toml")
    runtime = Runtime(config)
    
    # Starten (async)
    await runtime._async_start()
    
    # Event Loop ausführen
    await runtime.run()
    
    # Stoppen (async)
    await runtime._async_stop()

asyncio.run(main())
```

### Runtime-Lebenszyklus

1. **Initialisierung**: Runtime wird mit Konfiguration erstellt
2. **Start**: Alle aktivierten Adapter werden gestartet
3. **Laufzeit**: Runtime verarbeitet eingehende Requests
4. **Shutdown**: Graceful Shutdown aller Adapter

### Graceful Shutdown

Die Runtime unterstützt graceful Shutdown. Bei Verwendung von `HexSwitchService` werden Signal-Handler automatisch registriert:

```python
# Mit HexSwitchService (automatisch)
service = MyService()
service.start()  # Signal-Handler werden automatisch registriert

# Mit Runtime direkt (manuell)
import signal

def signal_handler(signum, frame):
    runtime.request_shutdown()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

---

## Adapter-Konfiguration

### Inbound Adapter: HTTP

**Konfiguration:**
```toml
[inbound.http]
enabled = true
port = 8000
base_path = "/api"

[[inbound.http.routes]]
path = "/hello"
method = "GET"
handler = "my_module.handlers:hello_handler"

[[inbound.http.routes]]
path = "/users/:id"
method = "GET"
handler = "my_module.handlers:get_user_handler"

[[inbound.http.routes]]
path = "/users"
method = "POST"
handler = "my_module.handlers:create_user_handler"
```

**Features:**
- RESTful API-Support
- Route-basierte Handler-Zuordnung
- Path-Parameter (`:id`)
- Query-Parameter
- Request Body Parsing

**Handler-Format:**
```
<module_path>:<function_name>
```

**Beispiel:**
```python
# my_module/handlers.py
from hexswitch.shared.envelope import Envelope

def hello_handler(envelope: Envelope) -> Envelope:
    return Envelope(
        status=200,
        body={"message": "Hello, World!"}
    )
```

### Inbound Adapter: WebSocket

**Konfiguration:**
```toml
[inbound.websocket]
enabled = true
port = 8080
path = "/ws"

[[inbound.websocket.handlers]]
path = "/orders/updates"
handler = "my_module.handlers:subscribe_order_updates"
```

**Features:**
- Bidirektionale Kommunikation
- Real-time Updates
- Path-basierte Handler-Zuordnung

### Inbound Adapter: gRPC

**Konfiguration:**
```toml
[inbound.grpc]
enabled = true
port = 50051
service_name = "MyService"

[[inbound.grpc.handlers]]
method = "GetUser"
handler = "my_module.handlers:get_user_handler"
```

**Features:**
- High-Performance RPC
- Protocol Buffers
- Service-basierte Handler-Zuordnung

### Inbound Adapter: MCP

**Konfiguration:**
```toml
[inbound.mcp]
enabled = true
port = 8080

[[inbound.mcp.handlers]]
tool = "my_tool"
handler = "my_module.handlers:my_tool_handler"
```

**Features:**
- Model Context Protocol Support
- AI/LLM-Integration

### Outbound Adapter: HTTP Client

**Konfiguration:**
```toml
[outbound.http_client]
enabled = true
name = "external_api"
base_url = "https://api.example.com"
timeout = 30

[outbound.http_client.headers]
Content-Type = "application/json"
Authorization = "Bearer ${API_TOKEN}"

outbound.http_client.ports = ["external_api_port"]
```

**Features:**
- RESTful API-Calls
- Request/Response-Handling
- Timeout-Konfiguration
- Custom Headers

**Verwendung in Handlern:**
```python
from hexswitch.shared.envelope import Envelope

def my_handler(envelope: Envelope) -> Envelope:
    # Request an externen Service
    request_envelope = Envelope(
        path="external_api_port",
        method="GET",
        body={"query": "data"}
    )
    
    # Über Runtime senden
    response = runtime.deliver(request_envelope, "external_api")
    return response
```

### Outbound Adapter: gRPC Client

**Konfiguration:**
```toml
[outbound.grpc_client]
enabled = true
name = "example2_grpc"
server_url = "example2:50051"
timeout = 30
service_name = "ExampleService"
ports = ["example2_grpc_port"]
```

**Features:**
- gRPC Service-Calls
- Protocol Buffers
- Service-basierte Kommunikation

### Outbound Adapter: WebSocket Client

**Konfiguration:**
```toml
[outbound.websocket_client]
enabled = true
name = "example3_ws"
url = "ws://example3:8080"
timeout = 30
reconnect = true
reconnect_interval = 5
ports = ["example3_ws_port"]
```

**Features:**
- Bidirektionale Client-Kommunikation
- Auto-Reconnect
- Real-time Updates

### Outbound Adapter: MCP Client

**Konfiguration:**
```toml
[outbound.mcp_client]
enabled = true
name = "mcp_service"
server_url = "http://localhost:8080"
timeout = 30
ports = ["mcp_service_port"]
```

**Features:**
- MCP-Protokoll-Client
- AI/LLM-Integration

### Outbound Adapter: NATS

**Konfiguration:**
```toml
[outbound.nats]
enabled = true
name = "nats_client"
servers = ["nats://localhost:4222"]
timeout = 30
ports = ["nats_client_port"]
```

**Features:**
- Message Broker Integration
- Pub/Sub-Pattern
- High-Performance Messaging

---

## Handler-Entwicklung

### Handler-Signatur

Alle Handler müssen folgende Signatur haben:

```python
from hexswitch.shared.envelope import Envelope

def my_handler(envelope: Envelope) -> Envelope:
    # Handler-Logik
    return Envelope(status=200, body={"result": "success"})
```

### Envelope-Struktur

```python
class Envelope:
    status: int                    # HTTP-Status-Code
    body: dict | list | str | None # Response-Body
    headers: dict                  # Response-Headers
    metadata: dict                 # Zusätzliche Metadaten
    path: str                      # Request-Pfad
    method: str                    # HTTP-Methode
```

### Handler-Beispiele

#### Einfacher GET-Handler

```python
from hexswitch.shared.envelope import Envelope

def get_user_handler(envelope: Envelope) -> Envelope:
    user_id = envelope.metadata.get("path_params", {}).get("id")
    
    # Business-Logik
    user = get_user_from_database(user_id)
    
    if user:
        return Envelope(
            status=200,
            body={"user": user}
        )
    else:
        return Envelope(
            status=404,
            body={"error": "User not found"}
        )
```

#### POST-Handler mit Request-Body

```python
from hexswitch.shared.envelope import Envelope

def create_user_handler(envelope: Envelope) -> Envelope:
    user_data = envelope.body
    
    # Validierung
    if not user_data or "name" not in user_data:
        return Envelope(
            status=400,
            body={"error": "Name is required"}
        )
    
    # Business-Logik
    user = create_user_in_database(user_data)
    
    return Envelope(
        status=201,
        body={"user": user}
    )
```

#### Handler mit Outbound-Adapter

```python
from hexswitch.shared.envelope import Envelope

def call_external_service_handler(envelope: Envelope) -> Envelope:
    # Request an externen Service
    request_envelope = Envelope(
        path="external_api_port",
        method="POST",
        body=envelope.body,
        metadata={"port_name": "external_api_port"}
    )
    
    # Über Runtime senden
    response = runtime.deliver(request_envelope, "external_api")
    
    # Response verarbeiten
    if response.status == 200:
        return Envelope(
            status=200,
            body={"result": response.body}
        )
    else:
        return Envelope(
            status=502,
            body={"error": "External service error"}
        )
```

### Handler-Registrierung

Handler werden über die Konfiguration registriert:

```toml
[inbound.http]

[[inbound.http.routes]]
path = "/users/:id"
method = "GET"
handler = "my_module.handlers:get_user_handler"
```

**Handler-Format:**
```
<module_path>:<function_name>
```

**Beispiele:**
- `my_module.handlers:get_user_handler`
- `package.subpackage.handlers:create_order_handler`
- `adapters.http_handlers:hello`

### Handler-Loading

Handler werden dynamisch geladen:

```python
# Handler werden automatisch geladen
# Format: module_path:function_name
handler = handler_loader.load_handler("my_module.handlers:get_user_handler")
```

---

## Beispiele

### Beispiel 1: Einfacher HTTP-Service

**Konfiguration (`hex-config.toml`):**
```toml
[service]
name = "hello-service"
runtime = "python"

[inbound.http]
enabled = true
port = 8000
base_path = "/api"

[[inbound.http.routes]]
path = "/hello"
method = "GET"
handler = "handlers:hello_handler"

[logging]
level = "INFO"
```

**Handler (`handlers.py`):**
```python
from hexswitch.shared.envelope import Envelope

def hello_handler(envelope: Envelope) -> Envelope:
    return Envelope(
        status=200,
        body={"message": "Hello, World!"}
    )
```

**Ausführung:**
```bash
hexswitch run
```

**Test:**
```bash
curl http://localhost:8000/api/hello
```

### Beispiel 2: Multi-Adapter-Service

**Konfiguration (`hex-config.toml`):**
```toml
[service]
name = "multi-service"
runtime = "python"

[inbound.http]
enabled = true
port = 8000
base_path = "/api"

[[inbound.http.routes]]
path = "/call/grpc"
method = "POST"
handler = "handlers:call_grpc_handler"

[[inbound.http.routes]]
path = "/call/websocket"
method = "POST"
handler = "handlers:call_websocket_handler"

[outbound.grpc_client]
enabled = true
name = "example2_grpc"
server_url = "example2:50051"
timeout = 30
service_name = "ExampleService"
ports = ["example2_grpc_port"]

[outbound.websocket_client]
enabled = true
name = "example3_ws"
url = "ws://example3:8080"
timeout = 30
reconnect = true
reconnect_interval = 5
ports = ["example3_ws_port"]

[logging]
level = "INFO"
```

**Handler (`handlers.py`):**
```python
from hexswitch.shared.envelope import Envelope

def call_grpc_handler(envelope: Envelope) -> Envelope:
    request = Envelope(
        path="example2_grpc_port",
        method="POST",
        body=envelope.body,
        metadata={"port_name": "example2_grpc_port"}
    )
    return runtime.deliver(request, "example2_grpc")

def call_websocket_handler(envelope: Envelope) -> Envelope:
    request = Envelope(
        path="example3_ws_port",
        method="POST",
        body=envelope.body,
        metadata={"port_name": "example3_ws_port"}
    )
    return runtime.deliver(request, "example3_ws")
```

### Beispiel 3: Docker-Compose-Setup

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  example1:
    build: ./example/services/example1
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./example/services/example1/hex-config.toml:/app/hex-config.toml

  example2:
    build: ./example/services/example2
    ports:
      - "8001:8000"
    environment:
      - LOG_LEVEL=INFO

  example3:
    build: ./example/services/example3
    ports:
      - "8002:8000"
    environment:
      - LOG_LEVEL=INFO
```

**Start:**
```bash
docker-compose up -d
```

---

## Best Practices

### Konfiguration

1. **Umgebungsvariablen verwenden**: Nutzen Sie Jinja2-Templates für umgebungsspezifische Konfigurationen
2. **Validierung**: Validieren Sie Konfigurationen vor dem Deployment
3. **Versionierung**: Versionskontrolle für Konfigurationsdateien
4. **Sicherheit**: Keine Secrets in Konfigurationsdateien (Umgebungsvariablen verwenden)

### Handler-Entwicklung

1. **Single Responsibility**: Ein Handler sollte eine klare Aufgabe haben
2. **Error Handling**: Immer Fehlerbehandlung implementieren
3. **Validierung**: Input-Validierung in Handlern
4. **Idempotenz**: GET-Requests sollten idempotent sein
5. **Logging**: Wichtige Operationen loggen

### Adapter-Verwendung

1. **Adapter-Namen**: Verwenden Sie aussagekräftige Namen für Adapter
2. **Port-Registrierung**: Registrieren Sie Outbound-Adapter bei Ports
3. **Timeout-Konfiguration**: Setzen Sie angemessene Timeouts
4. **Retry-Logik**: Nutzen Sie Retry-Middleware für kritische Operationen

### Performance

1. **Connection Pooling**: Nutzen Sie Connection Pooling für Outbound-Adapter
2. **Async-Handling**: Verwenden Sie async/await für I/O-Operationen
3. **Caching**: Implementieren Sie Caching für häufig genutzte Daten
4. **Monitoring**: Nutzen Sie Observability-Features für Performance-Monitoring

### Sicherheit

1. **Authentication**: Implementieren Sie Authentication in Handlern
2. **Authorization**: Prüfen Sie Berechtigungen vor Operationen
3. **Input Validation**: Validieren Sie alle Eingaben
4. **Secrets Management**: Verwenden Sie sichere Secrets-Verwaltung

---

## Troubleshooting

### Häufige Probleme

#### Problem: Handler wird nicht gefunden

**Fehlermeldung:**
```
Handler not found: my_module.handlers:my_handler
```

**Lösung:**
1. Prüfen Sie den Handler-Pfad in der Konfiguration
2. Stellen Sie sicher, dass das Modul importierbar ist
3. Prüfen Sie, ob die Funktion existiert und die richtige Signatur hat

#### Problem: Adapter startet nicht

**Fehlermeldung:**
```
Failed to start adapter 'http': <Fehler>
```

**Lösung:**
1. Prüfen Sie die Adapter-Konfiguration
2. Stellen Sie sicher, dass der Port nicht bereits belegt ist
3. Prüfen Sie die Logs für detaillierte Fehlermeldungen

#### Problem: Outbound-Adapter kann nicht verbinden

**Fehlermeldung:**
```
Connection failed: <Adapter-Name>
```

**Lösung:**
1. Prüfen Sie die Server-URL/Konfiguration
2. Stellen Sie sicher, dass der Ziel-Service erreichbar ist
3. Prüfen Sie Firewall/Netzwerk-Einstellungen
4. Prüfen Sie Timeout-Einstellungen

#### Problem: Konfiguration wird nicht geladen

**Fehlermeldung:**
```
Configuration error: <Fehler>
```

**Lösung:**
1. Validieren Sie die Konfiguration: `hexswitch validate`
2. Prüfen Sie die YAML-Syntax
3. Stellen Sie sicher, dass alle erforderlichen Felder vorhanden sind

### Debug-Modus

Aktivieren Sie den Debug-Modus für detaillierte Logs:

```bash
hexswitch --log-level DEBUG run
```

### Logging

Logs werden standardmäßig nach stdout geschrieben. Für Produktionsumgebungen:

```toml
[logging]
level = "INFO"
format = "json"  # Optional: JSON-Format für Log-Aggregation
```

### Performance-Problembehandlung

1. **Monitoring aktivieren**: Nutzen Sie Observability-Features
2. **Metriken prüfen**: Überwachen Sie Adapter-Performance
3. **Tracing**: Nutzen Sie Distributed Tracing für Request-Flows
4. **Profiling**: Verwenden Sie Profiling-Tools für Performance-Analyse

---

## Weitere Ressourcen

- **GitHub Repository**: https://github.com/R0bes/hexSwitch
- **Dokumentation**: https://r0bes.github.io/hexSwitch/
- **Issues**: https://github.com/R0bes/hexSwitch/issues
- **Architektur-Übersicht**: `docs/architecture_overview.md`
- **Entwicklungs-Guide**: `docs/development_guide.md`

---

## Changelog

### Version 0.1.2
- **Environment-Variable-Overrides**: Unterstützung für `HEX_` Präfix zur Konfigurationsüberschreibung
- **Docker Compose Integration**: Verbesserte Unterstützung für Multi-Service-Deployments mit Environment-Variablen
- **TOML-Konfiguration**: Vollständige Migration von YAML zu TOML (keine Backward Compatibility)
- **Adapter-Name-Erkennung**: Verbesserte Parsing-Logik für zusammengesetzte Adapter-Namen (z.B. `http_client`, `grpc_client`)

### Version 0.1.1
- Initiale Veröffentlichung
- HTTP, WebSocket, gRPC, MCP Adapter
- CLI-Tools
- Observability-Features
- **HexSwitchService**: Einfacher Entrypoint für Framework-Nutzung mit automatischer Runtime-Integration

---

**Letzte Aktualisierung:** 2025-12-13  
**Autor:** HexSwitch Contributors  
**Lizenz:** MIT

