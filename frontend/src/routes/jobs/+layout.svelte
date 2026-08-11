<script lang="ts">
  import JobsTabs from "@/features/jobs/components/nav/JobsTabs.svelte";
  
  let { children } = $props();
</script>


<svelte:head>
  <title>Oxiliere HR - Poste & Org.</title>
</svelte:head>


<div class="h-full flex flex-col bg-white overflow-hidden">
  <!-- Tabbed Header -->
  <JobsTabs />

  <!-- Main Content Area -->
  <div class="flex-1 overflow-hidden">
    {@render children()}
  </div>
</div>

