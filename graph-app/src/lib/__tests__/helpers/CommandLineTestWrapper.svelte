<script>
  import CommandLine from '../../CommandLine.svelte';

  export let lastDispatchedCommandDetail = null;
  export let commandLineInstance = null; // To access CommandLine's exported members if needed

  function handleCommandDispatch(event) {
    lastDispatchedCommandDetail = event.detail;
  }
</script>

<CommandLine on:command={handleCommandDispatch} bind:this={commandLineInstance} />
