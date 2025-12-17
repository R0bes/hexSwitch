import { useState, useCallback, useRef, useEffect } from 'react';
import type { MockRuntimeEvent, MockRuntimeState } from '../types/runtime';

export function useMockRuntime() {
  const [state, setState] = useState<MockRuntimeState>({
    isActive: false,
    events: [],
    metrics: {
      requestsProcessed: 0,
      eventsEmitted: 0,
      errors: 0,
      uptime: 0
    }
  });

  const startTimeRef = useRef<number>(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const eventIdCounterRef = useRef<number>(0);

  const addEvent = useCallback((event: Omit<MockRuntimeEvent, 'id' | 'timestamp'>) => {
    setState(prev => ({
      ...prev,
      events: [
        ...prev.events.slice(-99), // Keep last 100 events
        {
          ...event,
          id: `event-${eventIdCounterRef.current++}`,
          timestamp: Date.now()
        }
      ]
    }));
  }, []);

  const start = useCallback(() => {
    if (state.isActive) return;

    startTimeRef.current = Date.now();
    setState(prev => ({
      ...prev,
      isActive: true,
      events: [],
      metrics: {
        requestsProcessed: 0,
        eventsEmitted: 0,
        errors: 0,
        uptime: 0
      }
    }));

    // Simulate runtime startup
    addEvent({
      type: 'log',
      source: 'MockRuntime',
      message: 'Starting MockRuntime...'
    });

    setTimeout(() => {
      addEvent({
        type: 'log',
        source: 'MockRuntime',
        message: 'MockRuntime started successfully'
      });
    }, 500);

    // Update uptime every second
    intervalRef.current = setInterval(() => {
      setState(prev => ({
        ...prev,
        metrics: {
          ...prev.metrics,
          uptime: Math.floor((Date.now() - startTimeRef.current) / 1000)
        }
      }));
    }, 1000);

    // Simulate periodic events
    const eventInterval = setInterval(() => {
      if (!state.isActive) {
        clearInterval(eventInterval);
        return;
      }

      // Simulate random events
      const eventTypes = ['log', 'event', 'metric'] as const;
      const randomType = eventTypes[Math.floor(Math.random() * eventTypes.length)];
      
      if (randomType === 'metric') {
        setState(prev => ({
          ...prev,
          metrics: {
            ...prev.metrics,
            requestsProcessed: prev.metrics.requestsProcessed + 1
          }
        }));
      } else if (randomType === 'event') {
        setState(prev => ({
          ...prev,
          metrics: {
            ...prev.metrics,
            eventsEmitted: prev.metrics.eventsEmitted + 1
          }
        }));
      }

      addEvent({
        type: randomType,
        source: 'MockRuntime',
        message: `Mock ${randomType} event`
      });
    }, 3000);
  }, [state.isActive, addEvent]);

  const stop = useCallback(() => {
    if (!state.isActive) return;

    addEvent({
      type: 'log',
      source: 'MockRuntime',
      message: 'Stopping MockRuntime...'
    });

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    setTimeout(() => {
      setState(prev => ({
        ...prev,
        isActive: false
      }));

      addEvent({
        type: 'log',
        source: 'MockRuntime',
        message: 'MockRuntime stopped'
      });
    }, 500);
  }, [state.isActive, addEvent]);

  const simulateRequest = useCallback((portId: string, data?: any) => {
    if (!state.isActive) return;

    setState(prev => ({
      ...prev,
      metrics: {
        ...prev.metrics,
        requestsProcessed: prev.metrics.requestsProcessed + 1
      }
    }));

    addEvent({
      type: 'log',
      source: 'MockRuntime',
      message: `Processing request on port: ${portId}`,
      data: data ? { portId, ...data } : { portId }
    });
  }, [state.isActive, addEvent]);

  const simulateEvent = useCallback((eventName: string, data?: any) => {
    if (!state.isActive) return;

    setState(prev => ({
      ...prev,
      metrics: {
        ...prev.metrics,
        eventsEmitted: prev.metrics.eventsEmitted + 1
      }
    }));

    addEvent({
      type: 'event',
      source: 'MockRuntime',
      message: `Event emitted: ${eventName}`,
      data: data ? { eventName, ...data } : { eventName }
    });
  }, [state.isActive, addEvent]);

  const simulateError = useCallback((errorMessage: string) => {
    if (!state.isActive) return;

    setState(prev => ({
      ...prev,
      metrics: {
        ...prev.metrics,
        errors: prev.metrics.errors + 1
      }
    }));

    addEvent({
      type: 'error',
      source: 'MockRuntime',
      message: errorMessage
    });
  }, [state.isActive, addEvent]);

  const clearEvents = useCallback(() => {
    setState(prev => ({
      ...prev,
      events: []
    }));
  }, []);

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    state,
    start,
    stop,
    simulateRequest,
    simulateEvent,
    simulateError,
    clearEvents
  };
}


