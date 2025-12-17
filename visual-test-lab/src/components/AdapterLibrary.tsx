import { useState, useEffect } from 'react';
import { Plus, Trash2, Globe, Network, MessageSquare, Clock, Database, Box, Send, ExternalLink, Server, ChevronLeft, ChevronRight, X, ChevronDown } from 'lucide-react';
import { mockAdapters } from '../data/mockAdapters';
import { loadRealAdapters } from '../data/realAdapters';
import { useConfigurationContext } from '../contexts/ConfigurationContext';
import { useElementSelectionContext } from '../contexts/ElementSelectionContext';
import type { AdapterNode, MockNode } from '../data/mockAdapters';
import type { Port } from './CoreHexagon';

const iconMap: Record<string, any> = {
  Globe,
  Network,
  MessageSquare,
  Clock,
  Database,
  Box,
  Send,
  ExternalLink,
  Server
};

interface AdapterLibraryProps {
  selectedAdapterId: string | null;
  onAdapterSelect: (adapterId: string | null) => void;
}

type TabType = 'ports' | 'adapters' | 'mocks';

export default function AdapterLibrary({ selectedAdapterId, onAdapterSelect }: AdapterLibraryProps) {
  const { ports, adapterNodes, mockNodes, addAdapterNode, removeAdapterNode, addMockNode, removeMockNode, addPort, removePort } = useConfigurationContext();
  const { selectElement } = useElementSelectionContext();
  const [activeTab, setActiveTab] = useState<TabType>('ports');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [availableAdapters, setAvailableAdapters] = useState(mockAdapters);
  
  // Load real adapters on mount
  useEffect(() => {
    loadRealAdapters().then(adapters => {
      setAvailableAdapters(adapters);
    });
  }, []);
  
  // Inline add states
  const [addingAdapterToPort, setAddingAdapterToPort] = useState<string | null>(null);
  const [addingMockToAdapter, setAddingMockToAdapter] = useState<string | null>(null);
  const [newAdapterType, setNewAdapterType] = useState<string>('');
  const [newMockName, setNewMockName] = useState('');
  const [newMockType, setNewMockType] = useState<'http' | 'database' | 'message-broker' | 'cache'>('http');
  const [newMockDirection, setNewMockDirection] = useState<'inbound' | 'outbound'>('inbound');
  const [expandedPorts, setExpandedPorts] = useState<Set<string>>(new Set());
  const [expandedMocks, setExpandedMocks] = useState<Set<string>>(new Set());
  
  const togglePort = (portId: string) => {
    setExpandedPorts(prev => {
      const next = new Set(prev);
      if (next.has(portId)) {
        next.delete(portId);
      } else {
        next.add(portId);
      }
      return next;
    });
  };
  
  const toggleMock = (mockId: string) => {
    setExpandedMocks(prev => {
      const next = new Set(prev);
      if (next.has(mockId)) {
        next.delete(mockId);
      } else {
        next.add(mockId);
      }
      return next;
    });
  };

  const handleAddAdapter = (portId: string) => {
    setAddingAdapterToPort(portId);
    setNewAdapterType('');
  };

  const handleAddAdapterConfirm = (portId: string) => {
    if (!newAdapterType) return;
    
    const adapter = availableAdapters.find(a => a.id === newAdapterType);
    if (!adapter) return;

    let defaultConfig: Record<string, any> = {};
    if (adapter.id === 'http-inbound') {
      defaultConfig = { method: 'POST', path: '/api', handler: 'handlers:handle' };
    } else if (adapter.id === 'grpc-inbound') {
      defaultConfig = { service: 'Service', methods: ['Method'] };
    } else if (adapter.id === 'message-consumer') {
      defaultConfig = { topic: 'topic', events: ['Event'] };
    } else if (adapter.id === 'scheduler-trigger') {
      defaultConfig = { interval: '5s', task: 'Task', active: true };
    } else if (adapter.id === 'db-mock') {
      defaultConfig = { type: 'PostgreSQL', mode: 'deterministic', table: 'table' };
    } else if (adapter.id === 'http-client-mock') {
      defaultConfig = { endpoint: 'https://api.example.com', latency: 150 };
    }

    const newNode: AdapterNode = {
      id: `node-${newAdapterType}-${Date.now()}`,
      adapterId: newAdapterType,
      position: { x: 0, y: 0 },
      config: defaultConfig,
      status: 'connected',
      portId
    };

    addAdapterNode(newNode);
    setAddingAdapterToPort(null);
    setNewAdapterType('');
  };

  const handleAddMock = (adapterId: string) => {
    setAddingMockToAdapter(adapterId);
    setNewMockName('');
    setNewMockType('http');
    setNewMockDirection('inbound');
  };

  const handleAddMockConfirm = (adapterId: string) => {
    if (!newMockName) return;

    let defaultConfig: Record<string, any> = {};
    if (newMockType === 'http') {
      defaultConfig = { endpoint: 'http://example.com', methods: ['GET', 'POST'] };
    } else if (newMockType === 'database') {
      defaultConfig = { host: 'localhost', port: 5432, database: 'testdb' };
    } else if (newMockType === 'message-broker') {
      defaultConfig = { url: 'nats://localhost:4222', topics: ['topic'] };
    }

    const newMock: MockNode = {
      id: `mock-${Date.now()}`,
      name: newMockName,
      type: newMockType,
      direction: newMockDirection,
      config: defaultConfig,
      connectedToAdapter: adapterId,
      position: { x: 0, y: 0 }
    };

    addMockNode(newMock);
    setAddingMockToAdapter(null);
    setNewMockName('');
  };

  const handleRemoveAdapter = (nodeId: string) => {
    if (confirm('Are you sure you want to remove this adapter?')) {
      removeAdapterNode(nodeId);
    }
  };

  const handleRemoveMock = (mockId: string) => {
    if (confirm('Are you sure you want to remove this mock?')) {
      removeMockNode(mockId);
    }
  };

  const handleRemovePort = (portId: string) => {
    if (confirm('Are you sure you want to remove this port?')) {
      removePort(portId);
    }
  };

  if (isCollapsed) {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: 'var(--spacing-sm)',
        borderRight: '1px solid var(--border-color)',
        background: 'var(--bg-secondary)'
      }}>
        <button
          onClick={() => setIsCollapsed(false)}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-sm)',
            padding: 'var(--spacing-xs)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <ChevronRight size={18} />
        </button>
      </div>
    );
  }

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)'
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
          fontWeight: 600,
          margin: 0
        }}>
          Library
        </h3>
        <button
          onClick={() => setIsCollapsed(true)}
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
          <ChevronLeft size={18} />
        </button>
      </div>

      {/* Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        flexShrink: 0
      }}>
        {(['ports', 'adapters', 'mocks'] as TabType[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              flex: 1,
              padding: 'var(--spacing-sm)',
              background: activeTab === tab ? 'var(--bg-primary)' : 'transparent',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid var(--accent-teal)' : '2px solid transparent',
              color: activeTab === tab ? 'var(--text-primary)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: activeTab === tab ? 600 : 400,
              textTransform: 'capitalize',
              transition: 'all var(--transition-normal)'
            }}
          >
            {tab} {tab === 'ports' ? `(${ports.length})` : tab === 'adapters' ? `(${adapterNodes.length})` : `(${mockNodes.length})`}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--spacing-md)'
      }}>
        {/* Ports Tab */}
        {activeTab === 'ports' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
            {ports.map(port => {
              const adaptersOnPort = adapterNodes.filter(n => n.portId === port.id);
              const isExpanded = expandedPorts.has(port.id);
              return (
                <div
                  key={port.id}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--spacing-sm)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: isExpanded ? 'var(--spacing-xs)' : 0
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--spacing-xs)',
                      flex: 1
                    }}>
                      <button
                        onClick={() => togglePort(port.id)}
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
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                      </button>
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 'var(--spacing-xs)',
                          flex: 1,
                          cursor: 'pointer'
                        }}
                        onClick={() => selectElement('port', port.id)}
                      >
                        <span style={{
                          color: port.type === 'inbound' ? 'var(--accent-inbound)' : 'var(--accent-outbound)',
                          fontSize: '0.9rem',
                          fontWeight: 600
                        }}>
                          {port.label}
                        </span>
                        <span style={{
                          color: 'var(--text-muted)',
                          fontSize: '0.75rem'
                        }}>
                          ({adaptersOnPort.length})
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemovePort(port.id)}
                      style={{
                        padding: 'var(--spacing-xs)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--accent-magenta)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  
                  {isExpanded && (
                    <>
                      {addingAdapterToPort === port.id ? (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--spacing-xs)',
                      marginTop: 'var(--spacing-xs)',
                      padding: 'var(--spacing-xs)',
                      background: 'var(--bg-tertiary)',
                      borderRadius: 'var(--radius-sm)'
                    }}>
                      <select
                        value={newAdapterType}
                        onChange={(e) => setNewAdapterType(e.target.value)}
                        style={{
                          width: '100%',
                          padding: 'var(--spacing-xs)',
                          background: 'var(--bg-primary)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-primary)',
                          fontSize: '0.8rem'
                        }}
                      >
                        <option value="">Select adapter...</option>
                        {availableAdapters
                          .filter(a => {
                            const portType = port.type === 'inbound' ? 'inbound' : 'outbound';
                            return a.type === portType;
                          })
                          .map(adapter => (
                            <option key={adapter.id} value={adapter.id}>
                              {adapter.name}
                            </option>
                          ))}
                      </select>
                      <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                        <button
                          onClick={() => handleAddAdapterConfirm(port.id)}
                          disabled={!newAdapterType}
                          style={{
                            flex: 1,
                            padding: 'var(--spacing-xs)',
                            background: newAdapterType ? 'var(--accent-teal)' : 'var(--bg-tertiary)',
                            border: 'none',
                            borderRadius: 'var(--radius-sm)',
                            color: newAdapterType ? 'var(--bg-primary)' : 'var(--text-muted)',
                            cursor: newAdapterType ? 'pointer' : 'not-allowed',
                            fontSize: '0.8rem',
                            fontWeight: 600
                          }}
                        >
                          Add
                        </button>
                        <button
                          onClick={() => {
                            setAddingAdapterToPort(null);
                            setNewAdapterType('');
                          }}
                          style={{
                            padding: 'var(--spacing-xs)',
                            background: 'var(--bg-tertiary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: 'var(--radius-sm)',
                            color: 'var(--text-primary)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleAddAdapter(port.id)}
                      style={{
                        width: '100%',
                        marginTop: 'var(--spacing-xs)',
                        padding: 'var(--spacing-xs)',
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-primary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 'var(--spacing-xs)',
                        fontSize: '0.8rem'
                      }}
                    >
                      <Plus size={14} />
                      Add Adapter
                    </button>
                      )}
                    </>
                  )}
                </div>
              );
            })}
            <button
              onClick={() => {
                const newPort: Port = {
                  id: `port-${Date.now()}`,
                  label: 'New Port',
                  edgeIndex: ports.length % 6,
                  type: 'inbound'
                };
                addPort(newPort);
              }}
              style={{
                width: '100%',
                padding: 'var(--spacing-sm)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 'var(--spacing-xs)',
                fontSize: '0.85rem',
                fontWeight: 600
              }}
            >
              <Plus size={16} />
              Add Port
            </button>
          </div>
        )}

        {/* Adapters Tab */}
        {activeTab === 'adapters' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
            {adapterNodes.map(node => {
              const adapter = availableAdapters.find(a => a.id === node.adapterId);
              if (!adapter) return null;
              const Icon = iconMap[adapter.icon] || Globe;
              const port = ports.find(p => p.id === node.portId);

              return (
                <div
                  key={node.id}
                  style={{
                    background: selectedAdapterId === node.adapterId ? 'var(--bg-tertiary)' : 'var(--bg-primary)',
                    border: `2px solid ${selectedAdapterId === node.adapterId ? 'var(--accent-teal)' : 'var(--border-color)'}`,
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--spacing-sm)',
                    cursor: 'pointer',
                    transition: 'all var(--transition-normal)'
                  }}
                  onClick={() => onAdapterSelect(selectedAdapterId === node.adapterId ? null : node.adapterId)}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-sm)',
                    marginBottom: 'var(--spacing-xs)'
                  }}>
                    <Icon size={16} color={adapter.type === 'inbound' ? 'var(--accent-inbound)' : 'var(--accent-outbound)'} />
                    <span style={{ color: 'var(--text-primary)', flex: 1, fontSize: '0.9rem', fontWeight: 600 }}>
                      {adapter.name}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveAdapter(node.id);
                      }}
                      style={{
                        padding: 'var(--spacing-xs)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--accent-magenta)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  <div style={{
                    color: 'var(--text-secondary)',
                    fontSize: '0.75rem',
                    marginLeft: '24px'
                  }}>
                    Port: {port?.label || node.portId} • Status: {node.status}
                  </div>
                </div>
              );
            })}
            {adapterNodes.length === 0 && (
              <div style={{
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.85rem',
                padding: 'var(--spacing-lg)'
              }}>
                No adapters yet. Add one from the Ports tab.
              </div>
            )}
          </div>
        )}

        {/* Mocks Tab */}
        {activeTab === 'mocks' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
            {mockNodes.map(mock => {
              const adapter = adapterNodes.find(a => a.id === mock.connectedToAdapter);
              const adapterType = adapter ? availableAdapters.find(a => a.id === adapter.adapterId) : null;
              const MockIcon = iconMap[mock.type === 'http' ? 'Globe' : mock.type === 'database' ? 'Database' : mock.type === 'message-broker' ? 'MessageSquare' : 'Server'] || Server;
              const isExpanded = expandedMocks.has(mock.id);

              return (
                <div
                  key={mock.id}
                  style={{
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: 'var(--spacing-sm)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-sm)',
                    marginBottom: isExpanded ? 'var(--spacing-xs)' : 0
                  }}>
                    <button
                      onClick={() => toggleMock(mock.id)}
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
                      {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </button>
                    <MockIcon size={16} color={mock.direction === 'inbound' ? 'var(--accent-inbound-dark)' : 'var(--accent-outbound-dark)'} />
                    <span style={{ color: 'var(--text-primary)', flex: 1, fontSize: '0.9rem', fontWeight: 600 }}>
                      {mock.name}
                    </span>
                    <button
                      onClick={() => handleRemoveMock(mock.id)}
                      style={{
                        padding: 'var(--spacing-xs)',
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--accent-magenta)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                  
                  {isExpanded && (
                    <>
                      <div style={{
                        color: 'var(--text-secondary)',
                        fontSize: '0.75rem',
                        marginLeft: '24px',
                        marginBottom: 'var(--spacing-xs)'
                      }}>
                        {mock.type} • {mock.direction} • {adapterType?.name || 'No adapter'}
                      </div>
                      
                      {addingMockToAdapter === mock.connectedToAdapter && mock.connectedToAdapter ? (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 'var(--spacing-xs)',
                      marginTop: 'var(--spacing-xs)',
                      padding: 'var(--spacing-xs)',
                      background: 'var(--bg-tertiary)',
                      borderRadius: 'var(--radius-sm)'
                    }}>
                      <input
                        type="text"
                        value={newMockName}
                        onChange={(e) => setNewMockName(e.target.value)}
                        placeholder="Mock name..."
                        style={{
                          width: '100%',
                          padding: 'var(--spacing-xs)',
                          background: 'var(--bg-primary)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-primary)',
                          fontSize: '0.8rem'
                        }}
                      />
                      <select
                        value={newMockType}
                        onChange={(e) => setNewMockType(e.target.value as any)}
                        style={{
                          width: '100%',
                          padding: 'var(--spacing-xs)',
                          background: 'var(--bg-primary)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-primary)',
                          fontSize: '0.8rem'
                        }}
                      >
                        <option value="http">HTTP</option>
                        <option value="database">Database</option>
                        <option value="message-broker">Message Broker</option>
                        <option value="cache">Cache</option>
                      </select>
                      <select
                        value={newMockDirection}
                        onChange={(e) => setNewMockDirection(e.target.value as any)}
                        style={{
                          width: '100%',
                          padding: 'var(--spacing-xs)',
                          background: 'var(--bg-primary)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-primary)',
                          fontSize: '0.8rem'
                        }}
                      >
                        <option value="inbound">Inbound</option>
                        <option value="outbound">Outbound</option>
                      </select>
                      <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                        <button
                          onClick={() => mock.connectedToAdapter && handleAddMockConfirm(mock.connectedToAdapter)}
                          disabled={!newMockName}
                          style={{
                            flex: 1,
                            padding: 'var(--spacing-xs)',
                            background: newMockName ? 'var(--accent-teal)' : 'var(--bg-tertiary)',
                            border: 'none',
                            borderRadius: 'var(--radius-sm)',
                            color: newMockName ? 'var(--bg-primary)' : 'var(--text-muted)',
                            cursor: newMockName ? 'pointer' : 'not-allowed',
                            fontSize: '0.8rem',
                            fontWeight: 600
                          }}
                        >
                          Add
                        </button>
                        <button
                          onClick={() => {
                            setAddingMockToAdapter(null);
                            setNewMockName('');
                          }}
                          style={{
                            padding: 'var(--spacing-xs)',
                            background: 'var(--bg-tertiary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: 'var(--radius-sm)',
                            color: 'var(--text-primary)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ) : mock.connectedToAdapter ? (
                    <button
                      onClick={() => {
                        if (mock.connectedToAdapter) {
                          handleAddMock(mock.connectedToAdapter);
                        }
                      }}
                      style={{
                        width: '100%',
                        marginTop: 'var(--spacing-xs)',
                        padding: 'var(--spacing-xs)',
                        background: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-primary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 'var(--spacing-xs)',
                        fontSize: '0.8rem'
                      }}
                    >
                      <Plus size={14} />
                      Add Mock
                    </button>
                      ) : null}
                    </>
                  )}
                </div>
              );
            })}
            {adapterNodes.length > 0 && mockNodes.length === 0 && (
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--spacing-xs)',
                padding: 'var(--spacing-xs)',
                background: 'var(--bg-tertiary)',
                borderRadius: 'var(--radius-sm)'
              }}>
                <select
                  value={addingMockToAdapter || ''}
                  onChange={(e) => {
                    if (e.target.value) {
                      handleAddMock(e.target.value);
                    }
                  }}
                  style={{
                    width: '100%',
                    padding: 'var(--spacing-xs)',
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    fontSize: '0.8rem'
                  }}
                >
                  <option value="">Select adapter...</option>
                  {adapterNodes.map(node => {
                    const adapter = availableAdapters.find(a => a.id === node.adapterId);
                    return (
                      <option key={node.id} value={node.id}>
                        {adapter?.name || node.id}
                      </option>
                    );
                  })}
                </select>
                {addingMockToAdapter && (
                  <>
                    <input
                      type="text"
                      value={newMockName}
                      onChange={(e) => setNewMockName(e.target.value)}
                      placeholder="Mock name..."
                      style={{
                        width: '100%',
                        padding: 'var(--spacing-xs)',
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-primary)',
                        fontSize: '0.8rem'
                      }}
                    />
                    <select
                      value={newMockType}
                      onChange={(e) => setNewMockType(e.target.value as any)}
                      style={{
                        width: '100%',
                        padding: 'var(--spacing-xs)',
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-primary)',
                        fontSize: '0.8rem'
                      }}
                    >
                      <option value="http">HTTP</option>
                      <option value="database">Database</option>
                      <option value="message-broker">Message Broker</option>
                      <option value="cache">Cache</option>
                    </select>
                    <select
                      value={newMockDirection}
                      onChange={(e) => setNewMockDirection(e.target.value as any)}
                      style={{
                        width: '100%',
                        padding: 'var(--spacing-xs)',
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-primary)',
                        fontSize: '0.8rem'
                      }}
                    >
                      <option value="inbound">Inbound</option>
                      <option value="outbound">Outbound</option>
                    </select>
                    <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                      <button
                        onClick={() => addingMockToAdapter && handleAddMockConfirm(addingMockToAdapter)}
                        disabled={!newMockName}
                        style={{
                          flex: 1,
                          padding: 'var(--spacing-xs)',
                          background: newMockName ? 'var(--accent-teal)' : 'var(--bg-tertiary)',
                          border: 'none',
                          borderRadius: 'var(--radius-sm)',
                          color: newMockName ? 'var(--bg-primary)' : 'var(--text-muted)',
                          cursor: newMockName ? 'pointer' : 'not-allowed',
                          fontSize: '0.8rem',
                          fontWeight: 600
                        }}
                      >
                        Add
                      </button>
                      <button
                        onClick={() => {
                          setAddingMockToAdapter(null);
                          setNewMockName('');
                        }}
                        style={{
                          padding: 'var(--spacing-xs)',
                          background: 'var(--bg-tertiary)',
                          border: '1px solid var(--border-color)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-primary)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
            {adapterNodes.length === 0 && (
              <div style={{
                textAlign: 'center',
                color: 'var(--text-muted)',
                fontSize: '0.85rem',
                padding: 'var(--spacing-lg)'
              }}>
                No adapters available. Add an adapter first.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
