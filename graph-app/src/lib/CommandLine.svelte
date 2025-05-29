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
    background: #333333; /* Slightly lighter dark for contrast */
    color: #80ffea; /* Pastel cyan */
    border: 1px solid #b3ff99; /* Pastel lime border */
    border-radius: 6px; /* Rounded edges */
    padding: 0.75rem 1rem; /* Sensible padding */
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    transition: box-shadow 0.2s ease;
  }
  .cli-input:focus {
    outline: none;
    box-shadow: 0 0 6px #ff80bf; /* Pastel pink glow on focus */
  }
</style>
