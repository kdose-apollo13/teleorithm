<!-- src/lib/components/NodeList.svelte -->
<script>
  import NodeItem from './NodeItem.svelte';
  import { graphData, appState } from '$lib/stores'; // Correct import

  $: selectedIndex = $appState.selectedNodeIndex;
</script>

<div class="node-list">
  <h2>Node List</h2>
  {#each $graphData.nodes as node, index}
    <div class:selected={index === selectedIndex}>
      <NodeItem {node} {appState} on:nodeSelected />
    </div>
  {/each}
</div>

<style>
  .node-list {
    width: 100%;
    padding: 10px;
    background: #ffffff;
  }
  .selected {
    background: #e0e0ff;
  }
</style>
