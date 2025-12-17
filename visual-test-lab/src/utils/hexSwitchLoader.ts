/**
 * HexSwitch Configuration Loader
 * 
 * Utilities to load and parse real hexSwitch configuration files.
 * Reference: ../hex-config.yaml, ../src/hexswitch/config.py
 */

import type { HexSwitchConfig } from '../data/hexSwitchReference';

/**
 * Load hexSwitch configuration from YAML string
 * 
 * Note: This is a simplified parser. For full validation,
 * use the real hexSwitch CLI: hexswitch validate
 * 
 * @param yamlContent YAML configuration content
 * @returns Parsed configuration object
 */
export function parseHexSwitchConfig(yamlContent: string): HexSwitchConfig {
  // This is a placeholder - in a real implementation, you would use a YAML parser
  // For now, we'll return a basic structure
  // In production, use: import yaml from 'js-yaml'; return yaml.load(yamlContent);
  
  try {
    // Basic parsing (simplified - would need proper YAML parser in production)
    const lines = yamlContent.split('\n');
    const config: HexSwitchConfig = {
      service: { name: 'unknown' }
    };
    
    // Simple line-by-line parsing (this is just a placeholder)
    // Real implementation should use js-yaml or similar
    let currentSection: string | null = null;
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      
      if (trimmed.endsWith(':')) {
        currentSection = trimmed.slice(0, -1);
        if (currentSection === 'service') {
          config.service = { name: 'unknown' };
        } else if (currentSection === 'inbound') {
          config.inbound = {};
        } else if (currentSection === 'outbound') {
          config.outbound = {};
        }
      }
    }
    
    return config;
  } catch (error) {
    throw new Error(`Failed to parse hexSwitch config: ${error}`);
  }
}

/**
 * Convert hexSwitch config to Visual Test Lab format
 * 
 * @param config hexSwitch configuration
 * @returns Configuration in Visual Test Lab format
 */
export function convertHexSwitchToVisualLab(config: HexSwitchConfig) {
  const ports: Array<{ id: string; label: string; type: 'inbound' | 'outbound'; edgeIndex: number }> = [];
  const adapters: Array<{
    id: string;
    adapterId: string;
    portId: string;
    config: Record<string, any>;
    status: 'connected' | 'disconnected';
  }> = [];
  
  let edgeIndex = 0;
  
  // Process inbound adapters
  if (config.inbound) {
    for (const [adapterName, adapterConfig] of Object.entries(config.inbound)) {
      if (adapterConfig.enabled) {
        const portId = `port-inbound-${adapterName}`;
        ports.push({
          id: portId,
          label: `${adapterName} (inbound)`,
          type: 'inbound',
          edgeIndex: edgeIndex++
        });
        
        adapters.push({
          id: `adapter-${adapterName}`,
          adapterId: adapterName === 'http' ? 'http-inbound' : adapterName,
          portId,
          config: adapterConfig,
          status: 'connected'
        });
      }
    }
  }
  
  // Process outbound adapters
  if (config.outbound) {
    for (const [adapterName, adapterConfig] of Object.entries(config.outbound)) {
      if (adapterConfig.enabled) {
        const portId = `port-outbound-${adapterName}`;
        ports.push({
          id: portId,
          label: `${adapterName} (outbound)`,
          type: 'outbound',
          edgeIndex: edgeIndex++
        });
        
        adapters.push({
          id: `adapter-${adapterName}`,
          adapterId: adapterName === 'http_client' ? 'http-client' : 
                     adapterName === 'mcp_client' ? 'mcp-client' : adapterName,
          portId,
          config: adapterConfig,
          status: 'connected'
        });
      }
    }
  }
  
  return { ports, adapters };
}

/**
 * Validate hexSwitch configuration structure
 * 
 * Basic validation - for full validation use: hexswitch validate
 * 
 * @param config Configuration to validate
 * @returns Validation result
 */
export function validateHexSwitchConfig(config: HexSwitchConfig): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  if (!config.service) {
    errors.push('Missing required section: service');
  } else if (!config.service.name) {
    errors.push('Service section must contain "name"');
  }
  
  if (config.inbound) {
    for (const [adapterName, adapterConfig] of Object.entries(config.inbound)) {
      if (typeof adapterConfig !== 'object' || adapterConfig === null) {
        errors.push(`Adapter '${adapterName}' in 'inbound' must be an object`);
      } else if ('enabled' in adapterConfig && typeof adapterConfig.enabled !== 'boolean') {
        errors.push(`Adapter '${adapterName}' in 'inbound': 'enabled' must be a boolean`);
      }
    }
  }
  
  if (config.outbound) {
    for (const [adapterName, adapterConfig] of Object.entries(config.outbound)) {
      if (typeof adapterConfig !== 'object' || adapterConfig === null) {
        errors.push(`Adapter '${adapterName}' in 'outbound' must be an object`);
      } else if ('enabled' in adapterConfig && typeof adapterConfig.enabled !== 'boolean') {
        errors.push(`Adapter '${adapterName}' in 'outbound': 'enabled' must be a boolean`);
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

