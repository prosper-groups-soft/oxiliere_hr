<script lang="ts">
  import { leavesStore } from '../../stores/leaves.svelte';
  import { LEAVE_TYPE_LABELS, LEAVE_STATUS_LABELS } from '../../types/types';
  import type { LeaveType, LeaveStatus } from '../../types/types';
  import LeaveRequestRow from './views/LeaveRequestRow.svelte';
  import DataPagination from '@/components/layout/elements/DataPagination.svelte';
  import LeaveRequestSheet from './sheets/LeaveRequestSheet.svelte';
  import SearchBar from '@/components/shared/elements/SearchBar.svelte';
  import FilterChips from '@/components/shared/elements/FilterChips.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import * as DropdownMenu from '@/components/ui/dropdown-menu';
  import { Badge } from '@/components/ui/badge';
  import TooltipWrapper from '@/components/shared/containers/TooltipWrapper.svelte';
  import { cn } from '@/utilities/common/css';
  import { scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { cubicOut } from 'svelte/easing';

  const requests = $derived(leavesStore.paginatedRequests);
  let showRequestSheet = $state(false);

  const sortLabels: Record<string, string> = {
    createdAt: 'Date de création',
    startDate: 'Date de début',
    name: 'Nom (A-Z)',
    days: 'Durée',
  };

  const typeOptions: { value: LeaveType; label: string }[] = [
    { value: 'annual', label: 'Annuel' },
    { value: 'sick', label: 'Maladie' },
    { value: 'circumstantial', label: 'Circonstanciel' },
    { value: 'unpaid', label: 'Sans solde' },
  ];

  const statusOptions: { value: LeaveStatus; label: string }[] = [
    { value: 'pending', label: 'En attente' },
    { value: 'approved', label: 'Approuvé' },
    { value: 'rejected', label: 'Refusé' },
  ];

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'type') return LEAVE_TYPE_LABELS[value as LeaveType] ?? String(value);
    if (key === 'status') return LEAVE_STATUS_LABELS[value as LeaveStatus] ?? String(value);
    return String(value);
  }
</script>


<div class="flex h-full flex-col overflow-hidden">
  <!-- Request List Header -->
  {@render Header()}

  <!-- Filter Chips -->
  {#if leavesStore.activeFiltersCount > 0}
    <div class="border-b border-slate-100 bg-white py-1.5">
      <FilterChips
        filters={leavesStore.filters}
        activeFiltersCount={leavesStore.activeFiltersCount}
        getDisplayLabel={getFilterDisplayLabel}
        onRemove={(key, value) => leavesStore.toggleFilter(key as any, value)}
        onReset={() => leavesStore.resetFilters()}
      />
    </div>
  {/if}

  <!-- Request List -->
  <div class="flex-1 overflow-hidden flex flex-col">
    {#if requests.length === 0}
      <div class="flex-1 flex items-center justify-center">
        <Empty 
          title="Aucune demande" 
          description="Aucune demande de congé ne correspond à vos critères."
          icon="calendar-off"
          iconSize={24}
          iconStrokeWidth={1.1}
          iconClass="text-slate-300"
        />
      </div>
    {:else}
      <!-- Column Headers -->
      <div class="sticky top-0 z-10 flex items-center h-9 px-6 bg-slate-50/80 border-b border-slate-100">
        <span class="w-[25%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
        <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Type</span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Période</span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Motif</span>
        <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
        <span class="w-[10%]"></span>
      </div>

      <div class="flex-1 overflow-y-auto custom-scrollbar">
        {#each requests as request (request.id)}
          <div animate:flip={{ duration: 350, easing: cubicOut }}>
            <LeaveRequestRow {request} />
          </div>
        {/each}
      </div>

      {#if leavesStore.totalCount > 0}
        <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10 shrink-0">
          <DataPagination 
            currentCount={leavesStore.paginatedRequests.length}
            totalCount={leavesStore.totalCount}
            currentPage={leavesStore.currentPage}
            totalPages={leavesStore.totalPages}
            perPage={leavesStore.perPage}
            onPageChange={(p) => leavesStore.setPage(p)}
            onPerPageChange={(s) => leavesStore.setPerPage(s)}
            onNext={() => leavesStore.nextPage()}
            onPrev={() => leavesStore.prevPage()}
            unitLabel="demandes"
          />
        </div>
      {/if}
    {/if}
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-3 py-3 border-b border-slate-100 pl-4 pr-8">
    <div class="flex items-center gap-3">
      <div class="flex-1">
        <SearchBar 
          bind:value={leavesStore.filters.search} 
          placeholder="Rechercher un employé ou un département..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => leavesStore.setSearch("")}
        />
      </div>
      
      <div class="flex items-center gap-2">
        {@render SortMenu()}
        {@render Actions()}
      </div>
    </div>
  </div>
{/snippet}


{#snippet SortMenu()}
  <div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({ props })}
          <button 
            {...props} 
            class="h-7.5 px-3 flex items-center justify-start gap-2 cursor-pointer outline-none hover:bg-slate-50 transition-all min-w-35 max-w-50 border-none bg-transparent shadow-fine"
          >
            <div class="flex shrink-0 items-center justify-center">
              <AppIcon name="sort" size={16} class="text-slate-500" />
            </div>
            <span class="text-[0.84rem] text-slate-700 w-30 font-medium truncate">
              {sortLabels[leavesStore.sortBy] || "Trier par"}
            </span>
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="start" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Critères
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
        <DropdownMenu.RadioGroup value={leavesStore.sortBy} onValueChange={(v) => leavesStore.setSort(v)}>
          {#each Object.entries(sortLabels) as [value, label]}
            <DropdownMenu.RadioItem {value} class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              {label}
            </DropdownMenu.RadioItem>
          {/each}
        </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <div class="w-8 h-7.5 shrink-0 flex items-center justify-center border-l border-slate-100 bg-slate-50/30">
      <TooltipWrapper content={leavesStore.sortOrder === 'asc' ? 'Ordre croissant' : 'Ordre décroissant'}>
        {#snippet children(props)}
          <button 
            {...props}
            onclick={() => leavesStore.toggleSortOrder()}
            class="w-full h-full flex items-center justify-center hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <div class={cn("transition-transform duration-300 flex items-center justify-center", leavesStore.sortOrder === 'desc' ? "rotate-180" : "rotate-0")}>
              <AppIcon name="arrow-up" size={15} class={leavesStore.sortOrder === 'desc' ? "text-blue-600" : "text-slate-400"} />
            </div>
          </button>
        {/snippet}
      </TooltipWrapper>
    </div>
  </div>
{/snippet}


{#snippet Actions()}
  <div class="flex items-center gap-3">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger 
        class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all"
      >
        <AppIcon name="filter" size={16} class={leavesStore.activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
        <span class="text-[0.84rem] text-slate-700">Filtrer</span>
        {#if leavesStore.activeFiltersCount > 0}
          <div transition:scale={{ duration: 200, start: 0.8 }}>
            <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
              {leavesStore.activeFiltersCount}
            </Badge>
          </div>
        {/if}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="w-64 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
        <div class="p-2 max-h-80 overflow-y-auto">
          {@render FilterSection("Type", typeOptions, "type")}
          <DropdownMenu.Separator class="my-2 bg-slate-50" />
          {@render FilterSection("Statut", statusOptions, "status")}
          <DropdownMenu.Separator class="my-2 bg-slate-50" />
          {@render FilterSectionDepartment()}
        </div>

        {#if leavesStore.activeFiltersCount > 0}
          <div class="p-2 bg-slate-50/50 border-t border-slate-100">
            <Button variant="ghost" onclick={() => leavesStore.resetFilters()} class="w-full h-8 text-[0.84rem] bg-white text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
              Réinitialiser tout
            </Button>
          </div>
        {/if}
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <Button 
        onclick={() => showRequestSheet = true}
        class="bg-blue-600 hover:bg-blue-700 h-7.5 px-3 text-[0.84rem] text-white rounded-lg shadow-fine"
      >
        <AppIcon name="plus" size={17} />
        Nouvelle demande
      </Button>
  </div>
{/snippet}

<!-- Leave Request Sheet -->
<LeaveRequestSheet bind:open={showRequestSheet} />


{#snippet FilterSection(label: string, options: { value: string; label: string }[], filterKey: 'type' | 'status')}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={(leavesStore.filters[filterKey] as string[]).includes(option.value)}
      onCheckedChange={() => leavesStore.toggleFilter(filterKey, option.value)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {option.label}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}


{#snippet FilterSectionDepartment()}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    Département
  </DropdownMenu.Label>
  {#each leavesStore.departments as dept}
    <DropdownMenu.CheckboxItem 
      checked={leavesStore.filters.department.includes(dept)}
      onCheckedChange={() => leavesStore.toggleFilter('department', dept)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {dept}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

