<script>
  import { createEventDispatcher, afterUpdate } from 'svelte';

  export let node;
  export let filter;
  export let selected = false; // True if this item is the one NodeList has "focused" via j/k
  export let active = false;   // True if this item is the globally "activated" node

  let collapsed = false;
  const dispatch = createEventDispatcher();
  let itemElement;

  // For parent (NodeList) to call via 'm' key
  export function programmaticToggleCollapse() {
    collapsed = !collapsed;
    // Optionally dispatch an event if the parent needs to know about the collapse state change
    // dispatch('itemcollapsed', { id: node.id, collapsed });
  }

  function shouldShow(type, level) {
    if (!filter) return true;
    const filterUpper = filter.toUpperCase();
    const typeUpper = type.toUpperCase().charAt(0);
    const parsedLevel = parseInt(level, 10);
    if (isNaN(parsedLevel)) return false;
    let i = 0;
    while (i < filterUpper.length) {
        const char = filterUpper[i];
        if (['T', 'C', 'I', 'V'].includes(char)) {
            let currentType = char;
            let levels = '';
            i++;
            while (i < filterUpper.length && !isNaN(parseInt(filterUpper[i], 10))) {
                levels += filterUpper[i];
                i++;
            }
            if (currentType === typeUpper) {
                if (levels === '') return true;
                if (levels.includes(parsedLevel.toString())) return true;
            }
        } else {
            i++;
        }
    }
    return false;
  }

  function handleItemClick() {
    dispatch('select', node.id); // Notify parent (NodeList) of activation
  }

  function handleToggleButtonClick(event) {
    event.stopPropagation(); // Prevent item click when button is clicked
    programmaticToggleCollapse();
  }

  // If item itself gets focus (e.g. tabbing, if it were made focusable), handle Enter/Space for activation
  function handleItemKeydown(event) {
    if (selected && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      handleItemClick();
    }
  }
</script>

<style>
  .node-item {
    border: 1px solid #ccc;
    margin-bottom: 10px;
    border-radius: 5px;
    padding: 10px;
    cursor: pointer;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    outline: none;
  }
  .node-item.selected { /* Visual cue for NodeList's internal j/k focus */
    border-color: blue;
    box-shadow: 0 0 3px rgba(0, 0, 200, 0.4);
  }
  .node-item.active { /* Visual cue for the globally selected/active node */
    background-color: #e0e0ff;
    border-color: #9090ff;
  }
  /* If the item itself could be tab-focused (it's -1 now) */
  .node-item:focus-visible {
    outline: 2px solid orange; /* Distinct from 'selected' */
  }
  h2 {
    margin-top: 0;
    font-size: 1.2em;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .toggle-button {
    background: none;
    border: none;
    font-size: 1.2em;
    cursor: pointer;
    padding: 0.2em 0.5em;
    color: #333;
  }
  .toggle-button:hover {
    color: #000;
  }
  .metadata, .content-items { /* Styles from previous version */ }
</style>

<div
  bind:this={itemElement}
  class="node-item"
  class:selected
  class:active
  role="option"
  aria-selected={active.toString()}
  tabindex="-1" on:click={handleItemClick}
  on:keydown={handleItemKeydown} >
  <h2>
    <span>{node.id}</span>
    <button
      class="toggle-button"
      on:click={handleToggleButtonClick}
      aria-expanded={!collapsed}
      aria-label="Toggle content for {node.id}"
    >
      {collapsed ? '▶' : '▼'}
    </button>
  </h2>

  {#if !collapsed}
    <div class="metadata">
      <p><strong>Author:</strong> {node.metadata?.author || 'N/A'}</p>
      <p><strong>Timestamp:</strong> {node.metadata?.timestamp || 'N/A'}</p>
      <p><strong>Tags:</strong> {node.metadata?.tags?.join(', ') || 'N/A'}</p>
    </div>
    <div class="content-items">
      {#each node.content as item}
        {#if shouldShow(item.type, item.metadata.level)}
          {#if item.type === 'text'}
            <div class="content-text">{@html item.value}</div>
          {:else if item.type === 'code'}
            <pre class="content-code"><code>{item.value}</code></pre>
          {:else if item.type === 'image'}
            <img src={item.value} alt={item.metadata?.altText || `Image for ${node.id}`} />
          {:else if item.type === 'video'}
            <video src={item.value} controls>
              <track kind="captions" srclang="en" src={item.metadata?.captionSrc || ""} label={item.metadata?.captionLabel || "English Captions"} />
              Your browser does not support the video tag.
            </video>
          {/if}
        {/if}
      {/each}
    </div>
  {/if}
</div>
