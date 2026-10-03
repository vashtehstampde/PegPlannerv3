import type { CustomItemData } from './types';

const KEY = 'pegplanner_custom_items';

export function loadCustomItems(): CustomItemData[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveCustomItems(items: CustomItemData[]): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(items));
  } catch {
    // localStorage might be full (data URLs are large)
  }
}
