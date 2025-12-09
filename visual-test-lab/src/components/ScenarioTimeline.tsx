import { Send, Database, MessageSquare, Clock, CreditCard, CheckCircle } from 'lucide-react';
import { mockScenarios } from '../data/mockScenarios';

const iconMap: Record<string, any> = {
  Send,
  Database,
  MessageSquare,
  Clock,
  CreditCard,
  CheckCircle
};

interface ScenarioTimelineProps {
  scenarioId: string;
  isRunning: boolean;
  currentStepIndex?: number;
}

export default function ScenarioTimeline({ scenarioId, isRunning, currentStepIndex = 0 }: ScenarioTimelineProps) {
  const scenario = mockScenarios.find(s => s.id === scenarioId);
  if (!scenario) return null;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return '✓';
      case 'error':
        return '✗';
      case 'running':
        return '⟳';
      default:
        return '○';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'var(--accent-teal)';
      case 'error':
        return 'var(--accent-magenta)';
      case 'running':
        return 'var(--accent-cyan)';
      default:
        return 'var(--text-muted)';
    }
  };

  return (
    <div style={{
      height: '100%',
      padding: 'var(--spacing-md)',
      background: 'var(--bg-secondary)',
      overflowX: 'auto',
      overflowY: 'hidden'
    }}>
      <div style={{
        marginBottom: 'var(--spacing-sm)',
        color: 'var(--text-primary)',
        fontSize: '0.85rem',
        fontWeight: 600
      }}>
        Scenario Timeline
      </div>
      
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-md)',
        position: 'relative',
        minWidth: 'max-content'
      }}>
        {/* Connection line */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '48px',
          right: '48px',
          height: '2px',
          background: 'var(--border-color)',
          zIndex: 0
        }} />
        
        {scenario.steps.map((step, index) => {
          const Icon = iconMap[step.icon] || CheckCircle;
          const isActive = step.status === 'running' || (isRunning && index === currentStepIndex);
          const statusColor = getStatusColor(step.status);
          
          return (
            <div
              key={step.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '4px',
                position: 'relative',
                zIndex: 1,
                minWidth: '100px'
              }}
            >
              {/* Step node */}
              <div
                style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '50%',
                  background: isActive ? statusColor : 'var(--bg-tertiary)',
                  border: `2px solid ${isActive ? statusColor : 'var(--border-color)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'all var(--transition-normal)',
                  boxShadow: isActive ? `0 0 20px ${statusColor}` : 'none',
                  transform: isActive ? 'scale(1.1)' : 'scale(1)'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.borderColor = statusColor;
                    e.currentTarget.style.boxShadow = `0 0 10px ${statusColor}`;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.borderColor = 'var(--border-color)';
                    e.currentTarget.style.boxShadow = 'none';
                  }
                }}
              >
                <Icon
                  size={20}
                  color={isActive ? 'var(--bg-primary)' : 'var(--text-secondary)'}
                />
              </div>
              
              {/* Status indicator */}
              <div style={{
                position: 'absolute',
                top: '36px',
                right: '8px',
                width: '14px',
                height: '14px',
                borderRadius: '50%',
                background: statusColor,
                border: '2px solid var(--bg-secondary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '9px',
                fontWeight: 600,
                color: 'var(--bg-primary)',
                boxShadow: `0 0 8px ${statusColor}`
              }}>
                {getStatusIcon(step.status)}
              </div>
              
              {/* Step label */}
              <div style={{
                textAlign: 'center',
                maxWidth: '100px'
              }}>
                <div style={{
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  fontSize: '0.75rem',
                  fontWeight: isActive ? 600 : 400,
                  marginBottom: '2px'
                }}>
                  {step.name}
                </div>
                <div style={{
                  color: 'var(--text-muted)',
                  fontSize: '0.65rem'
                }}>
                  Step {index + 1}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

