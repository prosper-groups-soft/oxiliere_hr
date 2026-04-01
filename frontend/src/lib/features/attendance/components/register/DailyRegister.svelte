<script lang="ts">
  import { flip } from 'svelte/animate';
  import { cubicOut } from 'svelte/easing';
  import { attendanceStore } from "../../stores/attendance.svelte";
  import type { AttendanceStatus } from "../../types/types";
  import AttendanceHeader from "./AttendanceHeader.svelte";
  import AttendanceRecordRow from "./views/AttendanceRecordRow.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import FilterChips from '@/components/shared/elements/FilterChips.svelte';
  import { Button } from "@/components/ui/button";
  import { cn } from "@/utilities/common/css";

  const records = $derived(attendanceStore.filteredRecords);
  const anomaliesCount = $derived(attendanceStore.records.filter(r => r.anomalies.length > 0).length);
  
  type ChipFilterKey = 'department' | 'status';

  const chipFilters = $derived({
    department: attendanceStore.filters.department,
    status: attendanceStore.filters.status
  });
  const activeChipFiltersCount = $derived(
    attendanceStore.filters.department.length + attendanceStore.filters.status.length
  );

  const STATUS_LABELS: Record<AttendanceStatus, string> = {
    PRESENT: 'Présent',
    LATE: 'Retard',
    ABSENT: 'Absent',
    LEAVE: 'Congé',
    OFF: 'Repos',
    PENDING: 'En attente'
  };

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'department') return String(value);
    if (key === 'status') return STATUS_LABELS[value as AttendanceStatus] ?? String(value);
    return String(value);
  }

  function handleRemoveChip(key: string, value: unknown) {
    if (key === 'department' || key === 'status') {
      attendanceStore.toggleFilter(key as ChipFilterKey, value);
    }
  }

  function resetChipFilters() {
    attendanceStore.filters.department = [];
    attendanceStore.filters.status = [];
  }
</script>


<div class="flex h-full flex-col bg-white overflow-hidden">
  {@render Header()}

  <div class="flex-1 flex overflow-hidden">
    <div class="flex-1 flex flex-col min-w-0 border-r border-slate-100 bg-white">
      {#if records.length === 0}
        <div class="flex-1 flex items-center justify-center">
          <Empty 
            title="Aucun enregistrement" 
            description="Aucun pointage ne correspond à vos filtres actuels."
            icon="search"
            iconSize={24}
            iconStrokeWidth={1.1}
            iconClass="text-slate-300"
          />
        </div>
      {:else}
        {#if activeChipFiltersCount > 0}
          <div class="border-b border-slate-100 bg-white py-2">
            <FilterChips
              filters={chipFilters}
              activeFiltersCount={activeChipFiltersCount}
              getDisplayLabel={getFilterDisplayLabel}
              onRemove={handleRemoveChip}
              onReset={resetChipFilters}
            />
          </div>
        {/if}

        <div class="sticky top-0 z-10 flex items-center h-10 px-6 bg-white border-b border-slate-100">
          <span class="w-[30%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
          <div class="flex w-[20%] gap-8">
            <span class="w-14 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Arrivée</span>
            <span class="w-14 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Départ</span>
          </div>
          <span class="w-[25%] px-6 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-center">Activité</span>
          <div class="flex w-[25%] justify-end pr-14">
            <span class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar">
          <div class="flex flex-col">
            {#each records as record (record.id)}
              <div animate:flip={{ duration: 400, easing: cubicOut }}>
                <AttendanceRecordRow {record} />
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <aside class="w-72 flex flex-col bg-slate-50/20">
      <div class="h-10 px-4 flex items-center justify-between border-b border-slate-100 bg-white">
        <div class="flex items-center gap-2">
          <AppIcon name="alert-circle" size={15} class="text-slate-400" />
          <span class="text-[0.7rem] font-bold text-slate-500 uppercase tracking-widest">Anomalies</span>
        </div>
        {#if anomaliesCount > 0}
          <span class="text-[0.65rem] font-bold bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full">{anomaliesCount}</span>
        {/if}
      </div>
      
      <div class="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
        {#each attendanceStore.records.filter(r => r.anomalies.length > 0) as record}
          {@render AnomalyCard(record)}
        {:else}
          <div class="py-12 flex flex-col items-center justify-center opacity-40">
            <AppIcon name="check-circle" size={20} class="text-slate-400 mb-2" />
            <p class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">RAS</p>
          </div>
        {/each}
      </div>

      <div class="p-4 bg-white border-t border-slate-100">
        <Button 
          onclick={() => attendanceStore.togglePeriodLock()}
          disabled={attendanceStore.currentPeriodRecords.length === 0}
          variant="outline"
          class={cn(
            "w-full h-9 rounded-md text-[0.7rem] font-bold uppercase tracking-widest transition-all shadow-none border-slate-200",
            attendanceStore.isCurrentPeriodLocked 
              ? "bg-amber-50 text-amber-600 border-amber-100 hover:bg-amber-100" 
              : "bg-white text-slate-500 hover:text-slate-900 hover:border-slate-300"
          )}
        >
          <AppIcon name={attendanceStore.isCurrentPeriodLocked ? "unlock" : "lock"} size={13} class="mr-2" />
          {attendanceStore.isCurrentPeriodLocked ? 'Déverrouiller' : 'Clôturer la journée'}
        </Button>
      </div>
    </aside>
  </div>
</div>


{#snippet Header()}
  <AttendanceHeader />
{/snippet}


{#snippet AnomalyCard(record: any)}
  <div class="flex flex-col gap-2 p-3 bg-white border border-slate-100 rounded-md transition-all hover:border-slate-300">
    <div class="flex items-center justify-between">
      <span class="text-[0.85rem] font-medium text-slate-800 truncate">{record.employeeName}</span>
      <span class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-tighter">{record.department}</span>
    </div>
    
    <div class="flex flex-wrap gap-1">
      {#each record.anomalies as anomaly}
        <div class="flex items-center gap-1 text-amber-600 text-[0.72rem] font-medium">
          <span class="w-1 h-1 rounded-full bg-amber-500"></span>
          {anomaly}
        </div>
      {/each}
    </div>
  </div>
{/snippet}


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

