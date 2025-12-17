import { useState, useCallback, useEffect } from 'react';
import type { AdapterNode, MockNode } from '../data/mockAdapters';

export interface Port {
  id: string;
  label: string;
  edgeIndex: number;
  type: 'inbound' | 'outbound';
  config?: Record<string, any>;
}

interface ConfigurationState {
  adapterNodes: AdapterNode[];
  mockNodes: MockNode[];
  ports: Port[];
}

const STORAGE_KEY = 'hexswitch-visual-test-lab-config';

// Load initial state from localStorage or load from hexSwitch config
function loadInitialState(): ConfigurationState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return {
        adapterNodes: parsed.adapterNodes || [],
        mockNodes: parsed.mockNodes || [],
        ports: parsed.ports || []
      };
    }
  } catch (error) {
    console.warn('Failed to load configuration from localStorage:', error);
  }
  
  // Return empty state - will be loaded from hexSwitch config
  return {
    adapterNodes: [],
    mockNodes: [],
    ports: []
  };
}

export function useConfiguration() {
  const [state, setState] = useState<ConfigurationState>(loadInitialState);

  // Save to localStorage whenever state changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.warn('Failed to save configuration to localStorage:', error);
    }
  }, [state]);

  // Don't auto-load from hexSwitch config - start with empty state
  // Users can manually load config if needed

  // Adapter Node operations
  const addAdapterNode = useCallback((adapterNode: AdapterNode) => {
    setState(prev => ({
      ...prev,
      adapterNodes: [...prev.adapterNodes, adapterNode]
    }));
  }, []);

  const removeAdapterNode = useCallback((nodeId: string) => {
    setState(prev => ({
      ...prev,
      adapterNodes: prev.adapterNodes.filter(node => node.id !== nodeId),
      mockNodes: prev.mockNodes.filter(mock => mock.connectedToAdapter !== nodeId)
    }));
  }, []);

  const updateAdapterNode = useCallback((nodeId: string, updates: Partial<AdapterNode>) => {
    setState(prev => ({
      ...prev,
      adapterNodes: prev.adapterNodes.map(node =>
        node.id === nodeId ? { ...node, ...updates } : node
      )
    }));
  }, []);

  const updateAdapterConfig = useCallback((nodeId: string, config: Record<string, any>) => {
    updateAdapterNode(nodeId, { config });
  }, [updateAdapterNode]);

  // Mock Node operations
  const addMockNode = useCallback((mockNode: MockNode) => {
    setState(prev => ({
      ...prev,
      mockNodes: [...prev.mockNodes, mockNode]
    }));
  }, []);

  const removeMockNode = useCallback((mockId: string) => {
    setState(prev => ({
      ...prev,
      mockNodes: prev.mockNodes.filter(mock => mock.id !== mockId)
    }));
  }, []);

  const updateMockNode = useCallback((mockId: string, updates: Partial<MockNode>) => {
    setState(prev => ({
      ...prev,
      mockNodes: prev.mockNodes.map(mock =>
        mock.id === mockId ? { ...mock, ...updates } : mock
      )
    }));
  }, []);

  const updateMockConfig = useCallback((mockId: string, config: Record<string, any>) => {
    updateMockNode(mockId, { config });
  }, [updateMockNode]);

  // Port operations
  const updatePort = useCallback((portId: string, updates: Partial<Port>) => {
    setState(prev => ({
      ...prev,
      ports: prev.ports.map(port =>
        port.id === portId ? { ...port, ...updates } : port
      )
    }));
  }, []);

  const updatePortConfig = useCallback((portId: string, config: Record<string, any>) => {
    updatePort(portId, { config });
  }, [updatePort]);

  const addPort = useCallback((port: Port) => {
    setState(prev => ({
      ...prev,
      ports: [...prev.ports, port]
    }));
  }, []);

  const removePort = useCallback((portId: string) => {
    setState(prev => ({
      ...prev,
      ports: prev.ports.filter(port => port.id !== portId),
      adapterNodes: prev.adapterNodes.filter(node => node.portId !== portId)
    }));
  }, []);

  // Bulk operations
  const setAdapterNodes = useCallback((nodes: AdapterNode[]) => {
    setState(prev => ({ ...prev, adapterNodes: nodes }));
  }, []);

  const setMockNodes = useCallback((nodes: MockNode[]) => {
    setState(prev => ({ ...prev, mockNodes: nodes }));
  }, []);

  const reset = useCallback(() => {
    setState({
      adapterNodes: [],
      mockNodes: [],
      ports: []
    });
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    // State
    adapterNodes: state.adapterNodes,
    mockNodes: state.mockNodes,
    ports: state.ports,
    
    // Adapter Node operations
    addAdapterNode,
    removeAdapterNode,
    updateAdapterNode,
    updateAdapterConfig,
    setAdapterNodes,
    
    // Mock Node operations
    addMockNode,
    removeMockNode,
    updateMockNode,
    updateMockConfig,
    setMockNodes,
    
    // Port operations
    updatePort,
    updatePortConfig,
    addPort,
    removePort,
    
    // Utility
    reset
  };
}

