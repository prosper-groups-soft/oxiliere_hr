<script lang="ts">
  import type { RecruitmentCampaign } from '../../types/types';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { hr } from '@/hr/constants/navigation/navigation';
  import { cn } from '@/hr/utilities/common/css';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import * as Tabs from '@/components/ui/tabs';
  import { Button } from "@/components/ui/button";
  import { Badge } from "@/components/ui/badge";
  import CampaignSheet from "@/hr/modules/recruitment/components/shared/sheets/campaign/CampaignSheet.svelte";
  import CandidateSheet from "@/hr/modules/recruitment/components/shared/sheets/candidate/CandidateSheet.svelte";
  import { STATUS_CONFIG } from '@/hr/modules/recruitment/constants/recruitment';


  let { campaign } = $props<{ campaign: RecruitmentCampaign }>();
  
  let isEditSheetOpen = $state(false);
  let isAddCandidateSheetOpen = $state(false);

  const basePath = $derived(hr(`/recruitment/${campaign.id}`));

  const TABS = $derived([
    { id: 'overview', label: 'Vue d\'ensemble', path: `${basePath}`, icon: 'layout-dashboard' },
    { id: 'candidates', label: 'Candidats', path: `${basePath}/candidates`, icon: 'list' },
    { id: 'pipeline', label: 'Pipeline', path: `${basePath}/pipeline`, icon: 'kanban' },
    { id: 'scheduler', label: 'Planification', path: `${basePath}/scheduler`, icon: 'calendar' }
  ]);

  /**
   * Reactive value for the active tab ID based on the current path.
   */
  const activeTabId = $derived.by(() => {
    const path = page.url.pathname.replace(/\/$/, '') || basePath;
    
    // Exact match first, then partial
    const exactTab = TABS.find(t => t.path === path);
    if (exactTab) return exactTab.id;

    // Handle nested candidate profiles
    if (path.includes(`${basePath}/candidates`)) return 'candidates';
    
    const currentTab = TABS.find(t => path.includes(t.path) && t.path !== basePath);
    return currentTab ? currentTab.id : 'overview';
  });

  const handleTabChange = (value: string) => {
    const targetTab = TABS.find(t => t.id === value);
    if (targetTab) {
      goto(targetTab.path);
    }
  };

  // --- Sliding Indicator Logic ---
  let tabElements = $state<Record<string, HTMLElement | null>>({
    overview: null,
    pipeline: null,
    candidates: null,
    scheduler: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });


  const config = $derived(STATUS_CONFIG[campaign.status] || STATUS_CONFIG.DRAFT);
</script>


{#snippet TabTrigger(tab: typeof TABS[0])}
  <Tabs.Trigger 
    value={tab.id} 
    bind:ref={tabElements[tab.id]}
    class={cn(
      "relative flex items-center gap-2 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-1 pb-2.5 outline-none focus-visible:ring-0",
      "group cursor-pointer text-slate-800",
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="group-data-[state=active]:text-primary" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>  
  </Tabs.Trigger>
{/snippet}


<div class="bg-white border-b border-slate-100 px-6 pt-3 pb-0 pr-7 flex flex-col gap-3.5">
  <!-- Header of the campaign -->
  <div class="flex items-start justify-between">
    <div class="space-y-1.5">
      <div class="flex items-center gap-2">
        <h1 class="text-[1rem] font-bold text-slate-900 tracking-tight">{campaign.title}</h1>
        <Badge variant="outline" class={cn(
          "px-2 py-0.5 rounded-full border text-[0.62rem] font-bold uppercase tracking-wider shadow-none transition-all flex items-center gap-1.5",
          config.bg, config.color, config.border
        )}>
          <span class={cn("h-1.5 w-1.5 rounded-full", config.dot, campaign.status === 'OPEN' ? "animate-pulse" : "")}></span>
          {config.label}
        </Badge>
      </div>
      <div class="flex items-center gap-5 text-slate-500">
        <span class="flex items-center gap-1.5 text-[0.825rem]">
          <AppIcon name="map-pin" size={18} class="text-slate-400" /> {campaign.location}
        </span>
        <span class="flex items-center gap-1.5 text-[0.825rem]">
          <AppIcon name="briefcase" size={18} class="text-slate-400" /> {campaign.jobNames?.join(', ') || 'Non spécifié'}
        </span>
        <span class="flex items-center gap-1.5 text-[0.825rem]">
          <AppIcon name="users" size={18} class="text-slate-400" /> 
          <span class="font-medium text-slate-700 text-[0.85rem]">{campaign.metrics.inPipeline}</span> / {campaign.targetHires} embauches
        </span>
      </div>
    </div>
    
    <div class="flex gap-2.5">
      <Button 
        variant="outline" 
        size="sm" 
        class="h-7.5 px-4 text-slate-700 border-slate-200 hover:bg-slate-50 text-[0.84rem] shadow-fine"
        onclick={() => isEditSheetOpen = true}
      >
        <AppIcon name="edit" size={17} class="text-slate-500" />
        Editer campagne
      </Button>
      <Button 
        size="sm" 
        class="h-7.5 px-4 bg-primary hover:bg-primary/90 text-white text-[0.84rem] shadow-fine"
        onclick={() => isAddCandidateSheetOpen = true}
      >
        <AppIcon name="plus" size={17} />
        Ajouter candidat
      </Button>
    </div>
  </div>

  <!-- Tabs Navigation -->
  <div class="flex items-center overflow-x-auto no-scrollbar">
    <Tabs.Root value={activeTabId} onValueChange={handleTabChange} class="w-full">
      <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none">
        {#each TABS as tab}
          {@render TabTrigger(tab)}
        {/each}

        <!-- Sliding Indicator -->
        <div class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10" style={indicatorStyle}></div>
      </Tabs.List>
    </Tabs.Root>
  </div>
</div>


<CampaignSheet bind:open={isEditSheetOpen} {campaign} />
<CandidateSheet bind:open={isAddCandidateSheetOpen} campaignId={campaign.id} />

