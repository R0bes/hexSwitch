import type { ReportError } from '../../types/report';

interface ReportErrorsProps {
  errors: ReportError[];
}

export default function ReportErrors({ errors }: ReportErrorsProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-md)',
      maxHeight: '500px',
      overflowY: 'auto'
    }}>
      {errors.length === 0 ? (
        <div style={{
          color: 'var(--accent-teal)',
          fontSize: '0.9rem',
          textAlign: 'center',
          padding: 'var(--spacing-xl)',
          fontWeight: 600
        }}>
          ✓ No errors occurred
        </div>
      ) : (
        errors.map(error => (
          <div
            key={error.id}
            style={{
              padding: 'var(--spacing-md)',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--accent-magenta)',
              borderLeft: '4px solid var(--accent-magenta)'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 'var(--spacing-sm)'
            }}>
              <div>
                <span style={{ color: 'var(--accent-magenta)', fontWeight: 600, fontSize: '0.9rem' }}>
                  {error.stepName}
                </span>
                <span style={{ color: 'var(--text-muted)', marginLeft: 'var(--spacing-sm)', fontSize: '0.75rem' }}>
                  {error.stepId}
                </span>
              </div>
              <span style={{
                color: 'var(--text-muted)',
                fontSize: '0.75rem'
              }}>
                {new Date(error.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div style={{
              color: 'var(--text-primary)',
              marginBottom: 'var(--spacing-xs)',
              fontWeight: 600
            }}>
              {error.message}
            </div>
            <div style={{
              color: 'var(--text-secondary)',
              fontSize: '0.8rem',
              marginBottom: 'var(--spacing-xs)'
            }}>
              Source: {error.source}
            </div>
            {error.stack && (
              <details style={{
                marginTop: 'var(--spacing-sm)',
                padding: 'var(--spacing-sm)',
                background: 'var(--bg-primary)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.75rem',
                fontFamily: 'monospace',
                color: 'var(--text-secondary)'
              }}>
                <summary style={{
                  cursor: 'pointer',
                  color: 'var(--text-primary)',
                  marginBottom: 'var(--spacing-xs)'
                }}>
                  Stack Trace
                </summary>
                <pre style={{
                  margin: 0,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {error.stack}
                </pre>
              </details>
            )}
          </div>
        ))
      )}
    </div>
  );
}


