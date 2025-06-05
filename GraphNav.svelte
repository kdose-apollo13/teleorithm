<script>
  import { onMount } from 'svelte'; 

  // --- Core State ---
  let appLayout = { 
    viewMode: 'graphOnly', // 'graphOnly', 'nodesLeft', 'nodesCenter', 'nodesRight'
    graphVizIsCollapsed: false,
    nodeContentIsCollapsed: false 
  };

  let graphName = "No graph loaded";
  let graphNodes = []; 
  let selectedGraphNodeIdsFromViz = []; 
  
  let nodeDetailItems = []; 
  
  let commandText = '';
  let statusBarText = 'Status: Ready';

  $: nodeCount = graphNodes.length;
  $: selectedGraphNodeCountInViz = selectedGraphNodeIdsFromViz.length;

  // --- Keyboard Handler Helper ---
  function handleKeyPress(event, callback) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      callback();
    }
  }

  // --- GraphViz Component Data & Logic (Simulated) ---
  function loadDummyGraph() {
    graphName = "System Architecture Mk II";
    graphNodes = [
      { id: 'g_compute', name: 'Compute Cluster', content: 'High-performance compute nodes for parallel processing.', isGraphSelected: false },
      { id: 'g_storage', name: 'Central Storage', content: 'SAN with SSD tier for fast access, HDD for archive.', isGraphSelected: false },
      { id: 'g_network', name: 'Core Network Switch', content: 'Redundant, high-bandwidth fabric.', isGraphSelected: false },
      { id: 'g_api', name: 'API Gateway', content: 'Entry point for all external service requests.', isGraphSelected: false },
      { id: 'g_auth', name: 'Auth Service', content: 'Handles user authentication and authorization.', isGraphSelected: false },
    ];
    selectedGraphNodeIdsFromViz = []; 
    appLayout.graphVizIsCollapsed = false;
    if (appLayout.viewMode !== 'graphOnly' && selectedGraphNodeIdsFromViz.length === 0) {
        // appLayout.viewMode = 'graphOnly'; 
    }
    appLayout = {...appLayout};
    updateNodeDetailItems(); 
    updateStatusBar();
  }

  function toggleGraphNodeSelectionInViz(nodeId) {
    const node = graphNodes.find(n => n.id === nodeId);
    if (!node) return;

    node.isGraphSelected = !node.isGraphSelected;
    graphNodes = [...graphNodes]; 

    selectedGraphNodeIdsFromViz = graphNodes.filter(n => n.isGraphSelected).map(n => n.id);
    
    if (node.isGraphSelected && selectedGraphNodeIdsFromViz.length >= 1 && appLayout.viewMode === 'graphOnly') { // Changed to >=1
        appLayout.viewMode = 'nodesCenter'; 
    }
    appLayout = {...appLayout};
    updateNodeDetailItems();
    updateStatusBar();
  }

  function handleNodeDetailItemClosed(closedGraphNodeId) {
    const node = graphNodes.find(n => n.id === closedGraphNodeId);
    if (node) {
      node.isGraphSelected = false;
      graphNodes = [...graphNodes];
      selectedGraphNodeIdsFromViz = graphNodes.filter(n => n.isGraphSelected).map(n => n.id);
    }
    // if (selectedGraphNodeIdsFromViz.length === 0 && appLayout.viewMode !== 'graphOnly') {
    //     appLayout.viewMode = 'graphOnly'; 
    // }
    appLayout = {...appLayout};
    updateNodeDetailItems(); 
    updateStatusBar();
  }
  
  function updateNodeDetailItems() {
    const newDetailItems = [];
    selectedGraphNodeIdsFromViz.forEach(gid => {
      const existingItem = nodeDetailItems.find(item => item.graphNodeId === gid);
      const gNode = graphNodes.find(n => n.id === gid);
      if (gNode) { 
        if (existingItem) {
          newDetailItems.push({
            ...existingItem, 
            title: gNode.name, 
            content: gNode.content 
          }); 
        } else {
          newDetailItems.push({
            graphNodeId: gid,
            title: gNode.name,
            content: gNode.content,
            isSelectedForBulk: false,
            isCollapsed: false,
            uniqueViewId: 'view_' + gid + Math.random().toString(36).substr(2, 9) 
          });
        }
      }
    });
    nodeDetailItems = newDetailItems.sort((a, b) => 
        selectedGraphNodeIdsFromViz.indexOf(a.graphNodeId) - selectedGraphNodeIdsFromViz.indexOf(b.graphNodeId)
    );
  }

  function toggleNodeDetailItemSelection(uniqueViewId) {
    const item = nodeDetailItems.find(i => i.uniqueViewId === uniqueViewId);
    if (item) item.isSelectedForBulk = !item.isSelectedForBulk;
    nodeDetailItems = [...nodeDetailItems];
    updateStatusBar();
  }

  function toggleNodeDetailItemCollapse(uniqueViewId) {
    const item = nodeDetailItems.find(i => i.uniqueViewId === uniqueViewId);
    if (item) item.isCollapsed = !item.isCollapsed;
    nodeDetailItems = [...nodeDetailItems];
  }
  
  function setLayoutMode(mode) {
    appLayout.viewMode = mode;
    appLayout = {...appLayout}; 
    updateStatusBar();
  }
  
  function closeSelectedNodeDetailItems() {
    const idsToClose = nodeDetailItems.filter(item => item.isSelectedForBulk).map(item => item.graphNodeId);
    idsToClose.forEach(gid => handleNodeDetailItemClosed(gid)); 
  }

  function expandSelectedNodeDetailItems() {
    nodeDetailItems.forEach(item => { if (item.isSelectedForBulk) item.isCollapsed = false; });
    nodeDetailItems = [...nodeDetailItems];
  }

  function collapseSelectedNodeDetailItems() {
    nodeDetailItems.forEach(item => { if (item.isSelectedForBulk) item.isCollapsed = true; });
    nodeDetailItems = [...nodeDetailItems];
  }
  
  function executeCommand() {
    console.log('Executing command:', commandText);
    statusBarText = `Command executed: ${commandText}`;
    commandText = '';
  }

  function updateStatusBar() {
    const selectedNodeDetailItemCount = nodeDetailItems.filter(item => item.isSelectedForBulk).length;
    statusBarText = `Graph: ${graphName} (${nodeCount}) | Viz Sel: ${selectedGraphNodeCountInViz} | Layout: ${appLayout.viewMode} | Item Sel: ${selectedNodeDetailItemCount}`;
  }
  
  onMount(() => {
    loadDummyGraph(); 
    updateStatusBar();
  });

</script>

<main>
  <div class="main-view-area" 
       class:layout-mode-graph-only={appLayout.viewMode === 'graphOnly'}
       class:layout-mode-nodes-left={appLayout.viewMode === 'nodesLeft'}
       class:layout-mode-nodes-center={appLayout.viewMode === 'nodesCenter'}
       class:layout-mode-nodes-right={appLayout.viewMode === 'nodesRight'}>

    <div 
      class="component-pane graphviz-pane" 
      class:collapsed={appLayout.graphVizIsCollapsed}
      class:respect-header-height-only={appLayout.viewMode === 'nodesCenter' && appLayout.graphVizIsCollapsed}
    >
      <div class="component-header">
        <button class="load-graph-btn" on:click={loadDummyGraph} title="Load Graph (Dummy)">L</button>
        <span class="component-title" on:click={() => appLayout.graphVizIsCollapsed = !appLayout.graphVizIsCollapsed}>
          Graph View: {graphName}
        </span>
        <button 
            class="component-collapse-toggle" 
            on:click|stopPropagation={() => appLayout.graphVizIsCollapsed = !appLayout.graphVizIsCollapsed}
            aria-expanded={!appLayout.graphVizIsCollapsed}
        >
            {appLayout.graphVizIsCollapsed ? '▽' : '△'}
        </button>
      </div>
      {#if !appLayout.graphVizIsCollapsed}
        <div class="component-content graphviz-content">
          <div class="graph-metadata-line">
            <span>Nodes: {nodeCount} | Selected in Graph: {selectedGraphNodeCountInViz}</span>
          </div>
          <div class="dummy-graph-node-selector">
            {#if graphNodes.length === 0}
              <span style="font-style: italic; font-size: 0.9em;">No graph. Click 'L'.</span>
            {:else}
              <span>Click to select/deselect graph nodes: </span>
              {#each graphNodes as node (node.id)}
                <button 
                  class="graph-node-chip" 
                  class:selected={node.isGraphSelected}
                  on:click={() => toggleGraphNodeSelectionInViz(node.id)}
                  title="Toggle selection for {node.name}"
                >
                  {node.name}
                </button>
              {/each}
            {/if}
          </div>
          <div class="future-viz-placeholder">
            <p style="text-align:center; padding:20px; color:#aaa;">(Graph Visualization Area)</p>
          </div>
        </div>
      {/if}
    </div>

    {#if appLayout.viewMode !== 'graphOnly'}
      <div class="component-pane node-content-pane" class:collapsed={appLayout.nodeContentIsCollapsed}>
        <div class="component-header">
          <span class="component-title" on:click={() => appLayout.nodeContentIsCollapsed = !appLayout.nodeContentIsCollapsed}>
            Selected Node Details ({nodeDetailItems.length})
          </span>
           <button 
            class="component-collapse-toggle" 
            on:click|stopPropagation={() => appLayout.nodeContentIsCollapsed = !appLayout.nodeContentIsCollapsed}
            aria-expanded={!appLayout.nodeContentIsCollapsed}
            >
            {appLayout.nodeContentIsCollapsed ? '▽' : '△'}
        </button>
        </div>
        {#if !appLayout.nodeContentIsCollapsed}
          <div class="component-content node-content-list">
            {#if nodeDetailItems.length === 0}
              <p class="empty-node-content-message">
                {#if selectedGraphNodeCountInViz > 0}
                    All selected graph nodes are currently shown or no specific details to display.
                {:else}
                    Select nodes from the Graph View to see details.
                {/if}
              </p>
            {/if}
            {#each nodeDetailItems as item (item.uniqueViewId)}
              <div
                class="node-detail-item"
                role="listitem" 
                tabindex="0"
                aria-labelledby="detail-item-title-{item.uniqueViewId}"
                aria-selected={item.isSelectedForBulk}
                on:keydown={(e) => handleKeyPress(e, () => toggleNodeDetailItemSelection(item.uniqueViewId))}
              >
                <div class="detail-item-header">
                  <div
                    class="detail-item-selection-toggle"
                    role="checkbox"
                    aria-checked={item.isSelectedForBulk}
                    aria-label="Select {item.title}"
                    tabindex="0"
                    class:selected={item.isSelectedForBulk}
                    on:click|stopPropagation={() => toggleNodeDetailItemSelection(item.uniqueViewId)}
                    on:keydown|stopPropagation={(e) => handleKeyPress(e, () => toggleNodeDetailItemSelection(item.uniqueViewId))}
                  ></div>
                  <span 
                      id="detail-item-title-{item.uniqueViewId}" 
                      class="detail-item-title-text"
                      title="Toggle collapse for {item.title}"
                      on:click|stopPropagation={() => toggleNodeDetailItemCollapse(item.uniqueViewId)}
                  >
                      {item.title}
                  </span>
                  <div class="detail-item-controls">
                    <button
                      class="detail-item-control-btn"
                      title="Toggle collapse"
                      aria-expanded={!item.isCollapsed}
                      on:click|stopPropagation={() => toggleNodeDetailItemCollapse(item.uniqueViewId)}
                    >{item.isCollapsed ? '▽' : '△'}</button>
                    <button
                      class="detail-item-control-btn close"
                      title="Close this node detail (deselects from graph)"
                      on:click|stopPropagation={() => handleNodeDetailItemClosed(item.graphNodeId)}
                    >X</button>
                  </div>
                </div>
                {#if !item.isCollapsed}
                  <div class="detail-item-content">
                    <p>{item.content || 'No specific content.'}</p>
                    <small>Graph Node ID: {item.graphNodeId}</small>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <div class="cli-bar">
    <input type="text" placeholder="Enter command..." bind:value={commandText} on:keydown={(e) => e.key === 'Enter' && executeCommand()} aria-label="Command input" />
    <div class="layout-controls">
        <button on:click={() => setLayoutMode('graphOnly')} class:active={appLayout.viewMode === 'graphOnly'} title="Graph View Only">Gfx</button>
        <button on:click={() => setLayoutMode('nodesLeft')} class:active={appLayout.viewMode === 'nodesLeft'} title="Nodes Left | Graph Right">[N|Gfx]</button>
        <button on:click={() => setLayoutMode('nodesCenter')} class:active={appLayout.viewMode === 'nodesCenter'} title="Graph Top / Nodes Bottom">[Gfx/N]</button>
        <button on:click={() => setLayoutMode('nodesRight')} class:active={appLayout.viewMode === 'nodesRight'} title="Graph Left | Nodes Right">[Gfx|N]</button>
    </div>
    <button on:click={closeSelectedNodeDetailItems} title="Close Selected Items">X Sel</button>
    <button on:click={expandSelectedNodeDetailItems} title="Expand Selected Items">^ Sel</button>
    <button on:click={collapseSelectedNodeDetailItems} title="Collapse Selected Items">v Sel</button>
  </div>

  <div class="status-bar" role="status" aria-live="polite">
    {statusBarText}
  </div>
</main>

<style>
  :global(body, html) { margin: 0; padding: 0; height: 100%; font-family: sans-serif; overflow: hidden; box-sizing: border-box;}
  *, *:before, *:after { box-sizing: inherit; }
  main { display: flex; flex-direction: column; height: 100vh; background-color: #f0f0f0; }

  .main-view-area {
    display: flex;
    flex-grow: 1;
    overflow: hidden; 
    border-bottom: 1px solid #ccc;
  }

  .component-pane {
    display: flex;
    flex-direction: column;
    overflow: hidden; 
    border: 1px solid transparent; /* Default transparent border for layout modes to add specific ones */
    background-color: #fdfdfd;
  }
  
  /* --- Layout Mode Specific Styles --- */
  .main-view-area.layout-mode-graph-only .graphviz-pane { flex: 1 0 100%; }
  .main-view-area.layout-mode-graph-only .node-content-pane { display: none; }

  .main-view-area.layout-mode-nodes-left,
  .main-view-area.layout-mode-nodes-right {
    flex-direction: row; 
  }
  .main-view-area.layout-mode-nodes-left .graphviz-pane { flex: 3 1 60%; order: 2; border-left: 1px solid #ccc; }
  .main-view-area.layout-mode-nodes-left .node-content-pane { flex: 2 1 40%; order: 1; border-right: 1px solid #ccc; }

  .main-view-area.layout-mode-nodes-right .graphviz-pane { flex: 3 1 60%; order: 1; border-right: 1px solid #ccc;}
  .main-view-area.layout-mode-nodes-right .node-content-pane { flex: 2 1 40%; order: 2; border-left: 1px solid #ccc; }

  .main-view-area.layout-mode-nodes-center {
    flex-direction: column;
  }
  .main-view-area.layout-mode-nodes-center .graphviz-pane {
    flex: 3 1 65%; /* Default when expanded */
    border-bottom: 1px solid #ccc; 
  }
  .main-view-area.layout-mode-nodes-center .node-content-pane {
    flex: 2 1 35%; /* Default when graphviz is expanded */
  }

  /* Styles for when GraphViz pane is collapsed in nodesCenter mode */
  .main-view-area.layout-mode-nodes-center .graphviz-pane.respect-header-height-only {
    flex-grow: 0;      
    flex-shrink: 0;    
    flex-basis: auto;  
  }
  /* Ensure node-content-pane takes up remaining space when graphviz is collapsed to header */
  .main-view-area.layout-mode-nodes-center .graphviz-pane.respect-header-height-only + .node-content-pane {
    flex-grow: 1; 
  }
  /* --- End Layout Mode Specific Styles --- */


  .component-header {
    display: flex; align-items: center; padding: 6px 10px;
    background-color: #e8e8e8; border-bottom: 1px solid #d0d0d0; flex-shrink: 0;
  }
  .component-title { flex-grow: 1; font-weight: bold; font-size: 0.95em; cursor: pointer; }
  .component-title:hover { color: dodgerblue; }
  .load-graph-btn { padding: 4px 8px; margin-right: 10px; background-color: #555; color:white; border:none; border-radius:3px; cursor:pointer; font-size: 0.9em;}
  .load-graph-btn:hover { background-color: #666; }
  .component-collapse-toggle { background:none; border:none; cursor:pointer; font-size:1.1em; padding:0 5px; margin-left: auto;}

  .component-content { overflow-y: auto; flex-grow: 1; padding: 10px; }
  .component-pane.collapsed .component-content { display: none; }
  
  .graphviz-content .graph-metadata-line { font-size: 0.9em; margin-bottom: 10px; color: #444; }
  .graphviz-content .dummy-graph-node-selector { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; font-size: 0.9em; margin-bottom: 10px;}
  .graph-node-chip {
    padding: 4px 10px; border: 1px solid #b0b0b0; background-color: #f0f0f0;
    border-radius: 14px; cursor: pointer; font-size: 0.9em;
  }
  .graph-node-chip:hover { background-color: #e0e0e0; border-color: #999; }
  .graph-node-chip.selected { background-color: dodgerblue; color: white; border-color: dodgerblue; }
  .future-viz-placeholder { border: 1px dashed #ccc; background-color: #f9f9f9; min-height: 150px; display:flex; align-items:center; justify-content:center; }

  .empty-node-content-message { text-align:center; color:#777; padding:20px; font-style: italic;}
  
  .node-detail-item { border: 1px solid #d0d0d0; margin-bottom: 8px; background-color: #fff; border-radius: 3px; }
  .node-detail-item:focus-visible { outline: 2px solid dodgerblue; outline-offset: 1px;}
  .detail-item-header { display: flex; align-items: center; background-color: #f7f7f7; padding: 5px 8px; border-bottom: 1px solid #e7e7e7; }
  .detail-item-selection-toggle {
    width: 15px; height: 15px; border: 1px solid #888; background-color: white;
    margin-right: 8px; cursor: pointer; display:flex; align-items:center; justify-content:center; border-radius:3px; flex-shrink:0;
  }
  .detail-item-selection-toggle.selected { background-color: dodgerblue; border-color: dodgerblue; }
  .detail-item-selection-toggle.selected::after { content: '✔'; color: white; font-size: 10px; }
  .detail-item-title-text { flex-grow: 1; cursor: pointer; font-size: 0.9em; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .detail-item-title-text:hover { color: #0078d4; }
  .detail-item-controls { margin-left: auto; display:flex; align-items:center; flex-shrink:0; }
  .detail-item-control-btn { background:none; border:none; cursor:pointer; padding: 1px 3px; font-size:0.85em; margin-left:2px; color:#555 }
  .detail-item-control-btn.close { font-weight:bold; }
  .detail-item-control-btn:hover { color: #0078d4; }
  .detail-item-content { padding: 8px 10px; font-size: 0.85em; line-height:1.5; }
  .detail-item-content small { display:block; margin-top:6px; color:#888; font-size:0.9em; }

  .cli-bar {
    display: flex; align-items: center; padding: 7px 10px; background-color: #2d2d2d; color: white;
    border-top: 1px solid #404040; flex-shrink: 0;
  }
  .cli-bar input[type="text"] { flex-grow: 1; padding: 5px 8px; border:1px solid #555; background-color:#1e1e1e; color:white; border-radius:3px; font-size:0.9em;}
  .cli-bar .layout-controls { display: flex; margin-right: 10px; /* Spacing before other CLI buttons */}
  .cli-bar button { padding: 5px 9px; background-color: #4f4f4f; color:white; border:none; cursor:pointer; border-radius:3px; margin-left:5px; font-size:0.9em;}
  .cli-bar button:hover { background-color: #6a6a6a; }
  .cli-bar .layout-controls button { margin-left: 2px; margin-right: 2px; }
  .cli-bar .layout-controls button.active { background-color: dodgerblue; font-weight: bold; }

  .status-bar { padding: 7px 10px; background-color: #1e1e1e; color: #b0b0b0; font-size: 0.85em; text-align: left; border-top: 1px solid #333; flex-shrink: 0; }
</style>
