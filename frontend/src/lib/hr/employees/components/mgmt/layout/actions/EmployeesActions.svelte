<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { employeeStore } from "@/hr/employees/stores/employees.svelte";
  import { useOrgUnitsQuery } from "@/hr/jobs/queries/orgQueries";
  import { getOrgUnitIcon } from "@/hr/jobs/constants/orgUnit.constants";
  import { CONTRACT_TYPES } from "@/hr/employees/constants/contract";
  import { EMPLOYEE_STATUS_CONFIG } from "@/hr/employees/constants/employeeStatus";


  let { onAdd, onToggleViewMode } = $props<{ 
    onAdd: () => void;
    onToggleViewMode: () => void;
  }>();

  // Récupérer les unités organisationnelles via le query
  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results || []);

  const activeFiltersCount = $derived(employeeStore.activeFiltersCount);

  // Options pour les filtres de statut
  const statusOptions = $derived(
    Object.entries(EMPLOYEE_STATUS_CONFIG).map(([key, config]) => ({
      value: key,
      label: config.label
    }))
  );

  const contractTypeOptions = CONTRACT_TYPES;

  // Fonctions de filtre
  function clearOrgUnit() {
    employeeStore.filters.orgUnit = [];
  }

  function clearStatus() {
    employeeStore.filters.status = [];
  }

  function clearContractType() {
    employeeStore.filters.contractType = [];
  }

  function isOrgUnitActive(id: string): boolean {
    return employeeStore.filters.orgUnit?.includes(id) || false;
  }

  function isStatusActive(value: string): boolean {
    return employeeStore.filters.status?.includes(value as any) || false;
  }

  function isContractTypeActive(value: string): boolean {
    return employeeStore.filters.contractType?.includes(value as any) || false;
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

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Trier par
      </DropdownMenu.Label>

      {@render SortOption("Nom (A-Z)", "name", "asc")}
      {@render SortOption("Nom (Z-A)", "name", "desc")}
      {@render SortOption("Date d'embauche", "joinDate", "asc")}
      {@render SortOption("Statut", "status", "asc")}
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
        {#if (employeeStore.filters.orgUnit?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {employeeStore.filters.orgUnit?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Unité organisationnelle
      </DropdownMenu.Label>
      {#each orgUnits as unit}
        {@const active = isOrgUnitActive(unit.id)}
        {@const unitIcon = getOrgUnitIcon(unit.type)}
        <DropdownMenu.Item
          onclick={() => employeeStore.toggleFilter('orgUnit', unit.id)}
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

      {#if (employeeStore.filters.orgUnit?.length || 0) > 0}
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
        {#if (employeeStore.filters.status?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {employeeStore.filters.status?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut employé
      </DropdownMenu.Label>

      {#each statusOptions as option}
        {@const active = isStatusActive(option.value)}
        <DropdownMenu.Item
          onclick={() => employeeStore.toggleFilter('status', option.value)}
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

      {#if (employeeStore.filters.status?.length || 0) > 0}
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

  <!-- Contract Type Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="file-text" size={15} class="mr-1.5" />
        Contrat
        {#if (employeeStore.filters.contractType?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {employeeStore.filters.contractType?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Type de contrat
      </DropdownMenu.Label>

      {#each contractTypeOptions as option}
        {@const active = isContractTypeActive(option.value)}
        <DropdownMenu.Item
          onclick={() => employeeStore.toggleFilter('contractType', option.value)}
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

      {#if (employeeStore.filters.contractType?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearContractType()}
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
      onclick={() => employeeStore.resetFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- View Mode Toggle -->
  <Button
    onclick={onToggleViewMode}
    variant="ghost"
    size="sm"
    class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
  >
    {#if employeeStore.viewMode === 'list'}
      <AppIcon name="layout-grid" size={15} class="mr-1.5" />
      Grille
    {:else}
      <AppIcon name="list" size={15} class="mr-1.5" />
      Liste
    {/if}
  </Button>

  <!-- Add Button -->
  <Button
    onclick={onAdd}
    variant="default"
    size="sm"
    class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
  >
    <AppIcon name="plus" size={15} />
    Onboarding
  </Button>
</div>


{#snippet SortOption(label: string, sortBy: 'name' | 'joinDate' | 'status', order: 'asc' | 'desc')}
  {@const isActive = employeeStore.sortBy === sortBy && employeeStore.sortOrder === order}
  <DropdownMenu.Item
    onclick={() => { 
      employeeStore.setSort(sortBy); 
      employeeStore.sortOrder = order;
      // Reset to page 1 when changing sort
      employeeStore.currentPage = 1;
    }}
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

