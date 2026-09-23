<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";
  import { page } from "$app/state";

  const tabs = [
    { id: 'register', label: 'Suivi', icon: 'clipboard-list', path: hr('/attendance/register') },
    { id: 'config', label: 'Planning', icon: 'calendar-days', path: hr('/attendance/config') },
    { id: 'policies', label: 'Modèles', icon: 'layout-template', path: hr('/attendance/policies') },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: hr('/attendance/settings') },
  ];

  const activeTabId = $derived.by(() => tabs.find(t => page.url.pathname.startsWith(t.path))?.id ?? 'register');
</script>

<div class="border-b border-slate-100 px-4 flex items-center justify-between">
  <NavTabs {tabs} activeId={activeTabId} variant="underline" />
</div>
