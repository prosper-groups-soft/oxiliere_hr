<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";

  let { tabs, activeTab, onTabChange }: { tabs: { id: string; label: string; icon: string }[]; activeTab: string; onTabChange: (value: string) => void } = $props();

  const navTabs = $derived(tabs.map(t => ({ ...t, path: '' })));
</script>

<NavTabs tabs={navTabs} activeId={activeTab} variant="pill" onChange={onTabChange} />
