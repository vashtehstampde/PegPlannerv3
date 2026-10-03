import type { ManifestItem, CustomItemData } from './types';

export const MANIFEST: ManifestItem[] = [
  // ─── Pegs ───
  { id: 'single-hook',       name: 'Single Hook',        category: 'pegs',  src: './assets/pegs/single-hook.png?v=3',       realWidth: 1.5, realHeight: 5,   anchorX: 0.75, anchorY: 0.4 },
  { id: 'double-hook',       name: 'Double Hook',        category: 'pegs',  src: './assets/pegs/double-hook.png?v=3',       realWidth: 3,   realHeight: 5,   anchorX: 1.5,  anchorY: 0.4 },
  { id: 'angled-hook',       name: 'Angled Hook',        category: 'pegs',  src: './assets/pegs/angled-hook.png?v=3',       realWidth: 3,   realHeight: 3,   anchorX: 0.8,  anchorY: 0.4 },
  { id: 'shelf-bracket',     name: 'Shelf Bracket',      category: 'pegs',  src: './assets/pegs/shelf-bracket.png?v=3',     realWidth: 5,   realHeight: 5,   anchorX: 1.0,  anchorY: 0.4 },
  { id: 'multi-tool-rack',   name: 'Multi-Tool Rack',    category: 'pegs',  src: './assets/pegs/multi-tool-rack.png?v=3',   realWidth: 7,   realHeight: 2.5, anchorX: 3.5,  anchorY: 0.3 },
  { id: 'screwdriver-ring',  name: 'Screwdriver Ring',   category: 'pegs',  src: './assets/pegs/screwdriver-ring.png?v=3',  realWidth: 2,   realHeight: 4,   anchorX: 1.0,  anchorY: 0.3 },

  // ─── Standard Tools ───
  { id: 'hammer',              name: 'Claw Hammer',           category: 'tools', src: './assets/tools/hammer.png?v=3',              realWidth: 4,   realHeight: 13, anchorX: 2.0,  anchorY: 0.5 },
  { id: 'flathead-screwdriver',name: 'Flathead Screwdriver',  category: 'tools', src: './assets/tools/flathead-screwdriver.png?v=3',realWidth: 1.5, realHeight: 8,  anchorX: 0.75, anchorY: 0.3 },
  { id: 'phillips-screwdriver',name: 'Phillips Screwdriver',  category: 'tools', src: './assets/tools/phillips-screwdriver.png?v=3',realWidth: 1.5, realHeight: 8,  anchorX: 0.75, anchorY: 0.3 },
  { id: 'combination-wrench',  name: 'Combination Wrench',    category: 'tools', src: './assets/tools/combination-wrench.png?v=3', realWidth: 2,   realHeight: 10, anchorX: 1.0,  anchorY: 0.3 },
  { id: 'adjustable-wrench',   name: 'Adjustable Wrench',     category: 'tools', src: './assets/tools/adjustable-wrench.png?v=3',  realWidth: 2,   realHeight: 10, anchorX: 1.0,  anchorY: 0.3 },
  { id: 'needle-nose-pliers',  name: 'Needle-Nose Pliers',    category: 'tools', src: './assets/tools/needle-nose-pliers.png?v=3', realWidth: 2.5, realHeight: 9,  anchorX: 1.25, anchorY: 0.3 },
  { id: 'linesman-pliers',     name: 'Linesman Pliers',       category: 'tools', src: './assets/tools/linesman-pliers.png?v=3',    realWidth: 3,   realHeight: 9,  anchorX: 1.5,  anchorY: 0.3 },

  // ─── Power Tools (sideways hanging profile) ───
  { id: 'cordless-drill',  name: 'Cordless Drill',  category: 'power-tools', src: './assets/power-tools/cordless-drill.png?v=3', realWidth: 10, realHeight: 6,   anchorX: 1.5, anchorY: 0.4 },
  { id: 'circular-saw',    name: 'Circular Saw',    category: 'power-tools', src: './assets/power-tools/circular-saw.png?v=3',   realWidth: 10, realHeight: 5,   anchorX: 5.0, anchorY: 0.4 },
  { id: 'orbit-sander',    name: 'Orbital Sander',  category: 'power-tools', src: './assets/power-tools/orbit-sander.png?v=3',   realWidth: 8,  realHeight: 5,   anchorX: 4.0, anchorY: 0.3 },
  { id: 'impact-driver',   name: 'Impact Driver',   category: 'power-tools', src: './assets/power-tools/impact-driver.png?v=3',  realWidth: 9,  realHeight: 5.5, anchorX: 1.5, anchorY: 0.4 },

  // ─── Other ───
  { id: 'single-bin',      name: 'Single Bin',       category: 'other', src: './assets/other/single-bin.png?v=3',      realWidth: 6,  realHeight: 4,   anchorX: 3.0, anchorY: 0.3 },
  { id: 'bin-bank',        name: 'Bin Bank (3)',     category: 'other', src: './assets/other/bin-bank.png?v=3',        realWidth: 18, realHeight: 4,   anchorX: 9.0, anchorY: 0.3 },
  { id: 'magnetic-strip',  name: 'Magnetic Strip',   category: 'other', src: './assets/other/magnetic-strip.png?v=3',  realWidth: 14, realHeight: 1.5, anchorX: 2.0, anchorY: 0.3 },
  { id: 'level',           name: 'Spirit Level',     category: 'other', src: './assets/other/level.png?v=3',           realWidth: 12, realHeight: 1.5, anchorX: 2.0, anchorY: 0.3 },
  { id: 'cord-wrap',       name: 'Cord Wrap',        category: 'other', src: './assets/other/cord-wrap.png?v=3',       realWidth: 4,  realHeight: 4,   anchorX: 2.0, anchorY: 0.3 },
  { id: 'tape-measure',    name: 'Tape Measure',     category: 'other', src: './assets/other/tape-measure.png?v=3',    realWidth: 5,  realHeight: 4,   anchorX: 2.5, anchorY: 0.3 },
];

export const BOARD_SIZES: { label: string; w: number; h: number }[] = [
  { label: '2×2 ft', w: 2, h: 2 },
  { label: '2×4 ft (vertical)', w: 2, h: 4 },
  { label: '4×2 ft (landscape)', w: 4, h: 2 },
  { label: '4×4 ft', w: 4, h: 4 },
  { label: '8×4 ft (landscape)', w: 8, h: 4 },
];

export const CATEGORY_LABELS: Record<string, string> = {
  'pegs': 'Pegs',
  'tools': 'Standard Tools',
  'power-tools': 'Power Tools',
  'other': 'Other',
};

export function customToManifest(c: CustomItemData): ManifestItem {
  return {
    id: c.id,
    name: c.name,
    category: c.category,
    src: c.dataUrl,
    realWidth: c.realWidth,
    realHeight: c.realWidth * (c.imgH / c.imgW),
    anchorX: c.anchorFracX * c.realWidth,
    anchorY: c.anchorFracY * (c.realWidth * (c.imgH / c.imgW)),
    custom: true,
  };
}
