<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { jobsStore } from "@/features/jobs/stores/jobs.svelte";
  import { positionsStore } from "@/features/jobs/stores/positionsStore.svelte";
  import { cn } from "@/utilities/common/css";

  let { onAdd } = $props<{ onAdd: () => void }>();

  const SORT_LABELS: Record<string, string> = {
    name: "Titre",
    department: "Département",
    seniority: "Séniorité"
  };
</script>


<div class="flex items-center gap-3">
  <!-- Sort Menu -->
  <div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine h-7 overflow-hidden">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger class="h-full px-2.5 flex items-center gap-2 hover:bg-slate-50 transition-colors cursor-pointer shadow-fine">
        <AppIcon name="sort" size={15} class="text-slate-500" />
        <span class="text-[0.78rem] text-slate-700 font-medium">Trier: {SORT_LABELS[positionsStore.sortBy]}</span>
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="p-1 rounded-md shadow-fine bg-white border-slate-100">
        <DropdownMenu.RadioGroup value={positionsStore.sortBy} onValueChange={(v) => positionsStore.setSort(v)}>
          <DropdownMenu.RadioItem value="name" class="py-1.5 px-3 rounded-lg cursor-pointer text-xs pl-6">Titre (A-Z)</DropdownMenu.RadioItem>
          <DropdownMenu.RadioItem value="department" class="py-1.5 px-3 rounded-lg cursor-pointer text-xs pl-6">Département</DropdownMenu.RadioItem>
          <DropdownMenu.RadioItem value="seniority" class="py-1.5 px-3 rounded-lg cursor-pointer text-xs pl-6">Séniorité</DropdownMenu.RadioItem>
        </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
    <button onclick={() => positionsStore.toggleSortOrder()} class="w-7 h-full flex items-center justify-center border-l border-slate-100 hover:bg-slate-50 cursor-pointer">
      <div class={cn("transition-transform", positionsStore.sortOrder === 'desc' && "rotate-180")}>
        <AppIcon name="arrow-up" size={14} class={positionsStore.sortOrder === 'desc' ? "text-blue-600" : "text-slate-400"} />
      </div>
    </button>
  </div>

  <!-- Filter Dropdown -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="flex items-center gap-2 bg-white border border-slate-200 rounded-lg shadow-fine cursor-pointer h-7 px-2.5 hover:bg-slate-50 transition-all">
      <AppIcon name="filter" size={15} class={positionsStore.activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
      <span class="text-[0.78rem] text-slate-700 font-medium">Filtrer</span>
      {#if positionsStore.activeFiltersCount > 0}
        <div class="bg-blue-500 text-white text-[0.64rem] w-4 h-4 flex items-center justify-center rounded-full font-bold">
          {positionsStore.activeFiltersCount}
        </div>
      {/if}
    </DropdownMenu.Trigger>
    
    <DropdownMenu.Content align="end" class="w-64 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
      <div class="p-3 border-b border-slate-50 bg-slate-50/30">
        <input 
          type="text" 
          placeholder="Chercher..." 
          class="w-full text-[0.83rem] p-1.5 border rounded-md bg-white outline-none focus:border-blue-300"
        />
      </div>

      <div class="p-2 max-h-80 overflow-y-auto">
        {@render FilterSection("Département", jobsStore.departments.map(d => ({ id: d.id, name: d.name })), 'department')}
        <DropdownMenu.Separator class="my-2 bg-slate-50" />
        {@render FilterSection("Séniorité", jobsStore.seniorityLevels.map(l => ({ id: l.name, name: jobsStore.seniorityLabels[l.name] || l.name })), 'seniority')}
      </div>

      {#if positionsStore.activeFiltersCount > 0}
        <div class="p-2 bg-slate-50/50 border-t border-slate-100">
          <Button variant="ghost" onclick={() => positionsStore.resetFilters()} class="w-full h-8 text-[0.8rem] text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
            Réinitialiser tout
          </Button>
        </div>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <Button onclick={onAdd} class="bg-primary! hover:bg-primary/90 h-7 px-3 text-[0.78rem] text-white shadow-fine rounded-lg transition-all">
    <AppIcon name="plus" size={17} />
    Nouveau poste
  </Button>
</div>


{#snippet FilterSection(label: string, options: {id: any, name: string}[], filterKey: keyof typeof positionsStore.filters)}
  <DropdownMenu.Label class="text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={positionsStore.filters[filterKey].includes(option.id)}
      onCheckedChange={() => positionsStore.toggleFilter(filterKey, option.id)}
      class="rounded-lg py-1.5 px-2 text-[0.82rem] cursor-pointer pl-7"
    >
      {option.name}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}

