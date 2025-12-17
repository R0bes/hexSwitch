import { useState } from 'react';
import { Settings, Play, Square } from 'lucide-react';
import type { RuntimeType } from '../../types/runtime';
import MockRuntimePanel from './MockRuntimePanel';
import { useMockRuntime } from '../../hooks/useMockRuntime';

interface RuntimeLoaderProps {
  runtimeType: RuntimeType;
  onRuntimeTypeChange: (type: RuntimeType) => void;
}

export default function RuntimeLoader({ runtimeType, onRuntimeTypeChange }: RuntimeLoaderProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const mockRuntime = useMockRuntime();

  return (
    <div style={{
      position: 'absolute',
      top: 'var(--spacing-md)',
      right: 'var(--spacing-md)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-end',
      gap: 'var(--spacing-sm)'
    }}>
      {/* Runtime Type Selector */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-sm)',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: 'var(--spacing-sm)',
        boxShadow: 'var(--shadow-md)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-xs)',
          padding: 'var(--spacing-xs) var(--spacing-sm)',
          background: runtimeType === 'real' ? 'var(--accent-teal)' : 'var(--bg-tertiary)',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          transition: 'all var(--transition-normal)',
          border: runtimeType === 'real' ? '1px solid var(--accent-teal)' : '1px solid transparent'
        }}
        onClick={() => onRuntimeTypeChange('real')}
        >
          <Play size={14} fill={runtimeType === 'real' ? 'var(--bg-primary)' : 'transparent'} />
          <span style={{
            color: runtimeType === 'real' ? 'var(--bg-primary)' : 'var(--text-secondary)',
            fontSize: '0.85rem',
            fontWeight: runtimeType === 'real' ? 600 : 400
          }}>
            Real
          </span>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--spacing-xs)',
          padding: 'var(--spacing-xs) var(--spacing-sm)',
          background: runtimeType === 'mock' ? 'var(--accent-cyan)' : 'var(--bg-tertiary)',
          borderRadius: 'var(--radius-sm)',
          cursor: 'pointer',
          transition: 'all var(--transition-normal)',
          border: runtimeType === 'mock' ? '1px solid var(--accent-cyan)' : '1px solid transparent'
        }}
        onClick={() => onRuntimeTypeChange('mock')}
        >
          <Square size={14} fill={runtimeType === 'mock' ? 'var(--bg-primary)' : 'transparent'} />
          <span style={{
            color: runtimeType === 'mock' ? 'var(--bg-primary)' : 'var(--text-secondary)',
            fontSize: '0.85rem',
            fontWeight: runtimeType === 'mock' ? 600 : 400
          }}>
            Mock
          </span>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            padding: 'var(--spacing-xs)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <Settings size={16} />
        </button>
      </div>

      {/* MockRuntime Panel (when expanded and mock is selected) */}
      {isExpanded && runtimeType === 'mock' && (
        <div style={{
          width: '400px',
          maxHeight: '600px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-lg)',
          overflow: 'hidden'
        }}>
          <MockRuntimePanel
            state={mockRuntime.state}
            onStart={mockRuntime.start}
            onStop={mockRuntime.stop}
            onClearEvents={mockRuntime.clearEvents}
          />
        </div>
      )}
    </div>
  );
}


