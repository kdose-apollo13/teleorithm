<!-- src/lib/components/NodeItem.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  export let node;
  export let appState;
  const dispatch = createEventDispatcher();
  let expanded = true;

  $: filteredItems = node.items.filter(item => {
    const typeMatch = !$appState.filters.type || item.type === $appState.filters.type;
    const levelMatch = !$appState.filters.level || item.level === $appState.filters.level;
    return typeMatch && levelMatch;
  });

  function updateFilters(type, level) {
    dispatch('filterChange', { nodeId: node.id, type, level });
  }

  function selectNode() {
    dispatch('nodeSelected', { nodeId: node.id });
  }

  function toggleExpanded() {
    expanded = !expanded;
    dispatch('statusEvents', {
      message: `Node ${node.id} ${expanded ? 'expanded' : 'collapsed'} at ${new Date().toLocaleTimeString()}`
    });
  }
</script>

<div class="node-item">
  <div class="node-header" on:click={toggleExpanded}>
    <button>
      {expanded ? 'Collapse' : 'Expand'} {node.id}
    </button>
    <span>{node.metadata}</span>
  </div>

  {#if expanded}
    <div class="node-body">
      <div class="controls">
        <button on:click={selectNode}>Select Node</button>
        <select on:change={e => updateFilters(e.target.value, $appState.filters.level)}>
          <option value="">All Types</option>
          <option value="Text">Text</option>
          <option value="Code">Code</option>
          <option value="Img">Img</option>
          <option value="Vid">Vid</option>
        </select>
        <select on:change={e => updateFilters($appState.filters.type, parseInt(e.target.value))}>
          <option value="">All Levels</option>
          <option value="1">Level 1</option>
          <option value="2">Level 2</option>
          <option value="3">Level 3</option>
        </select>
      </div>
      <p>Filtered Items:</p>
      {#each filteredItems as item}
        <div class="item {item.type.toLowerCase()}">
          {item.type} (Level {item.level}): {item.content}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .node-item {
    width: 100%;
    border-bottom: 1px solid #eee;
    margin: 5px 0;
  }
  .node-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 5px;
    background: #f0f0f0;
    border: 1px solid #ccc;
    cursor: pointer;
  }
  .node-header button {
    padding: 5px 10px;
    background: #e0e0e0;
    border: 1px solid #ccc;
  }
  .node-body {
    padding: 10px;
    background: #fafafa;
  }
  .controls {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }
  .item {
    margin-bottom: 10px;
  }
</style>
