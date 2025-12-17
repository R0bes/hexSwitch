import type { ReportTrace } from '../../types/report';

interface ReportTracesProps {
  traces: ReportTrace[];
}

export default function ReportTraces({ traces }: ReportTracesProps) {
  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-md)',
      maxHeight: '500px',
      overflowY: 'auto'
    }}>
      {traces.length === 0 ? (
        <div style={{
          color: 'var(--text-muted)',
          fontSize: '0.9rem',
          textAlign: 'center',
          padding: 'var(--spacing-xl)'
        }}>
          No traces recorded
        </div>
      ) : (
        traces.map(trace => (
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
                  {trace.name}
                </span>
                <span style={{ color: 'var(--text-muted)', marginLeft: 'var(--spacing-sm)', fontSize: '0.85rem' }}>
                  {trace.id}
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
                {formatDuration(trace.duration)}
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
                  fontSize: '0.8rem',
                  padding: 'var(--spacing-xs)',
                  background: 'var(--bg-primary)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    {span.name}
                  </span>
                  <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    {formatDuration(span.duration)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}


