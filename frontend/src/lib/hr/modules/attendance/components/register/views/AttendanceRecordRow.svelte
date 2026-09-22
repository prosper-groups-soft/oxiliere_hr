<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import { Input } from "@/components/ui/input";
  import type { AttendanceRecord } from "../../../types/types";
  import type { AttendanceStatus } from "../../../constants/attendance.constants";
  import { useAdjustPunchMutation, useRecordPunchMutation } from "../../../queries/attendanceQueries";
  import { fade } from 'svelte/transition';
  import { STATUS_DOT_CONFIG } from "../../../constants/attendance.constants";

  
  let { record, onrequestjustify }: { record: AttendanceRecord; onrequestjustify?: (record: { id: string; employeeName: string; currentRemarks?: string }) => void } = $props();

  const statusConfig = STATUS_DOT_CONFIG;

  const palette = $derived(getAvatarPalette(record.employeeName));

  const profilePhoto = $derived(getMediaUrl(record.avatarUrl));

  const initials = $derived(
    record.firstName && record.lastName
      ? getInitials(record.firstName, record.lastName)
      : getInitials(...record.employeeName.split(' '))
  );

  const adjustPunchMutation = useAdjustPunchMutation();
  const recordPunchMutation = useRecordPunchMutation();

  const formatDuration = (minutes: number) => {
    const h = Math.floor(minutes / 60);
    const m = Math.round(minutes % 60);
    return `${h}h${m > 0 ? m.toString().padStart(2, '0') : ''}`;
  };

  const timeToMinutes = (time: string | null) => {
    if (!time) return null;
    const [h, m] = time.split(':').map(Number);
    return h * 60 + m;
  };

  // --- Logique de la Timeline Triple Segment ---
  const timeline = $derived.by(() => {
    const startDay = 7 * 60 + 30; // Fenêtre d'affichage : 07:30
    const endDay = 18 * 60 + 30;  // Fenêtre d'affichage : 18:30
    const totalMin = endDay - startDay;

    const checkIn = timeToMinutes(record.checkIn);
    const checkOut = timeToMinutes(record.checkOut);

    if (!checkIn) return null;

    const expectedIn = record.expectedIn ? timeToMinutes(record.expectedIn) : null;
    const expectedOut = record.expectedOut ? timeToMinutes(record.expectedOut) : null;

    if (expectedIn && expectedOut) {
      // --- Mode complet: planning disponible ---
      const lateDiff = (checkIn > expectedIn) ? (checkIn - expectedIn) : 0;
      const lateWidth = (lateDiff / totalMin) * 100;
      const isLate = lateDiff > 0;
      const workStart = Math.max(checkIn, expectedIn);
      const workEnd = checkOut ? Math.min(checkOut, expectedOut) : expectedOut;
      const normalWorkMin = Math.max(0, workEnd - workStart);
      const workWidth = (normalWorkMin / totalMin) * 100;
      const hasWork = normalWorkMin > 0;
      const overtimeDiff = (checkOut && checkOut > expectedOut) ? (checkOut - expectedOut) : 0;
      const overtimeWidth = (overtimeDiff / totalMin) * 100;
      const isOvertime = overtimeDiff > 0;

      return {
        lateDiff, lateWidth, lateStart: ((expectedIn - startDay) / totalMin) * 100, isLate,
        workWidth, workStart: ((workStart - startDay) / totalMin) * 100, hasWork,
        overtimeDiff, overtimeWidth, overtimeStart: ((expectedOut - startDay) / totalMin) * 100, isOvertime,
        hasExpected: true as const,
      };
    }

    // --- Mode simplifié: pas de planning, afficher seulement la plage réelle ---
    const workEnd = checkOut || startDay + totalMin;
    const workMin = Math.max(0, (workEnd - checkIn));
    return {
      lateDiff: 0, lateWidth: 0, lateStart: 0, isLate: false,
      workWidth: (workMin / totalMin) * 100, workStart: ((checkIn - startDay) / totalMin) * 100, hasWork: workMin > 0,
      overtimeDiff: 0, overtimeWidth: 0, overtimeStart: 0, isOvertime: false,
      hasExpected: false as const,
    };
  });

  let editingField = $state<'in' | 'out' | null>(null);
  let editValue = $state('');
  let tooltipPosition = $state<{ x: number; y: number } | null>(null);

  function startEdit(field: 'in' | 'out', current: string | null) {
    if (record.isLocked) return;
    editingField = field;
    editValue = current || '';
  }

  function saveEdit() {
    if (!editingField || !editValue) return;

    const punchId = editingField === 'in' ? record.checkInPunchId : record.checkOutPunchId;
    // Build an ISO timestamp from the register date + edited time (local)
    const adjusted = new Date(record.date + 'T' + editValue + ':00');
    // Adjust so the ISO string represents local time (not UTC)
    const localTimestamp = new Date(adjusted.getTime() - adjusted.getTimezoneOffset() * 60000).toISOString();

    if (punchId) {
      // Edit existing punch
      const startAt = editingField === 'in' ? localTimestamp : undefined;
      const endAt = editingField === 'out' ? localTimestamp : undefined;

      $adjustPunchMutation.mutate({
        punchId,
        data: { start_at: startAt, end_at: endAt },
      });
    } else {
      // Create new punch (no existing punch for this employee)
      $recordPunchMutation.mutate({
        timestamp: localTimestamp,
        punch_type: 'WORK',
        is_manual: true,
        employee_id: String(record.employeeId),
        latitude: null,
        longitude: null,
      });
    }
    editingField = null;
  }

  function updateTooltipPosition(event: MouseEvent) {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    tooltipPosition = {
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    };
  }

  function hideTooltip() {
    tooltipPosition = null;
  }
</script>


<div 
  in:fade={{ duration: 150 }}
  class="group/row flex items-center h-14 px-6 bg-white border-b border-slate-100 hover:bg-slate-50 transition-colors"
  onmouseenter={updateTooltipPosition}
  onmouseleave={hideTooltip}
  role="none"
>
  <div class="flex items-center w-[30%] min-w-0">
    <div class="relative" role="none" onclick={(e) => e.stopPropagation()}>
      <AvatarGallery
        name={record.employeeName}
        src={profilePhoto}
        onUpload={() => {}}
        disableUploadHover={false}
        iconSize={16}
        iconStroke={2}
        class="h-10 w-10 rounded-full shadow-fine"
      >
        <Avatar class="h-full w-full border border-slate-200">
          <AvatarImage src={profilePhoto} alt={record.employeeName} class="object-cover" />
          <AvatarFallback class={cn("text-[0.75rem] font-medium", palette.bg, palette.text)}>
            {initials}
          </AvatarFallback>
        </Avatar>
      </AvatarGallery>
    </div>
    <div class="flex flex-col ml-3 min-w-0">
      <span class="text-[0.88rem] text-slate-900 font-medium truncate leading-tight group-hover/row:text-primary">
        {record.employeeName}
      </span>
      <span class="text-[0.82rem] text-slate-400 truncate leading-tight">
        {record.jobTitle || record.orgUnit}
      </span>
    </div>
  </div>

  <div class="flex items-center w-[24%] gap-4">
    {@render TimeCell('in', record.checkIn, record.expectedIn, record.scheduleName)}
    {@render TimeCell('out', record.checkOut, record.expectedOut)}
  </div>

  <div class="flex items-center w-[21%] px-4">
    <div 
      class="group/timeline relative h-1 w-full bg-slate-100 rounded-full" 
      role="none"
    >
      {#if timeline}
        {#if timeline.isLate}
          <div class="absolute h-full bg-linear-to-r from-amber-300 to-amber-400 opacity-40 rounded-full" style="left: {timeline.lateStart}%; width: {timeline.lateWidth}%;"></div>
        {/if}
        {#if timeline.hasWork}
          <div class="absolute h-full bg-primary rounded-l-full" style="left: {timeline.workStart}%; width: {timeline.workWidth}%;"></div>
        {/if}
        {#if timeline.isOvertime}
          <div class="absolute h-full bg-linear-to-r from-emerald-400 to-emerald-500 rounded-r-full" style="left: {timeline.overtimeStart}%; width: {timeline.overtimeWidth}%;"></div>
        {/if}
      {/if}
    </div>
  </div>

  <div class="flex items-center justify-end w-[25%] gap-6">
    <div class="flex items-center gap-2">
      <span class="text-[0.875rem] text-slate-700 font-medium tabular-nums">
        {record.workDuration > 0 ? formatDuration(record.workDuration) : '--:--'}
      </span>
      {#if record.overtime > 0}
        <span class="text-[0.75rem] text-primary font-medium">+{formatDuration(record.overtime)}</span>
      {/if}
    </div>

    {@render StatusDot(record.status)}

    <button class={cn(
      "p-1.5 rounded-md transition-colors cursor-pointer",
      record.isLocked ? "text-slate-300" : "text-emerald-500 hover:bg-emerald-50"
    )}>
      <AppIcon name={record.isLocked ? "lock" : "unlock"} size={16} />
    </button>
  </div>

  {@render TimeTooltip()}
</div>


{#snippet TimeCell(field: 'in' | 'out', value: string | null, expected: string | null = null, scheduleName: string | null = null)}
  <div class="flex flex-col min-w-36">
    {#if editingField === field}
      <div class="flex items-center gap-1 w-full z-20 relative bg-white rounded-md shadow-sm">
        <Input 
          type="time"
          bind:value={editValue} 
          class="h-8 text-[0.875rem] flex-1 min-w-0 px-2 border-primary rounded-md shadow-none outline-none"
          onkeydown={(e) => { if (e.key === 'Enter') saveEdit(); }}
          autofocus
        />
        <button
          onclick={() => { saveEdit(); }}
          title="Valider"
          class="flex items-center justify-center h-6 w-6 rounded-md text-emerald-600 hover:bg-emerald-50 transition-colors cursor-pointer shrink-0"
        >
          <AppIcon name="check" size={14} strokeWidth={2.5} />
        </button>
        <button
          onclick={() => { editingField = null; }}
          title="Annuler"
          class="flex items-center justify-center h-6 w-6 rounded-md text-slate-400 hover:bg-slate-100 transition-colors cursor-pointer shrink-0"
        >
          <AppIcon name="x" size={14} />
        </button>
      </div>
    {:else}
      <button 
        onclick={() => startEdit(field, value)}
        class={cn(
          "text-[0.875rem] text-left tabular-nums transition-colors h-7 flex items-center gap-1 cursor-pointer", 
          value ? "text-slate-900" : "text-slate-300"
        )}
      >
        {value || '--:--'}
        {#if !record.isLocked && value}
          <AppIcon name="edit" size={16} class="opacity-0 group-hover/row:opacity-100 text-slate-400" />
        {/if}
      </button>
      {#if expected}
        <div class="flex items-center gap-1.5 mt-0.5">
          <span class="text-[0.7rem] text-slate-400 tabular-nums font-medium">{expected}</span>
          {#if field === 'in' && scheduleName}
            <span class="text-[0.65rem] bg-slate-100 text-slate-500 font-medium px-1 py-0.5 rounded-sm leading-none">{scheduleName}</span>
          {/if}
        </div>
      {/if}
    {/if}
  </div>
{/snippet}


{#snippet StatusDot(status: AttendanceStatus)}
  {@const config = statusConfig[status] || statusConfig["OFF"]}
  <div class="flex items-center gap-2 w-36 justify-end">
    {#if (status === 'ABSENT' || status === 'EXCUSED') && !record.isLocked}
      <button
        onclick={() => onrequestjustify?.({ id: record.id, employeeName: record.employeeName, currentRemarks: record.remarks })}
        title={status === 'EXCUSED' ? "Modifier la justification" : "Marquer comme absence justifiée"}
        class={cn(
          "text-[0.82rem] font-medium border px-2 py-0.5 rounded-md transition-colors cursor-pointer flex items-center gap-1",
          status === 'EXCUSED'
            ? "text-indigo-600 bg-indigo-50 hover:bg-indigo-100 border-indigo-200"
            : "text-teal-600 bg-teal-50 hover:bg-teal-100 border-teal-200"
        )}
      >
        {#if status === 'EXCUSED'}
          <AppIcon name="edit" size={12} class="inline mr-1" />
        {/if}
        {status === 'EXCUSED' ? "Modifier" : "Justifier"}
      </button>
    {/if}
    <span class={cn("text-[0.875rem] font-medium", config.textColor)}>{config.label}</span>
    <div class={cn("h-1.5 w-1.5 rounded-full", config.color)}></div>
  </div>
{/snippet}


{#snippet TimeTooltip()}
  {#if tooltipPosition && timeline}
    <div 
      class="fixed z-9999 pointer-events-none transition-opacity"
      style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px; transform: translateX(-50%) translateY(-100%);"
    >
      <div class="bg-slate-900 text-white text-[0.7rem] rounded px-2 py-1.5 shadow-xl flex flex-col gap-1 min-w-[150px]">
        {#if record.scheduleName}
          <div class="flex justify-between gap-4 border-b border-slate-700 pb-1 mb-1">
            <span class="text-slate-400 text-[0.82rem]">Planning:</span>
            <span class="font-bold text-[0.82rem]">{record.scheduleName}</span>
          </div>
        {/if}
        <div class="flex justify-between gap-4">
          <span class="text-slate-400 text-[0.82rem]">Attendu:</span>
          <span class="font-bold text-[0.82rem]">{record.expectedIn || '--:--'} - {record.expectedOut || '--:--'}</span>
        </div>
        <div class="flex justify-between gap-4">
          <span class="text-slate-400 text-[0.82rem]">Arrivée:</span>
          <span class="font-bold text-[0.82rem]">{record.checkIn || '--:--'}</span>
        </div>
        <div class="flex justify-between gap-4">
          <span class="text-slate-400 text-[0.82rem]">Départ:</span>
          <span class="font-bold text-[0.82rem]">{record.checkOut || '--:--'}</span>
        </div>
        {#if timeline.lateDiff > 0}
          <div class="flex justify-between text-amber-400">
            <span class="text-[0.82rem]">Retard:</span>
            <span class="text-[0.82rem]">{formatDuration(timeline.lateDiff)}</span>
          </div>
        {/if}
        {#if timeline.overtimeDiff > 0}
          <div class="flex justify-between text-emerald-400">
            <span class="text-[0.82rem]">Heures sup:</span>
            <span class="text-[0.82rem]">+{formatDuration(timeline.overtimeDiff)}</span>
          </div>
        {/if}
        <div class="border-t border-slate-700 mt-1 pt-1 flex justify-between">
          <span class="text-slate-400 text-[0.82rem]">Total:</span>
          <span class="text-primary text-[0.82rem]">{record.workDuration > 0 ? formatDuration(record.workDuration) : '--:--'}</span>
        </div>
      </div>
      <div class="w-2 h-2 bg-slate-900 rotate-45 absolute -bottom-1 left-1/2 -translate-x-1/2"></div>
    </div>
  {/if}
{/snippet}

