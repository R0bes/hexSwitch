import { Server, Database, MessageSquare, Globe } from 'lucide-react';
import { mockMockNodes } from '../data/mockAdapters';

const iconMap: Record<string, any> = {
  http: Globe,
  database: Database,
  'message-broker': MessageSquare,
  cache: Server
};

interface MockNodeProps {
  mockId: string;
  x: number;
  y: number;
  isHighlighted?: boolean;
}

export default function MockNode({ mockId, x, y, isHighlighted = false }: MockNodeProps) {
  const mock = mockMockNodes.find(m => m.id === mockId);
  if (!mock) return null;

  const Icon = iconMap[mock.type] || Globe;
  // Inbound mocks: dark cyan, Outbound mocks: dark magenta
  const baseColor = mock.direction === 'inbound' 
    ? 'var(--accent-inbound-dark)' 
    : 'var(--accent-outbound-dark)';
  const mockColor = isHighlighted ? 'var(--accent-teal)' : baseColor;

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Highlight ring */}
      {isHighlighted && (
        <circle
          cx="0"
          cy="0"
          r="85"
          fill="none"
          stroke="var(--accent-teal)"
          strokeWidth="3"
          opacity="0.6"
          style={{
            filter: 'blur(4px)',
            animation: 'pulse-glow 2s ease-in-out infinite'
          }}
        />
      )}
      
      {/* Card shadow */}
      <rect
        x="-70"
        y="-40"
        width="140"
        height="80"
        rx="8"
        fill="var(--bg-primary)"
        opacity="0.4"
      />
      
      {/* Card background */}
      <rect
        x="-72"
        y="-42"
        width="140"
        height="80"
        rx="8"
        fill={isHighlighted ? 'var(--bg-secondary)' : 'var(--bg-tertiary)'}
        stroke={mockColor}
        strokeWidth={isHighlighted ? '3' : '2'}
        strokeDasharray="4,4"
        style={{
          filter: isHighlighted 
            ? 'drop-shadow(0 0 12px rgba(0, 245, 255, 0.6))'
            : mock.direction === 'inbound'
            ? 'drop-shadow(var(--glow-inbound-dark))'
            : 'drop-shadow(var(--glow-outbound-dark))'
        }}
      />
      
      {/* Header */}
      <rect
        x="-72"
        y="-42"
        width="140"
        height="20"
        rx="8"
        fill="var(--bg-secondary)"
        opacity="0.7"
      />
      
      {/* Icon and Title */}
      <foreignObject x="-65" y="-38" width="16" height="16">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon size={14} color={isHighlighted ? 'var(--accent-teal)' : mockColor} />
        </div>
      </foreignObject>
      <text
        x="0"
        y="-28"
        fill="var(--text-primary)"
        fontSize="10"
        fontWeight="600"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        {mock.name}
      </text>
      
      {/* Subtitle with direction */}
      <text
        x="0"
        y="-15"
        fill={mock.direction === 'inbound' ? 'var(--accent-inbound-dark)' : 'var(--accent-outbound-dark)'}
        fontSize="8"
        fontWeight="600"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        {mock.direction === 'inbound' ? 'INBOUND' : 'OUTBOUND'} Mock
      </text>
      
      {/* Content area */}
      <rect x="-65" y="5" width="130" height="25" rx="4" fill="var(--bg-primary)" opacity="0.6" stroke="var(--border-color)" strokeWidth="0.5" />
      <text x="-60" y="18" fill="var(--text-muted)" fontSize="7" fontFamily="monospace" style={{ userSelect: 'none' }}>
        {mock.type === 'http' && mock.config.endpoint}
        {mock.type === 'database' && `${mock.config.host}:${mock.config.port}`}
        {mock.type === 'message-broker' && mock.config.url}
        {mock.type === 'cache' && 'Cache Store'}
      </text>
    </g>
  );
}

