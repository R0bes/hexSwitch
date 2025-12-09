import { useMemo, useState, useEffect, useRef } from 'react';
import CoreCircle from './CoreCircle';
import HexagonalShell from './HexagonalShell';
import AdapterNode from './AdapterNode';
import MockNode from './MockNode';
import ConnectionLine from './ConnectionLine';
import DashedConnectionLine from './DashedConnectionLine';
import { mockAdapterNodes, mockMockNodes, mockAdapters } from '../data/mockAdapters';
import { getAdapterPositionOnShell, getMockPosition, getEdgeCenter } from '../utils/hexagonGeometry';
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { DataFlowPulse } from '../hooks/useDataFlow';

// Port mapping: portId -> edgeIndex
const portToEdgeIndex: Record<string, number> = {
  'api-in': 0,
  'command-bus': 1,
  'event-in': 2,
  'repo-out': 3,
  'message-out': 4,
  'external-api-out': 5
};

interface HexagonalCanvasProps {
  selectedAdapterId: string | null;
  activePulses?: DataFlowPulse[];
}

export default function HexagonalCanvas({ selectedAdapterId, activePulses = [] }: HexagonalCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  
  // Fixed canvas size for consistent rendering - increased for better spacing
  const canvasWidth = 1400;
  const canvasHeight = 1000;
  const centerX = canvasWidth / 2;
  const centerY = canvasHeight / 2;
  const coreRadius = 100;
  const shellThickness = 120; // Much thicker shell for routing layer
  const shellRadius = coreRadius + shellThickness;
  const mockDistance = 280; // Distance from outer shell edge to mocks

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Calculate adapter positions on outer shell edge
  // Group adapters by port and distribute them around the port
  const adapterPositions = useMemo(() => {
    // Group adapters by portId
    const adaptersByPort = mockAdapterNodes.reduce((acc, node) => {
      if (!node.portId) return acc;
      if (!acc[node.portId]) acc[node.portId] = [];
      acc[node.portId].push(node);
      return acc;
    }, {} as Record<string, typeof mockAdapterNodes>);

    // Calculate positions for each adapter
    return mockAdapterNodes.map((node) => {
      if (!node.portId) return { nodeId: node.id, x: 0, y: 0, portId: undefined };
      
      const edgeIndex = portToEdgeIndex[node.portId];
      const adaptersOnPort = adaptersByPort[node.portId] || [];
      const adapterIndex = adaptersOnPort.findIndex(n => n.id === node.id);
      const totalAdaptersOnPort = adaptersOnPort.length;
      
      // Position adapters on the outer edge of the shell, distributed around the port
      const pos = getAdapterPositionOnShell(
        centerX, 
        centerY, 
        shellRadius, 
        edgeIndex,
        adapterIndex,
        totalAdaptersOnPort
      );
      return { nodeId: node.id, x: pos.x, y: pos.y, portId: node.portId };
    });
  }, [centerX, centerY, shellRadius]);

  // Calculate mock positions outside shell
  const mockPositions = useMemo(() => {
    return mockMockNodes.map((mock) => {
      const adapter = mockAdapterNodes.find(a => a.id === mock.connectedToAdapter);
      if (!adapter || !adapter.portId) return { mockId: mock.id, x: 0, y: 0 };
      
      const edgeIndex = portToEdgeIndex[adapter.portId];
      const pos = getMockPosition(centerX, centerY, shellRadius, edgeIndex, mockDistance);
      return { mockId: mock.id, x: pos.x, y: pos.y, adapterId: mock.connectedToAdapter };
    });
  }, []);

  // Routing lines: Ports (inner shell) to Adapters (outer shell)
  // For inbound: flow from adapter to port (towards core)
  // For outbound: flow from port to adapter (away from core)
  const portToAdapterRouting = useMemo(() => {
    return adapterPositions.map((adapterPos) => {
      const node = mockAdapterNodes.find(n => n.id === adapterPos.nodeId);
      if (!node || !node.portId) return null;
      
      const edgeIndex = portToEdgeIndex[node.portId];
      // Port position on inner shell edge (at core radius)
      const portPos = getEdgeCenter(centerX, centerY, coreRadius, edgeIndex);
      
      // Determine if adapter is inbound or outbound based on adapter type
      const adapter = mockAdapters.find(a => a.id === node.adapterId);
      const isInbound = adapter?.type === 'inbound';
      
      // For inbound: adapter -> port (towards core)
      // For outbound: port -> adapter (away from core)
      if (isInbound) {
        return {
          x1: adapterPos.x,
          y1: adapterPos.y,
          x2: portPos.x,
          y2: portPos.y,
          type: 'inbound' as const,
          connectionId: `routing-${node.portId}-${node.id}`
        };
      } else {
        return {
          x1: portPos.x,
          y1: portPos.y,
          x2: adapterPos.x,
          y2: adapterPos.y,
          type: 'outbound' as const,
          connectionId: `routing-${node.portId}-${node.id}`
        };
      }
    }).filter(Boolean) as Array<{ x1: number; y1: number; x2: number; y2: number; type: 'inbound' | 'outbound'; connectionId: string }>;
  }, [adapterPositions, centerX, centerY, coreRadius]);

  // Connection lines from core to ports (through inner shell edge)
  // For inbound: flow from port to core (towards core)
  // For outbound: flow from core to port (away from core)
  // Only one line per port (not per adapter)
  const coreToPortConnections = useMemo(() => {
    // Get unique ports
    const uniquePorts = Array.from(new Set(mockAdapterNodes.filter(n => n.portId).map(n => n.portId!)));
    
    return uniquePorts.map((portId) => {
      const edgeIndex = portToEdgeIndex[portId];
      const portPos = getEdgeCenter(centerX, centerY, coreRadius, edgeIndex);
      
      // Determine port type from first adapter on this port
      const firstAdapterOnPort = mockAdapterNodes.find(n => n.portId === portId);
      if (!firstAdapterOnPort) return null;
      
      const adapter = mockAdapters.find(a => a.id === firstAdapterOnPort.adapterId);
      const isInbound = adapter?.type === 'inbound';
      
      // For inbound: port -> core (towards core)
      // For outbound: core -> port (away from core)
      if (isInbound) {
        return {
          x1: portPos.x,
          y1: portPos.y,
          x2: centerX,
          y2: centerY,
          type: 'inbound' as const,
          connectionId: `core-port-${portId}`
        };
      } else {
        return {
          x1: centerX,
          y1: centerY,
          x2: portPos.x,
          y2: portPos.y,
          type: 'outbound' as const,
          connectionId: `core-port-${portId}`
        };
      }
    }).filter(Boolean) as Array<{ x1: number; y1: number; x2: number; y2: number; type: 'inbound' | 'outbound'; connectionId: string }>;
  }, [centerX, centerY, coreRadius]);

  // Dashed connection lines from mocks to adapters
  // Direction depends on mock direction:
  // - Inbound mocks: Mock -> Adapter (mock sends to adapter)
  // - Outbound mocks: Adapter -> Mock (adapter sends to mock)
  const mockToAdapterConnections = useMemo(() => {
    return mockPositions.map((mockPos) => {
      const adapterPos = adapterPositions.find(a => a.nodeId === mockPos.adapterId);
      if (!adapterPos) return null;
      
      const mock = mockMockNodes.find(m => m.id === mockPos.mockId);
      const isInbound = mock?.direction === 'inbound';
      
      // For inbound mocks: Mock -> Adapter (mock sends to adapter)
      // For outbound mocks: Adapter -> Mock (adapter sends to mock)
      if (isInbound) {
        return {
          x1: mockPos.x,
          y1: mockPos.y,
          x2: adapterPos.x,
          y2: adapterPos.y,
          direction: 'mock-to-adapter' as const
        };
      } else {
        return {
          x1: adapterPos.x,
          y1: adapterPos.y,
          x2: mockPos.x,
          y2: mockPos.y,
          direction: 'adapter-to-mock' as const
        };
      }
    }).filter(Boolean) as Array<{ x1: number; y1: number; x2: number; y2: number; direction: 'mock-to-adapter' | 'adapter-to-mock' }>;
  }, [mockPositions, adapterPositions]);

  // Zoom handlers
  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom(prev => Math.max(0.5, Math.min(3, prev + delta)));
  };

  return (
    <div 
      ref={containerRef}
      data-canvas-container
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        cursor: isPanning ? 'grabbing' : 'grab'
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >

      {/* Zoom Controls */}
      <div style={{
        position: 'absolute',
        top: 'var(--spacing-md)',
        right: 'var(--spacing-md)',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--spacing-xs)',
        background: 'var(--bg-secondary)',
        padding: 'var(--spacing-sm)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-lg)'
      }}>
        <button
          onClick={handleZoomIn}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            padding: 'var(--spacing-xs)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all var(--transition-normal)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.boxShadow = 'var(--glow-teal)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <ZoomIn size={18} />
        </button>
        <button
          onClick={handleZoomOut}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            padding: 'var(--spacing-xs)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all var(--transition-normal)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.boxShadow = 'var(--glow-teal)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <ZoomOut size={18} />
        </button>
        <button
          onClick={handleResetZoom}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            padding: 'var(--spacing-xs)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all var(--transition-normal)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.boxShadow = 'var(--glow-teal)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          <Maximize2 size={18} />
        </button>
        <div style={{
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
          marginTop: 'var(--spacing-xs)',
          paddingTop: 'var(--spacing-xs)',
          borderTop: '1px solid var(--border-color)'
        }}>
          {Math.round(zoom * 100)}%
        </div>
      </div>

      {/* SVG Canvas with zoom and pan */}
      <svg
        width={dimensions.width}
        height={dimensions.height}
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        style={{
          position: 'absolute',
          top: 0,
          left: 0
        }}
      >
        <g
          transform={`translate(${dimensions.width / 2 + pan.x}, ${dimensions.height / 2 + pan.y}) scale(${zoom}) translate(${-centerX}, ${-centerY})`}
        >
          {/* Dashed connections: Mocks to Adapters */}
          {mockToAdapterConnections.map((conn, index) => {
            const mock = mockPositions.find(m => {
              const adapterPos = adapterPositions.find(a => a.nodeId === m.adapterId);
              if (conn.direction === 'mock-to-adapter') {
                return adapterPos && adapterPos.x === conn.x2 && adapterPos.y === conn.y2;
              } else {
                return adapterPos && adapterPos.x === conn.x1 && adapterPos.y === conn.y1;
              }
            });
            const mockNode = mock ? mockMockNodes.find(m => m.id === mock.mockId) : null;
            const connectionId = mock ? `mock-${mock.mockId}->adapter-${mock.adapterId}` : `mock-conn-${index}`;
            const lineColor = mockNode?.direction === 'inbound' 
              ? 'var(--accent-inbound-dark)' 
              : 'var(--accent-outbound-dark)';
            
            return (
              <DashedConnectionLine
                key={`mock-conn-${index}`}
                x1={conn.x1}
                y1={conn.y1}
                x2={conn.x2}
                y2={conn.y2}
                activePulses={activePulses}
                connectionId={connectionId}
                direction={conn.direction}
                color={lineColor}
              />
            );
          })}
          
          {/* Routing lines: Ports (inner shell) to Adapters (outer shell) */}
          {portToAdapterRouting.map((conn, index) => {
            const adapterPos = adapterPositions[index];
            const node = mockAdapterNodes.find(n => n.id === adapterPos?.nodeId);
            const connectionId = node ? `routing-${node.portId}-${node.id}` : `routing-${index}`;
            
            return (
              <ConnectionLine
                key={`routing-${index}`}
                x1={conn.x1}
                y1={conn.y1}
                x2={conn.x2}
                y2={conn.y2}
                type={conn.type}
                activePulses={activePulses}
                connectionId={connectionId}
              />
            );
          })}
          
          {/* Core to Port connections */}
          {coreToPortConnections.map((conn, index) => {
            const node = mockAdapterNodes.filter(n => n.portId)[index];
            const connectionId = node ? `core-port-${node.portId}` : `core-port-${index}`;
            
            return (
              <ConnectionLine
                key={`core-port-${index}`}
                x1={conn.x1}
                y1={conn.y1}
                x2={conn.x2}
                y2={conn.y2}
                type={conn.type}
                activePulses={activePulses}
                connectionId={connectionId}
              />
            );
          })}
          
          {/* Core Circle */}
          <CoreCircle
            centerX={centerX}
            centerY={centerY}
            radius={coreRadius}
          />
          
          {/* Hexagonal Shell */}
          <HexagonalShell
            centerX={centerX}
            centerY={centerY}
            innerRadius={coreRadius}
            shellThickness={shellThickness}
          />
          
          {/* Adapter Nodes on outer shell edge */}
          {adapterPositions.map((pos) => {
            const node = mockAdapterNodes.find(n => n.id === pos.nodeId);
            const isHighlighted = selectedAdapterId ? node?.adapterId === selectedAdapterId : false;
            
            return (
              <AdapterNode
                key={pos.nodeId}
                nodeId={pos.nodeId}
                x={pos.x}
                y={pos.y}
                isHighlighted={isHighlighted}
              />
            );
          })}
          
          {/* Mock Nodes outside Shell */}
          {mockPositions.map((pos) => {
            const mock = mockMockNodes.find(m => m.id === pos.mockId);
            const connectedAdapter = mockAdapterNodes.find(a => a.id === mock?.connectedToAdapter);
            const isHighlighted = selectedAdapterId ? connectedAdapter?.adapterId === selectedAdapterId : false;
            
            return (
              <MockNode
                key={pos.mockId}
                mockId={pos.mockId}
                x={pos.x}
                y={pos.y}
                isHighlighted={isHighlighted}
              />
            );
          })}
        </g>
      </svg>
    </div>
  );
}
