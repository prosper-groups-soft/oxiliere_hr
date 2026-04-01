<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { Input } from "@/components/ui/input";
  import type { AttendanceRecord } from "../../../types/types";
  import { fade } from 'svelte/transition';

  let { record } = $props<{ record: AttendanceRecord }>();

  const statusConfig: Record<string, { label: string, color: string, textColor: string }> = {
    "PRESENT": { label: "Présent", color: "bg-emerald-500", textColor: "text-emerald-600" },
    "LATE": { label: "Retard", color: "bg-amber-500", textColor: "text-amber-600" },
    "ABSENT": { label: "Absent", color: "bg-rose-500", textColor: "text-rose-600" },
    "LEAVE": { label: "Congé", color: "bg-blue-500", textColor: "text-blue-600" },
    "OFF": { label: "Repos", color: "bg-slate-400", textColor: "text-slate-500" }
  };

  const palette = $derived(getAvatarPalette(record.employeeName));

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
    const expectedIn = timeToMinutes(record.expectedIn || "08:00") || (8 * 60);
    const expectedOut = timeToMinutes(record.expectedOut || "17:00") || (17 * 60);

    if (!checkIn) return null;

    // 1. Retard
    const lateDiff = (record.status === "LATE" && checkIn > expectedIn) ? (checkIn - expectedIn) : 0;
    const lateWidth = (lateDiff / totalMin) * 100;

    // 2. Travail Normal
    const workStart = Math.max(checkIn, expectedIn);
    const workEnd = checkOut ? Math.min(checkOut, expectedOut) : expectedOut;
    const normalWorkMin = Math.max(0, workEnd - workStart);
    const workWidth = (normalWorkMin / totalMin) * 100;

    // 3. Overtime
    const overtimeDiff = (checkOut && checkOut > expectedOut) ? (checkOut - expectedOut) : 0;
    const overtimeWidth = (overtimeDiff / totalMin) * 100;

    return {
      lateDiff, lateWidth, lateStart: ((expectedIn - startDay) / totalMin) * 100,
      workWidth, workStart: ((workStart - startDay) / totalMin) * 100,
      overtimeDiff, overtimeWidth, overtimeStart: ((expectedOut - startDay) / totalMin) * 100
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
    if (editingField === 'in') record.checkIn = editValue;
    else if (editingField === 'out') record.checkOut = editValue;
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
  class="group flex items-center h-14 px-6 bg-white border-b border-slate-100 hover:bg-slate-50 transition-colors"
>
  <div class="flex items-center w-[30%] min-w-0">
    <Avatar class="h-10 w-10 shrink-0 rounded-full overflow-hidden border border-slate-200">
      <AvatarImage src={record.avatarUrl} alt={record.employeeName} />
      <AvatarFallback class={cn("text-[0.75rem] font-medium", palette.bg, palette.text)}>
        {getInitials(...record.employeeName.split(' '))}
      </AvatarFallback>
    </Avatar>
    <div class="flex flex-col ml-3 min-w-0">
      <span class="text-[0.88rem] text-slate-900 font-medium truncate leading-tight group-hover:text-primary">{record.employeeName}</span>
      <span class="text-[0.85rem] text-slate-400 truncate mt-0.5">{record.department}</span>
    </div>
  </div>

  <div class="flex items-center w-[20%] gap-8">
    {@render TimeCell('in', record.checkIn)}
    {@render TimeCell('out', record.checkOut)}
  </div>

  <div class="flex items-center w-[25%] px-6">
    <div 
      class="group/timeline relative h-1 w-full bg-slate-100 rounded-full cursor-help" 
      onmouseenter={updateTooltipPosition} 
      onmouseleave={hideTooltip}
      role="none"
    >
      {#if timeline}
        {#if timeline.lateWidth > 0}
          <div class="absolute h-full bg-amber-400 opacity-40" style="left: {timeline.lateStart}%; width: {timeline.lateWidth}%;"></div>
        {/if}
        <div class="absolute h-full bg-primary" style="left: {timeline.workStart}%; width: {timeline.workWidth}%;"></div>
        {#if timeline.overtimeWidth > 0}
          <div class="absolute h-full bg-emerald-500" style="left: {timeline.overtimeStart}%; width: {timeline.overtimeWidth}%;"></div>
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
</div>


{#if tooltipPosition && timeline}
  <div 
    class="fixed z-9999 pointer-events-none transition-opacity"
    style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px; transform: translateX(-50%) translateY(-100%);"
  >
    <div class="bg-slate-900 text-white text-[0.7rem] rounded px-2 py-1.5 shadow-xl flex flex-col gap-1 min-w-[150px]">
      <div class="flex justify-between gap-4">
        <span class="text-slate-400 text-[0.82rem]">Attendu:</span>
        <span class="font-bold text-[0.82rem]">{record.expectedIn} - {record.expectedOut}</span>
      </div>
      {#if timeline.lateDiff > 0}
        <div class="flex justify-between text-amber-400">
          <span class="text-[0.82rem]">Retard:</span>
          <span class="text-[0.82rem]">{formatDuration(timeline.lateDiff)}</span>
        </div>
      {/if}
      {#if timeline.overtimeDiff > 0}
        <div class="flex justify-between text-emerald-400">
          <span class="text-[0.82rem]">Sup:</span>
          <span class="text-[0.82rem]">+{formatDuration(timeline.overtimeDiff)}</span>
        </div>
      {/if}
      <div class="border-t border-slate-700 mt-1 pt-1 flex justify-between">
        <span class="text-slate-400 text-[0.82rem]">Total:</span>
        <span class="text-primary text-[0.82rem]">{formatDuration(record.workDuration)}</span>
      </div>
    </div>
    <div class="w-2 h-2 bg-slate-900 rotate-45 absolute -bottom-1 left-1/2 -translate-x-1/2"></div>
  </div>
{/if}


{#snippet TimeCell(field: 'in' | 'out', value: string | null)}
  <div class="flex flex-col min-w-14">
    {#if editingField === field}
      <Input 
        bind:value={editValue} 
        class="h-7 text-[0.875rem] w-18 px-1 border-primary rounded-md shadow-none outline-none"
        onblur={saveEdit}
        autofocus
      />
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
          <AppIcon name="edit-3" size={16} class="opacity-0 group-hover/row:opacity-100 text-slate-400" />
        {/if}
      </button>
    {/if}
  </div>
{/snippet}


{#snippet StatusDot(status: string)}
  {@const config = statusConfig[status] || statusConfig["OFF"]}
  <div class="flex items-center gap-2 w-24 justify-end">
    <span class={cn("text-[0.875rem] font-medium", config.textColor)}>{config.label}</span>
    <div class={cn("h-1.5 w-1.5 rounded-full", config.color)}></div>
  </div>
{/snippet}

