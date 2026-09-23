<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";
  import { page } from "$app/state";

  const tabs = [
    { id: 'accounts', label: 'Comptes', icon: 'wallet', path: hr('/banking/accounts') },
    { id: 'directory', label: 'Institutions', icon: 'bank', path: hr('/banking/directory') },
  ];

  const activeTabId = $derived.by(() => tabs.find(t => page.url.pathname.startsWith(t.path))?.id ?? 'accounts');
</script>

<div class="border-b border-slate-100 px-4 flex items-center justify-between">
  <NavTabs {tabs} activeId={activeTabId} variant="underline" />
</div>
