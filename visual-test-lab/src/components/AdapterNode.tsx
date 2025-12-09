import { Globe, Database, MessageSquare, Clock, ExternalLink } from 'lucide-react';
import { mockAdapters, mockAdapterNodes } from '../data/mockAdapters';

const iconMap: Record<string, any> = {
  Globe,
  Database,
  MessageSquare,
  Clock,
  ExternalLink
};

interface AdapterNodeProps {
  nodeId: string;
  x: number;
  y: number;
  isHighlighted?: boolean;
}

export default function AdapterNode({ nodeId, x, y, isHighlighted = false }: AdapterNodeProps) {
  const node = mockAdapterNodes.find(n => n.id === nodeId);
  if (!node) return null;

  const adapter = mockAdapters.find(a => a.id === node.adapterId);
  if (!adapter) return null;

  const Icon = iconMap[adapter.icon] || Globe;
  const statusColor = node.status === 'connected' 
    ? 'var(--accent-teal)' 
    : node.status === 'error' 
    ? 'var(--accent-magenta)' 
    : 'var(--text-muted)';
  
  const highlightGlow = isHighlighted ? 'var(--glow-teal)' : (node.status === 'connected' ? 'var(--glow-teal)' : 'none');

  return (
    <g transform={`translate(${x}, ${y})`}>
      {/* Card shadow */}
      <rect
        x="-60"
        y="-35"
        width="120"
        height="70"
        rx="6"
        fill="var(--bg-primary)"
        opacity="0.4"
      />
      
      {/* Highlight ring */}
      {isHighlighted && (
        <circle
          cx="0"
          cy="0"
          r="75"
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
      
      {/* Card background with glow */}
      <rect
        x="-62"
        y="-37"
        width="120"
        height="70"
        rx="6"
        fill={isHighlighted ? 'var(--bg-tertiary)' : 'var(--bg-secondary)'}
        stroke={adapter.type === 'inbound' ? 'var(--accent-inbound)' : 'var(--accent-outbound)'}
        strokeWidth={isHighlighted ? '2.5' : '1.5'}
        style={{
          filter: highlightGlow
        }}
      />
      
      {/* Header */}
      <rect
        x="-62"
        y="-37"
        width="120"
        height="18"
        rx="6"
        fill="var(--bg-tertiary)"
        opacity="0.6"
      />
      
      {/* Icon and Title */}
      <foreignObject x="-55" y="-32" width="14" height="14">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon size={14} color={adapter.type === 'inbound' ? 'var(--accent-inbound)' : 'var(--accent-outbound)'} />
        </div>
      </foreignObject>
      <text
        x="0"
        y="-22"
        fill="var(--text-primary)"
        fontSize="10"
        fontWeight="600"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        {adapter.name}
      </text>
      
      {/* Direction label */}
      <text
        x="0"
        y="-10"
        fill={adapter.type === 'inbound' ? 'var(--accent-inbound)' : 'var(--accent-outbound)'}
        fontSize="7"
        fontWeight="700"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        {adapter.type === 'inbound' ? 'INBOUND' : 'OUTBOUND'}
      </text>
      
      {/* Subtitle */}
      <text
        x="0"
        y="0"
        fill="var(--text-secondary)"
        fontSize="7"
        textAnchor="middle"
        style={{ userSelect: 'none' }}
      >
        {adapter.type === 'inbound' 
          ? (node.config.method || node.config.topic || node.config.interval || 'Adapter')
          : (node.config.type || node.config.endpoint?.split('/').pop() || 'Adapter')}
      </text>
      
      {/* Status indicator */}
      <circle
        cx="50"
        cy="-28"
        r="3.5"
        fill={statusColor}
        style={{
          filter: `drop-shadow(0 0 3px ${statusColor})`
        }}
      />
      
      {/* Content area - simplified for smaller cards */}
      {adapter.id === 'http-inbound' && (
        <g>
          <text x="-55" y="8" fill="var(--text-secondary)" fontSize="7" fontWeight="500" style={{ userSelect: 'none' }}>
            {node.config.method} {node.config.path}
          </text>
          <rect x="-55" y="12" width="110" height="18" rx="3" fill="var(--bg-primary)" opacity="0.6" stroke="var(--border-color)" strokeWidth="0.5" />
          <text x="-50" y="24" fill="var(--accent-cyan)" fontSize="6" fontFamily="monospace" style={{ userSelect: 'none' }}>
            {'{ "orderId": 123 }'}
          </text>
        </g>
      )}
      
      {adapter.id === 'db-mock' && (
        <g>
          <text x="-55" y="8" fill="var(--text-secondary)" fontSize="7" fontWeight="500" style={{ userSelect: 'none' }}>
            {node.config.type}
          </text>
          <text x="-55" y="20" fill="var(--text-muted)" fontSize="6" style={{ userSelect: 'none' }}>
            Mode: {node.config.mode}
          </text>
          <text x="-55" y="30" fill="var(--accent-teal)" fontSize="6" fontFamily="monospace" style={{ userSelect: 'none' }}>
            Table: {node.config.table}
          </text>
        </g>
      )}
      
      {adapter.id === 'message-consumer' && (
        <g>
          <text x="-55" y="8" fill="var(--text-secondary)" fontSize="7" style={{ userSelect: 'none' }}>
            {node.config.topic}
          </text>
          <text x="-55" y="20" fill="var(--text-muted)" fontSize="6" style={{ userSelect: 'none' }}>
            • {node.config.events?.[0]}
          </text>
          <text x="-55" y="30" fill="var(--text-muted)" fontSize="6" style={{ userSelect: 'none' }}>
            Queue: 3
          </text>
        </g>
      )}
      
      {adapter.id === 'scheduler-trigger' && (
        <g>
          <text x="-55" y="8" fill="var(--text-secondary)" fontSize="7" style={{ userSelect: 'none' }}>
            {node.config.interval}
          </text>
          <text x="-55" y="20" fill="var(--text-muted)" fontSize="6" style={{ userSelect: 'none' }}>
            {node.config.task}
          </text>
          <text x="-55" y="30" fill={node.config.active ? 'var(--accent-teal)' : 'var(--text-muted)'} fontSize="7" style={{ userSelect: 'none' }}>
            {node.config.active ? '● Active' : '○ Paused'}
          </text>
        </g>
      )}
      
      {adapter.id === 'http-client-mock' && (
        <g>
          <text x="-55" y="8" fill="var(--text-secondary)" fontSize="7" fontWeight="500" style={{ userSelect: 'none' }}>
            POST {node.config.endpoint?.split('/').pop()}
          </text>
          <rect x="-55" y="12" width="110" height="15" rx="3" fill="var(--bg-primary)" opacity="0.6" stroke="var(--border-color)" strokeWidth="0.5" />
          <text x="-50" y="22" fill="var(--accent-magenta)" fontSize="6" fontFamily="monospace" style={{ userSelect: 'none' }}>
            {'{ "status": "approved" }'}
          </text>
        </g>
      )}
    </g>
  );
}

