import { useState, useCallback } from 'react';

export type SelectedElementType = 'adapter' | 'mock' | 'port' | null;

export interface SelectedElement {
  type: SelectedElementType;
  id: string;
}

export function useElementSelection() {
  const [selectedElement, setSelectedElement] = useState<SelectedElement | null>(null);

  const selectElement = useCallback((type: SelectedElementType, id: string) => {
    setSelectedElement({ type, id });
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedElement(null);
  }, []);

  const toggleSelection = useCallback((type: SelectedElementType, id: string) => {
    if (selectedElement?.type === type && selectedElement?.id === id) {
      clearSelection();
    } else {
      selectElement(type, id);
    }
  }, [selectedElement, selectElement, clearSelection]);

  const isSelected = useCallback((type: SelectedElementType, id: string) => {
    return selectedElement?.type === type && selectedElement?.id === id;
  }, [selectedElement]);

  return {
    selectedElement,
    selectElement,
    clearSelection,
    toggleSelection,
    isSelected
  };
}


