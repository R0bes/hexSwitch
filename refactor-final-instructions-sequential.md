# HexSwitch Refactor: Final Instructions (Sequential Phases, Testable States)

This is the **sequential** refactor plan to reach the target model (ports-only core, adapter plugins, canonical runtime pipeline, envelope data-only), while keeping the repository **working and testable after every phase**.

**Grounding:** Pain points and constraints come from the intake reports. fileciteturn5file7turn5file16  
**Target model:** `Runtime.emit`, central handler loading, adapter factory/plugin loading, pipeline + middleware, envelope without observability methods. fileciteturn5file4turn5file2

---

## Non-negotiables (global rules)

1) **Green after each phase**: tests pass, example(s) run.  
2) **Backward compatibility first**: config keeps working in Phase 1–3 (non-breaking). fileciteturn5file10turn5file8  
3) **No per-adapter event loops** in the target execution model.  
4) **Core knows only ports/handlers + Envelope**. No adapter/protocol imports. fileciteturn5file3turn5file16  
5) **Runtime does not import concrete adapters** (factory/registry). fileciteturn5file7turn5file16  
6) **Adapters do only IO + Protocol↔Envelope conversion**, and call runtime entrypoints (`dispatch`, `deliver`). fileciteturn5file15turn5file2  

---

## Branch workflow

- Use one branch: `refactor/hexswitch-target`
- Each phase is a mergeable PR:
  - `phase-0-safety-nets`
  - `phase-1-adapter-factory`
  - `phase-2-handler-loader`
  - `phase-3-runtime-emit`
  - `phase-4-canonical-pipeline`
  - `phase-5-envelope-data-only`
  - `phase-6-config-policies`
  - `phase-7-execution-unification` (optional)

---

## Phase 0 — Baseline, Safety Nets, and “Do Not Break” Invariants

### Goal
Freeze behavior and create tests that catch regressions early.

### Actions
1) Add **integration tests** for:
   - HTTP inbound → handler → HTTP response
   - One outbound emission path (whatever exists today: HTTP client / NATS / WS)
2) Add **golden tests** for Envelope fields currently relied upon (`trace_id`, `span_id`, `parent_span_id`). fileciteturn5file15turn5file10
3) Add a test asserting “runtime can start and stop cleanly” (no hanging threads/tasks).

### Acceptance Criteria
- `pytest -q` passes locally and in CI
- At least one inbound and one outbound path are covered

### Commands (English)
```bash
pytest -q
pytest -q -k "integration"
ruff check .
```

---

## Phase 1 — Adapter Factory + Adapter Registry (remove runtime’s concrete adapter imports)

### Why
Runtime imports concrete adapter classes directly. fileciteturn5file7turn5file16

### Goal
Runtime instantiates adapters via **import strings** (factory) and stores them in an **AdapterRegistry**.

### Actions
1) Add modules (adjust paths to repo layout):
   - `src/hexswitch/registry/adapters.py`
   - `src/hexswitch/registry/factory.py`
2) Implement `AdapterFactory.create(impl_path: str, cfg: dict) -> AdapterBase`
   - `impl_path`: `"module.sub:ClassName"`
3) Implement `AdapterRegistry`:
   - store instances + metadata (`name`, `direction`, `capabilities`)
4) Update runtime creation:
   - remove hardcoded `_create_inbound_adapter/_create_outbound_adapter` chains fileciteturn5file16turn5file14
   - replace with factory-based creation
5) Keep config backwards compatible:
   - loader maps old schema → new `impl/args` fields without breaking existing files.

### Acceptance Criteria
- Existing example configs still run
- `runtime.py` has no imports of concrete adapters

### Commands (English)
```bash
pytest -q
python -m hexswitch.app --config example/services/example1/hex-config.yaml run
```

---

## Phase 2 — Centralize Handler Loading (single HandlerLoader)

### Why
Handler loading is duplicated (importlib logic) across adapters/runtime paths. fileciteturn5file7turn5file17

### Goal
All handler resolving happens in one place:
- `HandlerLoader.resolve("pkg.mod:callable") -> callable`

Adapters never import handlers.

### Actions
1) Create `src/hexswitch/handlers/loader.py`:
   - caching
   - signature validation (inbound: `Envelope -> Envelope|None`)
2) Update config models to store handler references consistently.
3) Update adapters:
   - remove any importlib-based handler loading
   - request handler/port resolution from runtime/registry
4) Ensure decorator-based registration still works (no breaking).

### Acceptance Criteria
- No `importlib.import_module` usage inside adapters (only in HandlerLoader)
- All routes still call the same handlers as before

### Commands (English)
```bash
pytest -q
rg "importlib\.import_module" src/hexswitch/adapters -n
```

---

## Phase 3 — Outbound API: `Runtime.emit()` + Outbound routing table

### Why
Outbound adapters are currently bound as handlers (confusing and leaky abstraction). fileciteturn5file16turn5file7

### Goal
Clear outbound flow:
- Core builds Envelope via `@outbound_port`
- Runtime routes to adapter targets via route table
- Adapters are never registered as handlers

### Actions
1) Add registries:
   - `OutboundPortRegistry`: `port_name -> factory callable`
   - `OutboundRouteRegistry`: route key (`port_name` recommended) → targets[]
2) Add Runtime methods:
   - `emit(port_name: str, *args, **kwargs) -> Envelope | None`
   - `deliver(env: Envelope) -> None`
3) Add compatibility shim:
   - keep old “outbound adapter as handler” working temporarily with deprecation warnings
4) Convert at least one real outbound call site to `runtime.emit(...)`.

### Acceptance Criteria
- Outbound adapters are not in PortRegistry as handlers
- One e2e outbound path works via `Runtime.emit()`

### Commands (English)
```bash
pytest -q
rg "register.*outbound" src/hexswitch/runtime.py -n
```

---

## Phase 4 — Canonical Pipeline + Middleware Stack

### Why
No single canonical pipeline; adapter flows differ. fileciteturn5file15turn5file0

### Goal
Introduce a canonical pipeline with stable entrypoints:
- inbound: `runtime.dispatch(env)`
- outbound: `runtime.deliver(env)`

### Minimum stage order
1) normalize/enrich (ids, timestamps)
2) telemetry span start
3) validation (optional)
4) inbound routing
5) execute handler (concurrency gates)
6) error mapping (exceptions → error envelope)
7) outbound routing
8) adapter send

### Actions
1) Add:
   - `src/hexswitch/pipeline/pipeline.py`
   - `src/hexswitch/pipeline/middleware/*.py`
2) Implement middleware interface (English):
```python
from typing import Protocol

class Middleware(Protocol):
    async def __call__(self, ctx, env, next): ...
```
3) Update adapters:
   - inbound: only `await runtime.dispatch(env)`
   - outbound: only `await runtime.deliver(env)`
4) Add per-port concurrency gates (`asyncio.Semaphore`).
5) Ensure consistent error envelope behavior.

### Acceptance Criteria
- All inbound adapters call `runtime.dispatch`
- Middleware order is explicit and tested
- All protocols still function

### Commands (English)
```bash
pytest -q
rg "get_port_registry\(\)|PortRegistry" src/hexswitch/adapters -n
```

---

## Phase 5 — Envelope becomes data-only; Observability moves into middleware

### Why
Envelope currently contains tracing/span methods. fileciteturn5file15turn5file17

### Goal
- Envelope = data-only
- Observability done in runtime middleware
- Adapters only map telemetry context in/out

### Actions
1) Add `ObservabilityMiddleware`:
   - spans at ingress/dispatch/core/egress
   - metrics + structured logs
2) Deprecate Envelope tracing methods:
   - keep compatibility temporarily (warn + call middleware hooks or no-op)
3) Update handlers:
   - stop calling envelope span methods
   - use injected context (`ctx.tracer`, `ctx.logger`)
4) Ensure trace propagation works:
   - HTTP inbound extract
   - HTTP outbound inject
   - WS/NATS metadata mapping

### Acceptance Criteria
- No handler uses `Envelope.start_span()` (outside compat layer)
- Trace continuity verified for HTTP + one other protocol

### Commands (English)
```bash
pytest -q
rg "start_span\(|finish_span\(" src -n
```

---

## Phase 6 — Config-driven routing strategies + policies (retry/backpressure/timeouts)

### Why
Routing strategies are currently decorator-based (code), not config-driven. fileciteturn5file0turn5file10

### Goal
Config can define:
- strategy: `first | broadcast | round_robin`
- policies: retry/backoff, timeouts, backpressure profiles

### Actions
1) Extend config schema (non-breaking):
   - add optional `routing_strategy`
   - add optional `policies`
2) Add middleware:
   - `RetryMiddleware`
   - `TimeoutMiddleware`
   - `BackpressureMiddleware`
3) Default behavior matches current strategies if config omits fields.

### Acceptance Criteria
- Strategy can be changed via config only
- At least one test demonstrates strategy differences

---

## Phase 7 (Optional) — Execution model consolidation (single asyncio runtime)

### Why
Current system uses mixed concurrency models. fileciteturn5file16turn5file14

### Goal
Single runtime execution context:
- one asyncio loop
- blocking operations via runtime-owned executor
- deterministic shutdown

### Actions
1) Introduce adapter runners:
   - async runner
   - blocking runner (`asyncio.to_thread`)
2) Incrementally migrate adapters to be loop-friendly.
3) Ensure shutdown drains queues and cancels tasks in order.

### Acceptance Criteria
- No dedicated per-adapter loops/threads required for correctness
- Clean stop without hanging tasks/threads

---

## Definition of Done (end state)

- Runtime imports no concrete adapters fileciteturn5file16turn5file7
- Handler loading is centralized fileciteturn5file17turn5file7
- Outbound adapters are not handlers fileciteturn5file16turn5file7
- Canonical pipeline exists (`dispatch/deliver`) fileciteturn5file18turn5file15
- Envelope is data-only; telemetry is middleware-driven fileciteturn5file8turn5file15
- Routing strategies/policies are config-driven fileciteturn5file0turn5file10

---

## Appendix: Task slicing template (single-agent-friendly)

For each phase, create tasks as:
- **Task name**
- **Touched modules**
- **Behavior preserved**
- **Tests to add/update**
- **Acceptance criteria**
- **Rollback plan**
