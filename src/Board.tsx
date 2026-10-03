import {
  useRef, useEffect, useState, useCallback,
} from 'react';
import {
  RotateCw, FlipHorizontal, FlipVertical, Trash2, Link, Link2,
  X,
} from 'lucide-react';
import type { PlacedItem, ManifestItem } from './types';
import { uid } from './store';
import { clamp, roundTo } from './utils';

const INSET = 1; // 1 inch from edges
const PPI_BASE = 72; // base pixels per inch

interface BoardProps {
  boardW: number;  // feet
  boardH: number;  // feet
  material: 'wood' | 'diamond';
  zoom: number;
  panX: number;
  panY: number;
  items: PlacedItem[];
  onItemsChange: (items: PlacedItem[]) => void;
  onZoomChange: (z: number) => void;
  onPanChange: (x: number, y: number) => void;
  onFitToWindow: () => void;
}

export function Board({
  boardW, boardH, material, zoom, panX, panY, items, onItemsChange,
  onZoomChange, onPanChange, onFitToWindow,
}: BoardProps) {
  const boardWIn = boardW * 12;
  const boardHIn = boardH * 12;
  const ppi = PPI_BASE * zoom;
  const boardPxW = boardWIn * ppi;
  const boardPxH = boardHIn * ppi;

  // Grid: holes on 1" centers, 1" inset from edges
  const cols = Math.max(0, boardWIn - 2 * INSET + 1);
  const rows = Math.max(0, boardHIn - 2 * INSET + 1);

  const [selectedUid, setSelectedUid] = useState<string | null>(null);
  const [dragInfo, setDragInfo] = useState<{
    uid: string;
    startMouseX: number;
    startMouseY: number;
    startGridX: number;
    startGridY: number;
    moved: boolean;
  } | null>(null);
  const [panInfo, setPanInfo] = useState<{
    startMouseX: number;
    startMouseY: number;
    startPanX: number;
    startPanY: number;
  } | null>(null);
  const [dropHover, setDropHover] = useState(false);

  const boardRef = useRef<HTMLDivElement>(null);
  const canvasAreaRef = useRef<HTMLDivElement>(null);

  const selected = items.find((i) => i.uid === selectedUid) || null;

  // ─── Add item at specific grid position (from drag-drop) ───
  const addItemAt = useCallback((manifest: ManifestItem, gridCol: number, gridRow: number) => {
    const newItem: PlacedItem = {
      uid: uid('placed'),
      manifestId: manifest.id,
      src: manifest.src,
      name: manifest.name,
      category: manifest.category,
      anchorFracX: manifest.anchorX / manifest.realWidth,
      anchorFracY: manifest.anchorY / manifest.realHeight,
      widthIn: manifest.realWidth,
      heightIn: manifest.realHeight,
      gridX: clamp(gridCol, 0, cols - 1),
      gridY: clamp(gridRow, 0, rows - 1),
      rotation: 0,
      flipH: false,
      flipV: false,
      aspectLocked: true,
    };
    onItemsChange([...items, newItem]);
    setSelectedUid(newItem.uid);
  }, [items, onItemsChange, cols, rows]);

  // ─── Add item to center (fallback for click) ───
  const addItem = useCallback((manifest: ManifestItem) => {
    addItemAt(manifest, Math.floor(cols / 2), Math.floor(rows / 2));
  }, [addItemAt, cols, rows]);

  // Expose addItem to parent
  useEffect(() => {
    (window as any).__pegplannerAddItem = addItem;
    return () => { delete (window as any).__pegplannerAddItem; };
  }, [addItem]);

  // Expose fit-to-window
  useEffect(() => {
    (window as any).__pegplannerFit = onFitToWindow;
    return () => { delete (window as any).__pegplannerFit; };
  }, [onFitToWindow]);

  // ─── Convert screen coords to grid coords ───
  const screenToGrid = useCallback((clientX: number, clientY: number): { col: number; row: number } => {
    if (!canvasAreaRef.current) return { col: 0, row: 0 };
    const rect = canvasAreaRef.current.getBoundingClientRect();
    // Account for padding (32px) and pan offset
    const innerX = clientX - rect.left - 32 - panX;
    const innerY = clientY - rect.top - 32 - panY;
    // Convert to inches
    const inchX = innerX / ppi;
    const inchY = innerY / ppi;
    // Convert to grid (accounting for inset)
    const col = Math.round(inchX - INSET);
    const row = Math.round(inchY - INSET);
    return { col, row };
  }, [panX, panY, ppi]);

   // ─── Wheel zoom (scroll to zoom, no ctrl needed) ───
  useEffect(() => {
    const el = canvasAreaRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      if (e.ctrlKey || e.metaKey || Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        // Zoom with mouse anchor
        const rect = el.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const zoomDelta = e.deltaY > 0 ? 0.92 : 1.08;
        const newZoom = clamp(zoom * zoomDelta, 0.15, 5);
        
        // Adjust pan to keep mouse position under the same board point
        const oldPpi = PPI_BASE * zoom;
        const newPpi = PPI_BASE * newZoom;
        const newPanX = mouseX - (mouseX - panX) * (newPpi / oldPpi);
        const newPanY = mouseY - (mouseY - panY) * (newPpi / oldPpi);
        
        onZoomChange(newZoom);
        onPanChange(newPanX, newPanY);
      } else {
        // Horizontal scroll = pan
        onPanChange(panX - e.deltaX, panY);
      }
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, [zoom, panX, panY, onZoomChange, onPanChange]);

  // ─── Drag placed items ───
  useEffect(() => {
    if (!dragInfo) return;
    const handleMove = (e: MouseEvent) => {
      const dxIn = (e.clientX - dragInfo.startMouseX) / ppi;
      const dyIn = (e.clientY - dragInfo.startMouseY) / ppi;
      if (Math.abs(dxIn) > 0.1 || Math.abs(dyIn) > 0.1) {
        if (!dragInfo.moved) setDragInfo({ ...dragInfo, moved: true });
      }
      const newGridX = Math.round(dragInfo.startGridX + dxIn);
      const newGridY = Math.round(dragInfo.startGridY + dyIn);
      const clampedX = clamp(newGridX, 0, cols - 1);
      const clampedY = clamp(newGridY, 0, rows - 1);
      onItemsChange(items.map((it) =>
        it.uid === dragInfo.uid ? { ...it, gridX: clampedX, gridY: clampedY } : it
      ));
    };
    const handleUp = () => setDragInfo(null);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [dragInfo, ppi, items, onItemsChange, cols, rows]);

  // ─── Pan the canvas (drag on empty area) ───
  useEffect(() => {
    if (!panInfo) return;
    const handleMove = (e: MouseEvent) => {
      const dx = e.clientX - panInfo.startMouseX;
      const dy = e.clientY - panInfo.startMouseY;
      onPanChange(panInfo.startPanX + dx, panInfo.startPanY + dy);
    };
    const handleUp = () => setPanInfo(null);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [panInfo, onPanChange]);

  // ─── Touch pan support ───
  useEffect(() => {
    const el = canvasAreaRef.current;
    if (!el) return;
    let touchStart: { x: number; y: number; panX: number; panY: number } | null = null;
    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1 && !dragInfo) {
        touchStart = {
          x: e.touches[0].clientX,
          y: e.touches[0].clientY,
          panX,
          panY,
        };
      }
    };
    const onTouchMove = (e: TouchEvent) => {
      if (touchStart && e.touches.length === 1) {
        e.preventDefault();
        const dx = e.touches[0].clientX - touchStart.x;
        const dy = e.touches[0].clientY - touchStart.y;
        onPanChange(touchStart.panX + dx, touchStart.panY + dy);
      }
    };
    const onTouchEnd = () => { touchStart = null; };
    el.addEventListener('touchstart', onTouchStart, { passive: true });
    el.addEventListener('touchmove', onTouchMove, { passive: false });
    el.addEventListener('touchend', onTouchEnd);
    return () => {
      el.removeEventListener('touchstart', onTouchStart);
      el.removeEventListener('touchmove', onTouchMove);
      el.removeEventListener('touchend', onTouchEnd);
    };
  }, [panX, panY, onPanChange, dragInfo]);

  // ─── Click on empty board deselects ───
  const handleBoardMouseDown = (e: React.MouseEvent) => {
    const target = e.target as HTMLElement;
    if (target === boardRef.current || target.classList.contains('board-surface') ||
        target.classList.contains('holes-layer') || target.classList.contains('items-layer') ||
        target.classList.contains('canvas-area') || target.classList.contains('canvas-viewport')) {
      setSelectedUid(null);
      // Start panning
      setPanInfo({
        startMouseX: e.clientX,
        startMouseY: e.clientY,
        startPanX: panX,
        startPanY: panY,
      });
    }
  };

  // ─── Drag-and-drop from sidebar ───
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    setDropHover(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    if (e.currentTarget === e.target) {
      setDropHover(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDropHover(false);
    const manifestJson = e.dataTransfer.getData('application/json');
    if (!manifestJson) return;
    try {
      const manifest: ManifestItem = JSON.parse(manifestJson);
      const { col, row } = screenToGrid(e.clientX, e.clientY);
      addItemAt(manifest, col, row);
    } catch {
      // ignore
    }
  };

  // ─── Toolbar actions ───
  const updateItem = (uid: string, patch: Partial<PlacedItem>) => {
    onItemsChange(items.map((it) => it.uid === uid ? { ...it, ...patch } : it));
  };

  const deleteItem = (uid: string) => {
    onItemsChange(items.filter((it) => it.uid !== uid));
    setSelectedUid(null);
  };

  const rotateItem = (uid: string) => {
    const item = items.find((i) => i.uid === uid);
    if (!item) return;
    updateItem(uid, { rotation: (item.rotation + 90) % 360 });
  };

  const flipItem = (uid: string, dir: 'h' | 'v') => {
    const item = items.find((i) => i.uid === uid);
    if (!item) return;
    if (dir === 'h') updateItem(uid, { flipH: !item.flipH });
    else updateItem(uid, { flipV: !item.flipV });
  };

  const resizeItem = (uid: string, dim: 'w' | 'h', delta: number) => {
    const item = items.find((i) => i.uid === uid);
    if (!item) return;
    if (item.aspectLocked) {
      const ratio = item.heightIn / item.widthIn;
      if (dim === 'w') {
        const newW = Math.max(0.5, roundTo(item.widthIn + delta, 0.5));
        updateItem(uid, { widthIn: newW, heightIn: roundTo(newW * ratio, 0.5) });
      } else {
        const newH = Math.max(0.5, roundTo(item.heightIn + delta, 0.5));
        updateItem(uid, { heightIn: newH, widthIn: roundTo(newH / ratio, 0.5) });
      }
    } else {
      if (dim === 'w') {
        updateItem(uid, { widthIn: Math.max(0.5, roundTo(item.widthIn + delta, 0.5)) });
      } else {
        updateItem(uid, { heightIn: Math.max(0.5, roundTo(item.heightIn + delta, 0.5)) });
      }
    }
  };

  const toggleLock = (uid: string) => {
    const item = items.find((i) => i.uid === uid);
    if (!item) return;
    updateItem(uid, { aspectLocked: !item.aspectLocked });
  };

  // ─── Render holes ───
  const holes: { x: number; y: number }[] = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      holes.push({
        x: (INSET + c) * ppi,
        y: (INSET + r) * ppi,
      });
    }
  }
  const holeR = Math.max(2, ppi * 0.12);

  // ─── Compute toolbar position ───
  let toolbarStyle: React.CSSProperties = { display: 'none' };
  if (selected) {
    const anchorPxX = (INSET + selected.gridX) * ppi;
    const anchorPxY = (INSET + selected.gridY) * ppi;
    toolbarStyle = {
      left: anchorPxX,
      top: Math.max(0, anchorPxY - 60),
      transform: 'translateX(-50%)',
    };
  }

  return (
    <div
      className={`canvas-area ${panInfo ? 'panning' : ''} ${dropHover ? 'drop-hover' : ''}`}
      ref={canvasAreaRef}
      onMouseDown={handleBoardMouseDown}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div
        className="canvas-viewport"
        style={{
          width: boardPxW,
          height: boardPxH,
          transform: `translate(${panX}px, ${panY}px)`,
        }}
      >
        <div
          className="board"
          ref={boardRef}
          style={{ width: boardPxW, height: boardPxH }}
        >
          <div
            className="board-surface"
            style={{
              backgroundImage: `url(./assets/textures/${material}.png?v=3)`,
            }}
          />

          <div className="holes-layer">
            {holes.map((h, i) => (
              <div
                key={i}
                className="hole"
                style={{
                  left: h.x,
                  top: h.y,
                  width: holeR * 2,
                  height: holeR * 2,
                }}
              />
            ))}
          </div>

          <div className="items-layer">
            {items.map((item) => {
              const anchorPxX = (INSET + item.gridX) * ppi;
              const anchorPxY = (INSET + item.gridY) * ppi;
              const wPx = item.widthIn * ppi;
              const hPx = item.heightIn * ppi;
              const ax = item.anchorFracX * wPx;
              const ay = item.anchorFracY * hPx;
              const left = anchorPxX - ax;
              const top = anchorPxY - ay;

              const transforms: string[] = [];
              if (item.flipH || item.flipV) {
                transforms.push(`scale(${item.flipH ? -1 : 1}, ${item.flipV ? -1 : 1})`);
              }
              if (item.rotation !== 0) {
                transforms.push(`rotate(${item.rotation}deg)`);
              }

              return (
                <div
                  key={item.uid}
                  className={`placed-item ${selectedUid === item.uid ? 'selected' : ''} ${dragInfo?.uid === item.uid ? 'dragging' : ''}`}
                  style={{
                    left,
                    top,
                    width: wPx,
                    height: hPx,
                    ['--anchor-x' as any]: `${ax}px`,
                    ['--anchor-y' as any]: `${ay}px`,
                    transform: transforms.join(' '),
                  }}
                  onMouseDown={(e) => {
                    e.stopPropagation();
                    setSelectedUid(item.uid);
                    setDragInfo({
                      uid: item.uid,
                      startMouseX: e.clientX,
                      startMouseY: e.clientY,
                      startGridX: item.gridX,
                      startGridY: item.gridY,
                      moved: false,
                    });
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedUid(item.uid);
                  }}
                >
                  <img src={item.src} alt={item.name} draggable={false} />
                  {selectedUid === item.uid && (
                    <div
                      className="placed-item-anchor-dot"
                      style={{ left: ax, top: ay }}
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* Floating toolbar */}
          {selected && (
            <div className="item-toolbar" style={toolbarStyle} onClick={(e) => e.stopPropagation()} onMouseDown={(e) => e.stopPropagation()}>
              <div className="toolbar-group">
                <button className="btn btn-icon-sm" title="Rotate 90°" onClick={() => rotateItem(selected.uid)}>
                  <RotateCw size={14} />
                </button>
                <button className="btn btn-icon-sm" title="Flip horizontal" onClick={() => flipItem(selected.uid, 'h')}>
                  <FlipHorizontal size={14} />
                </button>
                <button className="btn btn-icon-sm" title="Flip vertical" onClick={() => flipItem(selected.uid, 'v')}>
                  <FlipVertical size={14} />
                </button>
              </div>

              <div className="toolbar-divider" />

              <div className="toolbar-group">
                <span className="toolbar-label">W</span>
                <div className="size-stepper">
                  <button onClick={() => resizeItem(selected.uid, 'w', -0.5)}>−</button>
                  <span className="size-value">{selected.widthIn.toFixed(1)}"</span>
                  <button onClick={() => resizeItem(selected.uid, 'w', 0.5)}>+</button>
                </div>
              </div>

              <div className="toolbar-group">
                <span className="toolbar-label">H</span>
                <div className="size-stepper">
                  <button onClick={() => resizeItem(selected.uid, 'h', -0.5)}>−</button>
                  <span className="size-value">{selected.heightIn.toFixed(1)}"</span>
                  <button onClick={() => resizeItem(selected.uid, 'h', 0.5)}>+</button>
                </div>
              </div>

              <div className="toolbar-group">
                <button
                  className={`lock-btn ${selected.aspectLocked ? 'locked' : ''}`}
                  title={selected.aspectLocked ? 'Aspect locked' : 'Aspect unlocked'}
                  onClick={() => toggleLock(selected.uid)}
                >
                  {selected.aspectLocked ? <Link size={14} /> : <Link2 size={14} />}
                </button>
              </div>

              <div className="toolbar-divider" />

              <div className="toolbar-group">
                <button className="btn btn-icon-sm btn-danger" title="Delete" onClick={() => deleteItem(selected.uid)}>
                  <Trash2 size={14} />
                </button>
                <button className="btn btn-icon-sm" title="Close toolbar" onClick={() => setSelectedUid(null)}>
                  <X size={14} />
                </button>
              </div>
            </div>
          )}

          {items.length === 0 && !dropHover && (
            <div className="empty-hint">
              Drag items from the catalog onto the board
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
