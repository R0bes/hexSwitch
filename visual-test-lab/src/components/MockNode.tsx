import { Server, Database, MessageSquare, Globe } from 'lucide-react';
import { useConfigurationContext } from '../contexts/ConfigurationContext';
import { useElementSelectionContext } from '../contexts/ElementSelectionContext';

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
  onDragStart?: (e: React.MouseEvent, id: string) => void;
  isDragging?: boolean;
  dragPosition?: { x: number; y: number } | null;
}

export default function MockNode({ mockId, x, y, isHighlighted = false, onDragStart, isDragging = false, dragPosition = null }: MockNodeProps) {
  const { mockNodes } = useConfigurationContext();
  const { isSelected, toggleSelection } = useElementSelectionContext();
  const mock = mockNodes.find(m => m.id === mockId);
  if (!mock) return null;

  const Icon = iconMap[mock.type] || Globe;
  // Inbound mocks: dark cyan, Outbound mocks: dark magenta
  const baseColor = mock.direction === 'inbound' 
    ? 'var(--accent-inbound-dark)' 
    : 'var(--accent-outbound-dark)';
  const isSelectedElement = isSelected('mock', mockId);
  const mockColor = isSelectedElement || isHighlighted ? 'var(--accent-teal)' : baseColor;
  
  const displayX = isDragging && dragPosition ? dragPosition.x : x;
  const displayY = isDragging && dragPosition ? dragPosition.y : y;
  
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    toggleSelection('mock', mockId);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0 && onDragStart) {
      e.stopPropagation();
      onDragStart(e, mockId);
    }
  };

  return (
    <g 
      transform={`translate(${displayX}, ${displayY})`} 
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      data-draggable="mock"
      style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
    >
      {/* Highlight ring */}
      {(isSelectedElement || isHighlighted) && (
        <circle
          cx="0"
          cy="0"
          r="85"
          fill="none"
          stroke="var(--accent-teal)"
          strokeWidth={isSelectedElement ? '4' : '3'}
          opacity={isSelectedElement ? '0.8' : '0.6'}
          style={{
            filter: 'blur(4px)',
            animation: isSelectedElement ? 'pulse-glow 2s ease-in-out infinite' : 'none'
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
        fill={isSelectedElement || isHighlighted ? 'var(--bg-secondary)' : 'var(--bg-tertiary)'}
        stroke={mockColor}
        strokeWidth={isSelectedElement ? '4' : (isHighlighted ? '3' : '2')}
        strokeDasharray="4,4"
        style={{
          filter: isSelectedElement || isHighlighted
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

