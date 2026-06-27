<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { calendarStore } from "@/features/calendar/stores/calendar.svelte";
  import { Badge } from "@/components/ui/badge";
  import { scale } from 'svelte/transition';
  import { TYPE_OPTIONS } from "@/features/calendar/constants/event.constants";

  let activeFiltersCount = $derived(calendarStore.typeFilters.length);
</script>


<div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden">
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="h-7.5 px-3 flex items-center justify-start gap-2 cursor-pointer outline-none hover:bg-slate-50 transition-all border-none bg-transparent">
      <div class="flex shrink-0 items-center justify-center">
        <AppIcon name="filter" size={17} class="text-slate-500" />
      </div>
      
      <span class="text-[0.84rem] text-slate-700 truncate">
        Filtres
      </span>
      
      {#if activeFiltersCount > 0}
        <div transition:scale={{ duration: 200, start: 0.8 }}>
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {activeFiltersCount}
          </Badge>
        </div>
      {/if}
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 min-w-48">
      <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
        Type d'événement
      </DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      
      {#each TYPE_OPTIONS as option}
        <DropdownMenu.CheckboxItem 
          checked={calendarStore.typeFilters.includes(option.value)}
          onCheckedChange={() => calendarStore.toggleTypeFilter(option.value)}
          class="py-2 pr-3 pl-8 rounded-lg cursor-pointer text-[0.85rem]!"
        >
          {option.label}
        </DropdownMenu.CheckboxItem>
      {/each}

      {#if activeFiltersCount > 0}
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
        <DropdownMenu.Item 
          onclick={() => calendarStore.resetFilters()}
          class="py-2 px-3 rounded-lg cursor-pointer text-[0.85rem]! text-red-500 hover:text-red-600! hover:bg-red-50/50! font-medium"
        >
          <AppIcon name="trash" size={16} class="text-inherit" />
          Effacer les filtres
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
</div>

