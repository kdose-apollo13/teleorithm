<script>
  import { onMount } from 'svelte';
  export let nodes = [];
  let selectedIndex = 0;
  let selectedNodes = new Set();
  let collapsedNodes = new Set();

  function handleKeydown(event) {
    if (event.key === 'j' && selectedIndex < nodes.length - 1) {
      selectedIndex += 1;
    } else if (event.key === 'k' && selectedIndex > 0) {
      selectedIndex -= 1;
    } else if (event.key === 'Enter') {
      const nodeId = nodes[selectedIndex].id;
      selectedNodes.has(nodeId) ? selectedNodes.delete(nodeId) : selectedNodes.add(nodeId);
      selectedNodes = new Set(selectedNodes);
    } else if (event.key === ' ') {
      const nodeId = nodes[selectedIndex].id;
      collapsedNodes.has(nodeId) ? collapsedNodes.delete(nodeId) : collapsedNodes.add(nodeId);
      collapsedNodes = new Set(collapsedNodes);
    }
  }

  let listElement;
  onMount(() => {
    listElement.focus();
    return () => {};
  });
</script>

<svelte:window on:keydown={handleKeydown} />

<div
  class="node-list"
  bind:this={listElement}
  tabindex="0"
  role="listbox"
  aria-label="Node List"
>
  {#each nodes as node, index}
    <div
      class="node-item"
      class:selected={index === selectedIndex}
      class:active={selectedNodes.has(node.id)}
      class:collapsed={collapsedNodes.has(node.id)}
      role="option"
      aria-selected={index === selectedIndex}
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
</div>

<style>
  .node-list {
    flex: 1; /* Fill available space */
    overflow-y: auto; /* Inner scrollbar when needed */
    background: #111;
    color: #0f0;
    font-family: 'IBM Plex Mono', monospace;
    padding: 1rem;
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
