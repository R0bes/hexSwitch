import { Play, Square, Trash2 } from 'lucide-react';
import type { MockRuntimeState } from '../../types/runtime';

interface MockRuntimePanelProps {
  state: MockRuntimeState;
  onStart: () => void;
  onStop: () => void;
  onClearEvents: () => void;
}

export default function MockRuntimePanel({ state, onStart, onStop, onClearEvents }: MockRuntimePanelProps) {
  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'error':
        return 'var(--accent-magenta)';
      case 'event':
        return 'var(--accent-cyan)';
      case 'metric':
        return 'var(--accent-teal)';
      default:
        return 'var(--text-secondary)';
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--spacing-md)',
      gap: 'var(--spacing-md)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: 'var(--spacing-md)'
      }}>
        <div>
          <h3 style={{
            color: 'var(--text-primary)',
            fontSize: '1rem',
            fontWeight: 600,
            marginBottom: 'var(--spacing-xs)'
          }}>
            MockRuntime
          </h3>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: state.isActive ? 'var(--accent-teal)' : 'var(--text-muted)',
              boxShadow: state.isActive ? '0 0 8px var(--accent-teal)' : 'none'
            }} />
            <span style={{
              color: 'var(--text-secondary)',
              fontSize: '0.85rem'
            }}>
              {state.isActive ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>
        <div style={{
          display: 'flex',
          gap: 'var(--spacing-xs)'
        }}>
          {state.isActive ? (
            <button
              onClick={onStop}
              style={{
                padding: 'var(--spacing-xs) var(--spacing-sm)',
                background: 'var(--accent-magenta)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--bg-primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)',
                fontSize: '0.85rem',
                fontWeight: 600
              }}
            >
              <Square size={14} />
              Stop
            </button>
          ) : (
            <button
              onClick={onStart}
              style={{
                padding: 'var(--spacing-xs) var(--spacing-sm)',
                background: 'var(--accent-teal)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--bg-primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)',
                fontSize: '0.85rem',
                fontWeight: 600
              }}
            >
              <Play size={14} fill="var(--bg-primary)" />
              Start
            </button>
          )}
          {state.events.length > 0 && (
            <button
              onClick={onClearEvents}
              style={{
                padding: 'var(--spacing-xs) var(--spacing-sm)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)',
                fontSize: '0.85rem)'
              }}
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Metrics */}
      {state.isActive && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: 'var(--spacing-sm)',
          padding: 'var(--spacing-sm)',
          background: 'var(--bg-primary)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-color)'
        }}>
          <MetricItem label="Uptime" value={formatUptime(state.metrics.uptime)} />
          <MetricItem label="Requests" value={state.metrics.requestsProcessed.toString()} />
          <MetricItem label="Events" value={state.metrics.eventsEmitted.toString()} />
          <MetricItem label="Errors" value={state.metrics.errors.toString()} color={state.metrics.errors > 0 ? 'var(--accent-magenta)' : undefined} />
        </div>
      )}

      {/* Events Log */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0
      }}>
        <h4 style={{
          color: 'var(--text-secondary)',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: 'var(--spacing-sm)',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Events ({state.events.length})
        </h4>
        <div style={{
          flex: 1,
          overflowY: 'auto',
          background: 'var(--bg-primary)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-color)',
          padding: 'var(--spacing-sm)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-xs)'
        }}>
          {state.events.length === 0 ? (
            <div style={{
              color: 'var(--text-muted)',
              fontSize: '0.85rem',
              textAlign: 'center',
              padding: 'var(--spacing-lg)'
            }}>
              No events yet
            </div>
          ) : (
            state.events.slice().reverse().map(event => (
              <div
                key={event.id}
                style={{
                  padding: 'var(--spacing-xs) var(--spacing-sm)',
                  background: 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: `3px solid ${getEventTypeColor(event.type)}`,
                  fontSize: '0.8rem',
                  fontFamily: 'monospace'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-xs)',
                  marginBottom: 'var(--spacing-xs)'
                }}>
                  <span style={{
                    color: getEventTypeColor(event.type),
                    fontWeight: 600,
                    fontSize: '0.75rem'
                  }}>
                    {event.type.toUpperCase()}
                  </span>
                  <span style={{
                    color: 'var(--text-muted)',
                    fontSize: '0.7rem'
                  }}>
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div style={{
                  color: 'var(--text-primary)',
                  fontSize: '0.8rem'
                }}>
                  {event.message}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function MetricItem({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <div style={{
        color: 'var(--text-muted)',
        fontSize: '0.75rem',
        marginBottom: '2px'
      }}>
        {label}
      </div>
      <div style={{
        color: color || 'var(--text-primary)',
        fontSize: '1rem',
        fontWeight: 600,
        fontFamily: 'monospace'
      }}>
        {value}
      </div>
    </div>
  );
}


