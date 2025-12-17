import { useState } from 'react';
import { Moon, Sun, User } from 'lucide-react';
import logo from '/assets/logo.png';

interface TopBarProps {
}

export default function TopBar({}: TopBarProps) {
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
        <img 
          src={logo} 
          alt="HexSwitch Logo" 
          style={{
            height: '40px',
            width: 'auto',
            filter: 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.3))'
          }}
        />
        <span style={{
          fontSize: '1.1rem',
          fontWeight: 600,
          color: 'var(--text-primary)'
        }}>
          HexSwitch – Visual Test Lab
        </span>
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
      </div>
    </div>
  );
}

