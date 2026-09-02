<script lang="ts">
  import { onMount } from 'svelte';
  import PayrollTabs from "@/features/payroll/components/nav/PayrollTabs.svelte";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";

  let { children } = $props();

  // Au chargement de toute page paie : si un run est déjà en cours côté backend,
  // l'onglet dynamique doit apparaître immédiatement.
  onMount(() => {
    payrollStore.syncActiveRunFromList().catch(console.error);
  });
</script>


<div class="flex flex-col h-full bg-white overflow-hidden">
  <PayrollTabs />

  <main class="flex-1 overflow-hidden relative bg-white">
    {@render children?.()}
  </main>
</div>

