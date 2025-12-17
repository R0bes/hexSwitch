import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import TopBar from './components/TopBar';
import AdapterLibrary from './components/AdapterLibrary';
import HexagonalCanvas from './components/HexagonalCanvas';
import LogsPanel from './components/LogsPanel';
import ScenarioTimeline from './components/ScenarioTimeline';
import ConfigurationPanel from './components/ConfigurationPanel';
import ScenarioReport from './components/ScenarioReport';
import RuntimeLoader from './components/runtime/RuntimeLoader';
import { mockScenarios } from './data/mockScenarios';
import { useDataFlow } from './hooks/useDataFlow';
import { useElementSelectionContext } from './contexts/ElementSelectionContext';
import { useScenarioReport } from './hooks/useScenarioReport';
import type { RuntimeType } from './types/runtime';

function App() {
  const [selectedScenario, setSelectedScenario] = useState(mockScenarios[0].id);
  const [isRunning, setIsRunning] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [selectedAdapterId, setSelectedAdapterId] = useState<string | null>(null);
  const [isLogsPanelOpen, setIsLogsPanelOpen] = useState(true);
  const [isAdapterLibraryOpen, setIsAdapterLibraryOpen] = useState(true);
  const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [runtimeType, setRuntimeType] = useState<RuntimeType>('mock');
  const { pulses, triggerPulse, clearPulses } = useDataFlow();
  const { selectedElement, clearSelection } = useElementSelectionContext();

  const currentScenario = mockScenarios.find(s => s.id === selectedScenario);
  const scenarioReport = useScenarioReport({
    scenarioId: selectedScenario,
    scenarioName: currentScenario?.name || 'Unknown',
    totalSteps: currentScenario?.steps.length || 0
  });

  // Open config panel when element is selected
  useEffect(() => {
    if (selectedElement) {
      setIsConfigPanelOpen(true);
    }
  }, [selectedElement]);

  const handleRunScenario = () => {
    setIsRunning(true);
    setCurrentStepIndex(0);
    clearPulses();
    scenarioReport.clearReport();
    scenarioReport.startCollection();
    
    // Simulate scenario execution - advance steps
    const scenario = mockScenarios.find(s => s.id === selectedScenario);
    if (!scenario) return;
    
    // Trigger data flow pulses based on scenario steps - SEQUENTIALLY (cascading)
    scenario.steps.forEach((step, index) => {
      const stepStartTime = index * 2000; // More time between steps to allow cascading
      
      // Record step start
      scenarioReport.recordStepStart(step.id, step.name);
      scenarioReport.recordLog({
        level: 'INFO',
        source: 'Scenario Runner',
        message: `Starting step: ${step.name}`,
        stepId: step.id
      });
      
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
    
    let completedSteps = 0;
    let failedSteps = 0;
    
    const interval = setInterval(() => {
      setCurrentStepIndex(prev => {
        const currentStep = scenario.steps[prev];
        if (currentStep) {
          // Record step completion
          const status = currentStep.status === 'error' ? 'error' : 'success';
          scenarioReport.recordStepEnd(currentStep.id, status);
          scenarioReport.recordLog({
            level: status === 'error' ? 'ERROR' : 'INFO',
            source: 'Scenario Runner',
            message: `Step completed: ${currentStep.name}`,
            stepId: currentStep.id
          });
          
          if (status === 'error') {
            failedSteps++;
            scenarioReport.recordError({
              stepId: currentStep.id,
              stepName: currentStep.name,
              message: `Step failed: ${currentStep.name}`,
              source: 'Scenario Runner'
            });
          } else {
            completedSteps++;
          }
        }
        
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
      
      // Generate and show report
      const report = scenarioReport.generateReport(completedSteps, failedSteps);
      if (report) {
        setShowReport(true);
      }
    }, totalDuration);
  };

  // Reset when scenario changes
  useEffect(() => {
    setCurrentStepIndex(0);
    setIsRunning(false);
  }, [selectedScenario]);

  const timelineHeight = '120px'; // Increased to prevent icon clipping
  const adapterLibraryWidth = '250px';
  const logsPanelWidth = '300px';
  const configPanelWidth = '350px';

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      display: 'grid',
      gridTemplateRows: `60px 1fr ${timelineHeight}`,
      gridTemplateColumns: `${isAdapterLibraryOpen ? adapterLibraryWidth : '0px'} 1fr ${isLogsPanelOpen ? logsPanelWidth : '0px'} ${isConfigPanelOpen ? configPanelWidth : '0px'}`,
      background: 'var(--bg-primary)',
      overflow: 'hidden',
      transition: 'grid-template-columns var(--transition-normal)'
    }}>
      {/* TopBar - spans full width */}
      <div style={{ gridColumn: '1 / -1' }}>
        <TopBar />
      </div>

      {/* Left Sidebar - Adapter Library */}
      <div style={{
        gridColumn: '1',
        gridRow: '2',
        position: 'relative',
        borderRight: '1px solid var(--border-color)',
        overflow: 'hidden',
        width: isAdapterLibraryOpen ? adapterLibraryWidth : '0px',
        transition: 'width var(--transition-normal)'
      }}>
        {isAdapterLibraryOpen && (
          <AdapterLibrary 
            selectedAdapterId={selectedAdapterId}
            onAdapterSelect={setSelectedAdapterId}
          />
        )}
      </div>

      {/* Toggle Button for Adapter Library - separate container that's always visible */}
      <div style={{
        gridColumn: '1',
        gridRow: '2',
        position: 'relative',
        pointerEvents: 'none',
        zIndex: 1001
      }}>
        <button
          onClick={() => setIsAdapterLibraryOpen(!isAdapterLibraryOpen)}
          style={{
            position: 'absolute',
            left: isAdapterLibraryOpen ? '-28px' : '0px',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '28px',
            height: '64px',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderLeft: isAdapterLibraryOpen ? 'none' : '1px solid var(--border-color)',
            borderRight: isAdapterLibraryOpen ? '1px solid var(--border-color)' : 'none',
            borderTopLeftRadius: isAdapterLibraryOpen ? 'var(--radius-md)' : '0',
            borderBottomLeftRadius: isAdapterLibraryOpen ? 'var(--radius-md)' : '0',
            borderTopRightRadius: isAdapterLibraryOpen ? '0' : 'var(--radius-md)',
            borderBottomRightRadius: isAdapterLibraryOpen ? '0' : 'var(--radius-md)',
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
          {isAdapterLibraryOpen ? (
            <ChevronLeft size={18} />
          ) : (
            <ChevronRight size={18} />
          )}
        </button>
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
        <RuntimeLoader
          runtimeType={runtimeType}
          onRuntimeTypeChange={setRuntimeType}
        />
      </div>

      {/* Right Sidebar - Logs Panel */}
      <div style={{
        gridColumn: '3',
        gridRow: '2',
        position: 'relative',
        borderLeft: '1px solid var(--border-color)',
        overflow: 'hidden',
        width: isLogsPanelOpen ? logsPanelWidth : '0px',
        transition: 'width var(--transition-normal)'
      }}>
        {isLogsPanelOpen && <LogsPanel />}
      </div>
      
      {/* Configuration Panel */}
      <div style={{
        gridColumn: '4',
        gridRow: '2',
        position: 'relative',
        borderLeft: '1px solid var(--border-color)',
        overflow: 'hidden',
        width: isConfigPanelOpen ? configPanelWidth : '0px',
        transition: 'width var(--transition-normal)'
      }}>
        {isConfigPanelOpen && (
          <ConfigurationPanel onClose={() => {
            setIsConfigPanelOpen(false);
            clearSelection();
          }} />
        )}
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
            right: '0px',
            top: '50%',
            transform: isLogsPanelOpen ? 'translateY(-50%) scaleY(-1)' : 'translateY(-50%)',
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

      {/* Toggle Button for Config Panel */}
      {isConfigPanelOpen && (
        <div style={{
          gridColumn: '4',
          gridRow: '2',
          position: 'relative',
          pointerEvents: 'none',
          zIndex: 1001
        }}>
          <button
            onClick={() => {
              setIsConfigPanelOpen(false);
              clearSelection();
            }}
            style={{
              position: 'absolute',
              right: '-28px',
              top: '50%',
              transform: 'translateY(-50%)',
              width: '28px',
              height: '64px',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRight: 'none',
              borderTopLeftRadius: 'var(--radius-md)',
              borderBottomLeftRadius: 'var(--radius-md)',
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
            <ChevronRight size={18} />
          </button>
        </div>
      )}

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
          onScenarioChange={setSelectedScenario}
          onRunScenario={handleRunScenario}
        />
      </div>

      {/* Report Modal */}
      {showReport && scenarioReport.report && (
        <ScenarioReport
          report={scenarioReport.report}
          onClose={() => setShowReport(false)}
        />
      )}
    </div>
  );
}

export default App;
