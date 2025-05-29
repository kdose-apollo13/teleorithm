<script>
  import CommandLine from '$lib/CommandLine.svelte';

  // This prop will be a callback function provided by the test.
  // It's a function, so its default is a no-op function.
  export let onCommandDispatched = (detail) => {};

  // No longer need to export lastDispatchedCommandDetail
  // export let lastDispatchedCommandDetail = null;

  function handleCommandDispatch(event) {
    // Call the callback prop with the event detail
    onCommandDispatched(event.detail);
  }
</script>

<CommandLine on:command={handleCommandDispatch} />
