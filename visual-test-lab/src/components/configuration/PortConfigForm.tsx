import { useState, useEffect } from 'react';
import type { Port } from '../CoreHexagon';

interface PortConfigFormProps {
  port: Port;
  onSave: (portId: string, config: Record<string, any>) => void;
  onCancel: () => void;
}

export default function PortConfigForm({ port, onSave, onCancel }: PortConfigFormProps) {
  const [config, setConfig] = useState<Record<string, any>>(port.config || {});

  useEffect(() => {
    setConfig(port.config || {});
  }, [port.config]);

  const handleSave = () => {
    onSave(port.id, config);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-md)'
    }}>
      <div>
        <h4 style={{
          color: 'var(--text-primary)',
          fontSize: '0.9rem',
          fontWeight: 600,
          marginBottom: 'var(--spacing-sm)'
        }}>
          {port.label} Configuration
        </h4>
        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '0.8rem',
          marginBottom: 'var(--spacing-md)'
        }}>
          Type: {port.type}
        </p>
      </div>

      {/* Generic JSON editor for port config */}
      <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        Configuration (JSON)
        <textarea
          value={JSON.stringify(config, null, 2)}
          onChange={(e) => {
            try {
              setConfig(JSON.parse(e.target.value));
            } catch {
              // Invalid JSON, ignore
            }
          }}
          style={{
            width: '100%',
            minHeight: '120px',
            padding: 'var(--spacing-xs)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-primary)',
            fontFamily: 'monospace',
            fontSize: '0.8rem',
            marginTop: 'var(--spacing-xs)',
            resize: 'vertical'
          }}
        />
      </label>

      <div style={{
        display: 'flex',
        gap: 'var(--spacing-sm)',
        justifyContent: 'flex-end',
        marginTop: 'var(--spacing-md)'
      }}>
        <button
          onClick={onCancel}
          style={{
            padding: 'var(--spacing-sm) var(--spacing-md)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-primary)',
            cursor: 'pointer'
          }}
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          style={{
            padding: 'var(--spacing-sm) var(--spacing-md)',
            background: 'var(--accent-teal)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--bg-primary)',
            cursor: 'pointer',
            fontWeight: 600
          }}
        >
          Save
        </button>
      </div>
    </div>
  );
}


