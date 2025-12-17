/**
 * hexSwitch API Client
 * 
 * Communicates with the real hexSwitch Python API server
 * to load configurations, validate, and get adapter metadata.
 */

const API_BASE_URL = 'http://localhost:8080';

export interface HexSwitchAdapter {
  id: string;
  name: string;
  type: 'inbound' | 'outbound';
  category: string;
  icon: string;
  description: string;
  source: string;
  configSchema: Record<string, any>;
}

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
 * Check if hexSwitch API server is available
 */
export async function checkAPIAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/adapters`, {
      method: 'GET',
      signal: AbortSignal.timeout(1000)
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Get list of available adapters from real hexSwitch
 */
export async function getAdapters(): Promise<HexSwitchAdapter[]> {
  const response = await fetch(`${API_BASE_URL}/api/adapters`);
  if (!response.ok) {
    throw new Error(`Failed to fetch adapters: ${response.statusText}`);
  }
  const data = await response.json();
  return data.adapters;
}

/**
 * Load configuration from hexSwitch
 */
export async function loadConfig(configPath?: string): Promise<HexSwitchConfig> {
  if (configPath) {
    const response = await fetch(`${API_BASE_URL}/api/config/load`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ path: configPath })
    });
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.statusText}`);
    }
    const data = await response.json();
    return data.config;
  } else {
    const response = await fetch(`${API_BASE_URL}/api/config`);
    if (!response.ok) {
      throw new Error(`Failed to get config: ${response.statusText}`);
    }
    const data = await response.json();
    return data.config;
  }
}

/**
 * Validate configuration using real hexSwitch validator
 */
export async function validateConfig(config: HexSwitchConfig): Promise<{
  valid: boolean;
  error?: string;
}> {
  const response = await fetch(`${API_BASE_URL}/api/config/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ config })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    return { valid: data.valid };
  } else {
    return { valid: false, error: data.error || 'Validation failed' };
  }
}

/**
 * Get execution plan from real hexSwitch
 */
export async function getExecutionPlan(): Promise<ExecutionPlan> {
  const response = await fetch(`${API_BASE_URL}/api/plan`);
  if (!response.ok) {
    throw new Error(`Failed to get execution plan: ${response.statusText}`);
  }
  const data = await response.json();
  return data.plan;
}

