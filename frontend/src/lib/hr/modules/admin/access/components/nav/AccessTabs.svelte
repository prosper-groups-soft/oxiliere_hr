<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import type { TabDef } from "@/hr/navigation/types";

  let { tabs, activeTabId, onTabChange }: { tabs: TabDef[]; activeTabId: string; onTabChange: (id: string) => void } = $props();
</script>

<NavTabs {tabs} {activeId: activeTabId} {onChange: onTabChange} variant="underline" />
