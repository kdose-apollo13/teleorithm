<script>
  import CommandLine from '../../CommandLine.svelte'; // Path to your actual component

  // This prop will store the detail of the last dispatched 'command' event.
  // It's exported so the test can access its value via the component instance.
  export let lastDispatchedCommandDetail = null;

  function handleCommandDispatch(event) {
    lastDispatchedCommandDetail = event.detail;
  }
</script>

<CommandLine on:command={handleCommandDispatch} />
