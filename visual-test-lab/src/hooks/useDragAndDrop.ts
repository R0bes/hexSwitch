import { useState, useCallback, useRef } from 'react';
import type { Point } from '../utils/hexagonGeometry';
import { projectPointToCircle, checkCollision, pointOnCircle } from '../utils/collisionDetection';
import type { Circle } from '../utils/collisionDetection';

export interface DragState {
  isDragging: boolean;
  draggedId: string | null;
  draggedType: 'adapter' | 'mock' | 'port' | null;
  startPosition: Point | null;
  currentPosition: Point | null;
}

export interface DragConstraints {
  type: 'free' | 'circle';
  circle?: Circle;
  tolerance?: number;
}

export function useDragAndDrop() {
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    draggedId: null,
    draggedType: null,
    startPosition: null,
    currentPosition: null
  });

  const constraintsRef = useRef<DragConstraints | null>(null);
  const existingPositionsRef = useRef<Array<{ x: number; y: number; id: string }>>([]);

  const startDrag = useCallback((
    id: string,
    type: 'adapter' | 'mock' | 'port',
    startPosition: Point,
    constraints?: DragConstraints,
    existingPositions?: Array<{ x: number; y: number; id: string }>
  ) => {
    setDragState({
      isDragging: true,
      draggedId: id,
      draggedType: type,
      startPosition,
      currentPosition: startPosition
    });
    
    constraintsRef.current = constraints || { type: 'free' };
    existingPositionsRef.current = existingPositions || [];
  }, []);

  const updateDrag = useCallback((position: Point): Point => {
    if (!dragState.isDragging || !constraintsRef.current) {
      return position;
    }

    let constrainedPosition = position;

    // Apply circle constraint
    if (constraintsRef.current.type === 'circle' && constraintsRef.current.circle) {
      const circle = constraintsRef.current.circle;
      const tolerance = constraintsRef.current.tolerance || 5;
      
      // Project point to circle if not already on it
      if (!pointOnCircle(position, circle, tolerance)) {
        constrainedPosition = projectPointToCircle(position, circle);
      }
    }

    // Check collision (but allow if it's the same position)
    const collision = checkCollision(
      constrainedPosition,
      existingPositionsRef.current,
      dragState.draggedId || undefined
    );

    // If collision, try to find a nearby valid position
    if (collision.collides && dragState.draggedType === 'mock') {
      // For mocks, we can move slightly to avoid collision
      // Try positions in a small spiral pattern
      const attempts = 8;
      const stepSize = 10;
      let found = false;
      
      for (let i = 1; i <= attempts && !found; i++) {
        const angle = (2 * Math.PI / attempts) * i;
        const offsetX = Math.cos(angle) * stepSize * i;
        const offsetY = Math.sin(angle) * stepSize * i;
        const testPosition = {
          x: constrainedPosition.x + offsetX,
          y: constrainedPosition.y + offsetY
        };
        
        const testCollision = checkCollision(
          testPosition,
          existingPositionsRef.current,
          dragState.draggedId || undefined
        );
        
        if (!testCollision.collides) {
          constrainedPosition = testPosition;
          found = true;
        }
      }
    }

    setDragState(prev => ({
      ...prev,
      currentPosition: constrainedPosition
    }));

    return constrainedPosition;
  }, [dragState.isDragging, dragState.draggedId, dragState.draggedType]);

  const endDrag = useCallback((): Point | null => {
    if (!dragState.isDragging) return null;

    const finalPosition = dragState.currentPosition;
    
    setDragState({
      isDragging: false,
      draggedId: null,
      draggedType: null,
      startPosition: null,
      currentPosition: null
    });
    
    constraintsRef.current = null;
    existingPositionsRef.current = [];

    return finalPosition;
  }, [dragState.isDragging, dragState.currentPosition]);

  const cancelDrag = useCallback(() => {
    setDragState({
      isDragging: false,
      draggedId: null,
      draggedType: null,
      startPosition: null,
      currentPosition: null
    });
    
    constraintsRef.current = null;
    existingPositionsRef.current = [];
  }, []);

  return {
    dragState,
    startDrag,
    updateDrag,
    endDrag,
    cancelDrag
  };
}

