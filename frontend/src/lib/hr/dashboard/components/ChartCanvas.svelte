<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  Chart.register(...registerables);

  let { type = 'bar', data, options }: { type: 'bar' | 'line' | 'doughnut'; data: any; options?: any } = $props();
  let canvas: HTMLCanvasElement;
  let chart: Chart | null = null;

  onMount(() => {
    chart = new Chart(canvas, { type, data, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: type === 'doughnut' } }, ...options } });
    return () => chart?.destroy();
  });

  $effect(() => {
    if (chart && data) {
      chart.data = data;
      chart.update();
    }
  });
</script>

<div class="h-48"><canvas bind:this={canvas}></canvas></div>
