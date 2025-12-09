import { useState } from 'react';
import { Hexagon, Play, Moon, Sun, User } from 'lucide-react';
import { mockScenarios } from '../data/mockScenarios';

interface TopBarProps {
  selectedScenario: string;
  onScenarioChange: (scenarioId: string) => void;
  onRunScenario: () => void;
}

export default function TopBar({ selectedScenario, onScenarioChange, onRunScenario }: TopBarProps) {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  return (
    <div style={{
      height: '60px',
      background: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 var(--spacing-lg)',
      boxShadow: 'var(--shadow-md)'
    }}>
      {/* Left: Logo */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-md)'
      }}>
        <Hexagon 
          size={24} 
          color="var(--accent-teal)" 
          style={{ filter: 'drop-shadow(var(--glow-teal))' }}
        />
        <span style={{
          fontSize: '1.1rem',
          fontWeight: 600,
          color: 'var(--text-primary)'
        }}>
          HexSwitch – Visual Test Lab
        </span>
      </div>

      {/* Center: Scenario Dropdown */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-sm)'
      }}>
        <span style={{
          color: 'var(--text-secondary)',
          fontSize: '0.9rem'
        }}>
          Scenario:
        </span>
        <select
          value={selectedScenario}
          onChange={(e) => onScenarioChange(e.target.value)}
          style={{
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-sm) var(--spacing-md)',
            color: 'var(--text-primary)',
            fontSize: '0.95rem',
            cursor: 'pointer',
            minWidth: '200px'
          }}
        >
          {mockScenarios.map(scenario => (
            <option key={scenario.id} value={scenario.id}>
              {scenario.name}
            </option>
          ))}
        </select>
      </div>

      {/* Right: Controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-md)'
      }}>
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          style={{
            background: 'transparent',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-sm)',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all var(--transition-normal)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-teal)';
            e.currentTarget.style.boxShadow = 'var(--glow-teal)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        >
          {theme === 'dark' ? <Moon size={18} /> : <Sun size={18} />}
        </button>

        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: 'var(--bg-tertiary)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer'
        }}>
          <User size={18} color="var(--text-secondary)" />
        </div>

        <button
          onClick={onRunScenario}
          style={{
            background: 'var(--accent-teal)',
            color: 'var(--bg-primary)',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--spacing-sm) var(--spacing-lg)',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--spacing-sm)',
            boxShadow: 'var(--glow-teal)',
            transition: 'all var(--transition-normal)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--accent-cyan)';
            e.currentTarget.style.transform = 'scale(1.05)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--accent-teal)';
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          <Play size={16} fill="var(--bg-primary)" />
          Run Scenario
        </button>
      </div>
    </div>
  );
}

