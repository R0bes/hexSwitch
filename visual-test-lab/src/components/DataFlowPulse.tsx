interface DataFlowPulseProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  progress: number; // 0 to 1
  color: string;
  size?: number;
}

export default function DataFlowPulse({ 
  x1, 
  y1, 
  x2, 
  y2, 
  progress, 
  color,
  size = 8 
}: DataFlowPulseProps) {
  // Calculate position along the line
  const x = x1 + (x2 - x1) * progress;
  const y = y1 + (y2 - y1) * progress;
  
  // Calculate distance for glow effect
  const distance = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
  const glowSize = Math.min(size * 3, distance * 0.1);

  return (
    <g>
      {/* Outer glow */}
      <circle
        cx={x}
        cy={y}
        r={glowSize}
        fill={color}
        opacity={0.3 * (1 - progress * 0.5)}
        style={{
          filter: `blur(${glowSize / 2}px)`
        }}
      />
      
      {/* Main pulse circle */}
      <circle
        cx={x}
        cy={y}
        r={size}
        fill={color}
        opacity={0.9 * (1 - progress * 0.3)}
        style={{
          filter: `drop-shadow(0 0 ${size}px ${color})`
        }}
      />
      
      {/* Inner highlight */}
      <circle
        cx={x}
        cy={y}
        r={size * 0.5}
        fill="white"
        opacity={0.6}
      />
    </g>
  );
}

