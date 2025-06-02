<!-- src/lib/components/StatusBar.svelte -->
<script>
  import { statusEvents } from '$lib/stores/statusEvents';
  import { afterUpdate } from 'svelte';

  let eventList;
  afterUpdate(() => {
    if (eventList) {
      eventList.scrollTop = eventList.scrollHeight;
    }
  });
</script>

<div class="status-bar">
  <h3>Status</h3>
  <ul bind:this={eventList}>
    {#each $statusEvents as event}
      <li>{event}</li>
    {/each}
  </ul>
</div>

<style>
  .status-bar {
    width: 100%;
    padding: 5px;
    background: #e8e8e8;
    max-height: 100px;
    overflow-y: auto;
    border-top: 1px solid #ccc;
  }
  ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  li {
    font-size: 12px;
  }
</style>
