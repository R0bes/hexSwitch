/**
 * Real hexSwitch Adapters
 * 
 * This file loads adapters from the real hexSwitch implementation
 * via the hexSwitch API server.
 */

import { getAdapters, checkAPIAvailable, type HexSwitchAdapter } from '../services/hexSwitchAPI';
import type { Adapter } from './mockAdapters';

// Fallback adapters if API is not available
const FALLBACK_ADAPTERS: Adapter[] = [
  {
    id: 'http',
    name: 'HTTP Adapter',
    type: 'inbound',
    category: 'Inbound',
    icon: 'Globe',
    description: 'HTTP REST API endpoint adapter (real: src/hexswitch/adapters/http/adapter.py)'
  },
  {
    id: 'http_client',
    name: 'HTTP Client',
    type: 'outbound',
    category: 'Outbound',
    icon: 'ExternalLink',
    description: 'HTTP client adapter (real: src/hexswitch/adapters/http_client/adapter.py)'
  },
  {
    id: 'mcp_client',
    name: 'MCP Client',
    type: 'outbound',
    category: 'Outbound',
    icon: 'Server',
    description: 'MCP client adapter (real: src/hexswitch/adapters/mcp_client/adapter.py)'
  }
];

/**
 * Convert hexSwitch adapter to Visual Test Lab format
 */
function convertAdapter(hexAdapter: HexSwitchAdapter): Adapter {
  // Map icons
  const iconMap: Record<string, string> = {
    'Globe': 'Globe',
    'ExternalLink': 'ExternalLink',
    'Server': 'Server'
  };
  
  return {
    id: hexAdapter.id,
    name: hexAdapter.name,
    type: hexAdapter.type,
    category: hexAdapter.category,
    icon: iconMap[hexAdapter.icon] || 'Globe',
    description: hexAdapter.description
  };
}

/**
 * Load real adapters from hexSwitch API
 */
let cachedAdapters: Adapter[] | null = null;
let adapterPromise: Promise<Adapter[]> | null = null;

export async function loadRealAdapters(): Promise<Adapter[]> {
  // Return cached if available
  if (cachedAdapters) {
    return cachedAdapters;
  }
  
  // Return existing promise if loading
  if (adapterPromise) {
    return adapterPromise;
  }
  
  // Start loading
  adapterPromise = (async () => {
    try {
      const available = await checkAPIAvailable();
      if (!available) {
        console.warn('hexSwitch API not available, using fallback adapters');
        cachedAdapters = FALLBACK_ADAPTERS;
        return FALLBACK_ADAPTERS;
      }
      
      const hexAdapters = await getAdapters();
      cachedAdapters = hexAdapters.map(convertAdapter);
      return cachedAdapters;
    } catch (error) {
      console.error('Failed to load adapters from hexSwitch API:', error);
      cachedAdapters = FALLBACK_ADAPTERS;
      return FALLBACK_ADAPTERS;
    } finally {
      adapterPromise = null;
    }
  })();
  
  return adapterPromise;
}

/**
 * Get adapters (synchronous, returns cached or fallback)
 */
export function getAdaptersSync(): Adapter[] {
  return cachedAdapters || FALLBACK_ADAPTERS;
}

