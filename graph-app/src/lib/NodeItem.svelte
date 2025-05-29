<script>
  export let node;
  export let isSelected = false;
  export let isActive = false;
  export let isCollapsed = false;

  $: itemClasses = `
    node-item
    ${isSelected ? 'selected' : ''}
    ${isActive ? 'active' : ''}
    ${isCollapsed ? 'collapsed' : ''}
  `;

  function formatDate(timestamp) {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch (e) {
      return timestamp; // fallback to raw timestamp if parsing fails
    }
  }
</script>

<div class={itemClasses} role="option" aria-selected={isSelected}>
  <div class="node-header">
    <span class="node-id">{node.id}</span>
    {#if node.metadata?.tags && node.metadata.tags.length}
      <span class="node-tags">[{node.metadata.tags.join(', ')}]</span>
    {/if}
    {#if node.metadata?.author}
      <span class.node-author>by: {node.metadata.author}</span>
    {/if}
    {#if node.metadata?.timestamp}
      <span class="node-timestamp">{formatDate(node.metadata.timestamp)}</span>
    {/if}
  </div>

  {#if !isCollapsed}
    <div class="node-content">
      {#each node.content || [] as contentItem, i (contentItem.type + i)}
        {#if contentItem.type === 'text'}
          <div class="content-text">{@html contentItem.value}</div>
        {:else if contentItem.type === 'code'}
          <pre class="content-code"><code>{contentItem.value}</code></pre>
        {:else}
          <div class="content-unknown">Unknown content type</div>
        {/if}
      {/each}
    </div>
  {/if}
</div>

<style>
  .node-item {
    border: 1px solid var(--border-color, #ccc);
    padding: 0.5em;
    margin-bottom: 0.5em;
    border-radius: 4px;
    background-color: var(--item-bg, #fff);
    cursor: default;
  }

  .node-header {
    display: flex;
    gap: 0.75em; /* Spacing between header elements */
    font-size: 0.9em;
    color: var(--text-muted-color, #555);
    margin-bottom: 0.5em;
    padding-bottom: 0.5em;
    border-bottom: 1px solid var(--border-color-light, #eee);
    align-items: center; /* Vertically align items in header */
    flex-wrap: wrap; /* Allow header items to wrap on small screens */
  }

  .node-id {
    font-weight: bold;
    color: var(--text-color, #333);
  }

  .node-tags,
  .node-author,
  .node-timestamp {
    font-size: 0.85em;
    background-color: var(--item-bg-subtle, #f7f7f7);
    padding: 0.1em 0.4em;
    border-radius: 3px;
  }

  .node-content {
    padding-top: 0.5em;
  }

  .content-text :global(h1), .content-text :global(h2), .content-text :global(h3) {
    margin-top: 0.5em;
    margin-bottom: 0.25em;
  }
  .content-text :global(p) {
    margin-top: 0;
    margin-bottom: 0.5em;
  }
  .content-text :global(img) {
    max-width: 100%;
    height: auto;
    border-radius: 3px;
  }

  .content-code {
    background-color: var(--code-bg, #f4f4f4);
    border: 1px solid var(--border-color-light, #eee);
    padding: 0.5em;
    border-radius: 4px;
    overflow-x: auto;
    font-family: monospace;
  }

  .node-item.selected {
    border-color: var(--selected-border-color, blue);
    box-shadow: 0 0 5px var(--selected-shadow-color, rgba(0,0,255,0.5));
  }

  .node-item.active {
    background-color: var(--active-bg-color, #e6f7ff);
  }

  .node-item.collapsed .node-content {
    display: none;
  }
</style>
