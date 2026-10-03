export function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

export function roundTo(v: number, step: number): number {
  return Math.round(v / step) * step;
}

/** Create a CSS transform string for a placed item given its state */
export function itemTransform(
  rotation: number,
  flipH: boolean,
  flipV: boolean,
  anchorPxX: number,
  anchorPxY: number,
): string {
  const parts: string[] = [];
  if (flipH || flipV) {
    parts.push(`scale(${flipH ? -1 : 1}, ${flipV ? -1 : 1})`);
  }
  if (rotation !== 0) {
    parts.push(`rotate(${rotation}deg)`);
  }
  return parts.join(' ');
}

/** Compute pixel position of a grid hole */
export function holePx(
  col: number,
  row: number,
  ppi: number,
  inset: number,
): { x: number; y: number } {
  return {
    x: (inset + col) * ppi,
    y: (inset + row) * ppi,
  };
}

export function downloadDataUrl(dataUrl: string, filename: string): void {
  const a = document.createElement('a');
  a.href = dataUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
