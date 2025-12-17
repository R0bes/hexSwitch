import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { useConfiguration } from '../hooks/useConfiguration';

type ConfigurationContextType = ReturnType<typeof useConfiguration>;

const ConfigurationContext = createContext<ConfigurationContextType | null>(null);

export function ConfigurationProvider({ children }: { children: ReactNode }) {
  const config = useConfiguration();
  return (
    <ConfigurationContext.Provider value={config}>
      {children}
    </ConfigurationContext.Provider>
  );
}

export function useConfigurationContext() {
  const context = useContext(ConfigurationContext);
  if (!context) {
    throw new Error('useConfigurationContext must be used within ConfigurationProvider');
  }
  return context;
}

