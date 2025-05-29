<!-- src/lib/NodeItem.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  import { shouldShow } from './filterUtils.js';

  export let node;
  export let filter;
  export let isFocused = false;
  export let isSelected = false;
  export let isCollapsed = false;

  const dispatch = createEventDispatcher();
</script>

<div
  class="node-item"
  class:selected={isFocused}
  class:active={isSelected}
  class:collapsed={isCollapsed}
  on:click={() => dispatch('select')}
  role="option"
  aria-selected={isSelected}
>
  <h2>
    {node.id}
    <button on:click|stopPropagation={() => dispatch('toggleCollapse')}>
      {isCollapsed ? '▶' : '▼'}
    </button>
  </h2>
  {#if !isCollapsed}
    {#each node.content as item}
      {#if shouldShow(filter, item.type, item.metadata?.level)}
        {#if item.type === 'text'}
          <div class="content-text">{@html item.value}</div>
        {:else if item.type === 'code'}
          <pre class="content-code"><code>{item.value}</code></pre>
        {/if}
      {/if}
    {/each}
  {/if}
</div>

<style>
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
  h2 {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0;
  }
  button {
    background: none;
    border: none;
    color: #0f0;
    cursor: pointer;
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
