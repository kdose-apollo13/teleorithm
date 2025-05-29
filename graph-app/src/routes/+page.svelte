<!-- src/routes/+page.svelte -->
<script>
  import { onMount } from 'svelte';
  import '../app.css';
  import NodeList from '$lib/NodeList.svelte';
  import CommandLine from '$lib/CommandLine.svelte';

  let nodes = [];
  let selectedNodeId = null;
  let focusedIndex = 0;
  let filter = 'TCIV';
  let focusedRegion = 'cli';
  let cliInputElement;
  let nodeListContainerElement;

  $: filteredNodes = filter === 'TCIV' ? nodes : nodes.filter(n => n.content.some(c => c.metadata?.level === filter));

  onMount(async () => {
    try {
      nodes = await window.api.listNodes();
      if (nodes.length > 0) focusedIndex = 0;
    } catch (error) {
      console.error('Failed to load nodes:', error);
      nodes = [];
    }
    window.addEventListener('keydown', handleKeydown, true);
    const focusInterval = setInterval(() => {
      if (cliInputElement) {
        focusCli();
        clearInterval(focusInterval);
      }
    }, 50);
    return () => {
      clearInterval(focusInterval);
      window.removeEventListener('keydown', handleKeydown, true);
    };
  });

  function focusCli() {
    focusedRegion = 'cli';
    nodeListContainerElement?.blur();
    if (cliInputElement) {
      cliInputElement.focus();
      console.log('Focus: CLI, Active:', document.activeElement?.className);
    }
  }

  function focusNodeList() {
    focusedRegion = 'nodelist';
    cliInputElement?.blur();
    nodeListContainerElement?.focus();
    console.log('Focus: NodeList, Active:', document.activeElement?.className);
  }

  function handleKeydown(event) {
    const { key } = event;
    console.log(`Key: ${key}, Region: ${focusedRegion}, Active: ${document.activeElement?.className}`);

    if (focusedRegion === 'cli') {
      if (key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        focusNodeList();
      }
    } else if (focusedRegion === 'nodelist') {
      if (key === ';') {
        event.preventDefault();
        event.stopPropagation();
        focusCli();
      } else if (key === 'j' && focusedIndex < filteredNodes.length - 1) {
        event.preventDefault();
        focusedIndex += 1;
      } else if (key === 'k' && focusedIndex > 0) {
        event.preventDefault();
        focusedIndex -= 1;
      } else if (key === 'Enter') {
        event.preventDefault();
        if (filteredNodes[focusedIndex]) {
          selectedNodeId = filteredNodes[focusedIndex].id;
        }
      } else if (key === 'm') {
        event.preventDefault();
        if (filteredNodes[focusedIndex]) {
          dispatchNodeCollapse(filteredNodes[focusedIndex].id);
        }
      }
    }
  }

  function handleCliCommand(event) {
    const command = event.detail.trim().toLowerCase();
    console.log('CLI Command:', command);
    if (command.startsWith('filter ')) {
      const filterValue = command.slice(7).trim().toUpperCase();
      filter = filterValue || 'TCIV';
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
      console.log('Collapse Node ID:', nodeId);
      if (nodes.some(n => n.id === nodeId)) {
        dispatchNodeCollapse(nodeId);
      } else {
        console.log('Node not found:', nodeId);
      }
    }
  }

  let collapsedNodes = new Set();
  function dispatchNodeCollapse(nodeId) {
    console.log('Collapsing:', nodeId);
    if (collapsedNodes.has(nodeId)) {
      collapsedNodes.delete(nodeId);
    } else {
      collapsedNodes.add(nodeId);
    }
    collapsedNodes = new Set(collapsedNodes);
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
    <NodeList nodes={filteredNodes} {focusedIndex} {selectedNodeId} {collapsedNodes} />
  </div>
  <div class="cli-container" class:region-focused={focusedRegion === 'cli'}>
    <CommandLine bind:inputElement={cliInputElement} on:command={handleCliCommand} />
  </div>
</div>
