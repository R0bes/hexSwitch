export interface Point {
  x: number;
  y: number;
}

/**
 * Calculate the vertices of a regular hexagon
 */
export function getHexagonVertices(centerX: number, centerY: number, radius: number): Point[] {
  const vertices: Point[] = [];
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i - Math.PI / 6; // Start at top
    vertices.push({
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    });
  }
  return vertices;
}

/**
 * Calculate the center point of a hexagon edge
 */
export function getEdgeCenter(
  centerX: number,
  centerY: number,
  radius: number,
  edgeIndex: number
): Point {
  const angle1 = (Math.PI / 3) * edgeIndex - Math.PI / 6;
  const angle2 = (Math.PI / 3) * (edgeIndex + 1) - Math.PI / 6;
  return {
    x: centerX + radius * Math.cos((angle1 + angle2) / 2),
    y: centerY + radius * Math.sin((angle1 + angle2) / 2)
  };
}

/**
 * Generate SVG path string for hexagon
 */
export function getHexagonPath(centerX: number, centerY: number, radius: number): string {
  const vertices = getHexagonVertices(centerX, centerY, radius);
  return `M ${vertices[0].x} ${vertices[0].y} ${vertices
    .slice(1)
    .map(v => `L ${v.x} ${v.y}`)
    .join(' ')} Z`;
}

/**
 * Calculate position on hexagon edge for adapter nodes (on the shell)
 * Supports multiple adapters per port by distributing them around the port position
 */
export function getAdapterPositionOnShell(
  centerX: number,
  centerY: number,
  shellRadius: number,
  edgeIndex: number,
  adapterIndex: number = 0,
  totalAdaptersOnPort: number = 1
): Point {
  // Base angle for the edge
  const baseAngle = (Math.PI / 3) * edgeIndex - Math.PI / 6;
  
  // If multiple adapters, distribute them around the port
  if (totalAdaptersOnPort > 1) {
    // Calculate offset angle (spread adapters in a small arc)
    const spreadAngle = Math.PI / 6; // 30 degrees total spread
    const offsetAngle = (adapterIndex - (totalAdaptersOnPort - 1) / 2) * (spreadAngle / (totalAdaptersOnPort - 1 || 1));
    const angle = baseAngle + offsetAngle;
    
    return {
      x: centerX + shellRadius * Math.cos(angle),
      y: centerY + shellRadius * Math.sin(angle)
    };
  }
  
  // Single adapter: position directly on edge
  return {
    x: centerX + shellRadius * Math.cos(baseAngle),
    y: centerY + shellRadius * Math.sin(baseAngle)
  };
}

/**
 * Calculate position outside hexagon for mock nodes
 */
export function getMockPosition(
  centerX: number,
  centerY: number,
  shellRadius: number,
  edgeIndex: number,
  distance: number
): Point {
  const angle = (Math.PI / 3) * edgeIndex - Math.PI / 6;
  return {
    x: centerX + (shellRadius + distance) * Math.cos(angle),
    y: centerY + (shellRadius + distance) * Math.sin(angle)
  };
}

/**
 * Calculate position around hexagon for adapter nodes (legacy, kept for compatibility)
 */
export function getAdapterPosition(
  centerX: number,
  centerY: number,
  hexRadius: number,
  adapterIndex: number,
  totalAdapters: number,
  distance: number
): Point {
  const angle = (2 * Math.PI / totalAdapters) * adapterIndex - Math.PI / 2;
  return {
    x: centerX + (hexRadius + distance) * Math.cos(angle),
    y: centerY + (hexRadius + distance) * Math.sin(angle)
  };
}

