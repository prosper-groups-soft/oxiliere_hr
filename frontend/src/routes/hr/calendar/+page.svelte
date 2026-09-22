<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import CalendarActions from "@/hr/calendar/components/layout/CalendarActions.svelte";
  import TimelineMaster from "@/hr/calendar/components/layout/TimelineMaster.svelte";
  import EventSheet from "@/hr/calendar/components/sheets/EventSheet.svelte";
  import MonthlyStats from "@/hr/calendar/components/elements/MonthlyStats.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import { calendarStore } from "@/hr/calendar/stores/calendar.svelte";
  import { Button } from "@/components/ui/button";
  import { ui } from "@/stores/ui.svelte";
  import type { CalendarEvent } from "@/hr/calendar/types/types";
  import { EVENT_TYPE_LABELS, EVENT_TYPE_COLORS } from "@/hr/calendar/types/types";
  import { MONTHS } from "@/hr/calendar/constants/event.constants";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";

  
  let isSheetOpen = $state(false);
  let selectedEvent = $state<CalendarEvent | null>(null);
  let selectedDateForSheet = $state<string | null>(null);
  let selectedDateEndForSheet = $state<string | null>(null);

  /**
   * GLOBAL ACTION REGISTRATION for Tools + Actions + Stats
   * Tous les snippets sont toujours enregistrés.
   * MonthlyStats gère lui-même sa visibilité selon la vue.
   */
  $effect(() => {
    ui.addActions('calendar-stats', MonthlyStatsAction);
    ui.addActions('calendar', CalendarActionsSnippet);

    return () => {
      ui.removeActions('calendar');
      ui.removeActions('calendar-stats');
    };
  });

  function getFilterLabel(key: string, value: any) {
    if (key === 'type') return EVENT_TYPE_LABELS[value as keyof typeof EVENT_TYPE_LABELS] || value;
    return value;
  }

  function openNewEvent() {
    selectedEvent = null;
    selectedDateForSheet = new Date().toISOString().split('T')[0];
    selectedDateEndForSheet = null;
    isSheetOpen = true;
  }

  const formatDate = (date: Date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  function handleDateClick(date: Date) {
    selectedEvent = null;
    selectedDateForSheet = formatDate(date);
    selectedDateEndForSheet = null;
    isSheetOpen = true;
  }

  function handleRangeSelect(start: Date, end: Date) {
    selectedEvent = null;
    selectedDateForSheet = formatDate(start);
    selectedDateEndForSheet = formatDate(end);
    isSheetOpen = true;
  }

  function handleEventClick(event: CalendarEvent) {
    selectedEvent = event;
    selectedDateForSheet = event.defaultDate;
    selectedDateEndForSheet = event.endDate || null;
    isSheetOpen = true;
  }

  function handleSearchResultClick(event: CalendarEvent) {
    const [y, m, d] = event.defaultDate.split('-').map(Number);
    calendarStore.selectedDate = new Date(y, m - 1, d);
    calendarStore.view = 'month';
    // handleEventClick(event);
    calendarStore.searchQuery = '';
  }

  async function handleEventMoved(event: CalendarEvent, newStartDate: string, newEndDate?: string) {
    try {
      await calendarStore.updateEvent(event.id, {
        defaultDate: newStartDate,
        endDate: newEndDate,
      });
    } catch (err) {
      // L'erreur est déjà gérée par le service via notification toast
    }
  }

  function formatSearchResultDate(event: CalendarEvent) {
    const start = new Date(event.defaultDate);
    const year = start.getFullYear();
    if (event.endDate && event.endDate !== event.defaultDate) {
      const end = new Date(event.endDate);
      if (start.getMonth() === end.getMonth()) {
        const monthStr = start.toLocaleDateString('fr-FR', { month: 'short' });
        return `${start.getDate()}-${end.getDate()} ${monthStr} ${year}`;
      } else {
        const startStr = start.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
        const endStr = end.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
        return `${startStr} - ${endStr} ${year}`;
      }
    }
    return start.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
  }
</script>


<svelte:head>
  <title>Oxiliere HR - Calendrier</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={{ type: calendarStore.typeFilters }}
      activeFiltersCount={calendarStore.typeFilters.length}
      getDisplayLabel={getFilterLabel}
      onRemove={(key, value) => {
        if (key === 'type') calendarStore.toggleTypeFilter(value as any);
      }}
      onReset={() => calendarStore.resetFilters()}
      class="px-4 pt-0.5 pb-2"
    />

    <main class="flex-1 min-h-0">
      <TimelineMaster 
        onDateClick={handleDateClick}
        onEventClick={handleEventClick}
        onRangeSelect={handleRangeSelect}
        onEventMoved={handleEventMoved}
      />
    </main>
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex items-center justify-between gap-4">
      <!-- Left: Title & Nav -->
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1 bg-slate-50 rounded-lg border border-slate-200/60 shadow-fine">
          <Button variant="ghost" size="icon" class="h-8 w-8 rounded-md hover:bg-white hover:shadow-sm" onclick={() => calendarStore.prevPeriod()}>
            <AppIcon name="prev" size={16} />
          </Button>
          <Button variant="ghost" class="h-8 px-3 text-xs font-medium rounded-md hover:bg-white hover:shadow-sm" onclick={() => calendarStore.goToday()}>
            Aujourd'hui
          </Button>
          <Button variant="ghost" size="icon" class="h-8 w-8 rounded-md hover:bg-white hover:shadow-sm" onclick={() => calendarStore.nextPeriod()}>
            <AppIcon name="next" size={16} />
          </Button>
        </div>
        
        <h1 class="text-[0.9rem] font-bold text-slate-900">
          {#if calendarStore.view === 'year'}
            {calendarStore.selectedDate.getFullYear()}
          {:else}
            {MONTHS[calendarStore.selectedDate.getMonth()]} {calendarStore.selectedDate.getFullYear()}
          {/if}
        </h1>
      </div>

      <!-- Right: Search -->
      <div class="flex-1 max-w-120 ml-auto relative">
        <SearchBar 
          bind:value={calendarStore.searchQuery} 
          placeholder="Rechercher un évènement..." 
          class="w-full"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => calendarStore.searchQuery = ""}
        />

        {#if calendarStore.searchQuery.trim()}
          <div class="absolute top-full right-0 left-0 mt-1.5 bg-white border border-slate-200 rounded-xl shadow-lg z-50 max-h-80 overflow-y-auto p-1.5 flex flex-col gap-1">
            {#if calendarStore.loading}
              <div class="py-8 px-4 flex items-center justify-center">
                <AnimateSpin class="border-primary size-5 text-slate-500 text-xs" text="Recherche en cours..." />
              </div>
            {:else if calendarStore.filteredEvents.length === 0}
              <div class="py-8 px-4 flex flex-col items-center justify-center text-center gap-2 text-slate-400 select-none">
                <div class="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 border border-slate-100">
                  <AppIcon name="search-x" size={26} class="stroke-[1.2]" />
                </div>
                <div class="flex flex-col gap-0.5">
                  <span class="text-[0.82rem] font-semibold text-slate-700">Aucun résultat trouvé</span>
                  <span class="text-[0.76rem] text-slate-400 max-w-[200px] leading-relaxed">Nous n'avons trouvé aucun événement correspondant à votre recherche.</span>
                </div>
              </div>
            {:else}
              {#each calendarStore.filteredEvents as event}
                {@const colorStyles = EVENT_TYPE_COLORS[event.type] || EVENT_TYPE_COLORS.training}
                <button 
                  class="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors text-left w-full cursor-pointer"
                  onclick={(e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    handleSearchResultClick(event);
                  }}
                >
                  <div class="flex items-center gap-2.5 min-w-0">
                    <span class="w-2.5 h-2.5 rounded-full shrink-0 {colorStyles.dot}"></span>
                    <div class="min-w-0">
                      <div class="text-[0.85rem] font-medium text-slate-700 truncate">{event.title}</div>
                      <div class="text-[0.75rem] text-slate-400">
                        {EVENT_TYPE_LABELS[event.type] || event.type}
                      </div>
                    </div>
                  </div>
                  <div class="text-[0.75rem] font-medium text-slate-500 whitespace-nowrap ml-2">
                    {formatSearchResultDate(event)}
                  </div>
                </button>
              {/each}
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
{/snippet}


<EventSheet 
  bind:open={isSheetOpen} 
  bind:calendarEvent={selectedEvent} 
  initialDate={selectedDateForSheet}
  initialEndDate={selectedDateEndForSheet}
/>


{#snippet CalendarActionsSnippet()}
  <CalendarActions 
    onNewEvent={openNewEvent}
  />
{/snippet}


{#snippet MonthlyStatsAction()}
  <MonthlyStats />
{/snippet}

