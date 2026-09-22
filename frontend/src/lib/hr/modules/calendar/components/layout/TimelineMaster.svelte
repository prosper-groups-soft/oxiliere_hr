<script lang="ts">
  import { calendarStore } from "@/hr/modules/calendar/stores/calendar.svelte";
  import type { CalendarEvent } from "../../types/types";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import Tooltip from "../../components/elements/Tooltip.svelte";
  import DayTooltip from "../../components/elements/DayTooltip.svelte";
  import { MONTHS, STATUS_PILL, TYPE_ICONS, TIME_BADGE_COLORS, MAX_VISIBLE_EVENTS } from "../../constants/event.constants";
  import { cn } from '@/hr/utilities/common/css';
  import { formatTimeDisplay, formatDateRange } from "../../constants/event.helpers";


  let { 
    onDateClick,
    onEventClick,
    onRangeSelect,
    onEventMoved
  } = $props<{ 
    onDateClick?: (date: Date) => void,
    onEventClick?: (event: CalendarEvent) => void,
    onRangeSelect?: (start: Date, end: Date) => void,
    onEventMoved?: (event: CalendarEvent, newStartDate: string, newEndDate?: string) => void
  }>();

  let view = $derived(calendarStore.view);
  
  // Drag selection state
  let isSelecting = $state(false);
  let selectionStart = $state<Date | null>(null);
  let selectionEnd = $state<Date | null>(null);

  // Drag & drop state
  let draggedEvent = $state<CalendarEvent | null>(null);
  let dragOverDateStr = $state<string | null>(null);

  function formatDate(date: Date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  function handleDragStart(e: DragEvent, event: CalendarEvent) {
    draggedEvent = event;
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', event.id);
    }
  }

  function handleDragEnd() {
    draggedEvent = null;
    dragOverDateStr = null;
  }

  function handleDrop(targetDate: Date | null) {
    if (!draggedEvent || !targetDate) return;
    
    const oldStart = draggedEvent.defaultDate;
    const oldStartDate = new Date(oldStart + 'T12:00:00');
    const diffDays = Math.round((targetDate.getTime() - oldStartDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return;
    
    const newStart = formatDate(targetDate);
    let newEnd: string | undefined;
    
    if (draggedEvent.endDate && draggedEvent.endDate !== draggedEvent.defaultDate) {
      const oldEnd = new Date(draggedEvent.endDate + 'T12:00:00');
      const rangeDays = Math.round((oldEnd.getTime() - oldStartDate.getTime()) / (1000 * 60 * 60 * 24));
      const newEndDate = new Date(targetDate);
      newEndDate.setDate(newEndDate.getDate() + rangeDays);
      newEnd = formatDate(newEndDate);
    }
    
    onEventMoved?.(draggedEvent, newStart, newEnd);
    
    draggedEvent = null;
    dragOverDateStr = null;
  }

  function handleMouseDown(date: Date | null) {
    if (!date) return;
    isSelecting = true;
    selectionStart = date;
    selectionEnd = date;
  }

  function handleMouseEnter(date: Date | null) {
    if (isSelecting && date) {
      selectionEnd = date;
    }
  }

  function handleMouseUp() {
    if (isSelecting && selectionStart && selectionEnd) {
      const start = selectionStart < selectionEnd ? selectionStart : selectionEnd;
      const end = selectionStart < selectionEnd ? selectionEnd : selectionStart;
      
      if (start.getTime() === end.getTime()) {
        onDateClick?.(start);
      } else {
        onRangeSelect?.(start, end);
      }
    }
    
    isSelecting = false;
    selectionStart = null;
    selectionEnd = null;
  }

  function isDateInSelection(date: Date | null) {
    if (!date || !selectionStart || !selectionEnd) return false;
    const start = selectionStart <= selectionEnd ? selectionStart : selectionEnd;
    const end = selectionStart <= selectionEnd ? selectionEnd : selectionStart;
    return date >= start && date <= end;
  }

  function isToday(date: Date | null) {
    if (!date) return false;
    const today = new Date();
    return date.getDate() === today.getDate() && 
           date.getMonth() === today.getMonth() && 
           date.getFullYear() === today.getFullYear();
  }

  function isSaturday(date: Date | null) {
    if (!date) return false;
    return date.getDay() === 6;
  }

  function isSunday(date: Date | null) {
    if (!date) return false;
    return date.getDay() === 0;
  }

  function isNonWorkingDay(date: Date): boolean {
    const events = calendarStore.getEventsForDate(date);
    return events.some((e: CalendarEvent) => e.isWorkable === false && e.status === 'APPROVED');
  }

  function getDaysInMonth(year: number, month: number) {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    let startDayOfWeek = firstDay.getDay() || 7;
    startDayOfWeek -= 1; // 0=Lun, 6=Dim
    
    const days = [];
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push({ date: null, isCurrentMonth: false });
    }
    
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push({ 
        date: new Date(year, month, i), 
        isCurrentMonth: true 
      });
    }
    
    const totalSlots = Math.ceil(days.length / 7) * 7;
    while(days.length < totalSlots) {
       days.push({ date: null, isCurrentMonth: false });
    }
    
    return days;
  }

  function getMonthEventCount(year: number, month: number) {
    const start = new Date(year, month, 1);
    const end = new Date(year, month + 1, 0);
    const startStr = start.toISOString().split('T')[0];
    const endStr = end.toISOString().split('T')[0];
    
    return calendarStore.filteredEvents.filter(e => {
      const evtStart = e.defaultDate;
      const evtEnd = e.endDate || e.defaultDate;
      return evtEnd >= startStr && evtStart <= endStr;
    }).length;
  }

  let daysInView = $derived(getDaysInMonth(
    calendarStore.selectedDate.getFullYear(),
    calendarStore.selectedDate.getMonth()
  ));

  let currentYear = $derived(calendarStore.selectedDate.getFullYear());
</script>


<svelte:window onmouseup={handleMouseUp} />


<div class="h-full flex flex-col bg-white overflow-hidden shadow-none rounded-none">
  <div class="flex-1 overflow-auto bg-slate-50/50 select-none">
    {#if view === 'month'}
      {@render MonthView()}
    {:else}
      {@render YearView()}
    {/if}
  </div>
</div>


{#snippet MonthView()}
  <div class="grid grid-cols-7 gap-px bg-slate-200 border border-slate-200 rounded-none overflow-visible">
    <!-- En-têtes des jours -->
    {#each ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'] as day, i}
      <div class="bg-white p-2 text-center text-[0.7rem] font-bold uppercase tracking-wider border-b border-slate-100
        {i === 5 ? 'bg-blue-50/60 text-blue-400' : ''}
        {i === 6 ? 'bg-indigo-50/60 text-indigo-400' : ''}
        {i < 5 ? 'text-slate-400' : ''}">
        {day}
      </div>
    {/each}
    
    <!-- Cellules des jours -->
    {#each daysInView as day}
      {@render DayCell(day)}
    {/each}
  </div>
{/snippet}


{#snippet DayCell(day: any)}
  {@const dayEvents = day.date ? calendarStore.getEventsForDate(day.date) : []}
  {@const isSelected = isDateInSelection(day.date)}
  {@const saturday = day.date ? isSaturday(day.date) : false}
  {@const sunday = day.date ? isSunday(day.date) : false}
  {@const nonWorking = day.date ? isNonWorkingDay(day.date) : false}
  {@const visibleEvents = dayEvents.slice(0, MAX_VISIBLE_EVENTS)}
  {@const hiddenCount = dayEvents.length - MAX_VISIBLE_EVENTS}
  {@const dateStr = day.date ? formatDate(day.date) : null}
  {@const isDragOver = dateStr !== null && dragOverDateStr === dateStr}
  
  <div 
    class={cn(
      "p-1.5 min-h-[110px] hover:bg-slate-50/50 cursor-pointer transition-colors group flex flex-col items-start justify-start border-b border-r border-slate-100 last:border-r-0",
      day.isCurrentMonth ? (saturday ? "day-saturday" : sunday ? "day-sunday" : "bg-white") : "bg-slate-50 opacity-40",
      isSelected && "bg-primary/10 ring-1 ring-inset ring-primary/20",
      nonWorking && !saturday && !sunday && "bg-red-50/40",
      isDragOver && "ring-2 ring-primary/40 bg-primary/5",
    )}
  role="none"
  onmousedown={() => handleMouseDown(day.date)}
  onmouseenter={() => handleMouseEnter(day.date)}
  ondragover={(e) => {
    e.preventDefault();
    if (day.date) dragOverDateStr = formatDate(day.date);
  }}
  ondragleave={() => {
    dragOverDateStr = null;
  }}
  ondrop={(e) => {
    e.preventDefault();
    handleDrop(day.date);
  }}
  >
  {#if day.date}
    {@const today = isToday(day.date)}
    <div class="flex items-center justify-between w-full mb-1">
        <span class="text-[0.7rem] font-bold w-5 h-5 flex items-center justify-center rounded-full transition-all
          {today ? 'bg-primary text-white shadow-fine text-[0.65rem]' : 'text-slate-500 group-hover:text-primary'}
          {saturday && !today ? 'text-blue-400' : ''}
          {sunday && !today ? 'text-indigo-400' : ''}">
          {day.date.getDate()}
        </span>
        <div class="flex items-center gap-0.5">
          {#if nonWorking}
            <span class="text-[0.55rem] text-red-400 font-medium" title="Jour non travaillé">🚫</span>
          {/if}
          {#if today}
            <span class="text-[0.5rem] font-bold text-primary uppercase tracking-widest opacity-60">Auj.</span>
          {/if}
        </div>
      </div>

      <!-- Events List -->
      <div class="flex flex-col gap-0.5 w-full mt-auto">
        {#each visibleEvents as event}
          {@render Event(event)}        
        {/each}
        {#if hiddenCount > 0}
          <button
            class="text-[0.62rem] font-medium text-primary/70 hover:text-primary transition-colors text-left px-1 py-0.5"
            onclick={(e) => {
              e.stopPropagation();
              onDateClick?.(day.date!);
            }}
          >
            +{hiddenCount} autre{hiddenCount > 1 ? 's' : ''}
          </button>
        {/if}
      </div>
    {/if}
  </div>
{/snippet}


{#snippet Event(event: CalendarEvent)}
  {@const isPending = event.status === 'PENDING'}
  {@const isRejected = event.status === 'REJECTED'}
  {@const isApproved = event.status === 'APPROVED'}
  {@const isRecurrent = event.recurrent && event.recurrent !== 'NONE'}
  {@const hasRange = event.endDate && event.endDate !== event.defaultDate}
  {@const icon = TYPE_ICONS[event.type] || 'calendar'}
  {@const timeDisplay = formatTimeDisplay(event)}
  {@const rangeDisplay = formatDateRange(event)}
  {@const statusPill = STATUS_PILL[event.status || 'APPROVED'] || 'bg-slate-100 text-slate-400'}
  
  <Tooltip {event} placement="top">
    <div 
      class="relative px-2 py-1.5 rounded-[4px] text-[0.65rem] font-medium transition-all hover:scale-[1.03] hover:shadow-md shadow-fine border-l-[3px] border-transparent cursor-grab active:cursor-grabbing flex flex-col gap-0.5
      {isPending ? 'opacity-90' : ''}
      {isRejected ? 'opacity-50 line-through' : ''}"
      class:opacity-30={draggedEvent?.id === event.id}
      role="button"
      tabindex="0"
      draggable="true"
      ondragstart={(e) => handleDragStart(e, event)}
      ondragend={handleDragEnd}
      class:bg-red-50={event.type === 'holiday'}
      class:text-red-700={event.type === 'holiday'}
      class:border-l-red-400={event.type === 'holiday'}
      class:bg-amber-50={event.type === 'closure'}
      class:text-amber-700={event.type === 'closure'}
      class:border-l-amber-400={event.type === 'closure'}
      class:bg-indigo-50={event.type === 'training'}
      class:text-indigo-700={event.type === 'training'}
      class:border-l-indigo-400={event.type === 'training'}
      class:bg-purple-50={event.type === 'deadline'}
      class:text-purple-700={event.type === 'deadline'}
      class:border-l-purple-400={event.type === 'deadline'}
      class:bg-pink-50={event.type === 'anniversary'}
      class:text-pink-700={event.type === 'anniversary'}
      class:border-l-pink-400={event.type === 'anniversary'}
      class:bg-teal-50={event.type === 'leave'}
      class:text-teal-700={event.type === 'leave'}
      class:border-l-teal-400={event.type === 'leave'}
      onclick={(e) => {
        e.stopPropagation();
        onEventClick?.(event);
      }}
      onkeydown={(e) => e.key === 'Enter' && onEventClick?.(event)}
    >
      <!-- Ligne 1: Icône + Titre -->
      <div class="flex items-center gap-1 min-w-0 leading-tight">
        <AppIcon name={icon} size={16} class="shrink-0 opacity-70" />
        <span class="truncate flex-1 min-w-0 text-[0.82rem]">{event.title}</span>
      </div>

      <!-- Ligne 2: Badges metadata -->
      <div class="flex flex-wrap items-center gap-1">
        {#if isPending}
          <span class="text-[0.75rem] font-semibold px-1 py-0.5 rounded-sm {statusPill} leading-none">En attente</span>
        {:else if isRejected}
          <span class="text-[0.75rem] font-semibold px-1 py-0.5 rounded-sm {statusPill} leading-none">Rejeté</span>
        {:else if isApproved}
          <span class="text-[0.75rem] font-semibold px-1 py-0.5 rounded-sm {statusPill} leading-none">Approuvé</span>
        {/if}
        
        {#if timeDisplay}
          <span class="text-[0.75rem] px-1 py-0.5 rounded {TIME_BADGE_COLORS[event.type] || 'bg-slate-100 text-slate-400'} leading-none">
            {timeDisplay}
          </span>
        {/if}
        
        {#if hasRange && !timeDisplay}
          <span class="text-[0.75rem] px-1 py-0.5 rounded bg-slate-100 text-slate-400 leading-none">
            {rangeDisplay}
          </span>
        {/if}
        
        {#if isRecurrent}
          <span class="text-[0.75rem] px-1 py-0.5 rounded-sm bg-slate-100 text-slate-500 leading-none">Récurrent</span>
        {/if}
        
        {#if calendarStore.hasConflict(event.id)}
          <span class="text-[0.75rem] px-1 py-0.5 rounded-sm bg-red-50 text-red-500 leading-none animate-pulse">Conflit</span>
        {/if}
      </div>
    </div>
  </Tooltip>
{/snippet}


{#snippet YearView()}
  {@const now = new Date()}
  {@const currentMonthIdx = now.getMonth()}
  {@const isCurrentYear = currentYear === now.getFullYear()}
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
    {#each MONTHS as month, i}
      {@const monthDays = getDaysInMonth(currentYear, i)}
      {@const monthEventCount = getMonthEventCount(currentYear, i)}
      {@const isCurrent = isCurrentYear && i === currentMonthIdx}
      <div 
        class={cn(
          "border cursor-pointer transition-all flex flex-col rounded-lg shadow-fine hover:shadow-sm overflow-hidden min-h-[240px]",
          isCurrent
            ? "bg-primary/2 border-primary/40 ring-1 ring-primary/15 hover:border-primary/60"
            : "bg-white border-slate-200 hover:border-blue-300"
        )}
        onclick={() => {
          const d = new Date(currentYear, i, 1);
          calendarStore.selectedDate = d;
          calendarStore.view = 'month';
        }}
        role="button"
        tabindex="0"
        onkeydown={(e) => e.key === 'Enter' && (calendarStore.view = 'month')}
      >
        <div class={cn(
          "font-bold px-4 py-2 border-b flex items-center justify-between",
          isCurrent
            ? "text-primary bg-primary/5 border-primary/10"
            : "text-slate-900 bg-slate-50/50 border-slate-100"
        )}>
          <span class="text-[0.87rem]">{month}</span>
          <div class="flex items-center gap-1.5">
            {#if monthEventCount > 0}
              <span class={cn(
                "text-[0.6rem] font-semibold px-1.5 py-0.5 rounded-full leading-none",
                isCurrent
                  ? "bg-primary/10 text-primary"
                  : "bg-slate-100 text-slate-500"
              )}>
                {monthEventCount}
              </span>
            {/if}
            <span class="text-[0.65rem] text-slate-400 font-medium">{currentYear}</span>
          </div>
        </div>
        <div class="w-full flex-1 bg-white p-3">
          {@render MiniMonth(monthDays)}
        </div>
      </div>
    {/each}
  </div>
{/snippet}


{#snippet MiniMonth(days: any[])}
  <div class="grid grid-cols-7 gap-px h-full">
    {#each ['L', 'M', 'M', 'J', 'V', 'S', 'D'] as day, i}
      <div class="text-[0.55rem] font-bold text-center mb-1
        {i === 5 ? 'text-amber-400/60' : ''}
        {i === 6 ? 'text-rose-400/60' : ''}
        {i < 5 ? 'text-slate-300' : ''}">
        {day}
      </div>
    {/each}
    
    {#each days as day}
      <div class="aspect-square relative">
        {#if day.date}
          {@const today = isToday(day.date)}
          {@const saturday = isSaturday(day.date)}
          {@const sunday = isSunday(day.date)}
          {@const events = calendarStore.getEventsForDate(day.date)}
          
          <DayTooltip date={day.date} {events} placement="top">
            <div class="w-full h-full flex flex-col items-center justify-center">
              <span 
                class="text-[0.65rem] {today ? 'text-primary font-bold' : (day.isCurrentMonth ? (saturday ? 'text-blue-400' : sunday ? 'text-indigo-400' : 'text-slate-600') : 'text-slate-300')}"
              >
                {day.date.getDate()}
              </span>
              
              <!-- Event indicator dots -->
              {#if events.length > 0}
                <div class="absolute bottom-0 flex gap-px">
                  {#each events.slice(0, 3) as event}
                    <div 
                      class="w-1.5 h-1.5 rounded-full ring-1 ring-white"
                      class:bg-red-500={event.type === 'holiday'}
                      class:bg-amber-500={event.type === 'closure'}
                      class:bg-indigo-500={event.type === 'training'}
                      class:bg-purple-500={event.type === 'deadline'}
                      class:bg-pink-500={event.type === 'anniversary'}
                      class:bg-teal-500={event.type === 'leave'}
                    ></div>
                  {/each}
                  {#if events.length > 3}
                    <span class="text-[0.5rem] text-slate-400 font-bold leading-none">+{events.length - 3}</span>
                  {/if}
                </div>
              {/if}
            </div>
          </DayTooltip>
        {/if}
      </div>
    {/each}
  </div>
{/snippet}


<style>
  .day-saturday { background-color: #eff6ff; }
  .day-sunday { background-color: #eef2ff; }
</style>

