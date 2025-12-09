# HexSwitch CLI & Shell Specification

## Purpose

This document defines the **official command-line shell for
HexSwitch**.\
It acts as the stable entry point for:

-   Config-driven runtime initialization
-   Validation & diagnostics
-   Future runtime execution
-   Developer ergonomics & automation

This shell **must remain backwards-compatible** across versions unless
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
  `--config`      Path to hex-config.yaml

------------------------------------------------------------------------

## Configuration File

**Default:** `hex-config.yaml`

``` yaml
service:
  name: example-service
  runtime: python

inbound:
  http:
    enabled: true
    base_path: /api
    routes:
      - path: /hello
        method: GET
        handler: adapters.http_handlers:hello

outbound:
  postgres:
    enabled: false
    dsn_env: POSTGRES_DSN

logging:
  level: INFO
```

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

### `hexswitch validate`

Validation layers: 1. File exists 2. YAML syntax valid 3. Required
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
