<!-- src/lib/components/Layout.svelte -->
<script>
  import { onMount } from 'svelte';
  import GraphViz from './GraphViz.svelte';
  import NodeList from './NodeList.svelte';
  import CliBar from './CliBar.svelte';
  import StatusBar from './StatusBar.svelte';
  import { appState } from '$lib/stores/appState';
  import { statusEvents } from '$lib/stores/statusEvents';

  // Sections for navigation
  const sections = ['graph-viz', 'node-list', 'cli-bar'];
  let currentSectionIndex = -1; // -1 for section-level focus

  function toggleSection(section) {
    appState.update(state => ({
      ...state,
      [section]: !state[section]
    }));
  }

  function handleNodeSelected(event) {
    appState.update(state => ({ ...state, selectedNode: event.detail.nodeId }));
    statusEvents.update(events => [
      ...events,
      `Node selected: ${event.detail.nodeId} at ${new Date().toLocaleTimeString()}`
    ]);
  }

  function handleFilterChange(event) {
    appState.update(state => ({
      ...state,
      filters: {
        type: event.detail.type || null,
        level: event.detail.level || null
      }
    }));
    statusEvents.update(events => [
      ...events,
      `Filter changed: type=${event.detail.type || 'None'}, level=${event.detail.level || 'None'}`
    ]);
  }

  // Key navigation
  function handleKeydown(event) {
    const key = event.key;
    statusEvents.update(events => [
      ...events,
      `Key: ${key} at ${new Date().toLocaleTimeString()}`
    ]);

    if (key === 'j') {
      // Move down
      currentSectionIndex = Math.min(currentSectionIndex + 1, sections.length - 1);
      appState.update(state => ({ ...state, focusedSection: sections[currentSectionIndex] }));
    } else if (key === 'k') {
      // Move up
      currentSectionIndex = Math.max(currentSectionIndex - 1, -1);
      appState.update(state => ({
        ...state,
        focusedSection: currentSectionIndex === -1 ? null : sections[currentSectionIndex]
      }));
    } else if (key === 'i') {
      // Enter section
      if (currentSectionIndex >= 0) {
        const sectionEl = document.querySelector(`.${sections[currentSectionIndex]}`);
        if (sectionEl) {
          const focusable = sectionEl.querySelector('input, button, select');
          if (focusable) focusable.focus();
        }
      }
    } else if (key === 'Escape') {
      // Return to section-level focus
      currentSectionIndex = -1;
      appState.update(state => ({ ...state, focusedSection: null }));
    } else if (key === ';') {
      // Focus CLI
      currentSectionIndex = sections.indexOf('cli-bar');
      appState.update(state => ({ ...state, focusedSection: 'cli-bar' }));
      const cliInput = document.querySelector('.cli-bar input');
      if (cliInput) cliInput.focus();
    }
  }

  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  });
</script>

<div class="layout">
  <!-- Graph Viz Section -->
  <button class="toggle-button" on:click={() => toggleSection('graphVizCollapsed')}>
    {$appState.graphVizCollapsed ? 'Show' : 'Hide'} Graph
  </button>
  {#if !$appState.graphVizCollapsed}
    <section class="graph-viz" class:active={$appState.focusedSection === 'graph-viz'}>
      <GraphViz {appState} on:nodeSelected={handleNodeSelected} />
    </section>
  {/if}

  <!-- Node List Section -->
  <button class="toggle-button" on:click={() => toggleSection('nodeListCollapsed')}>
    {$appState.nodeListCollapsed ? 'Show' : 'Hide'} Node List
  </button>
  {#if !$appState.nodeListCollapsed}
    <section class="node-list" class:active={$appState.focusedSection === 'node-list'}>
      <NodeList
        {appState}
        on:filterChange={handleFilterChange}
        on:nodeSelected={handleNodeSelected}
      />
    </section>
  {/if}

  <!-- CLI Bar -->
  <section class="cli-bar" class:active={$appState.focusedSection === 'cli-bar'}>
    <CliBar />
  </section>

  <!-- Status Bar -->
  <section class="status-bar" class:active={$appState.focusedSection === 'status-bar'}>
    <StatusBar {statusEvents} />
  </section>
</div>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100%;
  }
  .graph-viz, .node-list {
    flex: 1;
    overflow: auto;
    border: 1px solid #ccc;
  }
  .cli-bar, .status-bar {
    flex: 0 0 auto;
    border: 1px solid #ccc;
  }
  .active {
    border: 1px solid #00008b; /* Dark blue when focused */
  }
  .toggle-button {
    width: 100%;
    padding: 5px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    text-align: left;
  }
  .layout {
    justify-content: space-between;
  }
  .cli-bar, .status-bar {
    position: sticky;
    bottom: 0;
    z-index: 10;
    background: #fff;
  }
</style>

