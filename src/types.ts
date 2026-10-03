export type Category = 'pegs' | 'tools' | 'power-tools' | 'other';

export type ThemeMode = 'light' | 'dark';

export type BoardOrientation = { w: number; h: number };

export interface ManifestItem {
  id: string;
  name: string;
  category: Category;
  src: string;
  realWidth: number;  // inches
  realHeight: number; // inches
  anchorX: number;    // inches from left edge
  anchorY: number;    // inches from top edge
  custom?: boolean;
}

export interface PlacedItem {
  uid: string;
  manifestId: string;
  src: string;
  name: string;
  category: Category;
  anchorFracX: number; // 0–1 fraction of width
  anchorFracY: number; // 0–1 fraction of height
  widthIn: number;     // display width in inches
  heightIn: number;    // display height in inches
  gridX: number;       // grid column (0-based from first hole)
  gridY: number;       // grid row (0-based from first hole)
  rotation: number;    // 0 | 90 | 180 | 270
  flipH: boolean;
  flipV: boolean;
  aspectLocked: boolean;
}

export interface CustomItemData {
  id: string;
  name: string;
  category: Category;
  dataUrl: string;
  realWidth: number;  // inches
  imgW: number;       // natural pixel width
  imgH: number;       // natural pixel height
  anchorFracX: number;
  anchorFracY: number;
}
