<script>
  import { onMount } from 'svelte';
  import '../app.css';
  import NodeList from '$lib/NodeList.svelte';
  let nodes = [];
  let error = null;
  let selectedNodes = new Set();

  async function loadNodes() {
    try {
      console.log('window.api:', window.api);
      if (!window.api || !window.api.listNodes) {
        throw new Error('window.api.listNodes is not available');
      }
      nodes = await window.api.listNodes();
      console.log('Nodes received:', nodes);
    } catch (err) {
      error = err.message;
      console.error('Load nodes error:', err);
    }
  }

  function handleCommand(event) {
    const { cmd } = event.detail;
    const [action, ...args] = cmd.split(' ');
    if (action === 'select' && args[0]) {
      const nodeId = args[0];
      if (nodes.some(n => n.id === nodeId)) {
        selectedNodes.has(nodeId) ? selectedNodes.delete(nodeId) : selectedNodes.add(nodeId);
        selectedNodes = new Set(selectedNodes);
      }
    }
  }

  onMount(() => {
    loadNodes();
    return () => {};
  });
</script>

<main>
  {#if error}
    <p style="color: red;">Error: {error}</p>
  {/if}
  <NodeList {nodes} {selectedNodes} />
</main>

<style>
  main {
    font-family: 'IBM Plex Mono', monospace;
    background: #000;
    color: #0f0;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
  }
</style>
