<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { calendarStore } from "@/hr/modules/calendar/stores/calendar.svelte";
  import { notification } from "@/hr/stores/notification.svelte";
  import { TYPE_OPTIONS } from "@/hr/modules/calendar/constants/event.constants";
  import type { EventType } from "@/hr/modules/calendar/types/types";

  
  let { 
    onNewEvent
  } = $props<{
    onNewEvent?: () => void
  }>();

  const activeFiltersCount = $derived(calendarStore.typeFilters.length);
  let view = $derived(calendarStore.view);

  function setView(v: 'month' | 'year') {
    calendarStore.view = v;
  }

  function isTypeActive(value: EventType): boolean {
    return calendarStore.typeFilters.includes(value);
  }

  function toggleType(value: EventType) {
    calendarStore.toggleTypeFilter(value);
  }

  function clearAllFilters() {
    calendarStore.resetFilters();
  }

  async function handleResetHolidays() {
    notification.confirm({
      title: "Réinitialiser les jours fériés ?",
      message: `Cette action va re-supprimer tous les jours fériés (PUBLIC_HOLIDAY) et les réimporter depuis les données officielles. Les autres événements (formations, fermetures, échéances, anniversaires) ne seront pas affectés.`,
      type: 'danger',
      yesText: 'Oui, réinitialiser les fériés',
      onYes: async () => {
        await calendarStore.resetHolidays();
      }
    });
  }
</script>


<div class="flex items-center gap-2">
  <!-- Type Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="filter" size={15} class="mr-1.5" />
        Type
        {#if activeFiltersCount > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activeFiltersCount}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-52 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Type d'événement
      </DropdownMenu.Label>

      {#each TYPE_OPTIONS as option}
        {@const active = isTypeActive(option.value)}
        <DropdownMenu.Item
          onclick={() => toggleType(option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={option.icon} size={16} class="text-slate-500" />
            {option.label}
          </span>
          {#if active}
            <AppIcon name="check" size={16} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if activeFiltersCount > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearAllFilters()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser les filtres
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => clearAllFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- View Switcher -->
  <div class="flex items-center gap-1 bg-slate-100/80 p-0.5 rounded-lg relative">
    <div 
      class="absolute bg-white shadow-sm rounded-md transition-all duration-300 ease-in-out pointer-events-none h-[calc(100%-4px)] top-0.5"
      style="width: 52px; left: {view === 'month' ? '2px' : '58px'};"
    ></div>
    <button 
      class="w-[52px] h-6 text-[0.75rem] font-medium rounded-md cursor-pointer transition-colors relative z-10 {view === 'month' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}"
      onclick={() => setView('month')}
    >
      Mois
    </button>
    <button 
      class="w-[52px] h-6 text-[0.75rem] font-medium rounded-md cursor-pointer transition-colors relative z-10 {view === 'year' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}"
      onclick={() => setView('year')}
    >
      Année
    </button>
  </div>

  <!-- Tools Dropdown -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="settings" size={15} class="mr-1.5" />
        Outils
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-52 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Gestion
      </DropdownMenu.Label>

      <DropdownMenu.Item 
        onclick={handleResetHolidays}
        class="text-[0.86rem] py-1.5 cursor-pointer flex items-center gap-2 text-amber-600 hover:bg-amber-50/30! hover:text-amber-700!"
      >
        <AppIcon name="refresh" size={16} class="text-inherit" />
        <span>Réinitialiser les fériés</span>
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- New Event Button -->
  {#if onNewEvent}
    <Button
      onclick={onNewEvent}
      variant="default"
      size="sm"
      class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
    >
      <AppIcon name="plus" size={15} />
      Événement
    </Button>
  {/if}
</div>
