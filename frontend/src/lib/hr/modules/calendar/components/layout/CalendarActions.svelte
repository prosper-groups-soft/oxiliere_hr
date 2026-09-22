<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { calendarStore } from "@/hr/modules/calendar/stores/calendar.svelte";
  import { notification } from "@/hr/stores/notification.svelte";
  import { TYPE_OPTIONS } from "@/hr/modules/calendar/constants/event.constants";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import type { FilterDef } from "@/hr/actions/types";

  let { filterState = calendarStore, onNewEvent } = $props<{ filterState?: any; onNewEvent?: () => void }>();

  const filterDefs = $derived<FilterDef[]>([
    { key: 'type', label: "Type d'événement", icon: 'filter', mode: 'multi', options: TYPE_OPTIONS.map(o => ({ value: o.value, label: o.label })) }
  ]);

  const fs = $derived({
    get filters() { return { type: filterState.typeFilters ?? filterState.filters?.type ?? [] }; },
    get activeFiltersCount() { return filterState.typeFilters?.length ?? filterState.activeFiltersCount ?? 0; },
    toggleFilter: (_k: string, v: string) => filterState.toggleTypeFilter?.(v) ?? filterState.toggleFilter?.('type', v),
    resetFilters: () => filterState.resetFilters()
  });

  let view = $derived(calendarStore.view);
  function setView(v: 'month' | 'year') { calendarStore.view = v; }
  async function handleResetHolidays() {
    notification.confirm({
      title: "Réinitialiser les jours fériés ?",
      message: `Cette action va re-supprimer tous les jours fériés (PUBLIC_HOLIDAY) et les réimporter depuis les données officielles.`,
      type: 'danger',
      yesText: 'Oui, réinitialiser les fériés',
      onYes: async () => { await calendarStore.resetHolidays(); }
    });
  }
</script>

<ActionBar>
  <FilterMenu filterDefs={filterDefs} filterState={fs} />
  {#if fs.activeFiltersCount > 0}
    <button onclick={() => fs.resetFilters()} class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer">
      <span class="text-[0.8rem]">{fs.activeFiltersCount} filtre{fs.activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <div class="flex items-center gap-1 bg-slate-100/80 p-0.5 rounded-lg relative">
    <div class="absolute bg-white shadow-sm rounded-md transition-all duration-300 ease-in-out pointer-events-none h-[calc(100%-4px)] top-0.5" style="width: 52px; left: {view === 'month' ? '2px' : '58px'};"></div>
    <button class="w-[52px] h-6 text-[0.75rem] font-medium rounded-md cursor-pointer transition-colors relative z-10 {view === 'month' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}" onclick={() => setView('month')}>Mois</button>
    <button class="w-[52px] h-6 text-[0.75rem] font-medium rounded-md cursor-pointer transition-colors relative z-10 {view === 'year' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}" onclick={() => setView('year')}>Année</button>
  </div>

  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100">
        <AppIcon name="settings" size={15} class="mr-1.5" /> Outils
      </Button>
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-52 p-1 z-100">
      <DropdownMenu.Item onclick={handleResetHolidays} class="text-[0.86rem] py-1.5 cursor-pointer flex items-center gap-2 text-amber-600">
        <AppIcon name="refresh" size={16} /> Réinitialiser les fériés
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  {#if onNewEvent}
    <Button onclick={onNewEvent} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg">
      <AppIcon name="plus" size={15} /> Événement
    </Button>
  {/if}
</ActionBar>
