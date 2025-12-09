# HexSwitch Architecture Overview

## Introduction

HexSwitch is designed as a **hexagonal runtime switchboard for config-driven microservices**. This document provides a high-level overview of the architecture and current implementation status.

## Core Concept

HexSwitch aims to provide a runtime system that:

- Orchestrates microservices using a hexagonal (ports and adapters) architecture
- Uses configuration files to define service wiring and communication patterns
- Supports multiple inbound and outbound adapters (HTTP, message buses, etc.)
- Enables flexible, maintainable service composition

## Intended Architecture Components

### Core Runtime

The core runtime will be responsible for:

- Loading and parsing configuration files
- Managing the lifecycle of adapters and services
- Routing messages and requests between components
- Handling errors and providing observability

### Inbound Adapters

Inbound adapters will handle incoming requests/messages from external systems:

- **HTTP Adapter**: REST API endpoints
- **Message Bus Adapter**: Consume from message queues (e.g., RabbitMQ, Kafka)
- **gRPC Adapter**: gRPC service endpoints
- **WebSocket Adapter**: WebSocket connections

### Outbound Adapters

Outbound adapters will handle outgoing communication:

- **HTTP Client Adapter**: Make HTTP requests to other services
- **Message Bus Adapter**: Publish to message queues
- **Database Adapter**: Database connections
- **External Service Adapters**: Integration with third-party services

### Configuration-Driven Wiring

The system will use configuration files (e.g., YAML, JSON) to define:

- Which adapters to instantiate
- How adapters are connected
- Routing rules and transformations
- Service dependencies and health checks

## Hexagonal Architecture Pattern

HexSwitch follows the hexagonal architecture (ports and adapters) pattern:

```
                    ┌─────────────────┐
                    │   Core Runtime  │
                    │  (Application   │
                    │     Logic)      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐          ┌─────▼─────┐        ┌────▼────┐
   │ Inbound │          │  Outbound │        │  Other  │
   │ Adapter │          │  Adapter  │        │ Adapter │
   └─────────┘          └───────────┘        └─────────┘
```

- **Core Runtime**: Contains the business logic and orchestration
- **Adapters**: Isolated components that handle external communication
- **Ports**: Interfaces that define how adapters interact with the core

## Current Status

The current implementation includes:

- ✅ Project structure and scaffolding
- ✅ Development tooling (linting, testing, CI/CD)
- ✅ CLI with full command support
- ✅ Test framework setup
- ✅ **Core Runtime**: Runtime orchestration with lifecycle management
- ✅ **Configuration Parser**: Load and validate YAML configuration files
- ✅ **Adapter Framework**: Base classes and interfaces for adapters
- ✅ **HTTP Inbound Adapter**: REST API endpoints with route-based handler mapping
- ✅ **Handler System**: Dynamic loading and execution of handler functions
- ✅ **Orchestration**: Wire adapters together based on configuration
- ⏳ **Outbound Adapters**: Database and message bus adapters (planned)
- ⏳ **Additional Inbound Adapters**: gRPC, WebSocket, Message Bus (planned)
- ⏳ **Observability**: Metrics and tracing (planned)

## Implemented Components

### Core Runtime

The runtime (`src/hexswitch/runtime.py`) is responsible for:

- ✅ Loading and parsing configuration files
- ✅ Managing the lifecycle of adapters (start/stop)
- ✅ Graceful shutdown with signal handling
- ✅ Adapter factory pattern for creating adapters

### HTTP Inbound Adapter

The HTTP adapter (`src/hexswitch/adapters/http/`) provides:

- ✅ REST API endpoints with configurable base path
- ✅ Route-based handler mapping (path, method, handler)
- ✅ Support for GET, POST, PUT, DELETE, PATCH methods
- ✅ JSON request/response handling
- ✅ Configurable port (default: 8000)

### Handler System

The handler system (`src/hexswitch/handlers/`) enables:

- ✅ Dynamic loading of handler functions from string references
- ✅ Format: `module.path:function_name`
- ✅ Validation and error handling

## Future Development

Future development will focus on:

1. **Outbound Adapters**: Database adapters (PostgreSQL, etc.), HTTP client adapter
2. **Additional Inbound Adapters**: gRPC, WebSocket, Message Bus (RabbitMQ, Kafka)
3. **Observability**: Metrics collection, distributed tracing
4. **Advanced Features**: Live config reload, hot adapter swap, multi-runtime support

## Related Documentation

- [README.md](../README.md) - Project overview and setup
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines

