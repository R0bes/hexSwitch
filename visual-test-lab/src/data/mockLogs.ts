export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG';
  source: string;
  message: string;
  target?: string;
}

export const mockLogs: LogEntry[] = [
  {
    timestamp: '12:03:21.421',
    level: 'INFO',
    source: 'HTTP Adapter',
    message: 'POST /orders',
    target: 'Core'
  },
  {
    timestamp: '12:03:21.433',
    level: 'INFO',
    source: 'Core',
    message: 'Insert Order(id=123)',
    target: 'DB Mock'
  },
  {
    timestamp: '12:03:21.450',
    level: 'INFO',
    source: 'Core',
    message: '/charge',
    target: 'Payment Service Mock'
  },
  {
    timestamp: '12:03:21.600',
    level: 'INFO',
    source: 'Payment Service Mock',
    message: 'status=approved',
    target: 'Core'
  },
  {
    timestamp: '12:03:21.650',
    level: 'INFO',
    source: 'Core',
    message: 'Emit OrderCreated event',
    target: 'Message Publisher'
  },
  {
    timestamp: '12:03:21.700',
    level: 'WARN',
    source: 'Scheduler Trigger',
    message: 'PaymentCheck task delayed',
    target: 'Core'
  },
  {
    timestamp: '12:03:22.100',
    level: 'INFO',
    source: 'Message Consumer',
    message: 'Received OrderCreated',
    target: 'Core'
  },
  {
    timestamp: '12:03:22.150',
    level: 'DEBUG',
    source: 'Core',
    message: 'Business logic processing',
    target: undefined
  }
];

export interface Event {
  id: string;
  name: string;
  timestamp: string;
  payload: Record<string, any>;
}

export const mockEvents: Event[] = [
  {
    id: 'evt-001',
    name: 'OrderCreated',
    timestamp: '12:03:21.650',
    payload: { orderId: 123, total: 99.99, status: 'pending' }
  },
  {
    id: 'evt-002',
    name: 'OrderApproved',
    timestamp: '12:03:21.700',
    payload: { orderId: 123, paymentStatus: 'approved' }
  },
  {
    id: 'evt-003',
    name: 'OrderPaid',
    timestamp: '12:03:22.000',
    payload: { orderId: 123, transactionId: 'tx-456' }
  }
];

export interface Trace {
  id: string;
  duration: number;
  timestamp: string;
  spans: Array<{ name: string; duration: number }>;
}

export const mockTraces: Trace[] = [
  {
    id: 'df3a8b2c',
    duration: 182,
    timestamp: '12:03:21.421',
    spans: [
      { name: 'HTTP Adapter', duration: 12 },
      { name: 'Core Logic', duration: 17 },
      { name: 'DB Mock', duration: 50 },
      { name: 'Payment Mock', duration: 150 },
      { name: 'Event Emit', duration: 50 }
    ]
  },
  {
    id: 'a1b2c3d4',
    duration: 95,
    timestamp: '12:03:22.100',
    spans: [
      { name: 'Message Consumer', duration: 10 },
      { name: 'Core Logic', duration: 45 },
      { name: 'Event Processing', duration: 40 }
    ]
  }
];

