export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Circle {
  x: number;
  y: number;
  radius: number;
}

/**
 * Check if two bounding boxes overlap
 */
export function boxesOverlap(box1: BoundingBox, box2: BoundingBox): boolean {
  return (
    box1.x < box2.x + box2.width &&
    box1.x + box1.width > box2.x &&
    box1.y < box2.y + box2.height &&
    box1.y + box1.height > box2.y
  );
}

/**
 * Check if two circles overlap
 */
export function circlesOverlap(circle1: Circle, circle2: Circle): boolean {
  const dx = circle1.x - circle2.x;
  const dy = circle1.y - circle2.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return distance < (circle1.radius + circle2.radius);
}

/**
 * Check if a point is inside a circle
 */
export function pointInCircle(point: { x: number; y: number }, circle: Circle): boolean {
  const dx = point.x - circle.x;
  const dy = point.y - circle.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return distance <= circle.radius;
}

/**
 * Check if a point is on a circle (within tolerance)
 */
export function pointOnCircle(
  point: { x: number; y: number },
  circle: Circle,
  tolerance: number = 5
): boolean {
  const dx = point.x - circle.x;
  const dy = point.y - circle.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return Math.abs(distance - circle.radius) <= tolerance;
}

/**
 * Project a point onto a circle (snap to circle edge)
 */
export function projectPointToCircle(
  point: { x: number; y: number },
  circle: Circle
): { x: number; y: number } {
  const dx = point.x - circle.x;
  const dy = point.y - circle.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  
  if (distance === 0) {
    // Point is at center, return point on circle at angle 0
    return {
      x: circle.x + circle.radius,
      y: circle.y
    };
  }
  
  return {
    x: circle.x + (dx / distance) * circle.radius,
    y: circle.y + (dy / distance) * circle.radius
  };
}

/**
 * Get bounding box for a node at position (x, y) with given size
 */
export function getNodeBoundingBox(
  x: number,
  y: number,
  size: number = 40
): BoundingBox {
  return {
    x: x - size / 2,
    y: y - size / 2,
    width: size,
    height: size
  };
}

/**
 * Check if a position collides with any existing nodes
 */
export function checkCollision(
  position: { x: number; y: number },
  existingPositions: Array<{ x: number; y: number; id: string }>,
  excludeId?: string,
  nodeSize: number = 40,
  minDistance: number = 50
): { collides: boolean; collidingWith?: string } {
  const newBox = getNodeBoundingBox(position.x, position.y, nodeSize);
  
  for (const existing of existingPositions) {
    if (excludeId && existing.id === excludeId) continue;
    
    const existingBox = getNodeBoundingBox(existing.x, existing.y, nodeSize);
    
    // Expand boxes by minDistance
    const expandedNewBox: BoundingBox = {
      x: newBox.x - minDistance / 2,
      y: newBox.y - minDistance / 2,
      width: newBox.width + minDistance,
      height: newBox.height + minDistance
    };
    
    const expandedExistingBox: BoundingBox = {
      x: existingBox.x - minDistance / 2,
      y: existingBox.y - minDistance / 2,
      width: existingBox.width + minDistance,
      height: existingBox.height + minDistance
    };
    
    if (boxesOverlap(expandedNewBox, expandedExistingBox)) {
      return { collides: true, collidingWith: existing.id };
    }
  }
  
  return { collides: false };
}

