<!-- src/lib/components/StatusBar.svelte -->
<script>
  import { statusEvents } from '../stores/statusEvents';
</script>

<div class="status-bar">
  <h3>Status</h3>
  <ul>
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
  }
</style>
