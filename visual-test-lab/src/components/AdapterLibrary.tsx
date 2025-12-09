import { Globe, Network, MessageSquare, Clock, Database, Box, Send, ExternalLink } from 'lucide-react';
import { mockAdapters } from '../data/mockAdapters';

const iconMap: Record<string, any> = {
  Globe,
  Network,
  MessageSquare,
  Clock,
  Database,
  Box,
  Send,
  ExternalLink
};

interface AdapterLibraryProps {
  selectedAdapterId: string | null;
  onAdapterSelect: (adapterId: string | null) => void;
}

export default function AdapterLibrary({ selectedAdapterId, onAdapterSelect }: AdapterLibraryProps) {
  const inboundAdapters = mockAdapters.filter(a => a.type === 'inbound');
  const outboundAdapters = mockAdapters.filter(a => a.type === 'outbound');

  const AdapterItem = ({ adapter }: { adapter: typeof mockAdapters[0] }) => {
    const Icon = iconMap[adapter.icon] || Globe;
    const isSelected = selectedAdapterId === adapter.id;
    
    return (
      <div
        onClick={() => onAdapterSelect(isSelected ? null : adapter.id)}
        style={{
          background: isSelected ? 'var(--bg-tertiary)' : 'var(--bg-secondary)',
          border: `2px solid ${isSelected ? 'var(--accent-teal)' : 'var(--border-color)'}`,
          borderRadius: 'var(--radius-md)',
          padding: 'var(--spacing-sm) var(--spacing-md)',
          marginBottom: 'var(--spacing-sm)',
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-sm)',
          cursor: 'pointer',
          transition: 'all var(--transition-normal)',
          fontSize: '0.9rem',
          boxShadow: isSelected ? 'var(--glow-teal)' : 'none',
          transform: isSelected ? 'translateX(4px)' : 'translateX(0)'
        }}
        onMouseEnter={(e) => {
          if (!isSelected) {
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.boxShadow = 'var(--glow-teal)';
            e.currentTarget.style.transform = 'translateX(4px)';
          }
        }}
        onMouseLeave={(e) => {
          if (!isSelected) {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
            e.currentTarget.style.transform = 'translateX(0)';
          }
        }}
      >
        <Icon 
          size={18} 
          color={adapter.type === 'inbound' ? 'var(--accent-cyan)' : 'var(--accent-magenta)'}
        />
        <span style={{ color: 'var(--text-primary)', flex: 1 }}>
          {adapter.name}
        </span>
        {isSelected && (
          <span style={{ 
            color: 'var(--accent-teal)', 
            fontSize: '0.8rem',
            fontWeight: 600
          }}>
            ●
          </span>
        )}
      </div>
    );
  };

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      padding: 'var(--spacing-lg)',
      overflowY: 'auto'
    }}>
      <h3 style={{
        color: 'var(--text-primary)',
        fontSize: '1rem',
        fontWeight: 600,
        marginBottom: 'var(--spacing-lg)',
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}>
        Adapter Library
      </h3>

      <div style={{ marginBottom: 'var(--spacing-xl)' }}>
        <h4 style={{
          color: 'var(--accent-cyan)',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: 'var(--spacing-md)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Inbound
        </h4>
        {inboundAdapters.map(adapter => (
          <AdapterItem key={adapter.id} adapter={adapter} />
        ))}
      </div>

      <div>
        <h4 style={{
          color: 'var(--accent-magenta)',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: 'var(--spacing-md)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Outbound
        </h4>
        {outboundAdapters.map(adapter => (
          <AdapterItem key={adapter.id} adapter={adapter} />
        ))}
      </div>
    </div>
  );
}

