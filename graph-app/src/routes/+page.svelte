<script>
  import NodeList from '$lib/NodeList.svelte';
  import CommandLine from '$lib/CommandLine.svelte';
  import '../app.css';

  let nodes = [];

  window.api.listNodes().then((loadedNodes) => {
    nodes = loadedNodes;
  });

  function handleCommand(event) {
    const command = event.detail;
    console.log(`Command received: ${command}`);
    // TODO: Parse and execute the command
  }
</script>

<style>
  .container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden; /* Prevent body scrolling */
  }

  .node-list-container {
    flex: 1; /* Use flex: 1 for better sizing */
    overflow-y: auto;
    min-height: 0; /* Prevent flex overflow */
  }

  .cli-container {
    padding: 1rem;
    border-top: 1px solid #ccc;
    flex-shrink: 0; /* Prevent CLI from shrinking */
  }
</style>

<main>
    <div class="container">
      <div class="node-list-container">
        <NodeList {nodes} />
      </div>
      <div class="cli-container">
        <CommandLine on:command={handleCommand} />
      </div>
    </div>
</main>
