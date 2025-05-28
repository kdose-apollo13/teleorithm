<script>
  import { createEventDispatcher, onMount, afterUpdate } from 'svelte';

  export let node;
  export let filter;
  export let selected = false; // Is this item currently focused via keyboard in NodeList?
  export let active = false;   // Is this the "globally" active/selected node?

  let collapsed = false;
  const dispatch = createEventDispatcher();
  let itemElement; // bind:this for the main div

  // When 'selected' (focused by NodeList keyboard nav), this item should be focusable.
  afterUpdate(() => {
    if (selected && itemElement) {
      itemElement.focus();
    }
  });

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

  function toggleCollapseInternal(event) {
    event.stopPropagation(); // Prevent click on button from also triggering item click
    collapsed = !collapsed;
    dispatch('togglecollapse', { id: node.id, collapsed });
  }

  // This is the primary action for the item itself (e.g., making it the "active" node)
  function handleClick() {
    dispatch('select', node.id);
  }

  // A11y: Keyboard handler for the item itself
  function handleItemKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick(); // Dispatch 'select'
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
    transition: background-color 0.2s ease;
    outline: none; 
  }
  .node-item.selected:focus-visible, /* Combined state for keyboard focus */
  .node-item:focus-visible { 
    box-shadow: 0 0 0 2px blue; /* Visible focus outline */
    border-color: blue;
  }
  .node-item.active {
    background-color: #e0e0ff;
    border-color: #a0a0ff;
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
  }
  .metadata {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
  }
  .content-items {
    padding-left: 15px;
    border-left: 2px solid #eee;
    margin-top: 10px;
  }
  .content-items .content-text { margin-bottom: 0.5em; }
  .content-items .content-code {
    background-color: #f4f4f4;
    padding: 0.5em;
    border-radius: 4px;
    overflow-x: auto;
    margin-bottom: 0.5em;
  }
  .content-items img, .content-items video {
    max-width: 90%;
    height: auto;
    display: block;
    margin-bottom: 0.5em;
  }
</style>

<div
  bind:this={itemElement}
  class="node-item"
  class:selected
  class:active
  role="option"
  aria-selected={active.toString()} tabindex={selected ? 0 : -1}      on:click={handleClick}
  on:keydown={handleItemKeydown}     >
  <h2>
    <span>{node.id}</span>
    <button
      class="toggle-button"
      on:click={toggleCollapseInternal}
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
            <img src={item.value} alt={item.metadata?.altText || `Image content for ${node.id}`} />
          {:else if item.type === 'video'}
            <video src={item.value} controls>
              <track kind="captions" srclang="en" src={item.metadata?.captionSrc || ""} label={item.metadata?.captionLabel || "English Captions"} />
              Your browser does not support the video tag.
            </video> {/if}
        {/if}
      {/each}
    </div>
  {/if}
</div>
