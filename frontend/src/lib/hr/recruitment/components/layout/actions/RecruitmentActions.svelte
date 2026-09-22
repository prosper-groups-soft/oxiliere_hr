<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { recruitmentStore } from "@/hr/recruitment/stores/recruitment.svelte";
  import { CAMPAIGN_STATUS_OPTIONS } from "@/hr/recruitment/constants/recruitment";

  let { onAdd } = $props<{
    onAdd: () => void;
  }>();

  const activeFiltersCount = $derived(recruitmentStore.activeFiltersCount);

  // Fonctions de filtre
  function clearStatus() {
    recruitmentStore.campaignFilters.status = [];
  }

  function isStatusActive(value: string): boolean {
    return recruitmentStore.campaignFilters.status.includes(value);
  }
</script>


<div class="flex items-center gap-2">
  <!-- Sort Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="arrow-down-up" size={15} class="mr-1.5" />
        Tri
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Trier par
      </DropdownMenu.Label>

      {@render SortOption("Titre (A-Z)", "title", "asc")}
      {@render SortOption("Titre (Z-A)", "title", "desc")}
      {@render SortOption("Poste", "jobName", "asc")}
      {@render SortOption("Type", "type", "asc")}
      {@render SortOption("Statut", "status", "asc")}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Status Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="user-check" size={15} class="mr-1.5" />
        Statut
        {#if recruitmentStore.campaignFilters.status.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {recruitmentStore.campaignFilters.status.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut campagne
      </DropdownMenu.Label>

      {#each CAMPAIGN_STATUS_OPTIONS as option}
        {@const active = isStatusActive(option.value)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.toggleCampaignFilter('status', option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{option.label}</span>
          {#if active}
            <AppIcon name="check" size={16} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if recruitmentStore.campaignFilters.status.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearStatus()}
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
      onclick={() => recruitmentStore.resetCampaignFilters()}
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
    Nouvelle campagne
  </Button>
</div>


{#snippet SortOption(label: string, sortBy: string, order: 'asc' | 'desc')}
  {@const isActive = recruitmentStore.sortBy === sortBy && recruitmentStore.sortOrder === order}
  <DropdownMenu.Item
    onclick={() => {
      recruitmentStore.sortBy = sortBy;
      recruitmentStore.sortOrder = order;
      // Reset to page 1 when changing sort
      recruitmentStore.currentPage = 1;
    }}
    class={[
      "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
      isActive && "bg-slate-50 font-medium"
    ]}
  >
    <span class="text-[0.86rem]">{label}</span>
    {#if isActive}
      <AppIcon name="check" size={14} class="text-slate-600" />
    {/if}
  </DropdownMenu.Item>
{/snippet}

