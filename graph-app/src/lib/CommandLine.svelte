<!-- src/lib/CommandLine.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';

  export let inputElement;
  let command = '';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    if (command.trim()) {
      dispatch('command', command);
      command = '';
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
  <input
    bind:this={inputElement}
    type="text"
    class="cli-input"
    placeholder="Enter command..."
    bind:value={command}
    aria-label="Command input"
  />
</form>

<style>
  .cli-input {
    width: 100%;
    background: #111;
    color: #0f0;
    border: none;
    padding: 0.5rem;
    font-family: 'IBM Plex Mono', monospace;
  }
</style>
