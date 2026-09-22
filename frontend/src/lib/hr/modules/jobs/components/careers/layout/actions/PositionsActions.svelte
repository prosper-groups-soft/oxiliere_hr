<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import CurrencyToggle from "@/hr/components/ui/currency-toggle";
  import { getOrgUnitIcon } from "@/hr/modules/jobs/constants/orgUnit.constants";
  import { jobsStore } from "@/hr/modules/jobs/stores/jobs.svelte";
  import { positionsStore } from "@/hr/modules/jobs/stores/positionsStore.svelte";
  import { payrollConfigStore } from "@/hr/modules/payroll/stores/configuration/payrollConfigStore.svelte";

  let { onAdd } = $props<{ onAdd: () => void }>();

  const activeFiltersCount = $derived(positionsStore.activeFiltersCount);

  function clearOrgUnit() {
    positionsStore.filters.orgUnit = [];
  }

  function clearSeniority() {
    positionsStore.filters.seniority = [];
  }

  function isOrgUnitActive(id: string): boolean {
    return positionsStore.filters.orgUnit.includes(id);
  }

  function isSeniorityActive(name: string): boolean {
    return positionsStore.filters.seniority.includes(name as any);
  }
</script>


<div class="flex items-center gap-2">
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

    <DropdownMenu.Content align="end" class="w-48 p-1">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Trier par
      </DropdownMenu.Label>

      {@render SortOption("Titre (A-Z)", "name", "asc")}
      {@render SortOption("Titre (Z-A)", "name", "desc")}
      {@render SortOption("Unité", "orgUnit", "asc")}
      {@render SortOption("Séniorité", "seniority", "asc")}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Org Unit Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="building-2" size={15} class="mr-1.5" />
        Unité
        {#if positionsStore.filters.orgUnit.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {positionsStore.filters.orgUnit.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Unité organisationnelle
      </DropdownMenu.Label>

      {#each jobsStore.orgUnits as unit}
        {@const active = isOrgUnitActive(unit.id)}
        {@const unitIcon = getOrgUnitIcon(unit.type)}
        <DropdownMenu.Item
          onclick={() => positionsStore.toggleFilter('orgUnit', unit.id)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={unitIcon} size={16} class="text-slate-500" />
            {unit.name}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if positionsStore.filters.orgUnit.length > 0}
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

  <!-- Seniority Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="layers" size={15} class="mr-1.5" />
        Séniorité
        {#if positionsStore.filters.seniority.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {positionsStore.filters.seniority.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Niveau de séniorité
      </DropdownMenu.Label>

      {#each jobsStore.seniorityLevels as level}
        {@const active = isSeniorityActive(level.level)}
        {@const label = level.name}
        <DropdownMenu.Item
          onclick={() => positionsStore.toggleFilter('seniority', level.level)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if positionsStore.filters.seniority.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearSeniority()}
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
      onclick={() => positionsStore.resetFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- Currency Toggle -->
  <CurrencyToggle
    currency={(payrollConfigStore.configuration?.currency ?? 'CDF') === 'CDF' ? 'CDF' : 'USD'}
    onChange={(c) => payrollConfigStore.saveConfiguration({ currency: c })}
    size="sm"
  />

  <!-- Add Button -->
  <Button
    onclick={onAdd}
    variant="default"
    size="sm"
    class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
  >
    <AppIcon name="plus" size={15} />
    Nouveau poste
  </Button>
</div>


{#snippet SortOption(label: string, sortBy: 'name' | 'orgUnit' | 'seniority', order: 'asc' | 'desc')}
  {@const isActive = positionsStore.sortBy === sortBy && positionsStore.sortOrder === order}
  <DropdownMenu.Item
    onclick={() => { positionsStore.setSort(sortBy); positionsStore.sortOrder = order; }}
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
{/snippet}

