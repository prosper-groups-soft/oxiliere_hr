<script lang="ts">
  import { crossfade, scale } from 'svelte/transition';
  import { cubicInOut } from 'svelte/easing';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import ManualPunchSheet from "./sheets/ManualPunchSheet.svelte";
  import { attendanceStore } from "../../stores/attendance.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { cn } from "@/utilities/common/css";

  let showManualPunch = $state(false);
  let dateInput = $state<HTMLInputElement | null>(null);

  const activeFiltersCount = $derived(
    attendanceStore.filters.department.length + attendanceStore.filters.status.length
  );
  
  const departments = $derived([...new Set(employeeStore.employees.map(e => e.department))]);
  const statuses = [
    { value: 'PRESENT', label: 'Présent' },
    { value: 'LATE', label: 'Retard' },
    { value: 'ABSENT', label: 'Absent' },
    { value: 'LEAVE', label: 'Congé' },
    { value: 'OFF', label: 'Repos' }
  ];

  const dateQuickActions = [
    { label: 'Hier', value: -1 },
    { label: "Aujourd'hui", value: 0 },
    { label: 'Demain', value: 1 }
  ];

  const [send, receive] = crossfade({
    duration: 300,
    easing: cubicInOut
  });

  function handleQuickDate(offset: number) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    attendanceStore.filters.dateRange.from = d.toISOString().split('T')[0];
  }

  function handleDateChange(e: Event) {
    const val = (e.target as HTMLInputElement).value;
    if (val) {
      attendanceStore.filters.dateRange.from = val;
    }
  }

  function resetFilters() {
    attendanceStore.filters.department = [];
    attendanceStore.filters.status = [];
  }
</script>


<div class="flex flex-col gap-4 px-4 py-3 bg-white border-b border-slate-100 pr-8">
  <div class="flex items-center justify-between gap-6">
    <!-- Search & Filters -->
    <div class="flex items-center gap-3 flex-1">
      <SearchBar 
        bind:value={attendanceStore.filters.search}
        placeholder="Rechercher un employé..."
        class="w-125"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
        iconSize={22}
      />
    </div>

    <!-- Date Navigation Shell -->
    <div class="flex items-center gap-2.5">
      <div class="relative flex items-center bg-[#f5f6f7] p-1 py-0.5 rounded-xl border border-slate-200/40">
        {#each dateQuickActions as action}
          {@render DateButton(action.label, action.value)}
        {/each}
        
        <div class="w-px h-4 bg-slate-300 mx-1"></div>
        
        <div class="relative h-7.5 w-7.5">
          <Button 
            variant="ghost" 
            size="icon" 
            onclick={() => dateInput?.showPicker()}
            class="h-7.5 w-7.5 rounded-lg hover:bg-white hover:shadow-sm"
          >
            <AppIcon name="calendar" size={16} class="text-slate-500" />
          </Button>
          <input 
            type="date"
            bind:this={dateInput}
            onchange={handleDateChange}
            value={attendanceStore.filters.dateRange.from}
            class="absolute inset-0 opacity-0 pointer-events-none"
          />
        </div>
      </div>

      <div class="h-6 w-px bg-slate-200 mx-1"></div>

      <div class="flex items-center gap-2">
        <Button 
          onclick={() => showManualPunch = true}
          variant="outline" 
          class="h-7.5 px-4 rounded-lg border-slate-200 text-slate-600 gap-2 text-[0.85rem] shadow-fine hover:bg-slate-50 transition-all inline-flex items-center justify-center"
        >
          <AppIcon name="plus" size={17} class="text-slate-400" />
          Pointage
        </Button>

        <!-- Filtres Dropdown -->
        <DropdownMenu.Root>
          <DropdownMenu.Trigger class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all outline-none">
            <AppIcon name="filter" size={16} class={activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
            <span class="text-[0.85rem] text-slate-700">Filtres</span>
            {#if activeFiltersCount > 0}
              <div transition:scale={{ duration: 200, start: 0.8 }}>
                <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
                  {activeFiltersCount}
                </Badge>
              </div>
            {/if}
          </DropdownMenu.Trigger>

          <DropdownMenu.Content align="end" class="w-64 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden z-50">
            <div class="p-2 max-h-80 overflow-y-auto">
              {@render FilterSection("Département", departments, "department")}
              <DropdownMenu.Separator class="my-2 bg-slate-50" />
              {@render FilterSection("Statut", statuses.map(s => s.label), "status", statuses)}
            </div>

            {#if activeFiltersCount > 0}
              <div class="p-2 bg-slate-50/50 border-t border-slate-100">
                <Button variant="ghost" onclick={resetFilters} class="w-full h-8 text-[0.84rem] bg-white text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
                  Réinitialiser tout
                </Button>
              </div>
            {/if}
          </DropdownMenu.Content>
        </DropdownMenu.Root>
      </div>
    </div>
  </div>
</div>


<ManualPunchSheet bind:open={showManualPunch} />


{#snippet FilterSection(label: string, options: string[], filterKey: 'department' | 'status', fullOptions?: typeof statuses)}
  <DropdownMenu.Label class="text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option, i}
    {@const value = fullOptions ? fullOptions[i].value : option}
    <DropdownMenu.CheckboxItem 
      checked={attendanceStore.filters[filterKey].includes(value as any)}
      onCheckedChange={() => attendanceStore.toggleFilter(filterKey, value)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {option}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}


{#snippet DateButton(label: string, offset: number)}
  <!-- Simple calculation for active state checking -->
  {@const targetDate = (() => {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    return d.toISOString().split('T')[0];
  })()}
  {@const isActive = attendanceStore.filters.dateRange.from === targetDate}
  
  <Button 
    variant="ghost"
    onclick={() => handleQuickDate(offset)}
    class={cn(
      "relative h-7.5 px-3 rounded-lg transition-all cursor-pointer z-10 flex items-center justify-center border-none shadow-none",
      isActive ? "text-slate-900 bg-white" : "text-slate-500 hover:text-slate-700 hover:bg-slate-200/50"
    )}
  >
    <span class="relative z-20 text-[0.8rem] font-medium leading-none">{label}</span>
    {#if isActive}
      <div 
        in:receive={{ key: 'active-date' }}
        out:send={{ key: 'active-date' }}
        class="absolute inset-0 bg-white rounded-lg shadow-fine border border-slate-200/50 z-10"
      ></div>
    {/if}
  </Button>
{/snippet}

