# Adapter Development

## Creating New Adapters

**All new adapters MUST be created using the `hexswitch new_adapter` command.**

### Command Usage

```bash
hexswitch new_adapter <name> --type <inbound|outbound> [--description "Description"]
```

### What the Command Creates

The `new_adapter` command automatically creates:

1. **Adapter Implementation**
   - `src/hexswitch/adapters/<name>/adapter.py` - Main adapter class
   - `src/hexswitch/adapters/<name>/__init__.py` - Package exports

2. **Mock Implementation**
   - `tests/fixtures/mock_adapters/<name>_mock.py` - Mock adapter class
   - Automatically registered in `tests/fixtures/mock_adapters/__init__.py`

3. **Test File**
   - `tests/unit/test_<name>_adapter.py` - Unit tests for the adapter

### Naming Conventions

- **Adapter Name**: Use `snake_case` (e.g., `http_client`, `message_broker`)
- **Adapter Class**: `{Name}Adapter` in PascalCase (e.g., `HttpClientAdapter`)
- **Mock Class**: `Mock{Name}Adapter` (e.g., `MockHttpClientAdapter`)
- **File Names**: `snake_case` matching adapter name

### Required Steps After Creation

1. **Implement Adapter Logic**
   - Complete the TODO sections in the generated adapter file
   - Implement `start()`/`stop()` for inbound adapters
   - Implement `connect()`/`disconnect()` for outbound adapters

2. **Register in Runtime**
   - Update `src/hexswitch/runtime.py`
   - Add adapter to `_create_inbound_adapter()` or `_create_outbound_adapter()`
   - Example:
     ```python
     if name == "<adapter_name>":
         return <AdapterClass>(name, adapter_config)
     ```

3. **Implement Mock Behavior**
   - Complete the mock adapter implementation
   - Ensure mock follows the same interface as the real adapter
   - Mock should be usable for testing and visualization

4. **Write Tests**
   - Complete the generated test file
   - Add tests for adapter lifecycle
   - Add tests for error handling
   - Ensure tests use the mock adapter

### Mock Adapter Requirements

- **Every adapter MUST have a corresponding mock implementation**
- Mocks are located in `tests/fixtures/mock_adapters/`
- Mock class name MUST follow: `Mock{AdapterName}Adapter`
- Mocks MUST implement the same interface as the real adapter
- Mocks are used for:
  - Unit testing
  - Integration testing
  - Visualization in Visual Test Lab

### Validation

A test (`tests/unit/test_mock_coverage.py`) validates that:
- Every adapter in `runtime.py` has a corresponding mock
- Mock adapters follow the naming convention
- Mocks can be instantiated correctly

**This test MUST pass before merging adapter code.**

### Agent Guidelines

- **NEVER create adapters manually** - Always use `hexswitch new_adapter`
- **NEVER skip creating a mock** - Every adapter needs a mock
- **ALWAYS update runtime.py** - Register the adapter in the factory method
- **ALWAYS run the mock coverage test** - Ensure `test_mock_coverage.py` passes
- **ALWAYS follow naming conventions** - Consistency is critical

### Example Workflow

```bash
# 1. Create new adapter
hexswitch new_adapter grpc --type inbound --description "gRPC inbound adapter"

# 2. Implement adapter logic
# Edit src/hexswitch/adapters/grpc/adapter.py

# 3. Register in runtime
# Edit src/hexswitch/runtime.py - add to _create_inbound_adapter()

# 4. Complete mock implementation
# Edit tests/fixtures/mock_adapters/grpc_mock.py

# 5. Write tests
# Edit tests/unit/test_grpc_adapter.py

# 6. Verify mock coverage
pytest tests/unit/test_mock_coverage.py -v
```

