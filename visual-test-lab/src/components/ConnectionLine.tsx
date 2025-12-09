import DataFlowPulse from './DataFlowPulse';
import type { DataFlowPulse as PulseType } from '../hooks/useDataFlow';

interface ConnectionLineProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  type?: 'inbound' | 'outbound';
  activePulses?: PulseType[];
  connectionId?: string;
}

export default function ConnectionLine({ 
  x1, 
  y1, 
  x2, 
  y2, 
  type = 'inbound',
  activePulses = [],
  connectionId 
}: ConnectionLineProps) {
  const color = type === 'inbound' ? 'var(--accent-inbound)' : 'var(--accent-outbound)';
  
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
  
  // Determine animation class based on type
  // For inbound: flow from x1 to x2 (towards core)
  // For outbound: flow from x2 to x1 (away from core)
  const animationClass = type === 'inbound' ? 'flow-line-inbound' : 'flow-line-outbound';
  
  return (
    <g>
      {/* Glow effect behind line */}
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth="4"
        opacity="0.2"
        style={{
          filter: 'blur(4px)'
        }}
      />
      
      {/* Main line with animated flow */}
      <line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={color}
        strokeWidth="2"
        opacity="0.7"
        className={animationClass}
        style={{
          filter: `drop-shadow(0 0 4px ${color})`
        }}
      />
      
      {/* Arrow head */}
      <path
        d={`M ${x2} ${y2} L ${arrowX} ${arrowY} L ${arrowX2} ${arrowY2} Z`}
        fill={color}
        opacity="0.9"
        style={{
          filter: `drop-shadow(0 0 3px ${color})`
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
