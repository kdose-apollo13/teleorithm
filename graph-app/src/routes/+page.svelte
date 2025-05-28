<script>
  import { onMount } from 'svelte';
  import NodeList from '$lib/NodeList.svelte';
  let nodes = [];
  let error = null;

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

  onMount(() => {
    loadNodes();
    return () => {};
  });
</script>

<main>
  {#if error}
    <p style="color: red;">Error: {error}</p>
  {/if}
  <NodeList {nodes} />
</main>

<style>
  main {
    font-family: 'IBM Plex Mono', monospace;
    background: #000;
    color: #0f0;
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden; /* Prevent outer scrollbar */
    display: flex;
    flex-direction: column;
  }
</style>
