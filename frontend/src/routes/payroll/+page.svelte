<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  onMount(() => {
    goto('/payroll/payslips');
  });
</script>

<div class="flex items-center justify-center h-full">
  <div class="animate-pulse text-slate-400">Chargement...</div>
</div>



