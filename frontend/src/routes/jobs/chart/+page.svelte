<script lang="ts">
  import OrgCanvas from "@/features/jobs/components/org-chart/OrgCanvas.svelte";
  import OrgDrawer from "@/features/jobs/components/org-chart/OrgDrawer.svelte";
  import type { Department } from "@/features/jobs/types/types";
  import { jobsStore } from "$lib/features/jobs/stores/jobs.svelte";

  let isDrawerOpen = $state(false);
  let selectedDept = $state<Department | null>(null);

  function handleSelect(dept: Department) {
    selectedDept = dept;
    isDrawerOpen = true;
  }

  // Sync drawer state back to store for OrgNode highlights/animations
  $effect(() => {
    if (!isDrawerOpen) {
      jobsStore.setDept(null);
    }
  });
</script>


<div class="h-full flex flex-col bg-white overflow-hidden relative">
  <!-- Content: The Interactive Org Chart -->
  <OrgCanvas onSelect={handleSelect} />

  <!-- Selection Drawer -->
  <OrgDrawer bind:open={isDrawerOpen} department={selectedDept} />
</div>

