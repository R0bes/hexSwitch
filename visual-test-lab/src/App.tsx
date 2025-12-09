import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import TopBar from './components/TopBar';
import AdapterLibrary from './components/AdapterLibrary';
import HexagonalCanvas from './components/HexagonalCanvas';
import LogsPanel from './components/LogsPanel';
import ScenarioTimeline from './components/ScenarioTimeline';
import { mockScenarios } from './data/mockScenarios';
import { useDataFlow } from './hooks/useDataFlow';

function App() {
  const [selectedScenario, setSelectedScenario] = useState(mockScenarios[0].id);
  const [isRunning, setIsRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [selectedAdapterId, setSelectedAdapterId] = useState<string | null>(null);
  const [isLogsPanelOpen, setIsLogsPanelOpen] = useState(true);
  const { pulses, triggerPulse, clearPulses } = useDataFlow();

  const handleRunScenario = () => {
    setIsRunning(true);
    setCurrentStepIndex(0);
    clearPulses();
    
    // Simulate scenario execution - advance steps
    const scenario = mockScenarios.find(s => s.id === selectedScenario);
    if (!scenario) return;
    
    // Trigger data flow pulses based on scenario steps - SEQUENTIALLY (cascading)
    scenario.steps.forEach((step, index) => {
      const stepStartTime = index * 2000; // More time between steps to allow cascading
      
      setTimeout(() => {
        // Determine step type from name/icon
        const stepName = step.name.toLowerCase();
        const stepIcon = step.icon.toLowerCase();
        
        if (stepName.includes('http') && (stepName.includes('send') || stepName.includes('post'))) {
          // Inbound: Mock -> Adapter (wait) -> Adapter -> Port (wait) -> Port -> Core
          // Step 1: Mock sends to Adapter (800ms)
          triggerPulse('mock-mock-http-server->adapter-node-http-1', 'mock-to-adapter', 800);
          // Step 2: Adapter processes and sends to Port (starts after 800ms, duration 600ms)
          setTimeout(() => {
            triggerPulse('routing-api-in-node-http-1', 'inbound', 600);
            // Step 3: Port processes and sends to Core (starts after 800ms + 600ms, duration 400ms)
            setTimeout(() => {
              triggerPulse('core-port-api-in', 'inbound', 400);
            }, 600);
          }, 800);
        } else if (stepName.includes('db') || stepName.includes('database') || stepIcon === 'database') {
          // Outbound: Core -> Port (wait) -> Port -> Adapter (wait) -> Adapter -> Mock
          // Step 1: Core sends to Port (400ms)
          triggerPulse('core-port-repo-out', 'outbound', 400);
          // Step 2: Port processes and sends to Adapter (starts after 400ms, duration 600ms)
          setTimeout(() => {
            triggerPulse('routing-repo-out-node-db-1', 'outbound', 600);
            // Step 3: Adapter processes and sends to Mock (starts after 400ms + 600ms, duration 800ms)
            setTimeout(() => {
              triggerPulse('mock-mock-database->adapter-node-db-1', 'adapter-to-mock', 800);
            }, 600);
          }, 400);
        } else if (stepName.includes('emit') || stepName.includes('message') || stepIcon === 'messagesquare') {
          // Outbound: Core -> Port (wait) -> Port -> Adapter
          // Step 1: Core sends to Port (400ms)
          triggerPulse('core-port-message-out', 'outbound', 400);
          // Step 2: Port processes and sends to Adapter (starts after 400ms, duration 600ms)
          setTimeout(() => {
            triggerPulse('routing-message-out-node-message-1', 'outbound', 600);
          }, 400);
        } else if (stepName.includes('payment') || stepName.includes('external') || stepIcon === 'externallink' || stepIcon === 'creditcard') {
          // Outbound: Core -> Port (wait) -> Port -> Adapter (wait) -> Adapter -> Mock
          // Step 1: Core sends to Port (400ms)
          triggerPulse('core-port-external-api-out', 'outbound', 400);
          // Step 2: Port processes and sends to Adapter (starts after 400ms, duration 600ms)
          setTimeout(() => {
            triggerPulse('routing-external-api-out-node-http-client-1', 'outbound', 600);
            // Step 3: Adapter processes and sends to Mock (starts after 400ms + 600ms, duration 800ms)
            setTimeout(() => {
              triggerPulse('mock-mock-payment-service->adapter-node-http-client-1', 'adapter-to-mock', 800);
            }, 600);
          }, 400);
        }
      }, stepStartTime);
    });
    
    const interval = setInterval(() => {
      setCurrentStepIndex(prev => {
        if (prev >= scenario.steps.length - 1) {
          clearInterval(interval);
          setIsRunning(false);
          return prev;
        }
        return prev + 1;
      });
    }, 2000); // Match step interval
    
    // Cleanup after completion (allow time for all cascading pulses to complete)
    const totalDuration = scenario.steps.length * 2000 + 2000; // Extra buffer for cascading
    setTimeout(() => {
      clearInterval(interval);
      setIsRunning(false);
      setCurrentStepIndex(0);
      clearPulses();
    }, totalDuration);
  };

  // Reset when scenario changes
  useEffect(() => {
    setCurrentStepIndex(0);
    setIsRunning(false);
  }, [selectedScenario]);

  const timelineHeight = '80px';

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'grid',
      gridTemplateRows: `60px 1fr ${timelineHeight}`,
      gridTemplateColumns: '250px 1fr auto',
      background: 'var(--bg-primary)',
      overflow: 'hidden'
    }}>
      {/* TopBar - spans full width */}
      <div style={{ gridColumn: '1 / -1' }}>
        <TopBar
          selectedScenario={selectedScenario}
          onScenarioChange={setSelectedScenario}
          onRunScenario={handleRunScenario}
        />
      </div>

      {/* Left Sidebar - Adapter Library */}
      <div style={{
        gridColumn: '1',
        gridRow: '2',
        borderRight: '1px solid var(--border-color)',
        overflow: 'hidden'
      }}>
        <AdapterLibrary 
          selectedAdapterId={selectedAdapterId}
          onAdapterSelect={setSelectedAdapterId}
        />
      </div>

      {/* Center - Hexagonal Canvas */}
      <div style={{
        gridColumn: '2',
        gridRow: '2',
        position: 'relative',
        overflow: 'hidden',
        background: 'var(--bg-primary)',
        backgroundImage: `
          linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px'
      }}>
        <HexagonalCanvas 
          selectedAdapterId={selectedAdapterId} 
          activePulses={pulses}
        />
      </div>

      {/* Right Sidebar - Logs Panel */}
      <div style={{
        gridColumn: '3',
        gridRow: '2',
        position: 'relative',
        borderLeft: '1px solid var(--border-color)',
        overflow: 'hidden',
        width: isLogsPanelOpen ? '300px' : '0px',
        transition: 'width var(--transition-normal)'
      }}>
        {isLogsPanelOpen && <LogsPanel />}
      </div>
      
      {/* Toggle Button for Logs Panel - separate container that's always visible */}
      <div style={{
        gridColumn: '3',
        gridRow: '2',
        position: 'relative',
        pointerEvents: 'none',
        zIndex: 1001
      }}>
        <button
          onClick={() => setIsLogsPanelOpen(!isLogsPanelOpen)}
          style={{
            position: 'absolute',
            right: isLogsPanelOpen ? '-28px' : '0px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '28px',
            height: '64px',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRight: isLogsPanelOpen ? 'none' : '1px solid var(--border-color)',
            borderLeft: isLogsPanelOpen ? '1px solid var(--border-color)' : 'none',
            borderTopLeftRadius: isLogsPanelOpen ? '0' : 'var(--radius-md)',
            borderBottomLeftRadius: isLogsPanelOpen ? '0' : 'var(--radius-md)',
            borderTopRightRadius: isLogsPanelOpen ? 'var(--radius-md)' : '0',
            borderBottomRightRadius: isLogsPanelOpen ? 'var(--radius-md)' : '0',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-primary)',
            pointerEvents: 'auto',
            transition: 'all var(--transition-normal)',
            boxShadow: 'var(--shadow-md)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--bg-tertiary)';
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.boxShadow = 'var(--glow-teal)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--bg-secondary)';
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'var(--shadow-md)';
          }}
        >
          {isLogsPanelOpen ? (
            <ChevronRight size={18} />
          ) : (
            <ChevronLeft size={18} />
          )}
        </button>
      </div>

      {/* Bottom - Scenario Timeline */}
      <div style={{
        gridColumn: '1 / -1',
        gridRow: '3',
        borderTop: '1px solid var(--border-color)',
        overflow: 'hidden'
      }}>
        <ScenarioTimeline 
          scenarioId={selectedScenario}
          isRunning={isRunning}
          currentStepIndex={currentStepIndex}
        />
      </div>
    </div>
  );
}

export default App;
