/**
 * HexSwitch Reference
 * 
 * This file documents the real hexSwitch implementation structure
 * and serves as a reference for the Visual Test Lab.
 * 
 * Source: ../src/hexswitch/ (read-only reference)
 * Docker: ../devops/Dockerfile
 * Config: ../hex-config.yaml
 */

/**
 * Real hexSwitch Adapter Types (from src/hexswitch/runtime.py)
 */
export interface HexSwitchAdapter {
  name: string;
  type: 'inbound' | 'outbound';
  config: Record<string, any>;
}

/**
 * Real Inbound Adapters (from src/hexswitch/runtime.py)
 */
export const REAL_INBOUND_ADAPTERS = {
  http: {
    name: 'http',
    type: 'inbound' as const,
    description: 'HTTP REST API endpoint adapter',
    source: 'src/hexswitch/adapters/http/adapter.py',
    configSchema: {
      enabled: 'boolean',
      base_path: 'string (optional)',
      port: 'number (optional, 1-65535)',
      routes: 'array<{path: string, method: string, handler: string}>'
    },
    exampleConfig: {
      enabled: true,
      base_path: '/api',
      routes: [
        {
          path: '/hello',
          method: 'GET',
          handler: 'adapters.http_handlers:hello'
        }
      ]
    }
  }
};

/**
 * Real Outbound Adapters (from src/hexswitch/runtime.py)
 */
export const REAL_OUTBOUND_ADAPTERS = {
  http_client: {
    name: 'http_client',
    type: 'outbound' as const,
    description: 'HTTP client adapter for making requests to other services',
    source: 'src/hexswitch/adapters/http_client/adapter.py',
    configSchema: {
      enabled: 'boolean',
      base_url: 'string (optional)',
      timeout: 'number (optional, positive)',
      headers: 'object (optional)'
    },
    exampleConfig: {
      enabled: true,
      base_url: 'https://api.example.com',
      timeout: 30,
      headers: {
        'Content-Type': 'application/json'
      }
    }
  },
  mcp_client: {
    name: 'mcp_client',
    type: 'outbound' as const,
    description: 'MCP (Model Context Protocol) client adapter',
    source: 'src/hexswitch/adapters/mcp_client/adapter.py',
    configSchema: {
      enabled: 'boolean',
      server_url: 'string (required)',
      timeout: 'number (optional, positive)',
      headers: 'object (optional)'
    },
    exampleConfig: {
      enabled: true,
      server_url: 'http://localhost:8080',
      timeout: 30,
      headers: {}
    }
  }
};

/**
 * Real hexSwitch Configuration Structure (from src/hexswitch/config.py)
 */
export interface HexSwitchConfig {
  service: {
    name: string;
    runtime?: string;
  };
  inbound?: {
    [adapterName: string]: {
      enabled: boolean;
      [key: string]: any;
    };
  };
  outbound?: {
    [adapterName: string]: {
      enabled: boolean;
      [key: string]: any;
    };
  };
  logging?: {
    level?: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  };
}

/**
 * Example hexSwitch Configuration (from hex-config.yaml)
 */
export const EXAMPLE_HEXSWITCH_CONFIG: HexSwitchConfig = {
  service: {
    name: 'example-service',
    runtime: 'python'
  },
  inbound: {
    http: {
      enabled: true,
      base_path: '/api',
      routes: [
        {
          path: '/hello',
          method: 'GET',
          handler: 'adapters.http_handlers:hello'
        }
      ]
    }
  },
  outbound: {
    postgres: {
      enabled: false,
      dsn_env: 'POSTGRES_DSN'
    }
  },
  logging: {
    level: 'INFO'
  }
};

/**
 * Runtime Execution Plan Structure (from src/hexswitch/runtime.py)
 */
export interface ExecutionPlan {
  service: string;
  inbound_adapters: Array<{
    name: string;
    config: Record<string, any>;
  }>;
  outbound_adapters: Array<{
    name: string;
    config: Record<string, any>;
  }>;
}

/**
 * Adapter Factory Methods (from src/hexswitch/runtime.py)
 * 
 * Inbound adapters are created via: Runtime._create_inbound_adapter(name, config)
 * Outbound adapters are created via: Runtime._create_outbound_adapter(name, config)
 * 
 * Supported inbound adapters: 'http'
 * Supported outbound adapters: 'http_client', 'mcp_client'
 */

/**
 * Handler Reference Format (from src/hexswitch/config.py)
 * 
 * Format: 'module.path:function_name'
 * Example: 'adapters.http_handlers:hello'
 * 
 * Handlers are loaded dynamically via: hexswitch.handlers.load_handler(handler_path)
 */

/**
 * Docker Image Reference
 * 
 * Build: docker build -f devops/Dockerfile -t hexswitch:latest .
 * Run: docker run --rm hexswitch:latest hexswitch version
 * 
 * The Docker image contains the full hexSwitch runtime and can be used
 * to test configurations or run actual instances.
 */

/**
 * CLI Commands (from src/hexswitch/app.py)
 * 
 * - hexswitch version: Show version
 * - hexswitch init: Create example configuration
 * - hexswitch validate: Validate configuration
 * - hexswitch run: Start runtime
 * - hexswitch run --dry-run: Show execution plan without starting
 */

/**
 * Observability (from src/hexswitch/observability/)
 * 
 * - Metrics: Counter, Gauge, Histogram
 * - Tracing: Spans with tags
 * - Runtime metrics: adapter_starts_total, adapter_stops_total, adapter_errors_total, active_adapters
 */

