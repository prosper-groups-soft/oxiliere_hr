<script lang="ts">
  import { calendarStore } from "@/features/calendar/stores/calendar.svelte";
  import type { CalendarEvent } from "../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  let { 
    onDateClick,
    onEventClick,
    onRangeSelect
  } = $props<{ 
    onDateClick?: (date: Date) => void,
    onEventClick?: (event: CalendarEvent) => void,
    onRangeSelect?: (start: Date, end: Date) => void
  }>();

  let view = $derived(calendarStore.view);
  
  // Drag selection state
  let isSelecting = $state(false);
  let selectionStart = $state<Date | null>(null);
  let selectionEnd = $state<Date | null>(null);

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

  const months = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
  ];

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
  <div class="grid grid-cols-7 gap-px bg-slate-200 border border-slate-200 rounded-none overflow-hidden">
    <!-- En-têtes des jours -->
    {#each ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'] as day}
      <div class="bg-white p-2 text-center text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
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
  
  <div 
    class="p-2 min-h-[120px] hover:bg-slate-50/50 cursor-pointer transition-colors group flex flex-col items-start justify-start border-b border-r border-slate-100 last:border-r-0 {day.isCurrentMonth ? 'bg-white' : 'bg-slate-50 opacity-40'} {isSelected ? 'bg-primary/10! ring-1 ring-inset ring-primary/20' : ''}"
    role="none"
    onmousedown={() => handleMouseDown(day.date)}
    onmouseenter={() => handleMouseEnter(day.date)}
  >
    {#if day.date}
      {@const today = isToday(day.date)}
      <div class="flex items-center justify-between w-full mb-2">
        <span class="text-[0.75rem] font-bold w-6 h-6 flex items-center justify-center rounded-full transition-all {today ? 'bg-primary text-white shadow-fine' : 'text-slate-500 group-hover:text-primary group-hover:bg-primary/10'}">
          {day.date.getDate()}
        </span>
        {#if today}
          <span class="text-[0.6rem] font-bold text-primary uppercase tracking-widest mr-1 opacity-60">Auj.</span>
        {/if}
      </div>

      <!-- Events List -->
      <div class="flex flex-col gap-1 w-full mt-auto">
        {#each dayEvents as event}
          {@render Event(event)}        
        {/each}
      </div>
    {/if}
  </div>
{/snippet}


{#snippet Event(event: CalendarEvent)}
  <div 
    class="px-1.5 py-0.5 rounded-md text-[0.67rem] font-medium transition-all hover:scale-[1.02] shadow-fine border cursor-pointer flex items-center justify-between gap-1"
    role="button"
    tabindex="0"
    class:bg-red-50={event.type === 'holiday'}
    class:text-red-700={event.type === 'holiday'}
    class:border-red-200={event.type === 'holiday'}

    class:bg-amber-50={event.type === 'closure'}
    class:text-amber-700={event.type === 'closure'}
    class:border-amber-200={event.type === 'closure'}

    class:bg-indigo-50={event.type === 'training'}
    class:text-indigo-700={event.type === 'training'}
    class:border-indigo-200={event.type === 'training'}
    onclick={(e) => {
      e.stopPropagation();
      onEventClick?.(event);
    }}
    onkeydown={(e) => e.key === 'Enter' && onEventClick?.(event)}
  >
    <span class="truncate text-[0.72rem]">{event.title}</span>
    {#if calendarStore.hasConflict(event.id)}
      <div class="shrink-0 text-red-500 animate-pulse" title="Attention: Conflit avec un férié ou une fermeture">
        <AppIcon name="info" size={10} />
      </div>
    {/if}
  </div>
{/snippet}


{#snippet YearView()}
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
    {#each months as month, i}
      <div 
        class="bg-white border border-slate-200 hover:border-blue-300 cursor-pointer transition-all flex flex-col rounded-lg shadow-fine hover:shadow-sm overflow-hidden min-h-[240px]"
        onclick={() => {
          const d = new Date(currentYear, i, 1);
          calendarStore.selectedDate = d;
          calendarStore.view = 'month';
        }}
        role="button"
        tabindex="0"
        onkeydown={(e) => e.key === 'Enter' && (calendarStore.view = 'month')}
      >
        <div class="font-bold text-slate-900 px-4 py-2 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
          <span class="text-[0.87rem]">{month}</span>
          <span class="text-[0.65rem] text-slate-400 font-medium">{currentYear}</span>
        </div>
        <div class="w-full flex-1 bg-white p-3">
          {@render MiniMonth(getDaysInMonth(currentYear, i))}
        </div>
      </div>
    {/each}
  </div>
{/snippet}


{#snippet MiniMonth(days: any[])}
  <div class="grid grid-cols-7 gap-px h-full">
    {#each ['L', 'M', 'M', 'J', 'V', 'S', 'D'] as day}
      <div class="text-[0.55rem] font-bold text-slate-300 text-center mb-1">
        {day}
      </div>
    {/each}
    
    {#each days as day}
      <div class="aspect-square flex flex-col items-center justify-center relative">
        {#if day.date}
          {@const today = isToday(day.date)}
          <span class="text-[0.65rem] {today ? 'text-primary font-bold' : (day.isCurrentMonth ? 'text-slate-600' : 'text-slate-300')}">
            {day.date.getDate()}
          </span>
          
          <!-- Event indicator dot -->
          {@const events = calendarStore.filteredEvents.filter(e => {
            const dStr = day.date.toISOString().split('T')[0];
            return dStr >= e.defaultDate && dStr <= (e.endDate || e.defaultDate);
          })}
          
          {#if events.length > 0}
            <div class="absolute bottom-0.5 flex gap-0.5">
              {#each events.slice(0, 3) as event}
                <div 
                  class="w-1 h-1 rounded-full"
                  class:bg-red-500={event.type === 'holiday'}
                  class:bg-amber-500={event.type === 'closure'}
                  class:bg-indigo-500={event.type === 'training'}
                ></div>
              {/each}
            </div>
          {/if}
        {/if}
      </div>
    {/each}
  </div>
{/snippet}

