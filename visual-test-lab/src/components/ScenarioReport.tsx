import { useState } from 'react';
import { X, Download, FileText } from 'lucide-react';
import type { ScenarioReport } from '../types/report';
import ReportMetrics from './report/ReportMetrics';
import ReportLogs from './report/ReportLogs';
import ReportTraces from './report/ReportTraces';
import ReportErrors from './report/ReportErrors';

interface ScenarioReportProps {
  report: ScenarioReport;
  onClose: () => void;
}

type TabType = 'overview' | 'logs' | 'traces' | 'errors';

export default function ScenarioReport({ report, onClose }: ScenarioReportProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const handleExport = (format: 'json' | 'csv') => {
    if (format === 'json') {
      const dataStr = JSON.stringify(report, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `scenario-report-${report.scenarioId}-${Date.now()}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      // Export metrics as CSV
      const csvRows = [
        ['Metric', 'Value'],
        ['Scenario', report.scenarioName],
        ['Duration (ms)', report.metrics.duration.toString()],
        ['Total Steps', report.metrics.totalSteps.toString()],
        ['Completed Steps', report.metrics.completedSteps.toString()],
        ['Failed Steps', report.metrics.failedSteps.toString()],
        ['Throughput (steps/s)', report.metrics.throughput.toFixed(2)],
        ['Avg Step Duration (ms)', report.metrics.averageStepDuration.toFixed(2)]
      ];
      
      const csvContent = csvRows.map(row => row.join(',')).join('\n');
      const dataBlob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `scenario-report-${report.scenarioId}-${Date.now()}.csv`;
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
      padding: 'var(--spacing-lg)'
    }}>
      <div style={{
        width: '90vw',
        maxWidth: '1200px',
        height: '90vh',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 'var(--shadow-lg)'
      }}>
        {/* Header */}
        <div style={{
          padding: 'var(--spacing-lg)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexShrink: 0
        }}>
          <div>
            <h2 style={{
              color: 'var(--text-primary)',
              fontSize: '1.2rem',
              fontWeight: 600,
              marginBottom: 'var(--spacing-xs)'
            }}>
              Scenario Report: {report.scenarioName}
            </h2>
            <div style={{
              color: 'var(--text-muted)',
              fontSize: '0.85rem'
            }}>
              Generated at {new Date(report.generatedAt).toLocaleString()}
            </div>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)'
          }}>
            <button
              onClick={() => handleExport('json')}
              style={{
                padding: 'var(--spacing-sm)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)',
                fontSize: '0.85rem'
              }}
            >
              <Download size={16} />
              JSON
            </button>
            <button
              onClick={() => handleExport('csv')}
              style={{
                padding: 'var(--spacing-sm)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-xs)',
                fontSize: '0.85rem'
              }}
            >
              <FileText size={16} />
              CSV
            </button>
            <button
              onClick={onClose}
              style={{
                padding: 'var(--spacing-sm)',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-primary)',
          flexShrink: 0
        }}>
          {[
            { id: 'overview' as TabType, label: 'Overview' },
            { id: 'logs' as TabType, label: 'Logs' },
            { id: 'traces' as TabType, label: 'Traces' },
            { id: 'errors' as TabType, label: 'Errors' }
          ].map(tab => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: 'var(--spacing-md)',
                  background: isActive ? 'var(--bg-secondary)' : 'transparent',
                  border: 'none',
                  borderBottom: isActive ? '2px solid var(--accent-teal)' : '2px solid transparent',
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  fontWeight: isActive ? 600 : 400,
                  transition: 'all var(--transition-normal)'
                }}
              >
                {tab.label}
                {tab.id === 'errors' && report.errors.length > 0 && (
                  <span style={{
                    marginLeft: 'var(--spacing-xs)',
                    padding: '2px 6px',
                    background: 'var(--accent-magenta)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    color: 'var(--bg-primary)'
                  }}>
                    {report.errors.length}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--spacing-lg)'
        }}>
          {activeTab === 'overview' && (
            <ReportMetrics
              metrics={report.metrics}
              stepMetrics={report.stepMetrics}
            />
          )}
          {activeTab === 'logs' && (
            <ReportLogs logs={report.logs} />
          )}
          {activeTab === 'traces' && (
            <ReportTraces traces={report.traces} />
          )}
          {activeTab === 'errors' && (
            <ReportErrors errors={report.errors} />
          )}
        </div>
      </div>
    </div>
  );
}


