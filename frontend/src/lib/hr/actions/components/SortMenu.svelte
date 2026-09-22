<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";

  let { sortDefs, filterState }: { sortDefs: { options: { value: string; label: string }[] }; filterState: any } = $props();

  const currentSort = $derived(filterState.sortBy as string);
  const currentOrder = $derived(filterState.sortOrder as string);
</script>

<DropdownMenu.Root>
  <DropdownMenu.Trigger>
    <Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100">
      <AppIcon name="arrow-down-up" size={15} class="mr-1.5" /> Tri
    </Button>
  </DropdownMenu.Trigger>
  <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
    <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">Trier par</DropdownMenu.Label>
    {#each sortDefs.options as opt}
      {@const active = currentSort === opt.value}
      <DropdownMenu.Item onclick={() => filterState.setSort(opt.value, currentOrder)} class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", active && "bg-slate-50 font-medium"]}>
        <span class="text-[0.86rem]">{opt.label}</span>
        {#if active}<AppIcon name="check" size={14} class="text-slate-600" />{/if}
      </DropdownMenu.Item>
    {/each}
    <DropdownMenu.Separator />
    <DropdownMenu.Item onclick={() => filterState.setSort(currentSort, currentOrder === 'asc' ? 'desc' : 'asc')} class="text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between">
      <span class="text-[0.86rem]">Ordre {currentOrder === 'asc' ? 'croissant' : 'décroissant'}</span>
      <AppIcon name={currentOrder === 'asc' ? 'arrow-up' : 'arrow-down'} size={14} class="text-slate-600" />
    </DropdownMenu.Item>
  </DropdownMenu.Content>
</DropdownMenu.Root>
