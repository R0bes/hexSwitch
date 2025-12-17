# PyPI Upload Guide

Anleitung zum Hochladen von HexSwitch auf PyPI (Python Package Index).

## Automatischer Upload via CI/CD

**Neu**: HexSwitch wird automatisch zu PyPI hochgeladen, wenn:
- Ein Push auf den `main` Branch erfolgt UND
- Alle Tests (lint, test, type-check) erfolgreich sind

### GitHub Secrets konfigurieren

Für den automatischen Upload muss ein PyPI API Token als GitHub Secret konfiguriert werden:

1. **PyPI API Token erstellen**:
   - Gehe zu [pypi.org/account/login](https://pypi.org/account/login/)
   - Navigiere zu Account Settings → API tokens
   - Erstelle einen neuen API Token (Scope: "Entire account" oder nur für das Projekt)
   - Kopiere den Token (beginnt mit `pypi-...`)

2. **GitHub Secret hinzufügen**:
   - Gehe zu deinem GitHub Repository
   - Navigiere zu Settings → Secrets and variables → Actions
   - Klicke auf "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Dein PyPI API Token (z.B. `pypi-xxxxxxxxxxxxx`)
   - Klicke auf "Add secret"

3. **Automatischer Upload**:
   - Nach jedem erfolgreichen Push auf `main` wird das Package automatisch gebaut und zu PyPI hochgeladen
   - Der Upload erfolgt nur, wenn alle Tests bestehen

### Manueller Upload

Falls du manuell hochladen möchtest, folge den Anweisungen unten.

## Voraussetzungen

1. **PyPI Account**: Erstelle einen Account auf [pypi.org](https://pypi.org) und [test.pypi.org](https://test.pypi.org)
2. **API Token**: Erstelle einen API Token in deinem PyPI-Account (Account Settings → API tokens)
3. **Build Tools**: Installiere die notwendigen Tools:

```bash
pip install build twine
```

## Vorbereitung

### 1. Metadaten prüfen

Stelle sicher, dass alle Metadaten in `pyproject.toml` korrekt sind:

- ✅ Package-Name: `hexswitch`
- ✅ Version: Aktuelle Version
- ✅ Description: Kurzbeschreibung
- ✅ License: Muss gesetzt sein (aktuell: MIT)
- ✅ URLs: Repository-URLs aktualisieren (falls nötig)
- ✅ Authors: Autor-Informationen

### 2. Repository-URLs aktualisieren

Falls du ein GitHub-Repository hast, aktualisiere die URLs in `pyproject.toml`:

```toml
[project.urls]
Homepage = "https://github.com/deinusername/hexswitch"
Documentation = "https://github.com/deinusername/hexswitch#readme"
Repository = "https://github.com/deinusername/hexswitch"
Issues = "https://github.com/deinusername/hexswitch/issues"
```

### 3. LICENSE-Datei

Stelle sicher, dass eine `LICENSE` oder `LICENSE.txt` Datei im Projekt-Root existiert. Falls nicht, erstelle eine MIT-Lizenz-Datei.

## Build-Prozess

### Schritt 1: Package bauen

```bash
# Windows PowerShell
python scripts/build-package.py

# Linux/Mac
python3 scripts/build-package.py
```

Das Skript:
- Bereinigt alte Build-Verzeichnisse
- Baut Source Distribution (`.tar.gz`)
- Baut Wheel (`.whl`)
- Verifiziert das Package mit `twine check`

Die gebauten Dateien befinden sich im `dist/` Verzeichnis.

### Schritt 2: Lokal testen (optional)

Teste das Package lokal, bevor du es hochlädst:

```bash
# Installiere das gebaute Package
pip install dist/hexswitch-*.whl

# Teste die Installation
hexswitch version

# Deinstalliere wieder
pip uninstall hexswitch
```

## Upload-Prozess

### TestPyPI (Empfohlen für erste Tests)

1. **Upload zu TestPyPI**:

```bash
python scripts/upload-package.py --test
```

2. **Test-Installation von TestPyPI**:

```bash
pip install -i https://test.pypi.org/simple/ hexswitch
```

3. **Verifiziere die Installation**:

```bash
hexswitch version
```

### PyPI (Produktion)

**WICHTIG**: Stelle sicher, dass alles korrekt ist, bevor du zu PyPI hochlädst!

1. **Upload zu PyPI**:

```bash
python scripts/upload-package.py
```

Das Skript fragt zur Bestätigung, bevor es hochlädt.

2. **Installation von PyPI**:

Nach dem Upload (kann einige Minuten dauern):

```bash
pip install hexswitch
```

## Manuelle Upload-Methode

Falls du die Skripte nicht verwenden möchtest:

### Build

```bash
python -m build
```

### Upload zu TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

### Upload zu PyPI

```bash
python -m twine upload dist/*
```

## API Token Konfiguration

### Option 1: Environment Variable

```bash
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-xxxxxxxxxxxxx"

# Linux/Mac
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-xxxxxxxxxxxxx"
```

### Option 2: .pypirc Datei

Erstelle `~/.pypirc` (oder `%USERPROFILE%\.pypirc` auf Windows):

```ini
[pypi]
username = __token__
password = pypi-xxxxxxxxxxxxx

[testpypi]
username = __token__
password = pypi-xxxxxxxxxxxxx
```

**WICHTIG**: Füge `.pypirc` zu `.gitignore` hinzu!

## Versionierung

Bei jedem Upload muss die Version in `pyproject.toml` erhöht werden:

```toml
version = "0.1.0"  # → "0.1.1" für Patch-Release
version = "0.1.0"  # → "0.2.0" für Minor-Release
version = "0.1.0"  # → "1.0.0" für Major-Release
```

PyPI erlaubt keine erneuten Uploads derselben Version!

## Troubleshooting

### "Package already exists"

- Die Version existiert bereits auf PyPI
- Lösung: Version in `pyproject.toml` erhöhen

### "Invalid distribution"

- Das Package ist beschädigt oder unvollständig
- Lösung: `python scripts/build-package.py` erneut ausführen

### "Authentication failed"

- API Token ist falsch oder abgelaufen
- Lösung: Neuen Token in PyPI erstellen

### "Missing LICENSE file"

- Keine LICENSE-Datei gefunden
- Lösung: Erstelle eine `LICENSE` oder `LICENSE.txt` Datei

## Checkliste vor dem Upload

- [ ] Version in `pyproject.toml` erhöht
- [ ] Alle Tests bestehen (`pytest`)
- [ ] README.md ist aktuell
- [ ] LICENSE-Datei existiert
- [ ] Repository-URLs sind korrekt
- [ ] Package lokal getestet
- [ ] TestPyPI-Upload erfolgreich getestet
- [ ] API Token konfiguriert

## Weitere Ressourcen

- [PyPI Documentation](https://packaging.python.org/en/latest/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)

