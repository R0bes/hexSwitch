---
layout: default
title: HexSwitch CLI & Shell Specification
---

<div class="hexswitch-header">
  <div class="hexswitch-header-content">
    <div class="hexswitch-logo-container">
      <img src="{{ '/assets/logo.png' | relative_url }}" alt="HexSwitch Logo" class="hexswitch-logo" />
      <div class="hexswitch-title-group">
        <h1 class="hexswitch-title">HexSwitch</h1>
        <p class="hexswitch-tagline">CLI & Shell Specification</p>
      </div>
    </div>
  </div>
</div>

<div class="hexswitch-content">

# HexSwitch CLI & Shell Specification

## Purpose

This document defines the **official command-line shell for
HexSwitch**.\
It acts as the stable entry point for:

-   Config-driven runtime initialization
-   Validation & diagnostics
-   Future runtime execution
-   Developer ergonomics & automation

This shell follows semantic versioning
explicitly marked as breaking.

------------------------------------------------------------------------

## Design Principles

-   Zero hidden magic
-   Safe by default
-   Dry-run first
-   Explicit configuration paths
-   Human-readable diagnostics
-   Runtime logic lives elsewhere --- the shell only orchestrates

------------------------------------------------------------------------

## Command Overview

  Command                     Purpose
  --------------------------- ------------------------------
  `hexswitch version`         Show version & tagline
  `hexswitch init`            Create example configuration
  `hexswitch validate`        Validate configuration
  `hexswitch run`             Start runtime (future)
  `hexswitch run --dry-run`   Simulate runtime plan

------------------------------------------------------------------------

## Global Options

  Option          Description
  --------------- --------------------------------
  `--log-level`   DEBUG / INFO / WARNING / ERROR
  `--config`      Path to hex-config.toml

------------------------------------------------------------------------

## Configuration File

**Default:** `hex-config.toml`

HexSwitch supports both plain TOML files and Jinja2 templates (`.j2` extension). Templates allow dynamic configuration using environment variables.

**Plain TOML example:**
```toml
[service]
name = "example-service"
runtime = "python"

[inbound.http]
enabled = true
base_path = "/api"

[[inbound.http.routes]]
path = "/hello"
method = "GET"
handler = "adapters.http_handlers:hello"

[outbound.http_client]
enabled = false
base_url = "https://api.example.com"
timeout = 30

[outbound.mcp_client]
enabled = false
server_url = "https://mcp.example.com"
timeout = 30

[logging]
level = "INFO"
```

**Template example (`hex-config.toml.j2`):**
```toml
[service]
name = "{{ env.SERVICE_NAME | default('example-service') }}"
runtime = "python"

[inbound.http]
enabled = {{ env.ENABLE_HTTP | default(true) }}
port = {{ env.HTTP_PORT | default(8000) | int }}
base_path = "{{ env.BASE_PATH | default('/api') }}"

[[inbound.http.routes]]
path = "/hello"
method = "GET"
handler = "adapters.http_handlers:hello"

[outbound.http_client]
enabled = {{ env.ENABLE_HTTP_CLIENT | default(false) }}
base_url = "{{ env.HTTP_CLIENT_BASE_URL | default('https://api.example.com') }}"
timeout = {{ env.HTTP_CLIENT_TIMEOUT | default(30) | int }}

[outbound.mcp_client]
enabled = {{ env.ENABLE_MCP_CLIENT | default(false) }}
server_url = "{{ env.MCP_SERVER_URL | default('https://mcp.example.com') }}"
timeout = {{ env.MCP_CLIENT_TIMEOUT | default(30) | int }}

[logging]
level = "{{ env.LOG_LEVEL | default('INFO') }}"
```

**Template features:**
- Environment variables via `env.VAR_NAME`
- Jinja2 filters: `default()`, `int()`, `bool()`, etc.
- Automatic template detection for `.j2` files

------------------------------------------------------------------------

## Runtime Execution States

  State      Behavior
  ---------- -------------------------------
  INIT       Load config
  VALIDATE   Schema & logic check
  PLAN       Build adapter execution graph
  DRY-RUN    Print execution graph
  RUN        Start runtime loop

------------------------------------------------------------------------

## CLI Behavior Specification

### `hexswitch version`

Outputs: - Version - Tagline

### `hexswitch init`

Behavior: - Creates example config - Refuses overwrite unless `--force`

Options:
- `--template <name>`: Use specific template (without .j2 extension)
- `--list-templates`: List available templates
- `--force`: Overwrite existing configuration file

### `hexswitch validate`

Validation layers: 1. File exists 2. TOML syntax valid 3. Required
sections present 4. Adapter flags are booleans

### `hexswitch run`

Behavior: - Loads config - Runs validation - Builds runtime execution
graph (future) - Starts event loop (future)

With `--dry-run`: - Prints adapter activation plan - Does NOT start
runtime

------------------------------------------------------------------------

## Python Shell Architecture

    src/hexswitch/
      __init__.py
      app.py        <-- CLI entry point
      config.py     <-- config loading & validation
      runtime.py    <-- future orchestration core

------------------------------------------------------------------------

## Exit Codes

  Code   Meaning
  ------ --------------------------
  0      Success
  1      Validation error
  2      Runtime failure (future)

------------------------------------------------------------------------

## Logging Policy

  Level     Use
  --------- ----------------------------
  DEBUG     Internal state
  INFO      Runtime phase updates
  WARNING   Missing optional config
  ERROR     Fatal config/runtime error

------------------------------------------------------------------------

## Developer Workflow

``` bash
hexswitch init
hexswitch validate
hexswitch run --dry-run
hexswitch run
```

------------------------------------------------------------------------

## Security Considerations

-   No execution of handlers during validation
-   No dynamic imports during dry-run
-   Environment variables only resolved during RUN phase

------------------------------------------------------------------------

## New Agent Rules

Any future agent extending this shell MUST:

-   Preserve existing CLI contract
-   Add new commands via subparsers
-   Implement strict tests before merging
-   Document new flags in this file
-   Never auto-start network listeners during validation

------------------------------------------------------------------------

## Roadmap Hooks

  Feature                 Planned
  ----------------------- ----------
  Live config reload      yes
  Hot adapter swap        yes
  Multi-runtime support   yes
  Interactive TUI         optional

------------------------------------------------------------------------

## Status

This shell spec is **authoritative** for HexSwitch v0.x.

</div>

<div class="hexswitch-footer">
  <p>© 2025 HexSwitch | MIT License</p>
</div>
