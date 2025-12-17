export type RuntimeType = 'real' | 'mock';

export interface RuntimeConfig {
  type: RuntimeType;
  name: string;
  version?: string;
  status: 'stopped' | 'starting' | 'running' | 'stopping' | 'error';
}

export interface MockRuntimeEvent {
  id: string;
  timestamp: number;
  type: 'log' | 'event' | 'metric' | 'error';
  source: string;
  message: string;
  data?: Record<string, any>;
}

export interface MockRuntimeState {
  isActive: boolean;
  events: MockRuntimeEvent[];
  metrics: {
    requestsProcessed: number;
    eventsEmitted: number;
    errors: number;
    uptime: number;
  };
}


