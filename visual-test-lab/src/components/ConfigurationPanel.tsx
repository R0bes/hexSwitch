import { X } from 'lucide-react';
import { useConfigurationContext } from '../contexts/ConfigurationContext';
import { useElementSelectionContext } from '../contexts/ElementSelectionContext';
import AdapterConfigForm from './configuration/AdapterConfigForm';
import MockConfigForm from './configuration/MockConfigForm';
import PortConfigForm from './configuration/PortConfigForm';

interface ConfigurationPanelProps {
  onClose: () => void;
}

export default function ConfigurationPanel({ onClose }: ConfigurationPanelProps) {
  const { selectedElement } = useElementSelectionContext();
  const { 
    adapterNodes, 
    mockNodes, 
    ports, 
    updateAdapterConfig, 
    updateMockConfig, 
    updatePortConfig 
  } = useConfigurationContext();

  if (!selectedElement) {
    return (
      <div style={{
        height: '100%',
        padding: 'var(--spacing-lg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.9rem'
      }}>
        Select an element to configure
      </div>
    );
  }

  const handleAdapterSave = (nodeId: string, config: Record<string, any>) => {
    updateAdapterConfig(nodeId, config);
    onClose();
  };

  const handleMockSave = (mockId: string, config: Record<string, any>) => {
    updateMockConfig(mockId, config);
    onClose();
  };

  const handlePortSave = (portId: string, config: Record<string, any>) => {
    updatePortConfig(portId, config);
    onClose();
  };

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-primary)'
    }}>
      {/* Header */}
      <div style={{
        padding: 'var(--spacing-md)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0
      }}>
        <h3 style={{
          color: 'var(--text-primary)',
          fontSize: '1rem',
          fontWeight: 600
        }}>
          Configuration
        </h3>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            padding: 'var(--spacing-xs)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <X size={18} />
        </button>
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--spacing-lg)'
      }}>
        {selectedElement.type === 'adapter' && (() => {
          const node = adapterNodes.find(n => n.id === selectedElement.id);
          if (!node) return null;
          return (
            <AdapterConfigForm
              node={node}
              onSave={handleAdapterSave}
              onCancel={onClose}
            />
          );
        })()}

        {selectedElement.type === 'mock' && (() => {
          const mock = mockNodes.find(m => m.id === selectedElement.id);
          if (!mock) return null;
          return (
            <MockConfigForm
              mock={mock}
              onSave={handleMockSave}
              onCancel={onClose}
            />
          );
        })()}

        {selectedElement.type === 'port' && (() => {
          const port = ports.find(p => p.id === selectedElement.id);
          if (!port) return null;
          return (
            <PortConfigForm
              port={port}
              onSave={handlePortSave}
              onCancel={onClose}
            />
          );
        })()}
      </div>
    </div>
  );
}


