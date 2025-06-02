<script>
  import { onMount, tick } from 'svelte';
  import { writable } from 'svelte/store';

  // --- Configuration ---
  const BORDER_DEFAULT = 'border-gray-300';
  const BORDER_FOCUSED = 'border-darkblue-600 ring-1 ring-darkblue-600';
  const BG_SELECTED_NODE = 'bg-blue-200';

  // --- Stores for reactive state ---
  const eventLogs = writable([]);
  const focusedId = writable('graphviz-header'); // Visual focus
  const navigationContext = writable('sections'); // 'sections' or 'nodes'
  const lastFocusedIdBeforeCli = writable('graphviz-header');
  const previouslyFocusedNodeHeaderId = writable(null); // For returning from node item controls

  const graphVizVisible = writable(true);
  const nodeListVisible = writable(true);

  const initialNodes = [
    { id: 'node1', name: 'Alpha Node', metadata: 'Type: A, Status: Active', contentVisible: true, items: ['Detail A1 (Type X, Lvl 1)', 'Detail A2 (Type Y, Lvl 2)'], itemFilters: { type: '', level: '' }, selectedItem: null },
    { id: 'node2', name: 'Beta Node', metadata: 'Type: B, Status: Inactive', contentVisible: false, items: ['Detail B1 (Type X, Lvl 2)', 'Detail B2 (Type Z, Lvl 1)', 'Detail B3 (Type Y, Lvl 1)'], itemFilters: { type: '', level: '' }, selectedItem: null },
    { id: 'node3', name: 'Gamma Node', metadata: 'Type: A, Status: Pending', contentVisible: true, items: ['Detail G1 (Type Z, Lvl 3)'], itemFilters: { type: '', level: '' }, selectedItem: null },
  ];
  const nodes = writable(initialNodes);
  const cliInputValue = writable('');

  // --- Refs for DOM elements ---
  let graphvizHeaderRef;
  let graphvizContentDummySelectorRef;
  let nodeListHeaderRef;
  let nodeListFilterInputRef;
  let nodeHeaderRefs = {};
  let nodeContentDummySelectorRefs = {};
  let cliInputRef;
  let statusBarContentRef;

  // --- Helper Functions ---
  function logEvent(message) {
    const timestamp = new Date().toLocaleTimeString();
    eventLogs.update(logs => {
      const newLogs = [...logs, `[${timestamp}] ${message}`];
      if (newLogs.length > 100) newLogs.shift(); // Keep logs manageable
      return newLogs;
    });
    tick().then(() => {
      if (statusBarContentRef) {
        statusBarContentRef.scrollTop = statusBarContentRef.scrollHeight;
      }
    });
  }

  function setVisualFocus(id) {
    focusedId.set(id);
    logEvent(`Visual focus set to ${id}`);
  }

  // --- Toggle Functions ---
  function toggleGraphViz() {
    graphVizVisible.update(v => !v);
    logEvent(`GraphViz ${$graphVizVisible ? 'expanded' : 'collapsed'}`);
  }

  function toggleNodeList() {
    nodeListVisible.update(v => !v);
    logEvent(`NodeList ${$nodeListVisible ? 'expanded' : 'collapsed'}`);
    if (!$nodeListVisible && $navigationContext === 'nodes') {
      navigationContext.set('sections');
      setVisualFocus('nodelist-header');
    }
  }

  function toggleNodeContent(nodeId) {
    nodes.update(prevNodes =>
      prevNodes.map(n =>
        n.id === nodeId ? { ...n, contentVisible: !n.contentVisible } : n
      )
    );
    const node = $nodes.find(n => n.id === nodeId);
    logEvent(`Node ${node.name} ${node.contentVisible ? 'expanded' : 'collapsed'}`);
    // If node content is hidden and its controls were focused, blur and return focus to header
    if (!node.contentVisible && document.activeElement === nodeContentDummySelectorRefs[nodeId]) {
        nodeContentDummySelectorRefs[nodeId]?.blur();
        // Visual focus should already be on node header or handled by Esc
    }
  }

  // --- Keyboard Navigation ---
  onMount(() => {
    const sectionFocusOrder = ['graphviz-header', 'nodelist-header', 'cli-input'];

    const handleKeyDown = (event) => {
      const activeElement = document.activeElement;
      const currentFocusedId = $focusedId;
      const currentNavContext = $navigationContext;

      // Priority 1: Handle focused input elements
      if (activeElement && activeElement !== document.body) {
        if (activeElement === cliInputRef) {
          if (event.key === 'Escape') {
            event.preventDefault();
            cliInputRef.blur();
            navigationContext.set('sections');
            setVisualFocus($lastFocusedIdBeforeCli);
            logEvent('Exited CLI input (Esc)');
            return;
          }
          if (event.key === 'Enter') {
            event.preventDefault();
            handleCliSubmit();
            // cliInputRef.blur(); // Optionally blur after submit
            // navigationContext.set('sections');
            // setVisualFocus($lastFocusedIdBeforeCli);
            return;
          }
          // Allow typing (j, k, etc.) in CLI
          logEvent(`CLI Input Key: ${event.key}`);
          return;
        }
        // Handle Esc for other focusable controls
        if (event.key === 'Escape') {
          event.preventDefault();
          activeElement.blur();
          logEvent(`Blurred ${activeElement.id || 'control'} (Esc)`);
          if (activeElement === graphvizContentDummySelectorRef) {
            navigationContext.set('sections'); setVisualFocus('graphviz-header');
          } else if (activeElement === nodeListFilterInputRef) {
            navigationContext.set('sections'); setVisualFocus('nodelist-header');
          } else if (Object.values(nodeContentDummySelectorRefs).includes(activeElement)) {
            navigationContext.set('nodes'); // Stay in nodes context
            setVisualFocus($previouslyFocusedNodeHeaderId || 'nodelist-header'); // Return to the node header
          }
          return;
        }
        // Allow Space/Enter on focused buttons to trigger click (default behavior often works)
        if ((event.key === ' ' || event.key === 'Enter') && activeElement.tagName === 'BUTTON') {
            logEvent(`Button ${activeElement.textContent} activated by ${event.key}`);
            // Allow default action to proceed (which should be a click)
            return;
        }
         // If it's nodeListFilterInputRef, let most keys type
        if (activeElement === nodeListFilterInputRef && event.key.length === 1) {
            logEvent(`NodeList Filter Input Key: ${event.key}`);
            return;
        }
      }

      // Priority 2: Global navigation and actions
      // Prevent default for keys we will handle for navigation/toggling
      if (['j', 'k', 'i', ';', ' ', 'Escape'].includes(event.key)) {
        event.preventDefault();
        logEvent(`Global Key: ${event.key}, Context: ${currentNavContext}, Focused: ${currentFocusedId}`);
      } else {
        // Don't process other keys globally
        return;
      }

      if (event.key === 'j') {
        if (currentNavContext === 'sections') {
          const currentIndex = sectionFocusOrder.indexOf(currentFocusedId);
          if (currentIndex < sectionFocusOrder.length - 1) {
            setVisualFocus(sectionFocusOrder[currentIndex + 1]);
          }
        } else if (currentNavContext === 'nodes') {
          const activeNodes = $nodeListVisible ? $nodes.filter(n => $nodeListVisible) : []; // Ensure nodes are from visible list
          if (activeNodes.length === 0) return;
          const currentNodeHeaderId = currentFocusedId;
          const nodeIndex = activeNodes.findIndex(n => `node-${n.id}-header` === currentNodeHeaderId);
          if (nodeIndex < activeNodes.length - 1) {
            setVisualFocus(`node-${activeNodes[nodeIndex + 1].id}-header`);
          }
        }
      } else if (event.key === 'k') {
        if (currentNavContext === 'sections') {
          const currentIndex = sectionFocusOrder.indexOf(currentFocusedId);
          if (currentIndex > 0) {
            setVisualFocus(sectionFocusOrder[currentIndex - 1]);
          }
        } else if (currentNavContext === 'nodes') {
          const activeNodes = $nodeListVisible ? $nodes.filter(n => $nodeListVisible) : [];
          if (activeNodes.length === 0) return;
          const currentNodeHeaderId = currentFocusedId;
          const nodeIndex = activeNodes.findIndex(n => `node-${n.id}-header` === currentNodeHeaderId);
          if (nodeIndex > 0) {
            setVisualFocus(`node-${activeNodes[nodeIndex - 1].id}-header`);
          }
        }
      } else if (event.key === 'i') {
        if (currentNavContext === 'sections') {
          if (currentFocusedId === 'graphviz-header') {
            graphvizContentDummySelectorRef?.focus();
            logEvent('Entered GraphViz controls');
          } else if (currentFocusedId === 'nodelist-header') {
            if ($nodeListVisible && $nodes.length > 0) {
              navigationContext.set('nodes');
              setVisualFocus(`node-${$nodes[0].id}-header`);
              logEvent('Entered NodeList (node navigation)');
            } else {
              nodeListFilterInputRef?.focus();
              logEvent('Entered NodeList filter control');
            }
          } else if (currentFocusedId === 'cli-input') {
            lastFocusedIdBeforeCli.set(currentFocusedId); // Or the one before it if needed
            cliInputRef?.focus();
            logEvent('Entered CLI input field');
          }
        } else if (currentNavContext === 'nodes') { // A node header is visually focused
          const nodeId = currentFocusedId.replace('node-', '').replace('-header', '');
          const node = $nodes.find(n => n.id === nodeId);
          if (node && node.contentVisible) {
            nodeContentDummySelectorRefs[nodeId]?.focus();
            previouslyFocusedNodeHeaderId.set(currentFocusedId);
            logEvent(`Entered Node ${nodeId} item controls`);
          } else {
            logEvent(`Node ${nodeId} content not visible or node not found, cannot enter controls.`);
          }
        }
      } else if (event.key === 'Escape') {
        // This Esc is for when no specific input was focused (handled above)
        if (currentNavContext === 'nodes') {
          navigationContext.set('sections');
          setVisualFocus('nodelist-header');
          logEvent('Exited node navigation to sections');
        } else {
            logEvent('Global Escape (no specific context change)');
            // Potentially blur any lingering focus if not body, though activeElement check should catch most.
            if(document.activeElement !== document.body) document.activeElement?.blur();
        }
      } else if (event.key === ';') {
        if (currentNavContext === 'sections' && currentFocusedId !== 'cli-input') {
            lastFocusedIdBeforeCli.set(currentFocusedId);
        } else if (currentNavContext === 'nodes') {
            lastFocusedIdBeforeCli.set('nodelist-header'); // Sensible return point
        }
        // If already cli-input, lastFocusedIdBeforeCli is already set or remains.
        setVisualFocus('cli-input');
        cliInputRef?.focus();
        logEvent('Focused CLI via ;');
      } else if (event.key === ' ') {
        // Spacebar for toggles (if not handled by a focused button/input)
        if (currentFocusedId === 'graphviz-header') toggleGraphViz();
        else if (currentFocusedId === 'nodelist-header') toggleNodeList();
        else if (currentFocusedId.startsWith('node-') && currentFocusedId.endsWith('-header') && currentNavContext === 'nodes') {
          const nodeId = currentFocusedId.replace('node-', '').replace('-header', '');
          toggleNodeContent(nodeId);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  // --- CLI Command Handling ---
  function handleCliSubmit() {
    if ($cliInputValue.trim()) {
      logEvent(`CLI command: ${$cliInputValue}`);
      cliInputValue.set('');
    }
  }

  // --- Node Item Filtering & Selection (Dummy) ---
  function handleNodeItemFilterChange(nodeId, filterType, value) {
    nodes.update(prevNodes =>
      prevNodes.map(n =>
        n.id === nodeId ? { ...n, itemFilters: { ...n.itemFilters, [filterType]: value } } : n
      )
    );
    logEvent(`Node ${nodeId} filter changed: ${filterType} = ${value}`);
  }

  function selectNodeItem(nodeId, item) {
     nodes.update(prevNodes =>
      prevNodes.map(n =>
        n.id === nodeId ? { ...n, selectedItem: item } : n
      )
    );
    logEvent(`Node ${nodeId} item selected: ${item}`);
  }

  // Reactive class computation
  const getBorderClass = (id) => ($focusedId === id ? BORDER_FOCUSED : BORDER_DEFAULT);

</script>

<svelte:head>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'darkblue': {
              DEFAULT: '#00008b',
              '600': '#00008b',
            },
          }
        }
      }
    }
  </script>
  <style>
    .status-log-content::-webkit-scrollbar { width: 8px; }
    .status-log-content::-webkit-scrollbar-track { background: #f0f0f0; border-radius: 4px; }
    .status-log-content::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
    .status-log-content::-webkit-scrollbar-thumb:hover { background: #bbb; }
    :global(html, body) { height: 100%; margin: 0; font-family: sans-serif; }
    :global(#app) { height: 100%; }
    /* Ensure focused elements are clearly visible, even if just via border */
     *:focus { outline: none; } /* Remove default browser outline if we use borders */
  </style>
</svelte:head>

<div class="flex flex-col h-screen bg-white text-sm">
  <div class="flex-grow overflow-y-auto p-2 space-y-2">
    <div class="flex flex-col">
      <div
        bind:this={graphvizHeaderRef}
        id="graphviz-header"
        class="p-2 bg-gray-100 border rounded cursor-pointer {getBorderClass('graphviz-header')}"
        on:click={() => { navigationContext.set('sections'); setVisualFocus('graphviz-header'); toggleGraphViz(); }}
        tabindex="-1"
      >
        <div class="flex justify-between items-center">
          <span class="font-semibold">GraphViz</span>
          <div class="flex items-center space-x-2">
            <span class="text-xs">Status: {$graphVizVisible ? 'Show' : 'Hide'}</span>
            <button 
              class="text-xs px-2 py-1 border border-gray-400 rounded hover:bg-gray-200 focus:ring-1 focus:ring-darkblue-600"
              on:click|stopPropagation={(e) => { logEvent('GraphViz control placeholder clicked.'); graphvizContentDummySelectorRef?.focus(); }}
              bind:this={graphvizContentDummySelectorRef}
              tabindex="-1"
            >
              Graph Controls
            </button>
          </div>
        </div>
      </div>
      {#if $graphVizVisible}
        <div
          id="graphviz-content"
          class="p-4 border border-t-0 rounded-b {getBorderClass('graphviz-content')}"
          class:border-darkblue-600={document.activeElement === graphvizContentDummySelectorRef}
        >
          <p class="text-gray-700">Graph Visualization Area</p>
          <p class="text-xs text-gray-500 mb-2">Mock content. Click a dummy node to "select" it.</p>
          <div class="space-x-2">
            <button class="px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-darkblue-600" on:click={() => logEvent('GraphViz: Dummy Node 1 selected')}>Select Node 1</button>
            <button class="px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-darkblue-600" on:click={() => logEvent('GraphViz: Dummy Node 2 selected')}>Select Node 2</button>
          </div>
           {#if document.activeElement === graphvizContentDummySelectorRef}
            <p class="text-xs mt-2 text-darkblue-600">Graph controls are DOM focused.</p>
          {/if}
        </div>
      {/if}
    </div>

    <div class="flex flex-col">
      <div
        bind:this={nodeListHeaderRef}
        id="nodelist-header"
        class="p-2 bg-gray-100 border rounded cursor-pointer {getBorderClass('nodelist-header')}"
        on:click={() => { navigationContext.set('sections'); setVisualFocus('nodelist-header'); toggleNodeList(); }}
        tabindex="-1"
      >
        <div class="flex justify-between items-center">
          <span class="font-semibold">NodeList</span>
          <div class="flex items-center space-x-2">
            <span class="text-xs">Status: {$nodeListVisible ? 'Show' : 'Hide'}</span>
            <input 
              type="text" 
              placeholder="Filter nodes..."
              class="text-xs px-2 py-1 border border-gray-400 rounded focus:outline-none focus:ring-1 focus:ring-darkblue-600 w-32"
              on:click|stopPropagation
              on:input={(e) => logEvent(`NodeList filter input: ${e.target.value}`)}
              bind:this={nodeListFilterInputRef}
              tabindex="-1"
            />
          </div>
        </div>
      </div>
      {#if $nodeListVisible}
        <div
          id="nodelist-content"
          class="border border-t-0 rounded-b p-1 space-y-1 {getBorderClass('nodelist-content')}"
           class:border-darkblue-600={$navigationContext === 'nodes' || document.activeElement === nodeListFilterInputRef}
        >
          {#if $nodes.length === 0}
            <p class="text-gray-500 p-2">No nodes to display.</p>
          {:else}
            {#each $nodes as node (node.id)}
              <div class="flex flex-col">
                <div
                  bind:this={nodeHeaderRefs[node.id]}
                  id={`node-${node.id}-header`}
                  class="p-2 border rounded cursor-pointer {getBorderClass(`node-${node.id}-header`)} {$focusedId === `node-${node.id}-header` ? BG_SELECTED_NODE : 'bg-gray-100 hover:bg-gray-200'}"
                  on:click={() => { navigationContext.set('nodes'); setVisualFocus(`node-${node.id}-header`); toggleNodeContent(node.id); }}
                  tabindex="-1"
                >
                  <div class="flex justify-between items-center">
                    <span class="font-semibold">{node.name} <span class="text-xs text-gray-600">({node.id})</span></span>
                    <div class="text-xs flex items-center space-x-2">
                      <span class="text-gray-500">{node.metadata}</span>
                      <span>Status: {node.contentVisible ? 'Expand' : 'Collapse'}</span>
                    </div>
                  </div>
                </div>
                {#if node.contentVisible}
                  <div class="p-3 border border-t-0 rounded-b bg-white space-y-2 {getBorderClass(`node-${node.id}-content`)}"
                       class:border-darkblue-600={document.activeElement === nodeContentDummySelectorRefs[node.id]}
                  >
                    <p class="text-xs text-gray-600">Items for {node.name}:</p>
                    <div class="flex items-center space-x-2 text-xs mb-1">
                      <span>Filter by:</span>
                      <input type="text" placeholder="Type" class="px-1 py-0.5 border rounded w-20 focus:ring-1 focus:ring-darkblue-600 focus:outline-none" value={node.itemFilters.type} on:input={(e) => handleNodeItemFilterChange(node.id, 'type', e.target.value)} on:click|stopPropagation tabindex="-1"/>
                      <input type="text" placeholder="Level" class="px-1 py-0.5 border rounded w-20 focus:ring-1 focus:ring-darkblue-600 focus:outline-none" value={node.itemFilters.level} on:input={(e) => handleNodeItemFilterChange(node.id, 'level', e.target.value)} on:click|stopPropagation tabindex="-1"/>
                       <button 
                        class="px-1 py-0.5 border border-gray-400 rounded hover:bg-gray-200 focus:outline-none focus:ring-1 focus:ring-darkblue-600"
                        on:click|stopPropagation={(e) => { logEvent(`Node ${node.id} control placeholder clicked.`); nodeContentDummySelectorRefs[node.id]?.focus(); previouslyFocusedNodeHeaderId.set(`node-${node.id}-header`); }}
                        bind:this={nodeContentDummySelectorRefs[node.id]}
                        tabindex="-1"
                      >
                        Item Actions
                      </button>
                    </div>
                    <ul class="list-disc list-inside text-xs pl-2 space-y-0.5">
                      {#each node.items.filter(item => {
                        const typeMatch = node.itemFilters.type ? item.toLowerCase().includes(node.itemFilters.type.toLowerCase()) : true;
                        const levelMatch = node.itemFilters.level ? item.toLowerCase().includes(`lvl ${node.itemFilters.level.toLowerCase()}`) : true;
                        return typeMatch && levelMatch;
                      }) as item (item)}
                        <li class="cursor-pointer hover:text-blue-600 {node.selectedItem === item ? 'font-semibold text-blue-700' : ''}" on:click|stopPropagation={() => selectNodeItem(node.id, item)}>{item}</li>
                      {:else}
                        <p class="text-gray-500">No items match filters.</p>
                      {/each}
                    </ul>
                    {#if document.activeElement === nodeContentDummySelectorRefs[node.id]}
                      <p class="text-xs mt-1 text-darkblue-600">Node item actions are DOM focused.</p>
                    {/if}
                  </div>
                {/if}
              </div>
            {/each}
          {/if}
        </div>
      {/if}
    </div>
  </div>

  <div
    id="cli-bar"
    class="p-2 bg-gray-100 border-t {getBorderClass('cli-input')} flex items-center space-x-2"
  >
    <label for="cli-input-field" class="font-semibold">CLI:</label>
    <input
      bind:this={cliInputRef}
      id="cli-input-field"
      type="text"
      class="flex-grow p-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-darkblue-600"
      placeholder="Enter command..."
      bind:value={$cliInputValue}
      on:focus={() => { 
        if ($focusedId !== 'cli-input') { // If DOM focus happens via mouse click, ensure visual focus matches
            lastFocusedIdBeforeCli.set($focusedId); // Store where we came from
            setVisualFocus('cli-input'); 
            navigationContext.set('sections'); // Assume it's a section level focus if clicked directly
        }
        logEvent('CLI input DOM focused');
      }}
      tabindex="-1"
    />
  </div>

  <div class="p-2 bg-gray-100 border-t border-gray-300">
    <span class="font-semibold">Status:</span>
    <div bind:this={statusBarContentRef} class="status-log-content max-h-24 overflow-y-auto text-xs text-gray-700 bg-white p-1 border rounded">
      {#each $eventLogs as log, i (i)}
        <div>{log}</div>
      {:else}
        <div>No events yet.</div>
      {/each}
    </div>
  </div>
</div>

