// src/lib/stores/appState.js
import { writable } from 'svelte/store';

export const appState = writable({
  graphVizCollapsed: false,
  nodeListCollapsed: false,
  selectedNode: null,
  filters: { type: null, level: null },
  focusedSection: null // 'graph-viz', 'node-list', 'cli-bar', or null
});
