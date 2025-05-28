<script>
  import NodeList from '$lib/NodeList.svelte';
  import CommandLine from '$lib/CommandLine.svelte';
  import { onMount } from 'svelte';
  import '../app.css'; // Make sure global styles are applied

  let nodes = [];
  let selectedNodeId = null; // Still useful to know the "active" node
  let filter = 'TCIV'; // Default filter

  onMount(async () => {
      try {
        const loadedNodes = await window.api.listNodes();
        nodes = loadedNodes;
        if (nodes.length > 0) {
            selectedNodeId = nodes[0].id; // Set initial "active" node
        }
      } catch (error) {
          console.error("Failed to load nodes:", error);
          nodes = [];
      }
  });

  function handleCommand(event) {
    const command = event.detail.trim();
    console.log(`Command received: ${command}`);

    if (command.toLowerCase().startsWith('filter ')) {
      filter = command.substring(7).toUpperCase() || 'TCIV'; // Default if empty
      console.log(`Filter set to: ${filter}`);
    } else {
      console.log("Unknown command:", command);
    }
  }

  function handleSelect(event) {
    selectedNodeId = event.detail;
    console.log("Active Node Set To:", selectedNodeId);
  }

</script>

<style>
  .page-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden; /* Important: Prevents outer scrollbar */
  }

  .node-list-container {
    flex: 1; /* List takes up available space */
    overflow-y: auto; /* List itself scrolls */
    padding: 10px; /* Add some padding around the list */
  }

  .cli-container {
    padding: 0.5rem 1rem;
    border-top: 1px solid #ccc;
    background-color: #eee;
    flex-shrink: 0;
  }
</style>

<div class="page-container">
  <div class="node-list-container">
    <NodeList {nodes} {filter} {selectedNodeId} on:select={handleSelect} />
  </div>
  <div class="cli-container">
    <CommandLine on:command={handleCommand} />
  </div>
</div>
