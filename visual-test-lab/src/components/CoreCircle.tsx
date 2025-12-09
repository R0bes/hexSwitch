interface CoreCircleProps {
  centerX: number;
  centerY: number;
  radius: number;
}

export default function CoreCircle({ centerX, centerY, radius }: CoreCircleProps) {
  return (
    <g>
      {/* Outer glow */}
      <circle
        cx={centerX}
        cy={centerY}
        r={radius + 5}
        fill="none"
        stroke="var(--accent-core)"
        strokeWidth="2"
        opacity="0.3"
        style={{
          filter: 'blur(4px)'
        }}
      />
      
      {/* Main circle */}
      <circle
        cx={centerX}
        cy={centerY}
        r={radius}
        fill="var(--bg-secondary)"
        stroke="var(--accent-core)"
        strokeWidth="2.5"
        style={{
          filter: 'drop-shadow(var(--glow-core))'
        }}
      />
      
      {/* Internal pattern (subtle grid) */}
      <defs>
        <pattern id="circle-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
          <circle cx="10" cy="10" r="1" fill="var(--accent-core)" opacity="0.2" />
        </pattern>
      </defs>
      <circle
        cx={centerX}
        cy={centerY}
        r={radius - 2}
        fill="url(#circle-pattern)"
        opacity="0.3"
      />
      
      {/* Core label */}
      <text
        x={centerX}
        y={centerY - 8}
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

