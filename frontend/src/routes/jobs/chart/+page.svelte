<script lang="ts">
  import OrgCanvas from "@/features/jobs/components/org-chart/OrgCanvas.svelte";
  import OrgDrawer from "@/features/jobs/components/org-chart/OrgDrawer.svelte";
  import type { OrgUnit } from "@/features/jobs/types/org.types";
  import { jobsStore } from "@/features/jobs/stores/jobs.svelte";

  let isDrawerOpen = $state(false);
  let selectedOrgUnit = $state<OrgUnit | null>(null);

  function handleSelect(unit: OrgUnit) {
    // Spread pour forcer une nouvelle référence d'objet
    // → Svelte détecte le changement de prop même si c'est le même ID
    selectedOrgUnit = { ...unit };
    isDrawerOpen = true;
  }

  // Sync drawer state back to store for OrgNode highlights/animations
  $effect(() => {
    if (!isDrawerOpen) {
      jobsStore.setOrgUnit(null);
    }
  });
</script>


<div class="h-full flex flex-col bg-white overflow-hidden relative">
  <!-- Content: The Interactive Org Chart -->
  <OrgCanvas onSelect={handleSelect} />

  <!-- Selection Drawer -->
  {#key selectedOrgUnit?.id}
    <OrgDrawer bind:open={isDrawerOpen} orgUnit={selectedOrgUnit} />
  {/key}
</div>

