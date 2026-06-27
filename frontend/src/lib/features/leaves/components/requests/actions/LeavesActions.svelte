<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { leavesStore } from "../../../stores/leaves.svelte";
  import { LEAVE_TYPE_OPTIONS, LEAVE_STATUS_OPTIONS } from "../../../constants/leaves";
  import type { LeaveRequest } from "../../../types/types";


  let { 
    onAdd,
    requests = [],
  }: { 
    onAdd: () => void;
    requests?: LeaveRequest[];
  } = $props();

  const sortLabels: Record<string, string> = {
    createdAt: 'Date de création',
    startDate: 'Date de début',
    name: 'Nom (A-Z)',
    days: 'Durée',
  };

  const activeFiltersCount = $derived(leavesStore.activeFiltersCount);
  const orgUnits = $derived(leavesStore.getOrgUnits(requests));

  function clearType() {
    leavesStore.filters.type = [];
  }

  function clearStatus() {
    leavesStore.filters.status = [];
  }

  function clearOrgUnit() {
    leavesStore.filters.orgUnit = [];
  }

  function isTypeActive(value: string): boolean {
    return leavesStore.filters.type?.includes(value as any) || false;
  }

  function isStatusActive(value: string): boolean {
    return leavesStore.filters.status?.includes(value as any) || false;
  }

  function isOrgUnitActive(value: string): boolean {
    return leavesStore.filters.orgUnit?.includes(value as any) || false;
  }
</script>


<div class="flex items-center gap-2 pr-3">
  <!-- Sort Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="arrow-down-up" size={15} class="mr-1.5" />
        Tri
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Trier par
      </DropdownMenu.Label>

      {#each Object.entries(sortLabels) as [value, label]}
        {@const isActive = leavesStore.sortBy === value}
        <DropdownMenu.Item
          onclick={() => { leavesStore.setSort(value); leavesStore.currentPage = 1; }}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            isActive && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{label}</span>
          {#if isActive}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Type Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="calendar" size={15} class="mr-1.5" />
        Type
        {#if (leavesStore.filters.type?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {leavesStore.filters.type?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Type de congé
      </DropdownMenu.Label>

      {#each LEAVE_TYPE_OPTIONS as option}
        {@const active = isTypeActive(option.value)}
        <DropdownMenu.Item
          onclick={() => leavesStore.toggleFilter('type', option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{option.label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (leavesStore.filters.type?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearType()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Status Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="user-check" size={15} class="mr-1.5" />
        Statut
        {#if (leavesStore.filters.status?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {leavesStore.filters.status?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut
      </DropdownMenu.Label>

      {#each LEAVE_STATUS_OPTIONS as option}
        {@const active = isStatusActive(option.value)}
        <DropdownMenu.Item
          onclick={() => leavesStore.toggleFilter('status', option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{option.label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (leavesStore.filters.status?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearStatus()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- OrgUnit Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="building-2" size={15} class="mr-1.5" />
        Unité
        {#if (leavesStore.filters.orgUnit?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {leavesStore.filters.orgUnit?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Unité organisationnelle
      </DropdownMenu.Label>
      {#each orgUnits as unit}
        {@const active = isOrgUnitActive(unit)}
        <DropdownMenu.Item
          onclick={() => leavesStore.toggleFilter('orgUnit', unit)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{unit}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (leavesStore.filters.orgUnit?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearOrgUnit()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => leavesStore.resetFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- Add Button -->
  <Button
    onclick={onAdd}
    variant="default"
    size="sm"
    class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
  >
    <AppIcon name="plus" size={15} />
    Nouvelle demande
  </Button>
</div>
