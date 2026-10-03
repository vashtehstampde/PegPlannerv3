import {
  Sun, Moon, ZoomIn, ZoomOut, Maximize, Download,
  PanelLeft, Grid2x2, Eraser,
} from 'lucide-react';
import type { ThemeMode } from './types';
import { BOARD_SIZES } from './manifest';

interface HeaderProps {
  theme: ThemeMode;
  onToggleTheme: () => void;
  boardSizeIdx: number;
  onBoardSizeChange: (idx: number) => void;
  material: 'wood' | 'diamond';
  onMaterialChange: (m: 'wood' | 'diamond') => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitToWindow: () => void;
  onExport: () => void;
  onClearBoard: () => void;
  onToggleSidebar: () => void;
}

export function Header({
  theme, onToggleTheme, boardSizeIdx, onBoardSizeChange,
  material, onMaterialChange, zoom, onZoomIn, onZoomOut,
  onFitToWindow, onExport, onClearBoard, onToggleSidebar,
}: HeaderProps) {
  const zoomPct = Math.round(zoom * 100);
  return (
    <header className="app-header">
      <div className="app-header-left">
        <button className="btn btn-icon mobile-sidebar-toggle" onClick={onToggleSidebar} title="Toggle catalog">
          <PanelLeft size={18} />
        </button>
        <div className="app-logo">
          <Grid2x2 size={22} />
          <span>PegPlanner</span>
        </div>
      </div>

      <div className="app-header-controls">
        <select
          value={boardSizeIdx}
          onChange={(e) => onBoardSizeChange(Number(e.target.value))}
          title="Board size"
        >
          {BOARD_SIZES.map((s, i) => (
            <option key={i} value={i}>{s.label}</option>
          ))}
        </select>

        <select
          value={material}
          onChange={(e) => onMaterialChange(e.target.value as 'wood' | 'diamond')}
          title="Board material"
        >
          <option value="wood">Masonite</option>
          <option value="diamond">Diamond Plate</option>
        </select>

        <div className="header-divider" />

        <button className="btn btn-icon" onClick={onZoomOut} title="Zoom out">
          <ZoomOut size={16} />
        </button>
        <span className="zoom-indicator">{zoomPct}%</span>
        <button className="btn btn-icon" onClick={onZoomIn} title="Zoom in">
          <ZoomIn size={16} />
        </button>
        <button className="btn btn-icon" onClick={onFitToWindow} title="Fit to window">
          <Maximize size={16} />
        </button>

        <div className="header-divider" />

        <button className="btn btn-primary" onClick={onExport} title="Export snapshot">
          <Download size={16} />
          <span>Export</span>
        </button>

        <button className="btn btn-danger" onClick={onClearBoard} title="Clear all items from board">
          <Eraser size={16} />
          <span>Clear</span>
        </button>

        <div className="header-divider" />

        <button className="theme-toggle" onClick={onToggleTheme} title="Toggle theme">
          <span className="theme-toggle-knob">
            {theme === 'light' ? <Sun size={14} /> : <Moon size={14} />}
          </span>
        </button>
      </div>
    </header>
  );
}
