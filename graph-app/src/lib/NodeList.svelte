<script>
  import NodeItem from './NodeItem.svelte';

  export let nodes = [];
  // Ensure this prop name matches what's passed from +page.svelte
  export let focusedNodeIndex = -1; 
  export let selectedNodeIds = new Set();
  export let collapsedNodes = new Set();
  
  export let activeFilters = {};
  export let getFilteredContent;

</script>

<div
  class="node-list-container"
  role="listbox"
  aria-label="Node List"
  tabindex="-1"
  aria-activedescendant={ (nodes.length > 0 && focusedNodeIndex > -1 && nodes[focusedNodeIndex]) ? nodes[focusedNodeIndex].id : undefined }
>
  {#if nodes.length === 0}
    <p>No nodes loaded.</p>
  {:else}
    {#each nodes as node, index (node.id)}
      <div id={node.id} role="option" aria-selected={selectedNodeIds.has(node.id)}>
        <NodeItem
          {node}
          isSelected={index === focusedNodeIndex}
          isActive={selectedNodeIds.has(node.id)}
          isCollapsed={collapsedNodes.has(node.id)}
          displayContent={getFilteredContent(node.id, node.content || [])}
          isNodeListFocused={true} 
        />
      </div>
    {/each}
  {/if}
</div>

<style>
  /* ... styles remain the same as previous response ... */
  .node-list-container {
    padding: 0.5em;
    background-color: var(--container-bg, #fdfdfd);
    height: 100%;
    overflow-y: auto;
    border-radius: var(--border-radius, 4px);
  }
  .node-list-container:focus-visible {
    /* Outline typically handled by .region-focused if parent has it */
  }
  .node-list-container p {
    text-align: center;
    color: var(--text-muted-color, #777);
    padding: 1em;
  }
</style>

