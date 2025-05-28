<script>
  import NodeItem from './NodeItem.svelte';
  import { createEventDispatcher, onMount, onDestroy, tick } from 'svelte';

  export let nodes = [];
  export let filter = 'TCIV';
  export let selectedNodeId = null;

  let focusedIndex = 0;
  const dispatch = createEventDispatcher();
  let listElement; // To bind to the container div

  function handleKeydown(event) {
    if (!nodes || nodes.length === 0) return;

    let newIndex = focusedIndex;

    if (event.key === 'j') {
        event.preventDefault(); // Prevent page scroll
        newIndex = Math.min(focusedIndex + 1, nodes.length - 1);
    } else if (event.key === 'k') {
        event.preventDefault(); // Prevent page scroll
        newIndex = Math.max(focusedIndex - 1, 0);
    } else if (event.key === 'Enter') {
        event.preventDefault();
        dispatch('select', nodes[focusedIndex].id);
        // Toggle active state in NodeItem via its active prop
    } else if (event.key === ' ') {
        event.preventDefault();
        // We need a way to tell the focused NodeItem to toggle collapse.
        // This is tricky without direct component refs. We might need
        // to manage collapse state here or use a different approach.
        // For now, let's leave this, but acknowledge it needs work.
        console.log("Space pressed - collapse/expand TBD");
    }

    if (newIndex !== focusedIndex) {
        focusedIndex = newIndex;
        ensureVisible(focusedIndex);
    }
  }

  // Function to scroll the focused item into view
  async function ensureVisible(index) {
      await tick(); // Wait for DOM to update
      const items = listElement?.querySelectorAll('.node-item');
      if (items && items[index] && (typeof items[index].scrollIntoView === 'function')) {
          items[index].scrollIntoView({
              behavior: 'smooth',
              block: 'nearest', // 'start', 'center', 'end', or 'nearest'
          });
      }
  }

  function handleItemSelect(event) {
      dispatch('select', event.detail);
      // Update focusedIndex based on the clicked item's ID
      focusedIndex = nodes.findIndex(n => n.id === event.detail);
  }


  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    // Set initial focus if a node is selected
    if (selectedNodeId) {
        focusedIndex = nodes.findIndex(n => n.id === selectedNodeId);
        if (focusedIndex === -1) focusedIndex = 0; // Default to first if not found
    }
    // Set focus to the list itself so it can receive key events
    listElement?.focus();
  });

  onDestroy(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
</script>

<style>
    .node-list {
        padding: 10px;
        outline: none; /* Remove default focus outline if desired */
    }
</style>

<div
    class="node-list"
    role="listbox"
    aria-label="Node List"
    tabindex="0"
    bind:this={listElement}
    on:focus={() => listElement?.focus()}
>
  {#if nodes.length > 0}
      {#each nodes as node, index (node.id)}
        <NodeItem
          {node}
          {filter}
          selected={index === focusedIndex}
          active={node.id === selectedNodeId}
          on:select={handleItemSelect}
        />
      {/each}
  {:else}
      <p>Loading nodes or no nodes found...</p>
  {/if}
</div>
