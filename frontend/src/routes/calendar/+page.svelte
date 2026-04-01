<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import CalendarFilters from "@/features/calendar/components/elements/CalendarFilters.svelte";
  import TimelineMaster from "@/features/calendar/components/layout/TimelineMaster.svelte";
  import ViewSwitcher from "@/features/calendar/components/layout/ViewSwitcher.svelte";
  import EventSheet from "@/features/calendar/components/sheets/EventSheet.svelte";
  import ReplicateSheet from "@/features/calendar/components/sheets/ReplicateSheet.svelte";
  import MonthlyStats from "@/features/calendar/components/elements/MonthlyStats.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { calendarStore } from "@/features/calendar/stores/calendar.svelte";
  import { Button } from "@/components/ui/button";
  import { ui } from "@/stores/ui.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { CalendarEvent } from "@/features/calendar/types/types";

  let isSheetOpen = $state(false);
  let isReplicateSheetOpen = $state(false);
  let selectedEvent = $state<CalendarEvent | null>(null);
  let selectedDateForSheet = $state<string | null>(null);
  let selectedDateEndForSheet = $state<string | null>(null);

  /**
   * GLOBAL ACTION REGISTRATION for Stats
   */
  $effect(() => {
    if (calendarStore.view === 'month') {
      ui.addActions('calendar-stats', MonthlyStatsAction);
    } else {
      ui.removeActions('calendar-stats');
    }
    return () => ui.removeActions('calendar-stats');
  });

  const monthsList = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
  ];

  const typeLabels: Record<string, string> = {
    'holiday': 'Jour Férié',
    'closure': 'Fermeture Entreprise',
    'training': 'Formation'
  };

  function getFilterLabel(key: string, value: any) {
    if (key === 'type') return typeLabels[value] || value;
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
</script>


<svelte:head>
  <title>Oxiliere HR - Calendrier</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <main class="flex-1 min-h-0">
    <TimelineMaster 
      onDateClick={handleDateClick}
      onEventClick={handleEventClick}
      onRangeSelect={handleRangeSelect}
    />
  </main>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-3 pb-3 pt-3 px-4 mr-4">
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
            {monthsList[calendarStore.selectedDate.getMonth()]} {calendarStore.selectedDate.getFullYear()}
          {/if}
        </h1>
      </div>

      <!-- Right: Controls -->
      <div class="flex items-center gap-3">
        <div class="w-120">
          <SearchBar 
            bind:value={calendarStore.searchQuery} 
            placeholder="Rechercher un évènement..." 
            class="w-120"
            inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
            iconSize={22}
            onClear={() => calendarStore.searchQuery = ""}
          />
        </div>
        
        <ViewSwitcher />
        <CalendarFilters />
        
        <div class="h-8 w-px bg-slate-200 mx-1"></div>

        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            {#snippet child({ props })}
              <Button 
                {...props}
                variant="outline" 
                size="sm" 
                class="h-8 flex items-center shadow-fine rounded-lg bg-white border-slate-200 text-slate-600 gap-2 px-3"
              >
                <AppIcon name="settings" size={17} class="text-slate-500" />
                <span class="text-[0.84rem]">Outils</span>
              </Button>
            {/snippet}
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end" class="w-48 shadow-fine">
            <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
              Outils
            </DropdownMenu.Label>
            <DropdownMenu.Item onSelect={() => isReplicateSheetOpen = true} class="gap-2 cursor-pointer py-2 text-[0.85rem]!">
              <AppIcon name="copy" size={16} class="text-indigo-500" />
              <span class="text-[0.85rem]!">Répliquer l'année</span>
            </DropdownMenu.Item>
            <DropdownMenu.Item 
              onSelect={async () => {
                const count = await calendarStore.importHolidays(calendarStore.selectedDate.getFullYear());
                if (count > 0) {
                  import("@/stores/notification.svelte").then(({ notification }) => {
                    notification.toast.success(`${count} jours fériés importés.`);
                  });
                }
              }} 
              class="gap-2 cursor-pointer py-2 text-[0.85rem]!"
            >
              <AppIcon name="download" size={16} class="text-emerald-500" />
              <span class="text-[0.85rem]!">Importer fériés (RDC)</span>
            </DropdownMenu.Item>
            <DropdownMenu.Separator />
            <DropdownMenu.Item 
              onSelect={() => {
                notification.confirm({
                  title: 'Réinitialiser l\'année ?',
                  message: `Cette action supprimera tous les événements de l'année ${calendarStore.selectedDate.getFullYear()}. Cette opération est irréversible.`,
                  type: 'danger',
                  yesText: 'Oui, tout supprimer',
                  onYes: () => {
                    calendarStore.resetYear(calendarStore.selectedDate.getFullYear());
                    notification.toast.success(`Année ${calendarStore.selectedDate.getFullYear()} réinitialisée.`);
                  }
                });
              }} 
              class="gap-2 cursor-pointer py-2 text-red-500 hover:text-red-600! hover:bg-red-50! text-[0.85rem]!"
            >
              <AppIcon name="trash" size={16} class="text-inherit" />
              <span class=" text-[0.85rem]!">Réinitialiser l'année</span>
            </DropdownMenu.Item>
          </DropdownMenu.Content>
        </DropdownMenu.Root>

        <Button 
          variant="default" 
          size="sm" 
          class="h-8 flex items-center shadow-fine rounded-lg"
          onclick={openNewEvent}
        >
          <AppIcon name="plus" size={17} />
          <span class="text-[0.83rem]">Événement</span>
        </Button>
      </div>
    </div>

    {#if calendarStore.typeFilters.length > 0}
      <FilterChips 
        filters={{ type: calendarStore.typeFilters }}
        activeFiltersCount={calendarStore.typeFilters.length}
        getDisplayLabel={getFilterLabel}
        onRemove={(key, value) => {
          if (key === 'type') calendarStore.toggleTypeFilter(value as any);
        }}
        onReset={() => calendarStore.resetFilters()}
        class="px-0 pt-1"
      />
    {/if}
  </div>
{/snippet}


<EventSheet 
  bind:open={isSheetOpen} 
  bind:calendarEvent={selectedEvent} 
  initialDate={selectedDateForSheet}
  initialEndDate={selectedDateEndForSheet}
/>


<ReplicateSheet bind:open={isReplicateSheetOpen} />


{#snippet MonthlyStatsAction()}
  <MonthlyStats />
{/snippet}

