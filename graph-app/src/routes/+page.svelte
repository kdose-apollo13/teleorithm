<!-- src/routes/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import '../app.css';
  import NodeList from '$lib/NodeList.svelte';
  import CommandLine from '$lib/CommandLine.svelte';
  import { shouldShow } from '$lib/filterUtils.js';

  let nodes = [];
  let selectedNodeId = null;
  let focusedIndex = 0;
  let filter = 'TCIV';
  let focusedRegion = 'cli';
  let cliInputElement;
  let nodeListContainerElement;
  let collapsedNodes = new Set();

  // Filter nodes that have at least one content item matching the filter
  $: filteredNodes = nodes.filter(n => n.content.some(c => shouldShow(filter, c.type, c.metadata?.level)));

  onMount(async () => {
    nodes = await window.api.listNodes() || [];
    if (nodes.length > 0) focusedIndex = 0;
    if (cliInputElement) {
      cliInputElement.focus();
      focusedRegion = 'cli';
    }
    window.addEventListener('keydown', handleKeydown, true);
    return () => window.removeEventListener('keydown', handleKeydown, true);
  });

  function focusCli() {
    focusedRegion = 'cli';
    nodeListContainerElement?.blur();
    cliInputElement?.focus();
  }

  function focusNodeList() {
    focusedRegion = 'nodelist';
    cliInputElement?.blur();
    nodeListContainerElement?.focus();
  }

  function handleKeydown(event) {
    const { key } = event;
    if (focusedRegion === 'cli' && key === 'Escape') {
      event.preventDefault();
      focusNodeList();
    } else if (focusedRegion === 'nodelist') {
      switch (key) {
        case ';':
          event.preventDefault();
          focusCli();
          break;
        case 'j':
          if (focusedIndex < filteredNodes.length - 1) {
            event.preventDefault();
            focusedIndex += 1;
          }
          break;
        case 'k':
          if (focusedIndex > 0) {
            event.preventDefault();
            focusedIndex -= 1;
          }
          break;
        case 'Enter':
          event.preventDefault();
          if (filteredNodes[focusedIndex]) selectedNodeId = filteredNodes[focusedIndex].id;
          break;
        case 'm':
          event.preventDefault();
          if (filteredNodes[focusedIndex]) toggleCollapse(filteredNodes[focusedIndex].id);
          break;
      }
    }
  }

  function handleCliCommand(event) {
    const command = event.detail.trim().toLowerCase();
    if (command.startsWith('filter ')) {
      filter = command.slice(7).trim().toUpperCase() || 'TCIV';
    } else if (command.startsWith('select ')) {
      const nodeId = command.slice(7).trim();
      const idx = nodes.findIndex(n => n.id === nodeId);
      if (idx !== -1) {
        selectedNodeId = nodeId;
        focusedIndex = idx;
        focusNodeList();
      }
    } else if (command.startsWith('collapse ')) {
      const nodeId = command.slice(9).trim();
      if (nodes.some(n => n.id === nodeId)) toggleCollapse(nodeId);
    }
  }

  function toggleCollapse(nodeId) {
    collapsedNodes.has(nodeId) ? collapsedNodes.delete(nodeId) : collapsedNodes.add(nodeId);
    collapsedNodes = new Set(collapsedNodes); // Trigger reactivity
  }
</script>

<style>
  .page-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
    background: #000;
    color: #0f0;
    font-family: 'IBM Plex Mono', monospace;
  }
  .node-list-container {
    flex: 1;
    overflow-y: auto;
    outline: none;
  }
  .node-list-container.region-focused {
    box-shadow: inset 0 0 0 2px #0f0;
  }
  .cli-container {
    border-top: 1px solid #333;
    background: #111;
    padding: 0.5rem;
  }
  .cli-container.region-focused {
    box-shadow: inset 0 0 0 2px #0f0;
  }
</style>

<div class="page-container">
  <div class="node-list-container" class:region-focused={focusedRegion === 'nodelist'} bind:this={nodeListContainerElement}>
    <NodeList
      nodes={filteredNodes}
      {focusedIndex}
      {selectedNodeId}
      {collapsedNodes}
      {toggleCollapse}
      setSelectedNodeId={(id) => selectedNodeId = id}
      {filter}
    />
  </div>
  <div class="cli-container" class:region-focused={focusedRegion === 'cli'}>
    <CommandLine bind:inputElement={cliInputElement} on:command={handleCliCommand} />
  </div>
</div>
