<script lang="ts">
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import CandidatesList from '@/features/recruitment/components/lists/CandidatesList.svelte';
  import { stageConfig } from '@/features/recruitment/stores/recruitment.svelte';
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { scale } from "svelte/transition";
  import { 
    type CandidateStage, 
    type CandidateSource 
  } from '@/features/recruitment/types/types';
  import { cn } from "@/utilities/common/css";
  import { Badge } from "@/components/ui/badge";

  const candidates = $derived(recruitmentStore.filteredCandidates);

  const stageOptions = [
    { value: 'SCREENING' as CandidateStage, label: 'Tri', icon: 'filter' },
    { value: 'SHORTLIST' as CandidateStage, label: 'Shortlist', icon: 'star' },
    { value: 'INTERVIEW' as CandidateStage, label: 'Entretien', icon: 'users' },
    { value: 'OFFER' as CandidateStage, label: 'Offre', icon: 'send' },
    { value: 'REJECTED' as CandidateStage, label: 'Rejeté', icon: 'x' }
  ];

  const priorityOptions = [
    { value: 'HIGH' as const, label: 'Urgente', color: 'text-red-500' },
    { value: 'MEDIUM' as const, label: 'Normale', color: 'text-amber-500' },
    { value: 'LOW' as const, label: 'Faible', color: 'text-emerald-500' }
  ];

  const sourceOptions = [
    { value: 'LINKEDIN' as CandidateSource, label: 'LinkedIn' },
    { value: 'CAREER_SITE' as CandidateSource, label: 'Site Carrière' },
    { value: 'REFERRAL' as CandidateSource, label: 'Cooptation' },
    { value: 'DIRECT' as CandidateSource, label: 'Direct' }
  ];

  const activeStages = $derived(recruitmentStore.filters.stage || []);
  const activePriorities = $derived(recruitmentStore.filters.priority || []);
  const activeSources = $derived(recruitmentStore.filters.source || []);
</script>


<div class="h-full flex flex-col overflow-hidden bg-slate-50/20">
  <!-- Refactored Dropdown Filter Toolbar -->
  <div class="px-6 py-4 border-b border-slate-100 bg-white shadow-none flex items-center justify-between">
    <div class="flex items-center justify-between w-full">
      <!-- Search -->
      <SearchBar 
        bind:value={recruitmentStore.filters.search} 
        placeholder="Rechercher un candidat..."
        onClear={() => recruitmentStore.filters.search = ''}
        class="w-125"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
        iconSize={22}
      />

      <div class="flex items-center gap-2">
        {#if recruitmentStore.activeCandidateFiltersCount > 0}
          <button 
            onclick={() => recruitmentStore.resetFilters()}
            class="text-[0.82rem] text-slate-400 hover:text-red-500 flex items-center gap-1.5 transition-all cursor-pointer"
          >
            <AppIcon name="rotate-ccw" size={16} />
            Réinitialiser
          </button>
        {/if}
        {@render StageFilter()}
        {@render PriorityFilter()}
        {@render SourceFilter()}
      </div>
    </div>
  </div>

  <!-- Active Removal Chips (Dynamic Context) -->
  {#if recruitmentStore.activeCandidateFiltersCount > 0}
    <div class="px-6 py-2 border-b border-slate-100 bg-white/40">
      <FilterChips 
        filters={recruitmentStore.filters}
        activeFiltersCount={recruitmentStore.activeCandidateFiltersCount} 
        onRemove={(key, value) => recruitmentStore.toggleFilter(key as any, value)}
        onReset={() => recruitmentStore.resetFilters()}
        getDisplayLabel={(key, value) => {
          if (key === 'stage') return stageOptions.find(o => o.value === value)?.label || value;
          if (key === 'priority') return priorityOptions.find(o => o.value === value)?.label || value;
          if (key === 'source') return sourceOptions.find(o => o.value === value)?.label || value;
          return value;
        }}
        class="py-0 px-0"
      />
    </div>
  {/if}

  <div class="flex-1 overflow-hidden">
    <CandidatesList {candidates} {stageConfig} />
  </div>
</div>


{#snippet StageFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all outline-none">
      <AppIcon name="list-filter" size={16} class={activeStages.length > 0 ? "text-blue-500" : "text-slate-400"} />
      <span class="text-[0.84rem] text-slate-700">Étapes</span>
      {#if activeStages.length > 0}
        <div transition:scale={{ duration: 200, start: 0.8 }}>
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {activeStages.length}
          </Badge>
        </div>
      {/if}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="start" class="w-48 p-1 rounded-lg shadow-fine bg-white border-slate-100">
      <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">Filtrer par étape</DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      {#each stageOptions as stage}
        <DropdownMenu.CheckboxItem 
          checked={activeStages.includes(stage.value)}
          onCheckedChange={() => recruitmentStore.toggleFilter('stage', stage.value)}
          class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
        >
          <div class="flex items-center gap-2">
            <AppIcon name={stage.icon} size={17} class="text-slate-400" />
            {stage.label}
          </div>
        </DropdownMenu.CheckboxItem>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet PriorityFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all outline-none">
      <AppIcon name="flag" size={16} class={activePriorities.length > 0 ? "text-blue-500" : "text-slate-400"} />
      <span class="text-[0.84rem] text-slate-700">Priorité</span>
      {#if activePriorities.length > 0}
        <div transition:scale={{ duration: 200, start: 0.8 }}>
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {activePriorities.length}
          </Badge>
        </div>
      {/if}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="start" class="w-48 p-1 rounded-lg shadow-fine bg-white border-slate-100">
      <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">Filtrer par priorité</DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      {#each priorityOptions as prio}
        <DropdownMenu.CheckboxItem 
          checked={activePriorities.includes(prio.value)}
          onCheckedChange={() => recruitmentStore.toggleFilter('priority', prio.value)}
          class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
        >
          <div class="flex items-center gap-2">
            <div class={cn("h-2 w-2 rounded-full bg-current", prio.color)}></div>
            {prio.label}
          </div>
        </DropdownMenu.CheckboxItem>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet SourceFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all outline-none">
      <AppIcon name="share-2" size={16} class={activeSources.length > 0 ? "text-blue-500" : "text-slate-400"} />
      <span class="text-[0.84rem] text-slate-700">Source</span>
      {#if activeSources.length > 0}
        <div transition:scale={{ duration: 200, start: 0.8 }}>
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {activeSources.length}
          </Badge>
        </div>
      {/if}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="start" class="w-48 p-1 rounded-lg shadow-fine bg-white border-slate-100">
      <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">Filtrer par source</DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      {#each sourceOptions as src}
        <DropdownMenu.CheckboxItem 
          checked={activeSources.includes(src.value)}
          onCheckedChange={() => recruitmentStore.toggleFilter('source', src.value)}
          class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
        >
          <div class="flex items-center gap-2">
            {src.label}
          </div>
        </DropdownMenu.CheckboxItem>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

