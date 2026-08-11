<script lang="ts">
  import * as Tabs from '@/components/ui/tabs';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { goto } from '$app/navigation';
  import { cn } from '@/utilities/common/css';

  /**
   * EmployeeProfileTabs — Navigation par onglets du profil employé.
   * SRP : ce composant gère UNIQUEMENT la navigation (routing + indicateur animé).
   * L'onglet actif est une prop (calculée par le layout), pas un parsing d'URL ici.
   */

  interface TabDef {
    id: string;
    label: string;
    icon: string;
    count?: number;
  }

  let {
    employeeId,
    activeTabId,
    counts,
  }: {
    employeeId: string | number;
    activeTabId: string;
    counts: { education?: number; documents?: number };
  } = $props();

  const TABS: TabDef[] = $derived.by(() => [
    { id: 'profile', label: 'Profil', icon: 'user' },
    { id: 'contract', label: 'Contrat', icon: 'briefcase' },
    { id: 'education', label: 'Éducation', icon: 'graduation-cap', count: counts.education },
    { id: 'family', label: 'Famille', icon: 'users' },
    { id: 'account', label: 'Accès', icon: 'shield' },
    { id: 'documents', label: 'Documents', icon: 'files', count: counts.documents },
    { id: 'timeline', label: 'Parcours', icon: 'clock' },
  ]);

  function handleTabChange(value: string) {
    const baseUrl = `/employees/${employeeId}`;
    const targetUrl = value === 'profile' ? baseUrl : `${baseUrl}/${value}`;
    goto(targetUrl);
  }

  // --- Indicateur animé (ResizeObserver pour robustesse au resize) ---
  // Pré-initialisé à null : bind:ref exige null (pas undefined), sinon
  // props_invalid_value (Cannot do bind:ref={undefined} quand ref a une valeur de repli).
  let tabElements = $state<Record<string, HTMLElement | null>>({
    profile: null,
    contract: null,
    education: null,
    family: null,
    account: null,
    documents: null,
    timeline: null
  });
  let indicatorStyle = $state('');

  function updateIndicator() {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  }

  $effect(() => {
    updateIndicator();

    const observer = new ResizeObserver(() => updateIndicator());
    // Observer tous les éléments d'onglets pour repositionner au resize
    for (const el of Object.values(tabElements)) {
      if (el) observer.observe(el);
    }
    return () => observer.disconnect();
  });
</script>


{#snippet TabTrigger(tab: TabDef)}
  <Tabs.Trigger
    value={tab.id}
    bind:ref={tabElements[tab.id]}
    class={cn(
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-1 pb-2.5 outline-none focus-visible:ring-0",
      "font-bold group cursor-pointer text-slate-800",
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="text-slate-500 group-data-[state=active]:text-primary" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>

    {#if tab.count}
      <span class="flex h-4.5 w-4.5 items-center justify-center rounded-full bg-slate-100 px-1.5 text-[0.7rem] font-bold group-data-[state=active]:bg-primary group-data-[state=active]:text-white transition-colors">
        {tab.count}
      </span>
    {/if}
  </Tabs.Trigger>
{/snippet}


<Tabs.Root value={activeTabId} onValueChange={handleTabChange} class="w-full">
  <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none">
    {#each TABS as tab}
      {@render TabTrigger(tab)}
    {/each}

    <!-- Sliding Indicator -->
    <div
      class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10"
      style={indicatorStyle}
    ></div>
  </Tabs.List>
</Tabs.Root>
