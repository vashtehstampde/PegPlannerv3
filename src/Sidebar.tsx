import { useState, useRef } from 'react';
import {
  ChevronRight, Upload, Plus, Trash2,
} from 'lucide-react';
import type { Category, CustomItemData, ManifestItem } from './types';
import { MANIFEST, CATEGORY_LABELS, customToManifest } from './manifest';
import { uid } from './store';
import { loadCustomItems, saveCustomItems } from './customStorage';
import { CalibrationModal } from './CalibrationModal';

interface SidebarProps {
  onAddItem: (item: ManifestItem) => void;
  sidebarOpen: boolean;
  onCloseSidebar: () => void;
}

const CAT_ORDER: Category[] = ['pegs', 'tools', 'power-tools', 'other'];

export function Sidebar({ onAddItem, sidebarOpen, onCloseSidebar }: SidebarProps) {
  const [openCat, setOpenCat] = useState<Category | null>('pegs');
  const [customItems, setCustomItems] = useState<CustomItemData[]>(() => loadCustomItems());
  const [showCalibration, setShowCalibration] = useState<CustomItemData | null>(null);
  const [itemName, setItemName] = useState('');
  const [itemCategory, setItemCategory] = useState<Category>('tools');
  const [itemWidth, setItemWidth] = useState('6');
  const [aspectLocked, setAspectLocked] = useState(true);
  const fileRef = useRef<HTMLInputElement>(null);
  const pendingFile = useRef<{ dataUrl: string; w: number; h: number } | null>(null);

  const allManifest = [
    ...MANIFEST,
    ...customItems.map(customToManifest),
  ];

  const itemsByCat = (cat: Category) => allManifest.filter((m) => m.category === cat);

  const toggleCat = (cat: Category) => {
    setOpenCat(openCat === cat ? null : cat);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      const img = new Image();
      img.onload = () => {
        pendingFile.current = { dataUrl, w: img.naturalWidth, h: img.naturalHeight };
        setShowCalibration({
          id: uid('custom'),
          name: itemName || file.name.replace(/\.[^.]+$/, ''),
          category: itemCategory,
          dataUrl,
          realWidth: parseFloat(itemWidth) || 6,
          imgW: img.naturalWidth,
          imgH: img.naturalHeight,
          anchorFracX: 0.5,
          anchorFracY: 0.3,
        });
      };
      img.src = dataUrl;
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  const handleCalibrationSave = (data: CustomItemData) => {
    const updated = [...customItems, data];
    setCustomItems(updated);
    saveCustomItems(updated);
    setShowCalibration(null);
    pendingFile.current = null;
    setItemName('');
  };

  const handleCalibrationCancel = () => {
    setShowCalibration(null);
    pendingFile.current = null;
  };

  const handleDeleteCustom = (id: string) => {
    const updated = customItems.filter((c) => c.id !== id);
    setCustomItems(updated);
    saveCustomItems(updated);
  };

  const handleItemClick = (item: ManifestItem) => {
    onAddItem(item);
  };

  return (
    <>
      <div
        className={`sidebar-backdrop ${sidebarOpen ? 'show' : ''}`}
        onClick={onCloseSidebar}
      />
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <span>Asset Catalog</span>
        </div>

        <div className="sidebar-accordion">
          {CAT_ORDER.map((cat) => {
            const items = itemsByCat(cat);
            return (
              <div key={cat} className={`accordion-section ${openCat === cat ? 'open' : ''}`}>
                <div className="accordion-header" onClick={() => toggleCat(cat)}>
                  <span>{CATEGORY_LABELS[cat]}</span>
                  <ChevronRight size={16} className="chevron" />
                </div>
                <div className="accordion-body">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      className="catalog-item"
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData('application/json', JSON.stringify(item));
                        e.dataTransfer.effectAllowed = 'copy';
                      }}
                      onClick={() => handleItemClick(item)}
                      title={`${item.name} (${item.realWidth}"×${item.realHeight.toFixed(1)}") — drag to board or click to place`}
                    >
                      <img src={item.src} alt={item.name} draggable={false} />
                      <div className="catalog-item-name">
                        {item.name}
                        {item.custom && (
                          <button
                            className="btn btn-icon-sm btn-danger"
                            style={{ marginLeft: 4, padding: 2, width: 20, height: 20 }}
                            onClick={(e) => { e.stopPropagation(); handleDeleteCustom(item.id); }}
                            title="Delete custom item"
                          >
                            <Trash2 size={12} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}

          {/* Custom items section */}
          {customItems.length > 0 && null}
        </div>

        <div className="custom-section">
          <div className="custom-section-title">
            <Plus size={14} />
            Import Custom Item
          </div>
          <div className="form-row">
            <label>Name</label>
            <input
              type="text"
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              placeholder="e.g. My Custom Tool"
            />
          </div>
          <div className="form-row">
            <label>Category</label>
            <select
              value={itemCategory}
              onChange={(e) => setItemCategory(e.target.value as Category)}
              style={{ width: '100%' }}
            >
              <option value="pegs">Pegs</option>
              <option value="tools">Standard Tools</option>
              <option value="power-tools">Power Tools</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="form-row">
            <label>Real Width (inches)</label>
            <input
              type="number"
              value={itemWidth}
              onChange={(e) => setItemWidth(e.target.value)}
              min="0.5"
              step="0.5"
            />
          </div>
          <div className="form-row aspect-lock-row">
            <button
              className={`toggle-switch ${aspectLocked ? 'on' : ''}`}
              onClick={() => setAspectLocked(!aspectLocked)}
            />
            <label>Aspect Ratio Scale Lock</label>
          </div>
          <div className="form-row">
            <input
              ref={fileRef}
              type="file"
              accept="image/png"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
            <button className="upload-btn" onClick={() => fileRef.current?.click()}>
              <Upload size={16} />
              Upload PNG
            </button>
          </div>
        </div>
      </aside>

      {showCalibration && (
        <CalibrationModal
          data={showCalibration}
          onSave={handleCalibrationSave}
          onCancel={handleCalibrationCancel}
        />
      )}
    </>
  );
}
