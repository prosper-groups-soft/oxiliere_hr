<script lang="ts">
  import { useDailyViewQuery } from "../../../queries/attendanceQueries";
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { useOrgUnitsQuery } from "@/hr/modules/jobs/queries/orgQueries";
  import { getOrgUnitIcon } from "@/hr/modules/jobs/constants/orgUnit.constants";
  import { useFinalizeDayMutation, useUnfinalizeDayMutation } from "../../../queries/attendanceQueries";
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import { cn } from "@/hr/utilities/common/css";
  import type { DailyViewEntryOut } from "../../../api/attendance.endpoints";
  import { FILTER_STATUS_OPTIONS } from "../../../constants/attendance.constants";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import type { FilterDef } from "@/hr/actions/types";

  let { filterState = attendanceStore } = $props<{ filterState?: any }>();

  const dailyViewQuery = useDailyViewQuery(() => attendanceStore.filters.dateRange.from);
  const stats = $derived.by(() => {
    const data = $dailyViewQuery.data ?? [];
    return {
      presentCount: data.filter((e: DailyViewEntryOut) => e.status === 'PRESENT').length,
      lateCount: data.filter((e: DailyViewEntryOut) => e.status === 'LATE').length,
      absentCount: data.filter((e: DailyViewEntryOut) => e.status === 'ABSENT').length,
    };
  });
  const isFinalized = $derived(($dailyViewQuery.data ?? []).length > 0 && ($dailyViewQuery.data as DailyViewEntryOut[])[0]?.is_finalized);
  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results ?? []);

  const filterDefs = $derived<FilterDef[]>([
    { key: 'status', label: 'Statut', icon: 'user-check', mode: 'multi', options: FILTER_STATUS_OPTIONS.map(o => ({ value: o.value, label: o.label })) },
    { key: 'orgUnit', label: 'Unité', icon: 'building-2', mode: 'multi', options: orgUnits.map((u: any) => ({ value: u.id, label: u.name })) },
  ]);

  // Adapt filterState to FilterMenu expected shape if needed (attendanceStore already has filters/activeFiltersCount/toggleFilter/resetFilters)
  const fs = $derived(filterState);

  const finalizeMutation = useFinalizeDayMutation();
  const unfinalizeMutation = useUnfinalizeDayMutation();
  const isPending = $derived($finalizeMutation.isPending || $unfinalizeMutation.isPending);
  let confirmStep = $state<'idle' | 'confirm'>('idle');
  function handlePrimaryClick() { confirmStep = 'confirm'; }
  function handleConfirm() {
    confirmStep = 'idle';
    if (isFinalized) $unfinalizeMutation.mutate(attendanceStore.filters.dateRange.from);
    else $finalizeMutation.mutate(attendanceStore.filters.dateRange.from);
  }
  function handleCancel() { confirmStep = 'idle'; }
  const recordsCount = $derived(($dailyViewQuery.data ?? []).length);
</script>

<div class="flex items-center justify-between gap-3 px-4 py-1.5 shadow-fine bg-white">
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

  <div class="flex items-center gap-2 border-l border-slate-100 pl-0.5">
    <ActionBar>
      <FilterMenu filterDefs={filterDefs} filterState={fs} />
      {#if fs.activeFiltersCount > 0}
        <button onclick={() => fs.resetFilters()} class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer">
          <span class="text-[0.8rem]">{fs.activeFiltersCount} filtre{fs.activeFiltersCount > 1 ? 's' : ''}</span>
          <AppIcon name="x" size={13} />
        </button>
      {/if}
    </ActionBar>

    <span class="w-px h-5 bg-slate-200"></span>

    {#if confirmStep === 'confirm'}
      <span class="flex items-center gap-1.5 text-[0.77rem] text-slate-500 mr-1">{isFinalized ? "Déclôturer" : "Clôturer"} la journée ?</span>
      <Button onclick={handleCancel} variant="ghost" class="h-7 px-2 rounded-md text-[0.8rem] text-slate-500 hover:text-slate-700">Annuler</Button>
      <Button onclick={handleConfirm} disabled={isPending} variant={isFinalized ? "outline" : "default"} class={cn("h-7 px-2.5 rounded-md text-[0.8rem] transition-all", isFinalized && "border-amber-300 text-amber-700 hover:bg-amber-50")}>
        {#if isPending}<AnimateSpin text="" class="size-3 mr-1" />{/if}Oui
      </Button>
    {:else}
      <Button onclick={handlePrimaryClick} disabled={isPending || recordsCount === 0} variant="outline" class={cn("h-7 px-2.5 rounded-md text-[0.8rem] transition-all", isFinalized ? "text-amber-600 hover:text-amber-800 hover:border-amber-300 border-amber-200" : "text-slate-500 hover:text-slate-900 hover:border-slate-300 border-slate-200")}>
        {#if isPending}<AnimateSpin text="" class="size-3 mr-1" />{:else}<AppIcon name={isFinalized ? "unlock" : "lock"} size={13} class="mr-1" />{/if}
        {isFinalized ? "Déclôturer" : "Clôturer"}
      </Button>
    {/if}
  </div>
</div>
