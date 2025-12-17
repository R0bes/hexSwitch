# hexSwitch Integration

Das Visual Test Lab verwendet die **echte hexSwitch-Implementierung** als lokale Bibliothek.

## Setup

### 1. hexSwitch installieren

Stelle sicher, dass hexSwitch installiert ist:

```bash
# Im Hauptverzeichnis
pip install -e ".[dev]"
```

### 2. API-Server starten

Starte den hexSwitch API-Server:

```bash
# Im visual-test-lab Verzeichnis
python scripts/hexswitch_api.py
```

Der Server läuft standardmäßig auf `http://localhost:8080`.

### 3. Visual Test Lab starten

In einem anderen Terminal:

```bash
cd visual-test-lab
npm run dev
```

## API-Endpunkte

Der hexSwitch API-Server bietet folgende Endpunkte:

- `GET /api/adapters` - Liste aller verfügbaren Adapter aus der echten Implementierung
- `GET /api/config` - Aktuelle hex-config.yaml laden
- `GET /api/plan` - Execution Plan aus aktueller Config
- `POST /api/config/validate` - Konfiguration validieren (Body: `{"config": {...}}`)
- `POST /api/config/load` - Config aus Datei laden (Body: `{"path": "hex-config.yaml"}`)

## Funktionsweise

1. **Adapter-Loading**: Das Visual Test Lab lädt Adapter-Metadaten vom hexSwitch API-Server
2. **Fallback**: Falls der API-Server nicht verfügbar ist, werden Fallback-Adapter verwendet
3. **Konfiguration**: Die echte `hex-config.yaml` kann geladen und validiert werden
4. **Runtime**: Die echte hexSwitch-Runtime kann über die API gesteuert werden

## Dateien

- `scripts/export_adapters.py` - Exportiert Adapter-Metadaten als JSON
- `scripts/hexswitch_api.py` - API-Server für hexSwitch-Integration
- `src/services/hexSwitchAPI.ts` - TypeScript-Client für die API
- `src/data/realAdapters.ts` - Lädt echte Adapter vom API-Server

## Entwicklung

Um neue Adapter hinzuzufügen:

1. Adapter in `src/hexswitch/adapters/` implementieren
2. In `src/hexswitch/runtime.py` registrieren
3. In `scripts/export_adapters.py` Metadaten hinzufügen
4. API-Server neu starten

Das Visual Test Lab lädt die neuen Adapter automatisch.

