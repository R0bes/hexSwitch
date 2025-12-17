export interface Adapter {
  id: string;
  name: string;
  type: 'inbound' | 'outbound';
  category: string;
  icon: string;
  description: string;
}

/**
 * Adapter definitions based on real hexSwitch implementation.
 * 
 * Reference: ../src/hexswitch/runtime.py
 * Real adapters:
 * - Inbound: http (src/hexswitch/adapters/http/adapter.py)
 * - Outbound: http_client (src/hexswitch/adapters/http_client/adapter.py)
 * - Outbound: mcp_client (src/hexswitch/adapters/mcp_client/adapter.py)
 * 
 * Additional adapters are included for visualization/testing purposes.
 */
export const mockAdapters: Adapter[] = [
  // Real Inbound Adapters (from hexSwitch)
  {
    id: 'http-inbound',
    name: 'HTTP Adapter',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Globe',
    description: 'HTTP REST API endpoint adapter (real: src/hexswitch/adapters/http/adapter.py)'
  },
  
  // Planned/Visualization Inbound Adapters
  {
    id: 'grpc-inbound',
    name: 'gRPC Adapter',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Network',
    description: 'gRPC service adapter (planned)'
  },
  {
    id: 'message-consumer',
    name: 'Message Consumer',
    type: 'inbound',
    category: 'Inbound',
    icon: 'MessageSquare',
    description: 'Consume messages from broker (planned)'
  },
  {
    id: 'scheduler-trigger',
    name: 'Scheduler Trigger',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Clock',
    description: 'Time-based trigger adapter (planned)'
  },
  
  // Real Outbound Adapters (from hexSwitch)
  {
    id: 'http-client',
    name: 'HTTP Client',
    type: 'outbound',
    category: 'Outbound',
    icon: 'ExternalLink',
    description: 'HTTP client adapter (real: src/hexswitch/adapters/http_client/adapter.py)'
  },
  {
    id: 'mcp-client',
    name: 'MCP Client',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Server',
    description: 'MCP client adapter (real: src/hexswitch/adapters/mcp_client/adapter.py)'
  },
  
  // Planned/Visualization Outbound Adapters
  {
    id: 'db-mock',
    name: 'DB Mock',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Database',
    description: 'Mock database adapter (planned)'
  },
  {
    id: 'cache-mock',
    name: 'Cache Mock',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Box',
    description: 'Mock cache adapter (planned)'
  },
  {
    id: 'message-publisher',
    name: 'Message Publisher',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Send',
    description: 'Publish messages to broker (planned)'
  },
  
  // Legacy/Compatibility
  {
    id: 'http-client-mock',
    name: 'HTTP Client Mock',
    type: 'outbound',
    category: 'Outbound',
    icon: 'ExternalLink',
    description: 'Mock HTTP client adapter (use http-client instead)'
  }
];

export interface AdapterNode {
  id: string;
  adapterId: string;
  position: { x: number; y: number };
  config: Record<string, any>;
  status: 'connected' | 'disconnected' | 'error';
  portId?: string; // Which port on the shell this adapter connects to
}

export interface MockNode {
  id: string;
  name: string;
  type: 'http' | 'database' | 'message-broker' | 'cache';
  direction: 'inbound' | 'outbound'; // Direction of data flow
  position: { x: number; y: number };
  config: Record<string, any>;
  connectedToAdapter?: string; // Adapter ID this mock connects to
}

export const mockAdapterNodes: AdapterNode[] = [
  // No default adapter nodes - start with empty state
];

export const mockMockNodes: MockNode[] = [
  // No default mock nodes - start with empty state
];
