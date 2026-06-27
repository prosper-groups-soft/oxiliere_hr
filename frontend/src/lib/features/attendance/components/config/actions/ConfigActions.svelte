<script lang="ts">
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { useOrgUnitsQuery } from "@/features/jobs/queries/orgQueries";
  import { RECURRENCE_LABELS } from "../../../constants/attendance.constants";
  import { getOrgUnitIcon } from "@/features/jobs/constants/orgUnit.constants";


  const sortOptions: { label: string; sortBy: string; order: 'asc' | 'desc' }[] = [
    { label: "Nom (A-Z)", sortBy: "name", order: "asc" },
    { label: "Nom (Z-A)", sortBy: "name", order: "desc" },
    { label: "Modèle de travail", sortBy: "policy", order: "asc" },
  ];

  // Recurrence filter options: "Tous" is implicit (no selection)
  const recurrenceOptions = [
    { value: "NONE", label: RECURRENCE_LABELS.NONE },
    { value: "WEEKLY", label: RECURRENCE_LABELS.WEEKLY },
    { value: "BIWEEKLY", label: RECURRENCE_LABELS.BIWEEKLY },
    { value: "MONTHLY", label: RECURRENCE_LABELS.MONTHLY },
    { value: "QUARTERLY", label: RECURRENCE_LABELS.QUARTERLY },
  ];

  // Org units from API
  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results || []);

  const activeFiltersCount = $derived(attendanceStore.activeFiltersCount);

  function isOrgUnitActive(id: string): boolean {
    return attendanceStore.filters.orgUnit?.includes(id) || false;
  }

  function clearOrgUnitFilter() {
    attendanceStore.filters.orgUnit = [];
  }

  function isRecurrenceActive(value: string): boolean {
    return attendanceStore.filters.recurrence?.includes(value) || false;
  }

  function isSortActive(sortBy: string, order: string): boolean {
    return attendanceStore.sortBy === sortBy && attendanceStore.sortOrder === order;
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

      {#each sortOptions as option}
        {@const active = isSortActive(option.sortBy, option.order)}
        <DropdownMenu.Item
          onclick={() => {
            attendanceStore.setSort(option.sortBy);
            attendanceStore.sortOrder = option.order;
          }}
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
        Unités
        {#if (attendanceStore.filters.orgUnit?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {attendanceStore.filters.orgUnit?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Unités organisationnelles
      </DropdownMenu.Label>

      {#each orgUnits as unit}
        {@const active = isOrgUnitActive(unit.id)}
        <DropdownMenu.Item
          onclick={() => attendanceStore.toggleFilter('orgUnit', unit.id)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={getOrgUnitIcon(unit.type)} size={16} class="text-slate-500" />
            {unit.name}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (attendanceStore.filters.orgUnit?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearOrgUnitFilter()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Recurrence Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="refresh-cw" size={15} class="mr-1.5" />
        Récurrence
        {#if (attendanceStore.filters.recurrence?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {attendanceStore.filters.recurrence?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Récurrence
      </DropdownMenu.Label>

      {#each recurrenceOptions as option}
        {@const active = isRecurrenceActive(option.value)}
        <DropdownMenu.Item
          onclick={() => attendanceStore.toggleFilter('recurrence', option.value)}
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

      {#if (attendanceStore.filters.recurrence?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => attendanceStore.filters.recurrence = []}
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
      onclick={() => attendanceStore.resetFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}
</div>
