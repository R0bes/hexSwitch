import { useState, useEffect } from 'react';
import type { AdapterNode } from '../../data/mockAdapters';
import { mockAdapters } from '../../data/mockAdapters';

interface AdapterConfigFormProps {
  node: AdapterNode;
  onSave: (nodeId: string, config: Record<string, any>) => void;
  onCancel: () => void;
}

export default function AdapterConfigForm({ node, onSave, onCancel }: AdapterConfigFormProps) {
  const [config, setConfig] = useState<Record<string, any>>(node.config);
  const adapter = mockAdapters.find(a => a.id === node.adapterId);

  useEffect(() => {
    setConfig(node.config);
  }, [node.config]);

  const handleSave = () => {
    onSave(node.id, config);
  };

  if (!adapter) return null;

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
          {adapter.name} Configuration
        </h4>
        <p style={{
          color: 'var(--text-secondary)',
          fontSize: '0.8rem',
          marginBottom: 'var(--spacing-md)'
        }}>
          {adapter.description}
        </p>
      </div>

      {/* Dynamic form fields based on adapter type */}
      {adapter.id === 'http-inbound' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Method
            <input
              type="text"
              value={config.method || ''}
              onChange={(e) => setConfig({ ...config, method: e.target.value })}
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
            Path
            <input
              type="text"
              value={config.path || ''}
              onChange={(e) => setConfig({ ...config, path: e.target.value })}
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
            Handler
            <input
              type="text"
              value={config.handler || ''}
              onChange={(e) => setConfig({ ...config, handler: e.target.value })}
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

      {adapter.id === 'db-mock' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <label style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Type
            <input
              type="text"
              value={config.type || ''}
              onChange={(e) => setConfig({ ...config, type: e.target.value })}
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
            Table
            <input
              type="text"
              value={config.table || ''}
              onChange={(e) => setConfig({ ...config, table: e.target.value })}
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

      {/* Generic JSON editor for other adapters */}
      {!['http-inbound', 'db-mock'].includes(adapter.id) && (
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


