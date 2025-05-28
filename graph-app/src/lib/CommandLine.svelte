<!-- src/lib/CommandLine.svelte -->
<script>
  import { createEventDispatcher } from 'svelte';
  export let inputElement;
  let command = '';
  const dispatch = createEventDispatcher();

  function handleSubmit(event) {
    if (event.key === 'Enter' && command.trim()) {
      dispatch('command', command.trim());
      command = '';
    }
  }
</script>

<style>
  .cli-input {
    width: 100%;
    padding: 0.5rem;
    background: #111;
    color: #0f0;
    border: 1px solid #333;
    font-family: 'IBM Plex Mono', monospace;
    box-sizing: border-box;
  }
</style>

<input
  type="text"
  class="cli-input"
  placeholder="Enter command..."
  bind:value={command}
  bind:this={inputElement}
  on:keydown={handleSubmit}
/>
