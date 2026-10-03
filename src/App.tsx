import { useState, useEffect, useCallback, useRef } from 'react';
import html2canvas from 'html2canvas';
import type { ThemeMode, PlacedItem, ManifestItem } from './types';
import { BOARD_SIZES } from './manifest';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Board } from './Board';
import { clamp, downloadDataUrl } from './utils';

const THEME_KEY = 'pegplanner_theme';
const ITEMS_KEY = 'pegplanner_items';
const BOARD_KEY = 'pegplanner_board';
const MATERIAL_KEY = 'pegplanner_material';

function App() {
  // ─── Theme ───
  const [theme, setTheme] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem(THEME_KEY) as ThemeMode | null;
    return saved || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');

  // ─── Board config ───
  const [boardSizeIdx, setBoardSizeIdx] = useState(() => {
    const saved = parseInt(localStorage.getItem(BOARD_KEY) || '1');
    return isNaN(saved) ? 1 : clamp(saved, 0, BOARD_SIZES.length - 1);
  });
  const [material, setMaterial] = useState<'wood' | 'diamond'>(() => {
    return (localStorage.getItem(MATERIAL_KEY) as 'wood' | 'diamond') || 'wood';
  });
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => { localStorage.setItem(BOARD_KEY, String(boardSizeIdx)); }, [boardSizeIdx]);
  useEffect(() => { localStorage.setItem(MATERIAL_KEY, material); }, [material]);

  const boardSize = BOARD_SIZES[boardSizeIdx];
  const boardWIn = boardSize.w * 12;
  const boardHIn = boardSize.h * 12;
  const PPI_BASE = 72;

  // ─── Fit to window ───
  const fitToWindow = useCallback(() => {
    const area = document.querySelector('.canvas-area') as HTMLElement;
    if (!area) return;

    // Read actual padding from CSS
    const style = getComputedStyle(area);
    const padLeft = parseFloat(style.paddingLeft || '0');
    const padRight = parseFloat(style.paddingRight || '0');
    const padTop = parseFloat(style.paddingTop || '0');
    const padBottom = parseFloat(style.paddingBottom || '0');

    // Available space inside padding
    const innerW = area.clientWidth - padLeft - padRight;
    const innerH = area.clientHeight - padTop - padBottom;

    const fitZoom = Math.min(
      innerW / (boardWIn * PPI_BASE),
      innerH / (boardHIn * PPI_BASE)
    );

    const newZoom = clamp(fitZoom, 0.15, 5);
    const boardPxW = boardWIn * PPI_BASE * newZoom;
    const boardPxH = boardHIn * PPI_BASE * newZoom;

    // Center inside available space, offset by top-left padding
    const centerX = padLeft + (innerW - boardPxW) / 2;
    const centerY = padTop + (innerH - boardPxH) / 2;

    setZoom(newZoom);
    setPanX(centerX);
    setPanY(centerY);
  }, [boardWIn, boardHIn]);
  // Auto-fit on board size change
  useEffect(() => {
    fitToWindow();
  }, [boardSizeIdx, fitToWindow]);

  // Auto-fit on initial mount and window resize
  useEffect(() => {
    const timer = setTimeout(fitToWindow, 100);
    const onResize = () => fitToWindow();
    window.addEventListener('resize', onResize);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', onResize);
    };
  }, [fitToWindow]);

  const zoomIn = () => setZoom((z) => clamp(z * 1.2, 0.15, 5));
  const zoomOut = () => setZoom((z) => clamp(z * 0.8, 0.15, 5));

  // ─── Placed items ───
  const [items, setItems] = useState<PlacedItem[]>(() => {
    try {
      const raw = localStorage.getItem(ITEMS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem(ITEMS_KEY, JSON.stringify(items));
  }, [items]);

  const handleAddItem = useCallback((manifest: ManifestItem) => {
    (window as any).__pegplannerAddItem?.(manifest);
    setSidebarOpen(false);
  }, []);

  const handleClearBoard = useCallback(() => {
    if (items.length === 0) return;
    if (window.confirm('Remove all items from the board?')) {
      setItems([]);
    }
  }, [items.length]);

  // ─── Export ───
  const exportRef = useRef<HTMLDivElement>(null);
  const handleExport = async () => {
    const boardEl = document.querySelector('.board') as HTMLElement;
    if (!boardEl) return;
    try {
      const canvas = await html2canvas(boardEl, {
        backgroundColor: null,
        scale: 2,
        useCORS: true,
        logging: false,
      });
      const dataUrl = canvas.toDataURL('image/png');
      downloadDataUrl(dataUrl, `pegplanner-${Date.now()}.png`);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  return (
    <div className="app">
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        boardSizeIdx={boardSizeIdx}
        onBoardSizeChange={setBoardSizeIdx}
        material={material}
        onMaterialChange={setMaterial}
        zoom={zoom}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
        onFitToWindow={fitToWindow}
        onExport={handleExport}
        onClearBoard={handleClearBoard}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />
      <div className="app-body">
        <Sidebar
          onAddItem={handleAddItem}
          sidebarOpen={sidebarOpen}
          onCloseSidebar={() => setSidebarOpen(false)}
        />
        <div ref={exportRef} style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          <Board
            boardW={boardSize.w}
            boardH={boardSize.h}
            material={material}
            zoom={zoom}
            panX={panX}
            panY={panY}
            items={items}
            onItemsChange={setItems}
            onZoomChange={setZoom}
            onPanChange={(x, y) => { setPanX(x); setPanY(y); }}
            onFitToWindow={fitToWindow}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
