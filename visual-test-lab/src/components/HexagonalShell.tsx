import { getHexagonPath, getEdgeCenter } from '../utils/hexagonGeometry';

interface Port {
  id: string;
  label: string;
  edgeIndex: number;
  type: 'inbound' | 'outbound';
}

interface HexagonalShellProps {
  centerX: number;
  centerY: number;
  innerRadius: number; // Radius of the core circle
  shellThickness: number; // Thickness of the hexagonal shell
}

const ports: Port[] = [
  { id: 'api-in', label: 'API In', edgeIndex: 0, type: 'inbound' },
  { id: 'command-bus', label: 'Command Bus', edgeIndex: 1, type: 'inbound' },
  { id: 'event-in', label: 'Event In', edgeIndex: 2, type: 'inbound' },
  { id: 'repo-out', label: 'Repository Out', edgeIndex: 3, type: 'outbound' },
  { id: 'message-out', label: 'Message Out', edgeIndex: 4, type: 'outbound' },
  { id: 'external-api-out', label: 'External API Out', edgeIndex: 5, type: 'outbound' }
];

export default function HexagonalShell({ centerX, centerY, innerRadius, shellThickness }: HexagonalShellProps) {
  const outerRadius = innerRadius + shellThickness;
  const innerHexPath = getHexagonPath(centerX, centerY, innerRadius);
  const outerHexPath = getHexagonPath(centerX, centerY, outerRadius);

  return (
    <g>
      <defs>
        <filter id="shell-glow">
          <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        {/* Pattern for routing layer */}
        <pattern id="routing-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
          <path
            d="M 0 10 L 20 10 M 10 0 L 10 20"
            stroke="var(--accent-shell)"
            strokeWidth="0.5"
            opacity="0.2"
          />
        </pattern>
      </defs>
      
      {/* Outer glow */}
      <path
        d={outerHexPath}
        fill="none"
        stroke="var(--accent-shell)"
        strokeWidth="1"
        opacity="0.2"
        style={{
          filter: 'blur(3px)'
        }}
      />
      
      {/* Hexagonal shell - outer hexagon */}
      <path
        d={outerHexPath}
        fill="none"
        stroke="var(--accent-shell)"
        strokeWidth="2.5"
        opacity="0.7"
        style={{
          filter: 'drop-shadow(var(--glow-shell))'
        }}
      />
      
      {/* Hexagonal shell - inner hexagon */}
      <path
        d={innerHexPath}
        fill="none"
        stroke="var(--accent-shell)"
        strokeWidth="2"
        opacity="0.6"
        style={{
          filter: 'drop-shadow(0 0 8px rgba(6, 182, 212, 0.3))'
        }}
      />
      
      {/* Fill the shell area (routing layer) */}
      <path
        d={`${outerHexPath} ${innerHexPath.replace('M', 'M').replace(/Z$/, '')} Z`}
        fill="url(#routing-pattern)"
        fillRule="evenodd"
        opacity="0.15"
        stroke="none"
      />
      
      {/* Additional fill for better visibility */}
      <path
        d={`${outerHexPath} ${innerHexPath.replace('M', 'M').replace(/Z$/, '')} Z`}
        fill="var(--bg-secondary)"
        fillRule="evenodd"
        opacity="0.2"
        stroke="none"
      />

      {/* Ports on the inner shell edge (at core radius) */}
      {ports.map(port => {
        const portPos = getEdgeCenter(centerX, centerY, innerRadius, port.edgeIndex);
        const portColor = port.type === 'inbound' ? 'var(--accent-inbound-light)' : 'var(--accent-outbound-light)';
        
        return (
          <g key={port.id}>
            {/* Port circle on inner shell edge */}
            <circle
              cx={portPos.x}
              cy={portPos.y}
              r="10"
              fill={portColor}
              stroke="var(--bg-primary)"
              strokeWidth="2.5"
              style={{
                filter: `drop-shadow(0 0 8px ${portColor})`
              }}
            />
            
            {/* Port label card */}
            <g>
              {/* Calculate card dimensions and position */}
              {(() => {
                const cardWidth = Math.max(port.label.length * 6.5, 70);
                const cardHeight = 20;
                const cardX = portPos.x - (cardWidth / 2);
                // For inbound: card above port (negative offset)
                // For outbound: card below port (positive offset)
                const cardY = portPos.y + (port.type === 'inbound' ? -32 : 12);
                
                return (
                  <>
                    {/* Card shadow */}
                    <rect
                      x={cardX - 1}
                      y={cardY - 1}
                      width={cardWidth + 2}
                      height={cardHeight + 2}
                      rx="9"
                      fill="var(--bg-primary)"
                      opacity="0.4"
                    />
                    
                    {/* Card background */}
                    <rect
                      x={cardX}
                      y={cardY}
                      width={cardWidth}
                      height={cardHeight}
                      rx="9"
                      fill="var(--bg-secondary)"
                      stroke={portColor}
                      strokeWidth="1.5"
                      style={{
                        filter: `drop-shadow(0 0 6px ${portColor})`
                      }}
                    />
                    
                    {/* Text with outline for better readability */}
                    <text
                      x={portPos.x}
                      y={cardY + cardHeight / 2 + 4}
                      fill={portColor}
                      fontSize="9"
                      fontWeight="700"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      stroke="var(--bg-primary)"
                      strokeWidth="0.8"
                      strokeLinejoin="round"
                      paintOrder="stroke fill"
                      style={{ 
                        userSelect: 'none',
                        filter: `drop-shadow(0 0 3px ${portColor})`
                      }}
                    >
                      {port.label}
                    </text>
                  </>
                );
              })()}
            </g>
          </g>
        );
      })}
    </g>
  );
}
