import { useRef, useState, useEffect } from 'react';
import { Grid3x3, Check, X } from 'lucide-react';
import type { CustomItemData } from './types';

interface CalibrationModalProps {
  data: CustomItemData;
  onSave: (data: CustomItemData) => void;
  onCancel: () => void;
}

export function CalibrationModal({ data, onSave, onCancel }: CalibrationModalProps) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [anchor, setAnchor] = useState({ x: 0.5, y: 0.3 });
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const updateSize = () => {
      if (imgRef.current) {
        setImgSize({
          w: imgRef.current.clientWidth,
          h: imgRef.current.clientHeight,
        });
      }
    };
    updateSize();
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!imgRef.current) return;
    const rect = imgRef.current.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    // snap to 0.05 grid
    const snappedX = Math.round(x / 0.05) * 0.05;
    const snappedY = Math.round(y / 0.05) * 0.05;
    setAnchor({
      x: Math.max(0, Math.min(1, snappedX)),
      y: Math.max(0, Math.min(1, snappedY)),
    });
  };

  const handleSave = () => {
    onSave({
      ...data,
      anchorFracX: anchor.x,
      anchorFracY: anchor.y,
    });
  };

  return (
    <div className="calibration-overlay" onClick={onCancel}>
      <div className="calibration-modal" onClick={(e) => e.stopPropagation()}>
        <h2>Set Peg Anchor Point</h2>
        <p>
          Click on the image where the item hangs from its peg. The marker snaps to a grid.
          This is the point that snaps to the board's holes.
        </p>

        <div className="calibration-image-wrap" ref={wrapRef} onClick={handleClick}>
          <img
            ref={imgRef}
            src={data.dataUrl}
            alt="Custom item"
            draggable={false}
          />
          {/* Grid overlay */}
          {imgSize.w > 0 && (
            <svg
              className="calibration-grid"
              style={{
                left: imgRef.current?.offsetLeft ?? 0,
                top: imgRef.current?.offsetTop ?? 0,
                width: imgSize.w,
                height: imgSize.h,
              }}
            >
              {Array.from({ length: 21 }).map((_, i) => {
                const pos = (i / 20) * imgSize.w;
                return (
                  <line key={`v${i}`} x1={pos} y1={0} x2={pos} y2={imgSize.h}
                    stroke="rgba(37,99,235,0.2)" strokeWidth={1} />
                );
              })}
              {Array.from({ length: 21 }).map((_, i) => {
                const pos = (i / 20) * imgSize.h;
                return (
                  <line key={`h${i}`} x1={0} y1={pos} x2={imgSize.w} y2={pos}
                    stroke="rgba(37,99,235,0.2)" strokeWidth={1} />
                );
              })}
            </svg>
          )}
          {/* Anchor marker */}
          {imgSize.w > 0 && (
            <div
              className="calibration-anchor-marker"
              style={{
                left: (imgRef.current?.offsetLeft ?? 0) + anchor.x * imgSize.w,
                top: (imgRef.current?.offsetTop ?? 0) + anchor.y * imgSize.h,
              }}
            />
          )}
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          marginBottom: 16,
          fontSize: 13,
          color: 'var(--text-secondary)',
        }}>
          <Grid3x3 size={16} />
          Anchor at {Math.round(anchor.x * 100)}%, {Math.round(anchor.y * 100)}%
        </div>

        <div className="calibration-actions">
          <button className="btn" onClick={onCancel}>
            <X size={16} />
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            <Check size={16} />
            Save Item
          </button>
        </div>
      </div>
    </div>
  );
}
