<!-- src/lib/NodeList.svelte -->
<script>
  import NodeItem from './NodeItem.svelte';

  export let nodes = [];
  export let focusedIndex = 0;
  export let selectedNodeId = null;
  export let collapsedNodes = new Set();
  export let toggleCollapse;
  export let setSelectedNodeId;
  export let filter;

  let listElement;

  function ensureVisible(index) {
    const item = listElement?.querySelectorAll('.node-item')[index];
    item?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  $: if (nodes.length > 0 && focusedIndex >= 0) ensureVisible(focusedIndex);
</script>

<div class="node-list" role="listbox" aria-label="Node List" bind:this={listElement} tabindex="0">
  {#each nodes as node, index (node.id)}
    <NodeItem
      {node}
      {filter}
      isFocused={index === focusedIndex}
      isSelected={node.id === selectedNodeId}
      isCollapsed={collapsedNodes.has(node.id)}
      on:toggleCollapse={() => toggleCollapse(node.id)}
      on:select={() => setSelectedNodeId(node.id)}
    />
  {/each}
</div>

<style>
  .node-list {
    padding: 1rem;
    outline: none;
  }
</style>
