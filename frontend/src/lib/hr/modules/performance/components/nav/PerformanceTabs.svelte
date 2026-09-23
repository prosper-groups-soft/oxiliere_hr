<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";
  import { page } from "$app/state";

  const tabs = [
    { id: 'campaigns', label: 'Campagnes', icon: 'flag', path: hr('/performance/campaigns') },
    { id: 'reviews', label: 'Évaluations', icon: 'file-text', path: hr('/performance/reviews') },
  ];

  const activeTabId = $derived.by(() => {
    const tab = tabs.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id ?? 'campaigns';
  });
</script>

<div class="bg-white border-b border-slate-100">
  <div class="px-5">
    <NavTabs {tabs} activeId={activeTabId} variant="underline" />
  </div>
</div>
