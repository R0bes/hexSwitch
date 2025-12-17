import { useState, useEffect } from 'react';
import type { MockNode } from '../../data/mockAdapters';

interface MockConfigFormProps {
  mock: MockNode;
  onSave: (mockId: string, config: Record<string, any>) => void;
  onCancel: () => void;
}

export default function MockConfigForm({ mock, onSave, onCancel }: MockConfigFormProps) {
  const [config, setConfig] = useState<Record<string, any>>(mock.config);

  useEffect(() => {
    setConfig(mock.config);
  }, [mock.config]);

  const handleSave = () => {
    onSave(mock.id, config);
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
          {mock.name} Configuration
        </h4>
        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '0.8rem',
          marginBottom: 'var(--spacing-md)'
        }}>
          Type: {mock.type} • Direction: {mock.direction}
        </p>
      </div>

      {/* Dynamic form fields based on mock type */}
      {mock.type === 'http' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Endpoint
            <input
              type="text"
              value={config.endpoint || ''}
              onChange={(e) => setConfig({ ...config, endpoint: e.target.value })}
              style={{
                width: '100%',
                padding: 'var(--spacing-xs)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                marginTop: 'var(--spacing-xs)'
              }}
            />
          </label>
        </div>
      )}

      {mock.type === 'database' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Host
            <input
              type="text"
              value={config.host || ''}
              onChange={(e) => setConfig({ ...config, host: e.target.value })}
              style={{
                width: '100%',
                padding: 'var(--spacing-xs)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                marginTop: 'var(--spacing-xs)'
              }}
            />
          </label>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Port
            <input
              type="number"
              value={config.port || ''}
              onChange={(e) => setConfig({ ...config, port: parseInt(e.target.value) || 0 })}
              style={{
                width: '100%',
                padding: 'var(--spacing-xs)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                marginTop: 'var(--spacing-xs)'
              }}
            />
          </label>
        </div>
      )}

      {/* Generic JSON editor for other types */}
      {!['http', 'database'].includes(mock.type) && (
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
      )}

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


