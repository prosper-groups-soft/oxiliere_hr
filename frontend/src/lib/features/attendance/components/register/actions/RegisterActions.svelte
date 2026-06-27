<script lang="ts">
  import { useDailyViewQuery } from "../../../queries/attendanceQueries";
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { useOrgUnitsQuery } from "@/features/jobs/queries/orgQueries";
  import { getOrgUnitIcon } from "@/features/jobs/constants/orgUnit.constants";
  import { useFinalizeDayMutation, useUnfinalizeDayMutation } from "../../../queries/attendanceQueries";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { cn } from "@/utilities/common/css";
  import type { DailyViewEntryOut } from "../../../api/attendance.endpoints";
  import { FILTER_STATUS_OPTIONS } from "../../../constants/attendance.constants";
  import type { AttendanceStatus } from "../../../constants/attendance.constants";

  
  const dailyViewQuery = useDailyViewQuery(
    () => attendanceStore.filters.dateRange.from,
  );

  const stats = $derived.by(() => {
    const data = $dailyViewQuery.data ?? [];
    return {
      presentCount: data.filter((e: DailyViewEntryOut) => e.status === 'PRESENT').length,
      lateCount: data.filter((e: DailyViewEntryOut) => e.status === 'LATE').length,
      absentCount: data.filter((e: DailyViewEntryOut) => e.status === 'ABSENT').length,
    };
  });

  // Derive is_finalized from the register (all entries share the same register)
  const isFinalized = $derived(($dailyViewQuery.data ?? []).length > 0 && ($dailyViewQuery.data as DailyViewEntryOut[])[0]?.is_finalized);

  // --- Filters ---

  const activeFiltersCount = $derived(
    attendanceStore.filters.orgUnit.length + attendanceStore.filters.status.length
  );

  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results ?? []);
  const statuses = FILTER_STATUS_OPTIONS;

  function resetFilters() {
    attendanceStore.filters.orgUnit = [];
    attendanceStore.filters.status = [];
  }

  // Finalize / Unfinalize mutations
  const finalizeMutation = useFinalizeDayMutation();
  const unfinalizeMutation = useUnfinalizeDayMutation();
  const isPending = $derived($finalizeMutation.isPending || $unfinalizeMutation.isPending);

  // Inline confirmation state
  let confirmStep = $state<'idle' | 'confirm'>('idle');

  function handlePrimaryClick() {
    confirmStep = 'confirm';
  }

  function handleConfirm() {
    confirmStep = 'idle';
    if (isFinalized) {
      $unfinalizeMutation.mutate(attendanceStore.filters.dateRange.from);
    } else {
      $finalizeMutation.mutate(attendanceStore.filters.dateRange.from);
    }
  }

  function handleCancel() {
    confirmStep = 'idle';
  }

  const recordsCount = $derived(($dailyViewQuery.data ?? []).length);
</script>


<div class="flex items-center justify-between gap-3 px-4 py-1.5 shadow-fine bg-white">
  <!-- Stats Metrics (left) -->
  <div class="flex items-center gap-4">
    {#snippet Metric(label: string, value: number, color: string)}
      <div class="flex items-center gap-1.5">
        <div class="h-2 w-2 rounded-full {color}"></div>
        <span class="font-medium text-[0.8rem] text-slate-800">{value}</span>
        <span class="text-[0.75rem] text-slate-500">{label}</span>
      </div>
    {/snippet}
    {@render Metric("Présents", stats.presentCount, "bg-emerald-500")}
    {@render Metric("Retards", stats.lateCount, "bg-amber-500")}
    {@render Metric("Absents", stats.absentCount, "bg-rose-500")}
  </div>

  <!-- Right: filtres + actions -->
  <div class="flex items-center gap-2 border-l border-slate-100 pl-0.5">

    <!-- Filtres Dropdown (style ConfigActions) -->
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        <Button
          variant="ghost"
          size="sm"
          class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
        >
          <AppIcon name="filter" size={15} class="mr-1.5" />
          Filtres
          {#if activeFiltersCount > 0}
            <span class="ml-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
              {activeFiltersCount}
            </span>
          {/if}
        </Button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="w-56 p-1 z-50 h-75">
        <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
          Statut
        </DropdownMenu.Label>
        {#each statuses as s}
          {@const statusVal = s.value as AttendanceStatus}
          {@const checked = attendanceStore.filters.status.includes(statusVal)}
          <DropdownMenu.Item
            onclick={() => attendanceStore.toggleFilter('status', statusVal)}
            class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", checked && "bg-slate-50 font-medium"]}
          >
            <span class="text-[0.86rem]">{s.label}</span>
            {#if checked}
              <AppIcon name="check" size={14} class="text-slate-600" />
            {/if}
          </DropdownMenu.Item>
        {/each}

        <DropdownMenu.Separator class="my-1" />

        <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
          Unité
        </DropdownMenu.Label>
        {#each orgUnits as unit}
          {@const checked = attendanceStore.filters.orgUnit.includes(unit.id)}
          <DropdownMenu.Item
            onclick={() => attendanceStore.toggleFilter('orgUnit', unit.id)}
            class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", checked && "bg-slate-50 font-medium"]}
          >
            <span class="flex items-center gap-2 text-[0.86rem]">
              <AppIcon name={getOrgUnitIcon(unit.type)} size={16} class="text-slate-500" />
              {unit.name}
            </span>
            {#if checked}
              <AppIcon name="check" size={14} class="text-slate-600" />
            {/if}
          </DropdownMenu.Item>
        {/each}

        <DropdownMenu.Separator class="my-1" />
        <DropdownMenu.Item
          onclick={resetFilters}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser tout
        </DropdownMenu.Item>
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

    <!-- Séparateur -->
    <span class="w-px h-5 bg-slate-200"></span>

    <!-- Bouton Clôturer / Déclôturer + Inline Confirmation -->
    {#if confirmStep === 'confirm'}
      <!-- Inline confirmation: Annuler / Oui -->
      <span class="flex items-center gap-1.5 text-[0.77rem] text-slate-500 mr-1">
        {isFinalized ? "Déclôturer" : "Clôturer"} la journée ?
      </span>
      <Button
        onclick={handleCancel}
        variant="ghost"
        class="h-7 px-2 rounded-md text-[0.8rem] text-slate-500 hover:text-slate-700"
      >
        Annuler
      </Button>
      <Button
        onclick={handleConfirm}
        disabled={isPending}
        variant={isFinalized ? "outline" : "default"}
        class={cn(
          "h-7 px-2.5 rounded-md text-[0.8rem] transition-all",
          isFinalized && "border-amber-300 text-amber-700 hover:bg-amber-50"
        )}
      >
        {#if isPending}
          <AnimateSpin text="" class="size-3 mr-1" />
        {/if}
        Oui
      </Button>
    {:else}
      <Button
        onclick={handlePrimaryClick}
        disabled={isPending || recordsCount === 0}
        variant="outline"
        class={cn(
          "h-7 px-2.5 rounded-md text-[0.8rem] transition-all",
          isFinalized
            ? "text-amber-600 hover:text-amber-800 hover:border-amber-300 border-amber-200"
            : "text-slate-500 hover:text-slate-900 hover:border-slate-300 border-slate-200"
        )}
      >
        {#if isPending}
          <AnimateSpin text="" class="size-3 mr-1" />
        {:else}
          <AppIcon name={isFinalized ? "unlock" : "lock"} size={13} class="mr-1" />
        {/if}
        {isFinalized ? "Déclôturer" : "Clôturer"}
      </Button>
    {/if}
    
  </div>
</div> 
