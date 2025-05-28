<!-- src/lib/NodeList.svelte -->
<script>
  export let nodes = [];
  export let focusedIndex = 0;
  export let selectedNodeId = null;
  export let collapsedNodes = new Set();

  function ensureVisible(index) {
    const item = listElement?.querySelectorAll('.node-item')[index];
    if (item && typeof item.scrollIntoView === 'function') {
      item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  $: if (nodes.length > 0 && focusedIndex >= 0) {
    ensureVisible(focusedIndex);
  }

  let listElement;
</script>

<style>
  .node-list {
    padding: 1rem;
    outline: none;
  }
  .node-item {
    margin-bottom: 1rem;
    padding: 0.5rem;
    border: 1px solid #333;
  }
  .node-item.selected {
    background: #0f0;
    color: #000;
  }
  .node-item.active {
    border-color: #0f0;
  }
  .node-item.collapsed .content-text,
  .node-item.collapsed .content-code {
    display: none;
  }
  .content-text {
    margin: 0.5rem 0;
  }
  .content-code {
    background: #222;
    padding: 0.5rem;
    border-radius: 4px;
  }
</style>

<div class="node-list" role="listbox" aria-label="Node List" bind:this={listElement} tabindex="0">
  {#if nodes.length > 0}
    {#each nodes as node, index (node.id)}
      <div
        class="node-item"
        class:selected={index === focusedIndex}
        class:active={node.id === selectedNodeId}
        class:collapsed={collapsedNodes.has(node.id)}
        role="option"
        aria-selected={index === focusedIndex}
      >
        <h2>{node.id}</h2>
        {#if !collapsedNodes.has(node.id)}
          {#each node.content as item}
            {#if item.type === 'text'}
              <div class="content-text">{@html item.value}</div>
            {:else if item.type === 'code'}
              <pre class="content-code"><code>{item.value}</code></pre>
            {/if}
          {/each}
        {/if}
      </div>
    {/each}
  {:else}
    <p>No nodes found.</p>
  {/if}
</div>
