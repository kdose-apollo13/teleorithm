<!-- src/lib/components/GraphViz.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  export let appState;
  const dispatch = createEventDispatcher();

  function handleNodeClick(nodeId) {
    dispatch('nodeSelected', { nodeId });
  }
</script>

<div class="graph-viz">
  <h2>Mock Graph Visualization</h2>
  <p>Selected Node: {$appState.selectedNode || 'None'}</p>
  <div class="mock-graph">
    Mock Graph Area
    <button on:click={() => handleNodeClick('node1')}>Select Node 1</button>
    <button on:click={() => handleNodeClick('node2')}>Select Node 2</button>
  </div>
</div>

<style>
  .graph-viz {
    width: 100%;
    padding: 10px;
    background: #f0f0f0;
  }
  .mock-graph {
    height: 200px;
    background: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-style: italic;
  }
</style>
