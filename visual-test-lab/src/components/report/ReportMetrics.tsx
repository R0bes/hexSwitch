import type { ScenarioMetrics, StepMetrics } from '../../types/report';

interface ReportMetricsProps {
  metrics: ScenarioMetrics;
  stepMetrics: StepMetrics[];
}

export default function ReportMetrics({ metrics, stepMetrics }: ReportMetricsProps) {
  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-lg)'
    }}>
      {/* Overview Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 'var(--spacing-md)'
      }}>
        <MetricCard
          label="Total Duration"
          value={formatDuration(metrics.duration)}
          color="var(--accent-teal)"
        />
        <MetricCard
          label="Steps Completed"
          value={`${metrics.completedSteps} / ${metrics.totalSteps}`}
          color="var(--accent-cyan)"
        />
        <MetricCard
          label="Failed Steps"
          value={metrics.failedSteps.toString()}
          color={metrics.failedSteps > 0 ? 'var(--accent-magenta)' : 'var(--accent-teal)'}
        />
        <MetricCard
          label="Throughput"
          value={`${metrics.throughput.toFixed(2)} steps/s`}
          color="var(--accent-teal)"
        />
        <MetricCard
          label="Avg Step Duration"
          value={formatDuration(metrics.averageStepDuration)}
          color="var(--accent-teal)"
        />
        <MetricCard
          label="Start Time"
          value={formatTime(metrics.startTime)}
          color="var(--text-secondary)"
        />
      </div>

      {/* Step Details Table */}
      <div>
        <h4 style={{
          color: 'var(--text-primary)',
          fontSize: '0.9rem',
          fontWeight: 600,
          marginBottom: 'var(--spacing-md)'
        }}>
          Step Details
        </h4>
        <div style={{
          background: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          border: '1px solid var(--border-color)'
        }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.85rem'
          }}>
            <thead>
              <tr style={{
                background: 'var(--bg-tertiary)',
                borderBottom: '1px solid var(--border-color)'
              }}>
                <th style={{
                  padding: 'var(--spacing-sm)',
                  textAlign: 'left',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>Step</th>
                <th style={{
                  padding: 'var(--spacing-sm)',
                  textAlign: 'left',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>Status</th>
                <th style={{
                  padding: 'var(--spacing-sm)',
                  textAlign: 'right',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                  fontSize: '0.8rem'
                }}>Duration</th>
              </tr>
            </thead>
            <tbody>
              {stepMetrics.map((step, index) => (
                <tr
                  key={step.stepId}
                  style={{
                    borderBottom: index < stepMetrics.length - 1 ? '1px solid var(--border-color)' : 'none'
                  }}
                >
                  <td style={{
                    padding: 'var(--spacing-sm)',
                    color: 'var(--text-primary)'
                  }}>
                    {step.stepName}
                  </td>
                  <td style={{
                    padding: 'var(--spacing-sm)'
                  }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      background: step.status === 'success' 
                        ? 'var(--accent-teal)' 
                        : step.status === 'error'
                        ? 'var(--accent-magenta)'
                        : 'var(--bg-tertiary)',
                      color: step.status === 'success' || step.status === 'error'
                        ? 'var(--bg-primary)'
                        : 'var(--text-secondary)'
                    }}>
                      {step.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{
                    padding: 'var(--spacing-sm)',
                    textAlign: 'right',
                    color: 'var(--text-secondary)',
                    fontFamily: 'monospace'
                  }}>
                    {formatDuration(step.duration)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{
      background: 'var(--bg-secondary)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--spacing-md)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--spacing-xs)'
    }}>
      <div style={{
        color: 'var(--text-secondary)',
        fontSize: '0.75rem',
        fontWeight: 600,
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }}>
        {label}
      </div>
      <div style={{
        color,
        fontSize: '1.5rem',
        fontWeight: 700,
        fontFamily: 'monospace'
      }}>
        {value}
      </div>
    </div>
  );
}


