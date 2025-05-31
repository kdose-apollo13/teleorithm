<!-- src/routes/+page.svelte -->
<script>
  import { graphData } from '$lib/stores/graphData';
  import Layout from '$lib/components/Layout.svelte';

  async function loadData() {
    const filePath = '/home/deo/teleorithm/publ/grafnav/graph.json';
    const data = await window.electronAPI.loadGraphData(filePath);
    if (data) {
      graphData.set(data);
    }
  }

  loadData();
</script>

<Layout />
