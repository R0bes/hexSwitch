import { getHexagonPath, getEdgeCenter } from '../utils/hexagonGeometry';
import { useElementSelectionContext } from '../contexts/ElementSelectionContext';

export interface Port {
  id: string;
  label: string;
  edgeIndex: number;
  type: 'inbound' | 'outbound';
  config?: Record<string, any>;
}

interface CoreHexagonProps {
  centerX: number;
  centerY: number;
  radius: number;
  ports: Port[];
  onPortDragStart?: (e: React.MouseEvent, portId: string, position: { x: number; y: number }) => void;
  dragState?: {
    isDragging: boolean;
    draggedId: string | null;
    draggedType: 'port' | null;
    currentPosition: { x: number; y: number } | null;
  };
}

export default function CoreHexagon({ centerX, centerY, radius, ports, onPortDragStart, dragState }: CoreHexagonProps) {
  const { isSelected, toggleSelection } = useElementSelectionContext();
  const hexPath = getHexagonPath(centerX, centerY, radius);

  return (
    <g>
      {/* Hexagon with glow effect */}
      <defs>
        <filter id="hex-glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Outer glow */}
      <path
        d={hexPath}
        fill="none"
        stroke="var(--accent-teal)"
        strokeWidth="2"
        opacity="0.3"
        filter="url(#hex-glow)"
      />
      
      {/* Main hexagon */}
      <path
        d={hexPath}
        fill="var(--bg-secondary)"
        stroke="var(--accent-teal)"
        strokeWidth="2"
        style={{
          filter: 'drop-shadow(var(--glow-teal))'
        }}
      />
      
      {/* Internal pattern (subtle grid) */}
      <path
        d={hexPath}
        fill="url(#hex-pattern)"
        opacity="0.1"
      />
      
      <defs>
        <pattern id="hex-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
          <path
            d="M 0 10 L 10 0 L 20 10 L 10 20 Z"
            fill="none"
            stroke="var(--accent-teal)"
            strokeWidth="0.5"
            opacity="0.3"
          />
        </pattern>
      </defs>

      {/* Ports */}
      {ports.map(port => {
        const edgeCenter = getEdgeCenter(centerX, centerY, radius, port.edgeIndex);
        const portColor = port.type === 'inbound' ? 'var(--accent-cyan)' : 'var(--accent-magenta)';
        const isSelectedPort = isSelected('port', port.id);
        const finalPortColor = isSelectedPort ? 'var(--accent-teal)' : portColor;
        const isDragging = dragState?.isDragging && dragState.draggedId === port.id && dragState.draggedType === 'port';
        const displayPos = isDragging && dragState.currentPosition ? dragState.currentPosition : edgeCenter;
        
        const handlePortClick = (e: React.MouseEvent) => {
          e.stopPropagation();
          toggleSelection('port', port.id);
        };
        
        const handleMouseDown = (e: React.MouseEvent) => {
          if (e.button === 0 && onPortDragStart) {
            e.stopPropagation();
            onPortDragStart(e, port.id, edgeCenter);
          }
        };
        
        return (
          <g 
            key={port.id} 
            onClick={handlePortClick}
            onMouseDown={handleMouseDown}
            data-draggable="port"
            style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
          >
            {/* Connection line from edge to port */}
            <line
              x1={displayPos.x}
              y1={displayPos.y}
              x2={displayPos.x + (port.type === 'inbound' ? -15 : 15)}
              y2={displayPos.y}
              stroke={finalPortColor}
              strokeWidth={isSelectedPort ? '2' : '1'}
              opacity={isSelectedPort ? '0.8' : '0.5'}
            />
            
            {/* Port circle */}
            <circle
              cx={displayPos.x + (port.type === 'inbound' ? -15 : 15)}
              cy={displayPos.y}
              r={isSelectedPort ? '8' : '6'}
              fill={finalPortColor}
              stroke="var(--bg-primary)"
              strokeWidth={isSelectedPort ? '3' : '2'}
              style={{
                filter: isSelectedPort 
                  ? 'drop-shadow(0 0 8px var(--accent-teal))'
                  : `drop-shadow(0 0 4px ${portColor})`,
                transition: isDragging ? 'none' : 'all var(--transition-normal)'
              }}
            />
            
            {/* Port label with background */}
            <g>
              <rect
                x={displayPos.x + (port.type === 'inbound' ? -30 : 20) - (port.label.length * 3.5)}
                y={displayPos.y - 7}
                width={port.label.length * 7}
                height="14"
                rx="6"
                fill="var(--bg-secondary)"
                opacity="0.95"
                stroke={finalPortColor}
                strokeWidth={isSelectedPort ? '1' : '0.5'}
                style={{
                  filter: isSelectedPort
                    ? 'drop-shadow(0 0 4px var(--accent-teal))'
                    : `drop-shadow(0 0 2px ${portColor})`
                }}
              />
              <text
                x={displayPos.x + (port.type === 'inbound' ? -30 : 20)}
                y={displayPos.y + 3}
                fill={portColor}
                fontSize="9"
                fontWeight="600"
                textAnchor="middle"
                style={{ userSelect: 'none' }}
              >
                {port.label}
              </text>
            </g>
          </g>
        );
      })}

      {/* Core label */}
      <text
        x={centerX}
        y={centerY - 10}
        fill="var(--text-primary)"
        fontSize="14"
        fontWeight="600"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        Core Service
      </text>
      <text
        x={centerX}
        y={centerY + 8}
        fill="var(--text-secondary)"
        fontSize="11"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        Business Logic
      </text>
      
      {/* Lock icon hint */}
      <g transform={`translate(${centerX + radius - 15}, ${centerY - radius + 20})`}>
        <circle cx="0" cy="0" r="8" fill="var(--bg-tertiary)" opacity="0.5" />
        <text
          x="0"
          y="3"
          fill="var(--text-muted)"
          fontSize="10"
          textAnchor="middle"
          style={{ userSelect: 'none' }}
        >
          🔒
        </text>
      </g>
    </g>
  );
}

