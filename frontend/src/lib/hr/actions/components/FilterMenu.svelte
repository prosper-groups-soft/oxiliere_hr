<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import type { FilterDef } from "../types";

  let { filterDefs, filterState }: { filterDefs: FilterDef[]; filterState: any } = $props();

  const activeCount = $derived(filterState.activeFiltersCount as number);
</script>

<DropdownMenu.Root>
  <DropdownMenu.Trigger>
    <Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100">
      <AppIcon name="filter" size={15} class="mr-1.5" /> Filtres
      {#if activeCount>0}<span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">{activeCount}</span>{/if}
    </Button>
  </DropdownMenu.Trigger>
  <DropdownMenu.Content align="end" class="w-72 p-2 z-100 max-h-96 overflow-y-auto">
    <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">Filtres ({activeCount} actifs)</DropdownMenu.Label>
    {#each filterDefs as def}
      <div class="px-2 py-1.5">
        <div class="flex items-center gap-1.5 text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider mb-1">
          {#if def.icon}<AppIcon name={def.icon} size={12} />{/if}{def.label}
        </div>
        {#each def.options as opt}
          {@const active = (filterState.filters[def.key] as string[] ?? []).includes(opt.value)}
          <DropdownMenu.Item onclick={() => filterState.toggleFilter(def.key, opt.value)} class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", active && "bg-slate-50 font-medium"]}>
            <span class="text-[0.86rem]">{opt.label}</span>
            {#if active}<AppIcon name="check" size={14} class="text-slate-600" />{/if}
          </DropdownMenu.Item>
        {/each}
      </div>
      <DropdownMenu.Separator />
    {/each}
    {#if activeCount>0}
      <DropdownMenu.Item onclick={() => filterState.resetFilters()} class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer">
        <AppIcon name="x" size={16} class="text-inherit" /> Réinitialiser tout
      </DropdownMenu.Item>
    {/if}
  </DropdownMenu.Content>
</DropdownMenu.Root>
