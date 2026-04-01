<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(() => {
    goto('/jobs/chart', { replaceState: true });
  });
</script>


<div class="h-full flex items-center justify-center">
  <div class="animate-pulse text-slate-300">Redirection...</div>
</div>

