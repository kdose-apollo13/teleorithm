<script>
  import { createEventDispatcher } from 'svelte';

  export let inputElement = null; // For parent to bind if needed (e.g., for focusing)
  let command = '';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    // Runtime Debug: Check if this is called
    console.log('CommandLine.svelte: handleSubmit triggered with command:', command);
    if (command.trim() === '') return; // Optional: don't dispatch empty commands

    dispatch('command', command);
    command = ''; // Clear the input
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
