# HexSwitch Architecture Overview

## Introduction

HexSwitch is designed as a **hexagonal runtime switchboard for config-driven microservices**. This document provides a high-level overview of the intended architecture. **Note**: This is a placeholder document. No runtime behavior is currently implemented.

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

⚠️ **Important**: This architecture is a **placeholder**. The current implementation includes:

- ✅ Project structure and scaffolding
- ✅ Development tooling (linting, testing, CI/CD)
- ✅ Basic CLI skeleton
- ✅ Test framework setup
- ❌ No runtime implementation
- ❌ No adapter implementations
- ❌ No configuration parsing
- ❌ No service orchestration

## Future Development

Future development will focus on:

1. **Core Runtime**: Implement the basic runtime engine
2. **Configuration Parser**: Load and validate configuration files
3. **Adapter Framework**: Create the base classes and interfaces for adapters
4. **First Adapters**: Implement initial inbound/outbound adapters (e.g., HTTP)
5. **Orchestration**: Wire adapters together based on configuration
6. **Observability**: Add logging, metrics, and tracing

## Related Documentation

- [README.md](../README.md) - Project overview and setup
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines

