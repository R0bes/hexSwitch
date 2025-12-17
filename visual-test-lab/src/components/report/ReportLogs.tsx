import type { ReportLog } from '../../types/report';

interface ReportLogsProps {
  logs: ReportLog[];
}

export default function ReportLogs({ logs }: ReportLogsProps) {
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
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-sm)',
      maxHeight: '500px',
      overflowY: 'auto'
    }}>
      {logs.length === 0 ? (
        <div style={{
          color: 'var(--text-muted)',
          fontSize: '0.9rem',
          textAlign: 'center',
          padding: 'var(--spacing-xl)'
        }}>
          No logs recorded
        </div>
      ) : (
        logs.map((log, index) => (
          <div
            key={index}
            style={{
              padding: 'var(--spacing-sm)',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              borderLeft: `3px solid ${getLevelColor(log.level)}`,
              lineHeight: '1.6',
              fontSize: '0.85rem',
              fontFamily: 'monospace'
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
        ))
      )}
    </div>
  );
}


