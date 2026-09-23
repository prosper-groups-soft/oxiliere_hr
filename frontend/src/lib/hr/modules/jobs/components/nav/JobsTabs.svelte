<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";
  import { page } from "$app/state";

  const tabs = [
    { id: 'chart', label: 'Organigramme', icon: 'network', path: hr('/jobs/chart') },
    { id: 'careers', label: 'Carrières', icon: 'graduation-cap', path: hr('/jobs/careers') },
    { id: 'mobility', label: 'Mobilité', icon: 'refresh-cw', path: hr('/jobs/mobility') },
  ];

  const activeId = $derived.by(() => tabs.find(t => page.url.pathname.replace(/\/$/, '').includes(t.path))?.id ?? 'chart');
</script>

<div class="bg-white border-b border-slate-100 mb-2 mt-1.5 px-4">
  <div class="flex items-center justify-between">
    <NavTabs {tabs} activeId={activeId} variant="underline" />
    <div></div>
  </div>
</div>
