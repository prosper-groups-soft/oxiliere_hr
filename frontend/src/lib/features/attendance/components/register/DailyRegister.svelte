<script lang="ts">
  import { flip } from 'svelte/animate';
  import { cubicOut } from 'svelte/easing';
  import { attendanceStore } from "../../stores/attendance.svelte";
  import { STATUS_LABELS } from "../../constants/attendance.constants";
  import { get } from 'svelte/store';
  import { useDailyViewQuery, useUpdateTimesheetMutation } from "../../queries/attendanceQueries";
  import type { DailyViewEntryOut } from "../../api/attendance.endpoints";
  import type { AttendanceRecord, AttendanceStatus } from "../../types/types";
  import AttendanceHeader from "./AttendanceHeader.svelte";
  import AttendanceRecordRow from "./views/AttendanceRecordRow.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import FilterChips from '@/components/shared/elements/FilterChips.svelte';
  import { Button } from "@/components/ui/button";
  import { fade, slide } from 'svelte/transition';
  import { useCalendarEventsQuery } from "@/features/calendar/queries/calendarQueries";
  import { EVENT_TYPE_LABELS, EVENT_TYPE_COLORS } from "@/features/calendar/types/types";



  // Events for the current day
  const calendarEventsQuery = useCalendarEventsQuery(
    () => attendanceStore.filters.dateRange.from,
    () => attendanceStore.filters.dateRange.from,
  );

  // Refetch when date changes
  $effect(() => {
    attendanceStore.filters.dateRange.from;
    get(calendarEventsQuery).refetch();
  });

  const currentDayEvents = $derived(($calendarEventsQuery.data ?? []).filter(event => {
    const dateStr = attendanceStore.filters.dateRange.from;
    if (!dateStr) return false;
    if (!event.endDate || event.endDate === event.defaultDate) {
      return event.defaultDate === dateStr;
    }
    return dateStr >= event.defaultDate && dateStr <= event.endDate;
  }));


  let anomaliesPanelOpen = $state(true);

  // Justification dialog state (unique, shared across all rows)
  let showJustifyDialog = $state(false);
  let justifyTarget = $state<{ id: string; employeeName: string } | null>(null);
  let justifyText = $state('');

  const updateTimesheetMutation = useUpdateTimesheetMutation();

  function openJustifyDialog(record: { id: string; employeeName: string; currentRemarks?: string }) {
    justifyTarget = record;
    justifyText = record.currentRemarks || '';
    showJustifyDialog = true;
  }

  function confirmJustify() {
    if (!justifyTarget || !justifyText.trim()) return;
    $updateTimesheetMutation.mutate(
      {
        timesheetId: justifyTarget.id,
        data: { status: 'EXCUSED', remarks: justifyText.trim() },
      },
      {
        onSuccess: () => {
          cancelJustify();
        },
      }
    );
  }

  function cancelJustify() {
    showJustifyDialog = false;
    justifyText = '';
    justifyTarget = null;
  }

  // Helper: ISO duration string → minutes
  function parseISODurationToMinutes(duration: string): number {
    const daysMatch = duration.match(/(\d+)D/);
    const hoursMatch = duration.match(/(\d+)H/);
    const minutesMatch = duration.match(/(\d+)M(?!S)/);
    const days = daysMatch ? parseInt(daysMatch[1]) : 0;
    const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0;
    const minutes = minutesMatch ? parseInt(minutesMatch[1]) : 0;
    return days * 24 * 60 + hours * 60 + minutes;
  }

  // Helper: backend entry → frontend AttendanceRecord
  function entryToRecord(entry: DailyViewEntryOut): AttendanceRecord {
    return {
      id: String(entry.id),
      employeeId: entry.employee_id,
      employeeName: entry.employee_name,
      firstName: entry.first_name ?? undefined,
      lastName: entry.last_name ?? undefined,
      jobTitle: entry.job_title ?? undefined,
      avatarUrl: entry.avatar_url ?? undefined,
      orgUnit: entry.org_unit_name ?? '',
      orgUnitId: entry.org_unit_id ?? undefined,
      date: entry.register_date,
      checkIn: entry.check_in ?? null,
      checkOut: entry.check_out ?? null,
      checkInAt: entry.check_in_at ?? null,
      checkOutAt: entry.check_out_at ?? null,
      checkInPunchId: entry.check_in_punch_id ?? null,
      checkOutPunchId: entry.check_out_punch_id ?? null,
      isManualEntry: entry.is_manual_entry,
      expectedIn: entry.expected_in ?? undefined,
      expectedOut: entry.expected_out ?? undefined,
      expectedBreakDuration: entry.expected_break_duration ?? undefined,
      isWorkingDay: entry.is_working_day ?? false,
      scheduleName: entry.schedule_name ?? undefined,
      scheduleSource: entry.schedule_source ?? undefined,
      status: entry.status as AttendanceStatus,
      workDuration: entry.recorded_work ? parseISODurationToMinutes(entry.recorded_work) : 0,
      overtime: entry.overtime ? parseISODurationToMinutes(entry.overtime) : 0,
      isLocked: entry.is_locked,
      anomalies: entry.anomalies ?? [],
      remarks: entry.remarks ?? undefined,
    };
  }

  // TanStack Query pour la vue quotidienne — réactive aux filtres et à la date
  const dailyViewQuery = useDailyViewQuery(
    () => attendanceStore.filters.dateRange.from,
    () => attendanceStore.filters.search,
    () => attendanceStore.filters.orgUnit.join(','),
    () => attendanceStore.filters.status.join(','),
  );


  // $effect pour refetch quand les filtres changent — utiliser dailyViewQuery
  // (sans $) pour éviter de créer une dépendance réactive sur la valeur du store
  $effect(() => {
    attendanceStore.filters.dateRange.from;
    attendanceStore.filters.search;
    attendanceStore.filters.orgUnit;
    attendanceStore.filters.status;
    get(dailyViewQuery).refetch();
  });

  const records = $derived(($dailyViewQuery.data ?? []).map(entryToRecord));
  const recordsWithAnomalies = $derived(records.filter(r => r.anomalies.length > 0 || (r.status === 'EXCUSED' && r.remarks)));
  const anomaliesCount = $derived(recordsWithAnomalies.length);
  const isLoading = $derived($dailyViewQuery.isLoading);
  const isFetching = $derived($dailyViewQuery.isFetching);
  const isError = $derived($dailyViewQuery.isError);
  const hasData = $derived(records.length > 0);
  const isInitialLoading = $derived(isLoading && !$dailyViewQuery.isRefetching);
  
  const hasActiveFilters = $derived(
    attendanceStore.filters.search !== '' ||
    attendanceStore.filters.orgUnit.length > 0 ||
    attendanceStore.filters.status.length > 0
  );


  const chipFilters = $derived({
    search: attendanceStore.filters.search ? [attendanceStore.filters.search] : [],
    orgUnit: attendanceStore.filters.orgUnit,
    status: attendanceStore.filters.status
  });
  const activeChipFiltersCount = $derived(
    (attendanceStore.filters.search ? 1 : 0) +
    attendanceStore.filters.orgUnit.length +
    attendanceStore.filters.status.length
  );

  // Lookup map: orgUnitId → orgUnitName (pour l'affichage FilterChips)
  const orgUnitNameById = $derived.by(() => {
    const map = new Map<string, string>();
    for (const r of records) {
      if (r.orgUnitId && r.orgUnit) {
        map.set(r.orgUnitId, r.orgUnit);
      }
    }
    return map;
  });

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche : ${String(value)}`;
    if (key === 'orgUnit') return orgUnitNameById.get(String(value)) ?? String(value);
    if (key === 'status') return STATUS_LABELS[value as AttendanceStatus] ?? String(value);
    return String(value);
  }

  function handleRemoveChip(key: string, value: unknown) {
    if (key === 'search') {
      attendanceStore.filters.search = '';
    } else if (key === 'orgUnit' || key === 'status') {
      attendanceStore.toggleFilter(key, value);
    }
  }

  function resetAllFilters() {
    attendanceStore.filters.search = '';
    attendanceStore.filters.orgUnit = [];
    attendanceStore.filters.status = [];
  }
</script>


<div class="flex h-full flex-col bg-white overflow-hidden">
  {@render Header()}

  <div class="flex-1 flex overflow-hidden">
    <div class="flex-1 flex flex-col min-w-0 border-r border-slate-100 bg-white relative overflow-hidden">
      
      <!-- Event banner -->
      {@render EventBanner()}

      <!-- FilterChips toujours visible — même en chargement, erreur ou vide -->
      <FilterChips
        filters={chipFilters}
        activeFiltersCount={activeChipFiltersCount}
        getDisplayLabel={getFilterDisplayLabel}
        onRemove={handleRemoveChip}
        onReset={resetAllFilters}
        class="px-6 py-1 pt-0 shrink-0"
        badgeClass="bg-amber-50 text-amber-600 border-amber-100/50"
      />

      {#if isInitialLoading}
        <div transition:fade={{ duration: 150 }} class="absolute inset-0 flex items-center justify-center">
          <AnimateSpin text="Chargement des pointages" />
        </div>

      {:else if isError && !hasData}
        <div transition:fade={{ duration: 150 }} class="absolute inset-0 flex items-center justify-center p-8">
          <Empty
            title="Erreur de chargement"
            description="Impossible de charger les pointages pour cette date."
            icon="alert-circle"
            iconClass="text-red-400"            
            iconSize={28}
            iconStrokeWidth={1.3}
            iconContainerClass="bg-red-50/30"
          >
            <Button onclick={() => $dailyViewQuery.refetch()} variant="outline" class="h-7 rounded-lg">
              <AppIcon name="refresh-cw" />
              Réessayer
            </Button>
          </Empty>
        </div>

      {:else}
        {#if !hasData && !isLoading && !hasActiveFilters}
          <div transition:fade={{ duration: 150 }} class="absolute inset-0 flex items-center justify-center">
            <Empty 
              title="Aucun enregistrement" 
              description="Aucun pointage n'a encore été enregistré pour cette journée."
              icon="clipboard-list"
              iconSize={28}
              iconStrokeWidth={1.3}
              iconClass="text-slate-400"
            />
          </div>

        {:else if !hasData && !isLoading && hasActiveFilters}
          <div transition:fade={{ duration: 150 }} class="absolute inset-0 flex items-center justify-center">
            <Empty 
              title="Aucun résultat trouvé"
              description="Aucun pointage ne correspond à votre recherche ou à vos filtres actuels."
              icon="search-x"
              iconSize={28}
              iconStrokeWidth={1.3}
              iconClass="text-slate-400"
            >
              <Button variant="ghost" onclick={resetAllFilters} class="h-7 bg-slate-50">
                <AppIcon name="x" size={16} class="text-slate-400" />
                Réinitialiser la recherche
              </Button>
            </Empty>
          </div>

        {:else}
          <div class="flex-1 flex flex-col min-h-0">
            <!-- Overhead loading bar during refetch -->
            {#if isFetching}
              <div class="h-0.5 bg-slate-100 overflow-hidden">
                <div class="h-full bg-primary animate-[loadingSlide_1.2s_ease-in-out_infinite] rounded-full" style="width: 30%"></div>
              </div>
            {/if}

            <div class="sticky top-0 z-10 flex items-center h-10 px-6 bg-white border-b border-slate-100">
              <span class="w-[30%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé / Poste</span>
              <div class="flex w-[24%] gap-4">
                <span class="min-w-36 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Arrivée</span>
                <span class="min-w-36 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Départ</span>
              </div>
              <span class="w-[21%] px-4 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-center">Activité</span>
              <div class="flex w-[25%] justify-end gap-6">
                <span class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
                <div class="w-7 shrink-0"></div>
              </div>
            </div>

            <div class="flex-1 overflow-y-auto custom-scrollbar">
              <div class="flex flex-col">
                {#each records as record (record.id)}
                  <div animate:flip={{ duration: 400, easing: cubicOut }}>
                    <AttendanceRecordRow {record} onrequestjustify={openJustifyDialog} />
                  </div>
                {/each}
              </div>
            </div>
          </div>
        {/if}
      {/if}
    </div>

    {@render AnomaliesPanel()}
  </div>
</div>


{#snippet Header()}
  <AttendanceHeader />
{/snippet}


{#snippet AnomalyCard(record: any)}

  {@const isExcused = record.status === 'EXCUSED' && record.remarks}
  {@const isUnExcused = record.status === 'ABSENT' && !record.remarks}
  {@const isLate = record.status === 'LATE'}
  {@const borderColor = isExcused ? 'border-indigo-200' : isUnExcused ? 'border-rose-200' : isLate ? 'border-amber-200' : 'border-slate-200'}
  <div class="flex flex-col gap-2 p-3 bg-white border rounded-lg transition-all duration-200 hover:shadow-sm {borderColor}">
    <div class="flex items-center justify-between gap-2">
      <span class="text-[0.85rem] font-medium text-slate-800 truncate">{record.employeeName}</span>
      <span class="shrink-0 text-[0.6rem] font-bold text-slate-400 uppercase tracking-tighter bg-slate-50 px-1.5 py-0.5 rounded">{record.jobTitle}</span>
    </div>

    <div class="flex flex-col gap-1">
      {#if isLate}
        <div class="flex items-start gap-1.5 text-amber-700 text-[0.72rem] font-medium leading-snug">
          <span class="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400"></span>
          <span class="text-[0.72rem]">Retard détecté</span>
        </div>
      {/if}

      {#each record.anomalies as anomaly}
        {#if anomaly !== 'Absence non justifiée' && anomaly !== 'Retard détecté'}
          <div class="flex items-start gap-1.5 text-amber-700 text-[0.72rem] font-medium leading-snug">
            <span class="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400"></span>
            <span class="text-[0.72rem]">{anomaly}</span>
          </div>
        {/if}
      {/each}
    </div>

    {#if isExcused}
      <div class="flex items-start gap-1.5 pt-1.5 border-t border-indigo-100 text-indigo-700 text-[0.72rem] font-medium leading-snug">
        <span class="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400"></span>
        <span class="text-[0.72rem]">Absence justifiée&nbsp;: {record.remarks}</span>
      </div>
    {:else if isUnExcused}
      <div class="flex items-start gap-1.5 pt-1.5 border-t border-rose-100 text-rose-600 text-[0.72rem] font-medium leading-snug">
        <span class="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-rose-400"></span>
        <span class="text-[0.72rem]">Absence non justifiée</span>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet EventBanner()}
  {#if currentDayEvents.length > 0}
    <div class="flex items-center gap-2 px-6 py-2 bg-linear-to-r from-amber-50/80 via-amber-50/50 to-transparent border-b border-amber-100/60">
      <AppIcon name="calendar" size={14} class="text-amber-500 shrink-0" />
      <span class="text-[0.7rem] font-bold text-amber-700 uppercase tracking-widest shrink-0">Événements</span>
      <div class="flex items-center gap-1.5 flex-wrap">
        {#each currentDayEvents as event}
          {@const colors = EVENT_TYPE_COLORS[event.type]}
          {@const label = EVENT_TYPE_LABELS[event.type]}
          <span class="inline-flex items-center gap-1.5 text-[0.72rem] font-medium px-2 py-0.5 rounded-full border {colors.bg} {colors.text} {colors.border}">
            <span class="h-1.5 w-1.5 shrink-0 rounded-full {colors.dot}"></span>
            {event.title}
            <span class="text-[0.65rem] opacity-70">({label})</span>
          </span>
        {/each}
      </div>
    </div>
  {/if}
{/snippet}


{#snippet AnomaliesPanel()}
  <aside
    class="relative flex flex-col overflow-hidden transition-[width] duration-300 ease-in-out"
    style="width: {anomaliesPanelOpen ? '19rem' : '36px'}"
  >
    {#if anomaliesPanelOpen}
      <!-- EXPANDED STATE -->
      <div class="flex w-full flex-1 flex-col min-h-0 shrink-0 bg-slate-50/20">
        <!-- Header -->
        <div class="flex h-10 shrink-0 items-center justify-between border-b border-slate-100 bg-white pl-2 pr-3">
          <div class="flex items-center gap-2">
            <button
              onclick={() => anomaliesPanelOpen = false}
              class="flex items-center justify-center h-8 w-8 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              title="Réduire"
            >
              <AppIcon name="chevron-left" size={16} class="rotate-180" />
            </button>
            <AppIcon name="circle-alert" size={16} class="text-slate-400" />
            <span class="text-[0.7rem] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
              Anomalies
            </span>
            {#if anomaliesCount > 0}
              <span class="text-[0.65rem] font-bold bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full">
                {anomaliesCount}
              </span>
            {/if}
          </div>
          <div
            onclick={() => anomaliesPanelOpen = false}
            class="flex items-center justify-center h-5 w-5 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            title="Réduire"
            role="none"
          >
            <AppIcon name="x" size={15} />
          </div>
        </div>

        <!-- Content (slide only for list) -->
        <div transition:slide={{ duration: 200, easing: cubicOut }} class="flex flex-1 flex-col min-h-0">
          <div class="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
            {#if recordsWithAnomalies.length > 0}
              {#each recordsWithAnomalies as record (record.id)}
                {@render AnomalyCard(record)}
              {/each}
            {:else}
              <div class="flex flex-col items-center justify-center py-16">
                <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50">
                  <AppIcon name="circle-check" size={24} class="text-emerald-400" />
                </div>
                <p class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest mb-1">Aucune anomalie</p>
                <p class="text-[0.75rem] text-slate-400">Tout est en ordre pour cette journée</p>
              </div>
            {/if}
          </div>
        </div>

      </div>
    {:else}
      <!-- COLLAPSED STATE — indigo band -->
      <button
        onclick={() => anomaliesPanelOpen = true}
        class="flex flex-col items-center justify-center gap-4 w-9 h-full bg-indigo-50 hover:bg-indigo-100 border-l border-indigo-100 cursor-pointer transition-colors duration-200"
      >
        <div class="relative flex flex-col items-center gap-3">
          <AppIcon name="chevron-left" size={20} class="text-indigo-400" />
          {#if anomaliesCount > 0}
            <span class="text-[0.6rem] font-bold bg-indigo-200 text-indigo-700 w-5 h-5 flex items-center justify-center rounded-full">
              {anomaliesCount}
            </span>
          {/if}
        </div>
      </button>
    {/if}
  </aside>
{/snippet}


{#if showJustifyDialog && justifyTarget}
  <div
    role="none"
    onclick={cancelJustify}
    onkeydown={(e) => { if (e.key === 'Escape') cancelJustify(); }}
    class="fixed inset-0 z-9999 flex items-center justify-center bg-black/30"
  >
    <div
      role="none"
      onclick={(e) => e.stopPropagation()}
      class="bg-white rounded-xl shadow-2xl border border-slate-200 p-5 w-full max-w-md mx-4"
    >
      <h3 class="text-base font-semibold text-slate-900 mb-1">Justifier l'absence</h3>
      <p class="text-sm text-slate-500 mb-4">
        Saisissez le motif de justification pour <span class="font-medium text-slate-700">{justifyTarget.employeeName}</span>
      </p>
      <textarea
        bind:value={justifyText}
        placeholder="Motif de l'absence justifiée..."
        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 resize-none focus:outline-none focus:ring-3.5 focus:ring-indigo-400 focus:border-transparent transition-shadow"
        rows="3"
        onkeydown={(e) => {
          if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            confirmJustify();
          }
          if (e.key === 'Escape') {
            cancelJustify();
          }
        }}
      ></textarea>
      <div class="px-0 py-0 flex flex-col gap-3 mt-5">
        <div class="flex gap-3 w-full">
          <button
            onclick={cancelJustify}
            class="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-lg border border-slate-200 bg-white shadow-fine text-slate-600 font-medium text-[0.88rem] hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <AppIcon name="x" size={17} class="text-slate-300" />
            Annuler
          </button>
          <button
            onclick={confirmJustify}
            disabled={!justifyText.trim() || $updateTimesheetMutation.isPending}
            class="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-lg bg-indigo-600 text-white font-medium text-[0.88rem] shadow-fine hover:opacity-90 transition-all disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
          >
            {#if $updateTimesheetMutation.isPending}
              <AnimateSpin class="border-white size-3" text="" />
            {:else}
              <AppIcon name="check" size={17} />
            {/if}
            Confirmer
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }

  :global {
    @keyframes loadingSlide {
      0% { transform: translateX(-100%); }
      50% { transform: translateX(200%); }
      100% { transform: translateX(400%); }
    }
  }
</style>

