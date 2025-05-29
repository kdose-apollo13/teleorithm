<script>
  import NodeItem from './NodeItem.svelte'; // Import the new component

  export let nodes = [];
  export let focusedIndex = -1;
  export let selectedNodeId = null; // Can be a single ID
  export let collapsedNodes = new Set(); // Set of IDs

  // If you intend to support multiple selected nodes (as per Shift+j/k discussion)
  // you might want to change selectedNodeId to a Set:
  // export let selectedNodeIds = new Set();
</script>

<div class="node-list-container" role="listbox" aria-label="Node List">
  {#if nodes.length === 0}
    <p>No nodes loaded.</p>
  {:else}
    {#each nodes as node, index (node.id)}
      <NodeItem
        {node}
        isSelected={index === focusedIndex}
        isActive={node.id === selectedNodeId}
        isCollapsed={collapsedNodes.has(node.id)}
        aria-selected={index === focusedIndex}
      />
      {/each}
  {/if}
</div>

<style>
  .node-list-container {
    padding: 1em;
    background-color: var(--container-bg, #f9f9f9);
    height: 100%;
    overflow-y: auto;
    border: 1px solid var(--border-color, #ccc);
    border-radius: 4px;
  }

  .node-list-container p {
    text-align: center;
    color: var(--text-muted-color, #777);
  }
</style>
