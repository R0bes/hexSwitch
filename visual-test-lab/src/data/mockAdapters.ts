export interface Adapter {
  id: string;
  name: string;
  type: 'inbound' | 'outbound';
  category: string;
  icon: string;
  description: string;
}

export const mockAdapters: Adapter[] = [
  // Inbound Adapters
  {
    id: 'http-inbound',
    name: 'HTTP Adapter',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Globe',
    description: 'HTTP REST API endpoint adapter'
  },
  {
    id: 'grpc-inbound',
    name: 'gRPC Adapter',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Network',
    description: 'gRPC service adapter'
  },
  {
    id: 'message-consumer',
    name: 'Message Consumer',
    type: 'inbound',
    category: 'Inbound',
    icon: 'MessageSquare',
    description: 'Consume messages from broker'
  },
  {
    id: 'scheduler-trigger',
    name: 'Scheduler Trigger',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Clock',
    description: 'Time-based trigger adapter'
  },
  
  // Outbound Adapters
  {
    id: 'db-mock',
    name: 'DB Mock',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Database',
    description: 'Mock database adapter'
  },
  {
    id: 'cache-mock',
    name: 'Cache Mock',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Box',
    description: 'Mock cache adapter'
  },
  {
    id: 'message-publisher',
    name: 'Message Publisher',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Send',
    description: 'Publish messages to broker'
  },
  {
    id: 'http-client-mock',
    name: 'HTTP Client Mock',
    type: 'outbound',
    category: 'Outbound',
    icon: 'ExternalLink',
    description: 'Mock HTTP client adapter'
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
  // Multiple adapters for api-in port
  {
    id: 'node-http-1',
    adapterId: 'http-inbound',
    position: { x: 0, y: 0 }, // Will be calculated on shell edge
    config: {
      method: 'POST',
      path: '/orders',
      handler: 'adapters.http_handlers:createOrder'
    },
    status: 'connected',
    portId: 'api-in'
  },
  {
    id: 'node-grpc-1',
    adapterId: 'grpc-inbound',
    position: { x: 0, y: 0 }, // Will be calculated on shell edge
    config: {
      service: 'OrderService',
      methods: ['CreateOrder', 'GetOrder']
    },
    status: 'connected',
    portId: 'api-in' // Same port as HTTP adapter
  },
  {
    id: 'node-db-1',
    adapterId: 'db-mock',
    position: { x: 0, y: 0 },
    config: {
      type: 'PostgreSQL',
      mode: 'deterministic',
      table: 'orders'
    },
    status: 'connected',
    portId: 'repo-out'
  },
  {
    id: 'node-message-1',
    adapterId: 'message-consumer',
    position: { x: 0, y: 0 },
    config: {
      topic: 'order.events',
      events: ['OrderCreated', 'OrderPaid', 'OrderCancelled']
    },
    status: 'connected',
    portId: 'event-in'
  },
  {
    id: 'node-scheduler-1',
    adapterId: 'scheduler-trigger',
    position: { x: 0, y: 0 },
    config: {
      interval: '5s',
      task: 'PaymentCheck',
      active: true
    },
    status: 'connected',
    portId: 'command-bus'
  },
  {
    id: 'node-http-client-1',
    adapterId: 'http-client-mock',
    position: { x: 0, y: 0 },
    config: {
      endpoint: 'https://payments/charge',
      latency: 150,
      response: { status: 'approved' }
    },
    status: 'connected',
    portId: 'external-api-out'
  }
];

export const mockMockNodes: MockNode[] = [
  {
    id: 'mock-http-server',
    name: 'HTTP Server',
    type: 'http',
    direction: 'inbound', // Mock sends data to adapter (inbound to system)
    position: { x: 0, y: 0 }, // Will be calculated outside shell
    config: {
      endpoint: 'http://api.example.com',
      methods: ['GET', 'POST']
    },
    connectedToAdapter: 'node-http-1' // Connected to HTTP adapter specifically
  },
  {
    id: 'mock-grpc-server',
    name: 'gRPC Server',
    type: 'http', // Using http type for visualization
    direction: 'inbound', // Mock sends data to adapter (inbound to system)
    position: { x: 0, y: 0 }, // Will be calculated outside shell
    config: {
      endpoint: 'grpc://api.example.com:50051',
      service: 'OrderService'
    },
    connectedToAdapter: 'node-grpc-1' // Connected to gRPC adapter specifically
  },
  {
    id: 'mock-database',
    name: 'PostgreSQL Mock',
    type: 'database',
    direction: 'outbound', // Adapter sends data to mock (outbound from system)
    position: { x: 0, y: 0 },
    config: {
      host: 'localhost',
      port: 5432,
      database: 'testdb'
    },
    connectedToAdapter: 'node-db-1'
  },
  {
    id: 'mock-message-broker',
    name: 'NATS Mock',
    type: 'message-broker',
    direction: 'inbound', // Mock sends messages to adapter (inbound to system)
    position: { x: 0, y: 0 },
    config: {
      url: 'nats://localhost:4222',
      topics: ['order.events']
    },
    connectedToAdapter: 'node-message-1'
  },
  {
    id: 'mock-payment-service',
    name: 'Payment Service',
    type: 'http',
    direction: 'outbound', // Adapter sends requests to mock (outbound from system)
    position: { x: 0, y: 0 },
    config: {
      endpoint: 'https://payments.example.com',
      latency: 150
    },
    connectedToAdapter: 'node-http-client-1'
  }
];
