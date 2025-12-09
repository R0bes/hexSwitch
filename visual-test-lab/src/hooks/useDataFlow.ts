import { useState, useCallback, useRef, useEffect } from 'react';

export interface DataFlowPulse {
  id: string;
  connectionId: string; // Identifier for the connection (e.g., 'mock-http-server->node-http-1')
  startTime: number;
  duration: number; // Duration in ms
  type: 'inbound' | 'outbound' | 'mock-to-adapter' | 'adapter-to-mock';
  color: string;
}

interface UseDataFlowReturn {
  pulses: DataFlowPulse[];
  triggerPulse: (connectionId: string, type: 'inbound' | 'outbound' | 'mock-to-adapter' | 'adapter-to-mock', duration?: number) => void;
  clearPulses: () => void;
}

export function useDataFlow(): UseDataFlowReturn {
  const [pulses, setPulses] = useState<DataFlowPulse[]>([]);
  const pulseIdCounter = useRef(0);

  const triggerPulse = useCallback((
    connectionId: string,
    type: 'inbound' | 'outbound' | 'mock-to-adapter' | 'adapter-to-mock',
    duration: number = 1500
  ) => {
    const pulseId = `pulse-${pulseIdCounter.current++}`;
    let color: string;
    if (type === 'inbound') {
      color = 'var(--accent-inbound-light)';
    } else if (type === 'outbound') {
      color = 'var(--accent-outbound-light)';
    } else if (type === 'mock-to-adapter') {
      color = 'var(--accent-inbound-light)'; // Mocks sending to inbound adapters
    } else { // adapter-to-mock
      color = 'var(--accent-outbound-light)'; // Adapters sending to outbound mocks
    }

    const newPulse: DataFlowPulse = {
      id: pulseId,
      connectionId,
      startTime: Date.now(),
      duration,
      type,
      color
    };

    setPulses(prev => [...prev, newPulse]);

    // Auto-remove pulse after duration
    setTimeout(() => {
      setPulses(prev => prev.filter(p => p.id !== pulseId));
    }, duration);
  }, []);

  const clearPulses = useCallback(() => {
    setPulses([]);
  }, []);

  // Cleanup old pulses
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      setPulses(prev => prev.filter(p => now - p.startTime < p.duration));
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return { pulses, triggerPulse, clearPulses };
}

