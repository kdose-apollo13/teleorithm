<!-- src/lib/components/NodeList.svelte -->
<script>
  import NodeItem from './NodeItem.svelte';
  import { graphData } from '../stores/graphData';
  export let appState;
</script>

<div class="node-list">
  <h2>Mock Node List</h2>
  <p>Filters: Type={$appState.filters.type || 'None'}, Level={$appState.filters.level || 'None'}</p>
  {#each $graphData.nodes as node}
    <NodeItem {node} {appState} on:filterChange on:nodeSelected />
  {/each}
</div>

<style>
  .node-list {
    width: 100%;
    padding: 10px;
    background: #ffffff;
  }
</style>
