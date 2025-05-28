<script>
  import { createEventDispatcher } from 'svelte';

  let command = '';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    dispatch('command', command);
    command = '';
  }
</script>

<style>
  .cli-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
</style>

<form on:submit|preventDefault={handleSubmit}>
  <input
    type="text"
    class="cli-input"
    placeholder="Enter command..."
    bind:value={command}
  />
</form>
