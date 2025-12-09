import DataFlowPulse from './DataFlowPulse';
import type { DataFlowPulse as PulseType } from '../hooks/useDataFlow';

interface DashedConnectionLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color?: string;
  activePulses?: PulseType[];
  connectionId?: string;
  direction?: 'mock-to-adapter' | 'adapter-to-mock';
}

export default function DashedConnectionLine({ 
  x1, 
  y1, 
  x2, 
  y2, 
  color,
  activePulses = [],
  connectionId,
  direction = 'mock-to-adapter'
}: DashedConnectionLineProps) {
  // Calculate arrow direction
  const dx = x2 - x1;
  const dy = y2 - y1;
  const angle = Math.atan2(dy, dx);
  const arrowLength = 8;
  const arrowAngle = Math.PI / 6;
  
  const arrowX = x2 - arrowLength * Math.cos(angle - arrowAngle);
  const arrowY = y2 - arrowLength * Math.sin(angle - arrowAngle);
  const arrowX2 = x2 - arrowLength * Math.cos(angle + arrowAngle);
  const arrowY2 = y2 - arrowLength * Math.sin(angle + arrowAngle);
  
  // Animation direction based on connection type
  // mock-to-adapter: flows from x1 to x2 (normal)
  // adapter-to-mock: flows from x2 to x1 (reverse)
  const animationClass = direction === 'mock-to-adapter' 
    ? 'flow-line-dashed' 
    : 'flow-line-dashed-reverse';
  
  return (
    <g>
      {/* Glow effect behind line */}
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth="3"
        opacity="0.15"
        strokeDasharray="8,4"
        style={{
          filter: 'blur(3px)'
        }}
      />
      
      {/* Main dashed line with animated flow */}
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth="2"
        opacity="0.6"
        strokeDasharray="8,4"
        className={animationClass}
        style={{
          filter: `drop-shadow(0 0 3px ${color})`
        }}
      />
      
      {/* Arrow head */}
      <path
        d={`M ${x2} ${y2} L ${arrowX} ${arrowY} L ${arrowX2} ${arrowY2} Z`}
        fill={color}
        opacity="0.8"
        style={{
          filter: `drop-shadow(0 0 2px ${color})`
        }}
      />
      
      {/* Data flow pulses */}
      {activePulses
        .filter(pulse => pulse.connectionId === connectionId)
        .map(pulse => {
          const elapsed = Date.now() - pulse.startTime;
          const progress = Math.min(elapsed / pulse.duration, 1);
          
          return (
            <DataFlowPulse
              key={pulse.id}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              progress={progress}
              color={pulse.color}
            />
          );
        })}
    </g>
  );
}
