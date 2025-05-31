<script>
  import { onMount, tick } from 'svelte';
  import CommandLine from '$lib/CommandLine.svelte';
  import NodeList from '$lib/NodeList.svelte';
  // import NodeView from '$lib/NodeView.svelte'; // Assuming you'll have a dedicated view

  let nodes = [];
  let currentFocus = 'cli'; // 'cli', 'nodelist', 'nodeview'
  let focusedNodeIndex = -1; // Index in the nodes array for nodelist navigation
  
  // --- State for multiple selections ---
  let selectedNodeIds = new Set(); // Use a Set to store IDs of selected nodes
  
  let collapsedNodes = new Set();
  let commandHistory = [];
  let historyIndex = -1;

  // Filter state - will be expanded later
  let activeFilters = {}; // Key: nodeId, Value: filterString

  async function loadNodes() {
    if (typeof window !== 'undefined' && window.api && window.api.listNodes) {
      try {
        const fetchedNodes = await window.api.listNodes();
        nodes = fetchedNodes.sort((a, b) => (a.id || '').localeCompare(b.id || ''));
        if (nodes.length > 0) {
          // focusedNodeIndex = 0; // Don't auto-focus first node on load
        }
        console.log('Nodes loaded in +page.svelte:', nodes);
      } catch (error) {
        console.error('Error loading nodes in +page.svelte:', error);
        nodes = [{ id: 'error', content: [{ type: 'text', value: '<p>Error loading nodes.</p>' }] }];
      }
    } else {
      console.warn('window.api.listNodes not available. Are you in Electron with preload script?');
      nodes = [{ id: 'placeholder', content: [{ type: 'text', value: '<p>Node loading API not available.</p>' }] }];
    }
  }

  onMount(async () => {
    await loadNodes();
    // Ensure CLI is focused initially
    const cliInput = document.querySelector('.cli-container input');
    if (cliInput) {
      cliInput.focus();
    }

    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => {
      window.removeEventListener('keydown', handleGlobalKeyDown);
    };
  });

  function focusCli() {
    currentFocus = 'cli';
    focusedNodeIndex = -1; // Reset nodelist focus when CLI takes over
    const input = document.querySelector('.cli-container input');
    if (input) input.focus();
    console.log('Focus: CLI');
  }

  function focusNodeList() {
    if (nodes.length === 0) {
      focusCli(); // Can't focus nodelist if empty
      return;
    }
    currentFocus = 'nodelist';
    if (focusedNodeIndex === -1 && nodes.length > 0) {
        focusedNodeIndex = 0;
    }
    const cliInput = document.querySelector('.cli-container input');
    if (cliInput) cliInput.blur();
    // Actual focus on the list container for key events, item gets visual "selected" class
    const nodeListEl = document.querySelector('.nodelist-region .node-list-container');
    if (nodeListEl) nodeListEl.focus(); // Needs tabindex="-1" on the div
    console.log('Focus: NodeList, Index:', focusedNodeIndex);
  }

  // Placeholder for focusNodeView if you implement it
  // function focusNodeView() {
  //   if (selectedNodeIds.size === 0 && nodes.length > 0) {
  //       selectedNodeIds = new Set([nodes[focusedNodeIndex === -1 ? 0 : focusedNodeIndex].id]);
  //   }
  //   if (selectedNodeIds.size > 0) {
  //       currentFocus = 'nodeview';
  //       const cliInput = document.querySelector('.cli-container input');
  //       if (cliInput) cliInput.blur();
  //       console.log('Focus: NodeView, Selected:', Array.from(selectedNodeIds));
  //   } else {
  //       focusNodeList(); // Can't focus view if nothing is selected
  //   }
  // }

  let escapePressCount = 0;
  let escapeTimer = null;

  function handleGlobalKeyDown(event) {
    // console.log(`Key: ${event.key}, Shift: ${event.shiftKey}, Focus: ${currentFocus}, EscapeCount: ${escapePressCount}`);

    if (event.key === 'Escape') {
      event.preventDefault();
      clearTimeout(escapeTimer);
      escapePressCount++;

      if (currentFocus === 'nodelist') {
        if (escapePressCount >= 2 || selectedNodeIds.size === 0) {
          selectedNodeIds = new Set(); // Clear selection
          nodes = [...nodes]; // Trigger reactivity for NodeList
          focusCli();
          escapePressCount = 0;
        } else { // First escape in nodelist with items selected
          focusCli(); // Go to CLI, retain selection
          escapePressCount = 0; // Reset count for next cycle
        }
      } else if (currentFocus === 'cli' && document.activeElement === document.querySelector('.cli-container input')) {
        if (document.querySelector('.cli-container input').value === '') { // Only switch if CLI is empty
            focusNodeList();
        } else {
            // If CLI has text, first escape might clear it (handled by CommandLine.svelte internally)
            // or do nothing to allow text manipulation. For now, we assume it just moves focus if empty.
        }
        escapePressCount = 0;
      } else if (currentFocus === 'nodeview') {
        // focusNodeList(); // Example: escape from nodeview goes to nodelist
        // escapePressCount = 0;
      } else {
        focusCli(); // Default focus
        escapePressCount = 0;
      }
      
      escapeTimer = setTimeout(() => { escapePressCount = 0; }, 300); // Reset count after 300ms
      return;
    }
    
    // Reset escape count if any other key is pressed
    if (event.key !== 'Shift') { // Allow shift to be pressed without resetting escape sequence
        escapePressCount = 0;
        clearTimeout(escapeTimer);
    }

    if (event.key === ';' && currentFocus !== 'cli') {
        event.preventDefault();
        focusCli();
        return;
    }

    if (currentFocus === 'nodelist') {
      if (nodes.length === 0) return;

      let newIndex = focusedNodeIndex;
      const currentFocusedNodeId = focusedNodeIndex !== -1 && nodes[focusedNodeIndex] ? nodes[focusedNodeIndex].id : null;

      if (event.key === 'j') {
        event.preventDefault();
        newIndex = Math.min(nodes.length - 1, (focusedNodeIndex === -1 ? 0 : focusedNodeIndex) + 1);
        if (event.shiftKey && newIndex !== focusedNodeIndex && nodes[newIndex]) {
            selectedNodeIds.add(nodes[newIndex].id);
            selectedNodeIds = new Set(selectedNodeIds); // Trigger reactivity
        }
      } else if (event.key === 'k') {
        event.preventDefault();
        newIndex = Math.max(0, (focusedNodeIndex === -1 ? nodes.length -1 : focusedNodeIndex) - 1);
         if (event.shiftKey && newIndex !== focusedNodeIndex && nodes[newIndex]) {
            selectedNodeIds.add(nodes[newIndex].id);
            selectedNodeIds = new Set(selectedNodeIds); // Trigger reactivity
        }
      } else if (event.key === 'Shift' && !event.repeat) { // Check for Shift key press (not hold)
        // This is tricky because Shift is a modifier. We'll handle Shift + Space or Shift + Enter for explicit toggle
        // For now, Shift + j/k handles adding. Explicit toggle is below.
      } else if (event.code === 'Space' && event.shiftKey) { // Shift + Space to toggle selection
        event.preventDefault();
        if (currentFocusedNodeId) {
          if (selectedNodeIds.has(currentFocusedNodeId)) {
            selectedNodeIds.delete(currentFocusedNodeId);
          } else {
            selectedNodeIds.add(currentFocusedNodeId);
          }
          selectedNodeIds = new Set(selectedNodeIds); // Trigger reactivity
        }
      }
      // More robust Shift handling may require tracking keydown/keyup for Shift itself
      // The Shift + j/k already adds to selection upon movement.
      // Single Shift press to toggle is complex due to its nature as a modifier.
      // Let's use Shift+Space for an explicit toggle of the *currently focused* item for now.

      if (newIndex !== focusedNodeIndex) {
        focusedNodeIndex = newIndex;
        // console.log('NodeList Nav:', focusedNodeIndex, 'Selected:', Array.from(selectedNodeIds));
      }
    }
  }

  function handleCommand(event) {
    const command = event.detail.trim();
    if (!command) return;

    commandHistory = [command, ...commandHistory].slice(0, 100); // Keep last 100
    historyIndex = -1; // Reset history index

    console.log('Command received:', command);
    const [action, ...args] = command.toLowerCase().split(' ');

    if (action === 'select' && args[0] === 'none' || action === 'deselect' && args[0] === 'all') {
        selectedNodeIds = new Set();
        nodes = [...nodes]; // reactivity
        console.log('All nodes deselected');
    } else if (action === 'filter') { // Placeholder for future filter logic
        const filterValue = args.join(' ');
        // This will be enhanced later to apply to selectedNodeIds
        console.log(`Filter command: '${filterValue}' on selected:`, Array.from(selectedNodeIds));
        // Apply filter to selected nodes
        const newActiveFilters = { ...activeFilters };
        selectedNodeIds.forEach(id => {
            newActiveFilters[id] = filterValue;
        });
        activeFilters = newActiveFilters;

    } else if (action === 'collapse') {
      if (args.length > 0) {
        args.forEach(nodeId => collapsedNodes.add(nodeId));
        collapsedNodes = new Set(collapsedNodes); // reactivity
      }
    } else if (action === 'expand') {
       if (args.length > 0) {
        args.forEach(nodeId => collapsedNodes.delete(nodeId));
        collapsedNodes = new Set(collapsedNodes); // reactivity
      }
    } else if (action === 'help') {
        // show help
    }
    // Add more command handlers here
    tick().then(() => { // Ensure DOM updates before trying to refocus
      const cliInput = document.querySelector('.cli-container input');
      if (cliInput) {
        cliInput.focus();
        cliInput.select(); // Optionally select the (now empty) text
      }
    });
  }

  // Function to get content for a given node ID, applying filters
  function getFilteredContent(nodeId, contentArray) {
    const filterString = activeFilters[nodeId];
    if (!filterString) return contentArray;

    // Placeholder: Implement actual filtering based on filterString
    // For now, just returns all content if a filter is set for the node
    // We will use filterUtils.js here later
    console.log(`Filtering content for ${nodeId} with filter: ${filterString}`);
    // This is where the enhanced filter logic will go.
    // For `t1c`: Text level 1 AND all Code levels.
    // For `t`: All text levels.
    
    // Dummy implementation:
    // return contentArray.filter(item => item.type === 'text' && item.metadata?.level === '1');
    
    // More advanced parsing needed here for filterUtils.js
    // This is a simplified placeholder:
    const normalizedFilter = filterString.toLowerCase();
    let showAllOfType = {}; // T: true, C: true
    let specificLevels = {}; // T: [1], C: []

    let currentType = null;
    for (let i = 0; i < normalizedFilter.length; i++) {
        const char = normalizedFilter[i];
        if (['t', 'c', 'i', 'v'].includes(char)) {
            currentType = char.toUpperCase();
            if (i + 1 === normalizedFilter.length || isNaN(parseInt(normalizedFilter[i+1]))) {
                showAllOfType[currentType] = true; // e.g., "T" or "T" at end of "T1C"
                 if(!specificLevels[currentType]) specificLevels[currentType] = [];
            } else {
                 if(!specificLevels[currentType]) specificLevels[currentType] = [];
            }
        } else if (currentType && !isNaN(parseInt(char))) {
            showAllOfType[currentType] = false; // Has specific levels
            specificLevels[currentType].push(parseInt(char));
        } else {
            currentType = null; // Reset if unexpected char
        }
    }
    
    return contentArray.filter(item => {
        const itemTypeChar = item.type.toUpperCase().charAt(0);
        const itemLevel = parseInt(item.metadata?.level, 10);

        if (specificLevels[itemTypeChar]) { // Check specific levels first
            if (showAllOfType[itemTypeChar] && specificLevels[itemTypeChar].length === 0) return true; // Matched "T" or "C" alone
            return specificLevels[itemTypeChar].includes(itemLevel);
        }
        return false; // Default to not showing if no rule matches
    });
  }
</script>

<div id="app-container">
  <div class="main-layout">
    <div class="nodelist-region" class:region-focused={currentFocus === 'nodelist'}>
      <NodeList
        {nodes}
        bind:focusedNodeIndex
        bind:selectedNodeIds
        {collapsedNodes}
        {activeFilters} 
        {getFilteredContent}
      />
    </div>
    <div class="nodeview-region" class:region-focused={currentFocus === 'nodeview'}>
      {#if selectedNodeIds.size > 0}
        <h4>Selected Node(s) View (Content based on filter)</h4>
        {#each Array.from(selectedNodeIds) as selectedId}
            {@const node = nodes.find(n => n.id === selectedId)}
            {#if node}
            <div class="selected-node-view-item">
                <h5>{node.id}</h5>
                {#each getFilteredContent(node.id, node.content || []) as contentItem, i (contentItem.type + i)}
                     {#if contentItem.type === 'text'}
                        <div class="content-text">{@html contentItem.value}</div>
                    {:else if contentItem.type === 'code'}
                        <pre class="content-code"><code>{contentItem.value}</code></pre>
                    {/if}
                {/each}
            </div>
            {/if}
        {/each}
       {:else}
        <p class="placeholder-text">Select a node to view its details here. Apply filters via CLI.</p>
       {/if}
    </div>
  </div>

  <div class="cli-container cli-region" class:region-focused={currentFocus === 'cli'}>
    <CommandLine on:command={handleCommand} bind:commandHistory bind:historyIndex />
  </div>
</div>

<style>
  #app-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: var(--background-color, #f0f2f5);
  }

  .main-layout {
    display: flex;
    flex-grow: 1;
    overflow: hidden; /* Important for child overflow scrolling */
    padding: 0.5rem;
    gap: 0.5rem;
  }

  .nodelist-region {
    flex: 1; /* Takes 1/3 of the space if nodeview is 2 */
    overflow-y: auto; /* Allows nodelist to scroll independently */
    border-radius: var(--border-radius, 4px);
  }

  .nodeview-region {
    flex: 2; /* Takes 2/3 of the space */
    overflow-y: auto; /* Allows nodeview to scroll independently */
    padding: 1em;
    border-radius: var(--border-radius, 4px);
    background-color: var(--surface-color);
  }
  .selected-node-view-item {
    margin-bottom: 1em;
    padding: 0.5em;
    border: 1px dashed var(--border-color-light);
  }
  .selected-node-view-item h5 {
    margin-top: 0;
    color: var(--primary-color);
  }
   .placeholder-text {
    color: var(--text-muted-color);
    text-align: center;
    margin-top: 2rem;
  }

  .cli-container {
    flex-shrink: 0; /* Prevents CLI from shrinking */
    padding: 0.5rem;
    border-top: 1px solid var(--border-color, #dee2e6);
    background-color: var(--surface-color);
  }

  /* Focus styling is in app.css for .region-focused */
</style>
