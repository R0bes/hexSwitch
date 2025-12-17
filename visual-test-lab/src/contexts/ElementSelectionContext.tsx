import { createContext, useContext } from 'react';
import type { ReactNode } from 'react';
import { useElementSelection } from '../hooks/useElementSelection';

type ElementSelectionContextType = ReturnType<typeof useElementSelection>;

const ElementSelectionContext = createContext<ElementSelectionContextType | null>(null);

export function ElementSelectionProvider({ children }: { children: ReactNode }) {
  const selection = useElementSelection();
  return (
    <ElementSelectionContext.Provider value={selection}>
      {children}
    </ElementSelectionContext.Provider>
  );
}

export function useElementSelectionContext() {
  const context = useContext(ElementSelectionContext);
  if (!context) {
    throw new Error('useElementSelectionContext must be used within ElementSelectionProvider');
  }
  return context;
}

