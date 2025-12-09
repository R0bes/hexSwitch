import { useState } from 'react';
import { FileText, MessageSquare, Activity } from 'lucide-react';
import { mockLogs, mockEvents, mockTraces } from '../data/mockLogs';

type TabType = 'logs' | 'events' | 'traces';

export default function LogsPanel() {
  const [activeTab, setActiveTab] = useState<TabType>('logs');

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return 'var(--accent-magenta)';
      case 'WARN':
        return '#ffaa00';
      case 'INFO':
        return 'var(--accent-cyan)';
      case 'DEBUG':
        return 'var(--text-muted)';
      default:
        return 'var(--text-secondary)';
    }
  };

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-primary)'
    }}>
      {/* Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)'
      }}>
        {[
          { id: 'logs' as TabType, label: 'Logs', icon: FileText },
          { id: 'events' as TabType, label: 'Events', icon: MessageSquare },
          { id: 'traces' as TabType, label: 'Traces', icon: Activity }
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1,
                padding: 'var(--spacing-md)',
                background: isActive ? 'var(--bg-primary)' : 'transparent',
                border: 'none',
                borderBottom: isActive ? '2px solid var(--accent-teal)' : '2px solid transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--spacing-sm)',
                fontSize: '0.9rem',
                fontWeight: isActive ? 600 : 400,
                transition: 'all var(--transition-normal)'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--spacing-md)',
        fontFamily: 'monospace',
        fontSize: '0.85rem'
      }}>
        {activeTab === 'logs' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
            {mockLogs.map((log, index) => (
              <div
                key={index}
                style={{
                  padding: 'var(--spacing-sm)',
                  background: 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: `3px solid ${getLevelColor(log.level)}`,
                  lineHeight: '1.6'
                }}
              >
                <span style={{ color: 'var(--text-muted)' }}>
                  [{log.timestamp}]
                </span>
                <span
                  style={{
                    color: getLevelColor(log.level),
                    fontWeight: 600,
                    marginLeft: 'var(--spacing-sm)',
                    marginRight: 'var(--spacing-sm)'
                  }}
                >
                  {log.level}
                </span>
                <span style={{ color: 'var(--text-primary)' }}>
                  {log.source}
                </span>
                {log.target && (
                  <>
                    <span style={{ color: 'var(--text-muted)', margin: '0 var(--spacing-xs)' }}>
                      →
                    </span>
                    <span style={{ color: 'var(--text-primary)' }}>
                      {log.target}
                    </span>
                  </>
                )}
                <span style={{ color: 'var(--text-secondary)', marginLeft: 'var(--spacing-sm)' }}>
                  : {log.message}
                </span>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'events' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            {mockEvents.map(event => (
              <div
                key={event.id}
                style={{
                  padding: 'var(--spacing-md)',
                  background: 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--spacing-sm)',
                  marginBottom: 'var(--spacing-sm)'
                }}>
                  <div style={{
                    padding: 'var(--spacing-xs) var(--spacing-sm)',
                    background: 'var(--accent-purple)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: 'var(--bg-primary)'
                  }}>
                    {event.name}
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {event.timestamp}
                  </span>
                </div>
                <div style={{
                  padding: 'var(--spacing-sm)',
                  background: 'var(--bg-primary)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  fontFamily: 'monospace',
                  overflowX: 'auto'
                }}>
                  {JSON.stringify(event.payload, null, 2)}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'traces' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
            {mockTraces.map(trace => (
              <div
                key={trace.id}
                style={{
                  padding: 'var(--spacing-md)',
                  background: 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 'var(--spacing-md)'
                }}>
                  <div>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                      Trace #{trace.id}
                    </span>
                    <span style={{ color: 'var(--text-muted)', marginLeft: 'var(--spacing-sm)', fontSize: '0.85rem' }}>
                      {trace.timestamp}
                    </span>
                  </div>
                  <div style={{
                    padding: 'var(--spacing-xs) var(--spacing-sm)',
                    background: 'var(--accent-blue)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: 'var(--bg-primary)'
                  }}>
                    {trace.duration} ms
                  </div>
                </div>
                
                {/* Duration bar */}
                <div style={{
                  width: '100%',
                  height: '4px',
                  background: 'var(--bg-primary)',
                  borderRadius: '2px',
                  marginBottom: 'var(--spacing-md)',
                  position: 'relative'
                }}>
                  <div style={{
                    width: '100%',
                    height: '100%',
                    background: 'var(--accent-blue)',
                    borderRadius: '2px',
                    opacity: 0.7
                  }} />
                </div>
                
                {/* Spans */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                  {trace.spans.map((span, index) => (
                    <div key={index} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      fontSize: '0.8rem'
                    }}>
                      <span style={{ color: 'var(--text-secondary)' }}>
                        {span.name}
                      </span>
                      <span style={{ color: 'var(--text-muted)' }}>
                        {span.duration} ms
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

