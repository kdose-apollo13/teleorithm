<!-- src/lib/components/Layout.svelte -->
<script>
  import { onMount } from 'svelte';
  import GraphViz from './GraphViz.svelte';
  import NodeList from './NodeList.svelte';
  import CliBar from './CliBar.svelte';
  import StatusBar from './StatusBar.svelte';
  import { appState, graphData, statusEvents } from '$lib/stores';

  const sections = ['graph-viz', 'node-list', 'cli-bar'];
  let currentSectionIndex = -1; // -1 for no section focus
  let lastSectionIndex = -1; // Track last section for Esc

  function toggleSection(section) {
    appState.update(state => ({
      ...state,
      [section]: !state[section]
    }));
    statusEvents.update(events => [
      ...events,
      `Toggled ${section}: ${!$appState[section] ? 'expanded' : 'collapsed'} at ${new Date().toLocaleTimeString()}`
    ]);
  }

  function handleNodeSelected(event) {
    appState.update(state => ({
      ...state,
      selectedNode: event.detail.nodeId,
      selectedNodeIndex: $graphData.nodes.findIndex(n => n.id === event.detail.nodeId)
    }));
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

  function handleKeydown(event) {
    const key = event.key;
    statusEvents.update(events => [
      ...events,
      `Key: ${key} at ${new Date().toLocaleTimeString()}`
    ]);

    if (key === 'j' || key === 'k') {
      if ($appState.focusedSection === 'node-list' && !$appState.nodeListCollapsed) {
        const nodeCount = $graphData.nodes.length;
        if (nodeCount > 0) {
          appState.update(state => {
            let newIndex = state.selectedNodeIndex;
            if (key === 'j') newIndex = Math.min(newIndex + 1, nodeCount - 1);
            else if (key === 'k') newIndex = Math.max(newIndex - 1, 0);
            return { ...state, selectedNodeIndex: newIndex };
          });
          return;
        }
      }
      // Section navigation
      if (key === 'j') currentSectionIndex = Math.min(currentSectionIndex + 1, sections.length - 1);
      else if (key === 'k') currentSectionIndex = Math.max(currentSectionIndex - 1, -1);
      if (currentSectionIndex !== -1) lastSectionIndex = currentSectionIndex;
      appState.update(state => ({
        ...state,
        focusedSection: currentSectionIndex === -1 ? null : sections[currentSectionIndex],
        selectedNodeIndex: -1 // Reset node selection when changing sections
      }));
    } else if (key === 'i') {
      event.preventDefault(); // Prevent 'i' from typing
      if (currentSectionIndex >= 0) {
        const sectionEl = document.querySelector(`.${sections[currentSectionIndex]}`);
        if (sectionEl) {
          const focusable = sectionEl.querySelector('input, button, select');
          if (focusable) focusable.focus();
        }
      }
    } else if (key === 'Escape') {
      currentSectionIndex = lastSectionIndex;
      appState.update(state => ({
        ...state,
        focusedSection: currentSectionIndex === -1 ? null : sections[currentSectionIndex],
        selectedNodeIndex: -1
      }));
      document.activeElement?.blur();
    } else if (key === ';') {
      event.preventDefault();
      currentSectionIndex = sections.indexOf('cli-bar');
      lastSectionIndex = currentSectionIndex;
      appState.update(state => ({ ...state, focusedSection: 'cli-bar' }));
      const cliInput = document.querySelector('.cli-bar input');
      if (cliInput) cliInput.focus();
    } else if (key === ' ') {
      event.preventDefault(); // Prevent scrolling
      if ($appState.focusedSection === 'graph-viz') {
        toggleSection('graphVizCollapsed');
      } else if ($appState.focusedSection === 'node-list') {
        toggleSection('nodeListCollapsed');
      } else if ($appState.selectedNodeIndex >= 0) {
        // Node toggle (handled in NodeItem)
        const nodeId = $graphData.nodes[$appState.selectedNodeIndex]?.id;
        if (nodeId) {
          statusEvents.update(events => [
            ...events,
            `Toggled node ${nodeId} at ${new Date().toLocaleTimeString()}`
          ]);
        }
      }
    }
  }

  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  });
</script>

<div class="layout">
  <!-- Top Header Bar -->
  <div class="header-bar">
    <button
      class="header-button"
      class:active={$appState.focusedSection === 'graph-viz'}
      on:click={() => toggleSection('graphVizCollapsed')}
    >
      {$appState.graphVizCollapsed ? 'Show' : 'Hide'} GraphViz
    </button>
    <button
      class="header-button"
      class:active={$appState.focusedSection === 'node-list'}
      on:click={() => toggleSection('nodeListCollapsed')}
    >
      {$appState.nodeListCollapsed ? 'Show' : 'Hide'} NodeList
    </button>
  </div>

  <!-- Main Content -->
  <div class="main-content">
    {#if !$appState.graphVizCollapsed}
      <section class="graph-viz" class:active={$appState.focusedSection === 'graph-viz'}>
        <GraphViz {appState} on:nodeSelected={handleNodeSelected} />
      </section>
    {/if}
    {#if !$appState.nodeListCollapsed}
      <section class="node-list" class:active={$appState.focusedSection === 'node-list'}>
        <NodeList
          {appState}
          on:filterChange={handleFilterChange}
          on:nodeSelected={handleNodeSelected}
        />
      </section>
    {/if}
  </div>

  <!-- Bottom Wrapper -->
  <div class="bottom-wrapper">
    <section class="cli-bar" class:active={$appState.focusedSection === 'cli-bar'}>
      <CliBar />
    </section>
    <section class="status-bar">
      <StatusBar />
    </section>
  </div>
</div>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    width: 100%;
  }
  .header-bar {
    display: flex;
    flex-direction: column;
    padding: 5px;
    background: #f0f0f0;
    border-bottom: 1px solid #ccc;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 20;
  }
  .header-button {
    width: 100%;
    padding: 10px;
    background: #e0e0e0;
    border: 1px solid #ccc;
    cursor: pointer;
    margin-bottom: 2px;
    text-align: left;
  }
  .header-button.active {
    border: 1px solid #00008b;
    background: #d0d0ff;
  }
  .main-content {
    flex: 1;
    margin-top: 80px; /* Space for header-bar */
    margin-bottom: 150px; /* Space for bottom-wrapper */
    overflow-y: auto;
  }
  .graph-viz, .node-list {
    border: 1px solid #ccc;
    margin: 5px;
  }
  .bottom-wrapper {
    position: fixed;
    bottom: 0;
    width: 100%;
    z-index: 10;
    background: #fff;
  }
  .cli-bar {
    border: 1px solid #ccc;
    z-index: 12;
  }
  .status-bar {
    border: 1px solid #ccc;
    z-index: 11;
  }
  .active {
    border: 1px solid #00008b;
  }
</style>
