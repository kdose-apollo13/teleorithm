<!-- src/lib/components/CliBar.svelte -->
<script>
  import { statusEvents } from '$lib/stores/statusEvents';
  let inputValue = '';

  function handleInput(event) {
    if (event.key === 'Enter' && inputValue) {
      statusEvents.update(events => [
        ...events,
        `CLI command: ${inputValue} at ${new Date().toLocaleTimeString()}`
      ]);
      inputValue = '';
    }
  }
</script>

<div class="cli-bar">
  <h3>CLI</h3>
  <input
    type="text"
    bind:value={inputValue}
    on:keypress={handleInput}
    placeholder="Type commands here"
  />
</div>

<style>
  .cli-bar {
    width: 100%;
    padding: 10px;
    background: #f8f8f8;
    border-top: 1px solid #ccc;
  }
  input {
    width: 100%;
    padding: 5px;
  }
</style>
