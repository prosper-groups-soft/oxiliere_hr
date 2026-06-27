<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { transitionsStore } from "../../../../stores/transitionsStore.svelte";
  import { TRANSITION_TYPE_OPTIONS } from "../../../../constants/transition.constants";
  import type { TransitionType } from "../../../../types/types";

  let {
    onAdd
  }: {
    onAdd: () => void;
  } = $props();

  const activeFiltersCount = $derived(transitionsStore.activeFiltersCount);

  function selectType(type: TransitionType) {
    transitionsStore.setTransitionType(type);
  }

  function isTypeActive(type: TransitionType): boolean {
    return transitionsStore.filters.transitionType[0] === type;
  }

  function clearTypeFilter() {
    transitionsStore.clearTransitionType();
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
        <AppIcon name="arrow-left-right" size={15} class="mr-1.5" />
        Type
        {#if transitionsStore.filters.transitionType.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {transitionsStore.filters.transitionType.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Type de mouvement
      </DropdownMenu.Label>

      {#each TRANSITION_TYPE_OPTIONS as type}
        {@const active = isTypeActive(type.value)}
        <DropdownMenu.Item
          onclick={() => selectType(type.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={type.icon} size={16} class={type.color} />
            {type.label}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if transitionsStore.filters.transitionType.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearTypeFilter()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => transitionsStore.resetFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- Add Button -->
  <Button
    onclick={onAdd}
    variant="default"
    size="sm"
    class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
  >
    <AppIcon name="plus" size={15} />
    Nouveau mouvement
  </Button>
</div>

