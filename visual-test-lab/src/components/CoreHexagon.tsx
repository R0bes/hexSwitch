import { getHexagonPath, getEdgeCenter } from '../utils/hexagonGeometry';

interface Port {
  id: string;
  label: string;
  edgeIndex: number;
  type: 'inbound' | 'outbound';
}

interface CoreHexagonProps {
  centerX: number;
  centerY: number;
  radius: number;
}

const ports: Port[] = [
  { id: 'api-in', label: 'API In', edgeIndex: 0, type: 'inbound' },
  { id: 'command-bus', label: 'Command Bus', edgeIndex: 1, type: 'inbound' },
  { id: 'event-in', label: 'Event In', edgeIndex: 2, type: 'inbound' },
  { id: 'repo-out', label: 'Repository Out', edgeIndex: 3, type: 'outbound' },
  { id: 'message-out', label: 'Message Out', edgeIndex: 4, type: 'outbound' },
  { id: 'external-api-out', label: 'External API Out', edgeIndex: 5, type: 'outbound' }
];

export default function CoreHexagon({ centerX, centerY, radius }: CoreHexagonProps) {
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
        
        return (
          <g key={port.id}>
            {/* Connection line from edge to port */}
            <line
              x1={edgeCenter.x}
              y1={edgeCenter.y}
              x2={edgeCenter.x + (port.type === 'inbound' ? -15 : 15)}
              y2={edgeCenter.y}
              stroke={portColor}
              strokeWidth="1"
              opacity="0.5"
            />
            
            {/* Port circle */}
            <circle
              cx={edgeCenter.x + (port.type === 'inbound' ? -15 : 15)}
              cy={edgeCenter.y}
              r="6"
              fill={portColor}
              stroke="var(--bg-primary)"
              strokeWidth="2"
              style={{
                filter: `drop-shadow(0 0 4px ${portColor})`
              }}
            />
            
            {/* Port label with background */}
            <g>
              <rect
                x={edgeCenter.x + (port.type === 'inbound' ? -30 : 20) - (port.label.length * 3.5)}
                y={edgeCenter.y - 7}
                width={port.label.length * 7}
                height="14"
                rx="6"
                fill="var(--bg-secondary)"
                opacity="0.95"
                stroke={portColor}
                strokeWidth="0.5"
                style={{
                  filter: `drop-shadow(0 0 2px ${portColor})`
                }}
              />
              <text
                x={edgeCenter.x + (port.type === 'inbound' ? -30 : 20)}
                y={edgeCenter.y + 3}
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

