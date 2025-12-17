import { useState, useRef } from 'react';
import { Send, Database, MessageSquare, Clock, CreditCard, CheckCircle, Play } from 'lucide-react';
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
  onScenarioChange?: (scenarioId: string) => void;
  onRunScenario?: () => void;
}

export default function ScenarioTimeline({ 
  scenarioId, 
  isRunning, 
  currentStepIndex = 0,
  onScenarioChange,
  onRunScenario
}: ScenarioTimelineProps) {
  const scenario = mockScenarios.find(s => s.id === scenarioId);
  const [hoveredStepIndex, setHoveredStepIndex] = useState<number | null>(null);
  const stepsContainerRef = useRef<HTMLDivElement>(null);
  
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

  // Calculate progress percentage
  const progressPercentage = scenario.steps.length > 0 
    ? ((currentStepIndex + 1) / scenario.steps.length) * 100 
    : 0;

  return (
    <div style={{
      height: '100%',
      padding: 'var(--spacing-sm) var(--spacing-md)',
      background: 'var(--bg-secondary)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      minHeight: '120px' // Ensure enough height
    }}>
      {/* Header with Controls and Progress Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 'var(--spacing-md)',
        marginBottom: 'var(--spacing-sm)',
        flexShrink: 0
      }}>
        {/* Left: Controls (Scenario Selector + Run Button) - stacked vertically */}
        {(onScenarioChange || onRunScenario) && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-xs)',
            flexShrink: 0
          }}>
            {onScenarioChange && (
              <select
                value={scenarioId}
                onChange={(e) => onScenarioChange(e.target.value)}
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--spacing-xs) var(--spacing-sm)',
                  color: 'var(--text-primary)',
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  minWidth: '180px'
                }}
              >
                {mockScenarios.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            )}
            
            {onRunScenario && (
              <button
                onClick={onRunScenario}
                disabled={isRunning}
                style={{
                  background: isRunning ? 'var(--bg-tertiary)' : 'var(--accent-teal)',
                  color: isRunning ? 'var(--text-muted)' : 'var(--bg-primary)',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  padding: 'var(--spacing-xs) var(--spacing-md)',
                  fontWeight: 600,
                  cursor: isRunning ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 'var(--spacing-xs)',
                  boxShadow: isRunning ? 'none' : 'var(--glow-teal)',
                  transition: 'all var(--transition-normal)',
                  fontSize: '0.85rem',
                  width: '100%'
                }}
                onMouseEnter={(e) => {
                  if (!isRunning) {
                    e.currentTarget.style.background = 'var(--accent-cyan)';
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isRunning) {
                    e.currentTarget.style.background = 'var(--accent-teal)';
                    e.currentTarget.style.transform = 'scale(1)';
                  }
                }}
              >
                <Play size={14} fill={isRunning ? 'var(--text-muted)' : 'var(--bg-primary)'} />
                {isRunning ? 'Running...' : 'Run'}
              </button>
            )}
          </div>
        )}
        
        {/* Right: Progress Bar and Steps - stacked vertically */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-xs)',
          minWidth: 0,
          minHeight: 0
        }}>
          {/* Progress Bar */}
          <div style={{
            width: '100%',
            height: '4px',
            background: 'var(--bg-tertiary)',
            borderRadius: '2px',
            overflow: 'hidden',
            position: 'relative',
            flexShrink: 0
          }}>
            <div style={{
              width: `${progressPercentage}%`,
              height: '100%',
              background: isRunning ? 'var(--accent-cyan)' : 'var(--accent-teal)',
              borderRadius: '2px',
              transition: 'width 0.3s ease',
              boxShadow: `0 0 8px ${isRunning ? 'var(--accent-cyan)' : 'var(--accent-teal)'}`
            }} />
          </div>
          
          {/* Scrollable Timeline Container - directly under Progress Bar */}
          <div style={{
            flex: 1,
            overflowX: 'auto',
            overflowY: 'visible', // Allow tooltips to be visible
            paddingTop: 'var(--spacing-xs)',
            paddingBottom: 'var(--spacing-xs)',
            paddingRight: 'var(--spacing-md)',
            paddingLeft: 'var(--spacing-xs)',
            minHeight: '0' // Important for flex child
          }}>
            <div 
              ref={stepsContainerRef}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 'var(--spacing-md)',
                position: 'relative',
                minWidth: 'max-content',
                paddingLeft: 'var(--spacing-md)',
                paddingRight: 'var(--spacing-md)',
                height: '100%',
                paddingTop: 'var(--spacing-xs)',
                paddingBottom: 'var(--spacing-xs)'
              }}
            >
          {/* Connection line */}
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '40px',
            right: '40px',
            height: '2px',
            background: 'var(--border-color)',
            zIndex: 0,
            transform: 'translateY(-50%)'
          }} />
          
          {/* Progress line (filled portion) */}
          {isRunning && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '40px',
              width: `calc(${progressPercentage}% * (100% - 80px) / 100)`,
              height: '2px',
              background: 'var(--accent-cyan)',
              zIndex: 1,
              transform: 'translateY(-50%)',
              transition: 'width 0.3s ease',
              boxShadow: '0 0 4px var(--accent-cyan)'
            }} />
          )}
        
          {scenario.steps.map((step, index) => {
            const Icon = iconMap[step.icon] || CheckCircle;
            const isActive = step.status === 'running' || (isRunning && index === currentStepIndex);
            const isCompleted = index < currentStepIndex || step.status === 'success';
            const isHovered = hoveredStepIndex === index;
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
                  zIndex: 2,
                  minWidth: '80px',
                  paddingTop: 'var(--spacing-xs)',
                  paddingBottom: 'var(--spacing-xs)'
                }}
                onMouseEnter={() => setHoveredStepIndex(index)}
                onMouseLeave={() => setHoveredStepIndex(null)}
              >
                {/* Tooltip */}
                {isHovered && (
                  <div style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    marginBottom: 'var(--spacing-xs)',
                    padding: 'var(--spacing-xs) var(--spacing-sm)',
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    fontSize: '0.75rem',
                    whiteSpace: 'nowrap',
                    zIndex: 1000,
                    boxShadow: 'var(--shadow-lg)',
                    pointerEvents: 'none'
                  }}>
                    <div style={{ fontWeight: 600, marginBottom: '2px' }}>{step.name}</div>
                    <div style={{ 
                      fontSize: '0.7rem', 
                      color: 'var(--text-secondary)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}>
                      {step.status || 'pending'}
                    </div>
                  </div>
                )}
                
                {/* Step node - smaller to fit better */}
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: isActive 
                      ? statusColor 
                      : isCompleted 
                      ? 'var(--bg-tertiary)' 
                      : 'var(--bg-tertiary)',
                    border: `2px solid ${isActive ? statusColor : isCompleted ? 'var(--accent-teal)' : 'var(--border-color)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    transition: 'all var(--transition-normal)',
                    boxShadow: isActive 
                      ? `0 0 16px ${statusColor}` 
                      : isHovered 
                      ? `0 0 8px ${statusColor}` 
                      : 'none',
                    transform: isActive ? 'scale(1.15)' : isHovered ? 'scale(1.05)' : 'scale(1)',
                    position: 'relative'
                  }}
                >
                  <Icon
                    size={18}
                    color={isActive ? 'var(--bg-primary)' : isCompleted ? 'var(--accent-teal)' : 'var(--text-secondary)'}
                  />
                  
                  {/* Active pulse animation */}
                  {isActive && (
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      width: '40px',
                      height: '40px',
                      borderRadius: '50%',
                      border: `2px solid ${statusColor}`,
                      animation: 'pulse-ring 2s ease-out infinite',
                      pointerEvents: 'none'
                    }} />
                  )}
                </div>
                
                {/* Status indicator - smaller and better positioned */}
                <div style={{
                  position: 'absolute',
                  top: '28px',
                  right: '4px',
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  background: statusColor,
                  border: '2px solid var(--bg-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '8px',
                  fontWeight: 600,
                  color: 'var(--bg-primary)',
                  boxShadow: `0 0 6px ${statusColor}`,
                  zIndex: 3
                }}>
                  {getStatusIcon(step.status)}
                </div>
                
                {/* Step label - more compact */}
                <div style={{
                  textAlign: 'center',
                  maxWidth: '80px',
                  marginTop: '2px'
                }}>
                  <div style={{
                    color: isActive ? 'var(--text-primary)' : isCompleted ? 'var(--text-secondary)' : 'var(--text-muted)',
                    fontSize: '0.7rem',
                    fontWeight: isActive ? 600 : 400,
                    lineHeight: '1.2',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {step.name}
                  </div>
                  <div style={{
                    color: 'var(--text-muted)',
                    fontSize: '0.6rem',
                    marginTop: '1px'
                  }}>
                    #{index + 1}
                  </div>
                </div>
              </div>
            );
          })}
            </div>
          </div>
        </div>
      </div>
      
      {/* CSS Animation for pulse ring */}
      <style>{`
        @keyframes pulse-ring {
          0% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
          }
          100% {
            transform: translate(-50%, -50%) scale(1.5);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}
