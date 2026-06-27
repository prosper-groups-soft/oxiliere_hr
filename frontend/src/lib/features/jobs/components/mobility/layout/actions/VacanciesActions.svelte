<script lang="ts">
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { vacanciesStore } from "../../../../stores/vacanciesStore.svelte";
  import { VACANCY_PRIORITY_OPTIONS, VACANCY_STATUS_OPTIONS } from "../../../../constants/vacancy.constants";
  import type { VacancyPriority, VacancyStatus } from "../../../../types/types";

  let {
    onAdd
  }: {
    onAdd: () => void;
  } = $props();

  const activeFiltersCount = $derived(vacanciesStore.activeFiltersCount);

  function selectPriority(priority: VacancyPriority) {
    vacanciesStore.setPriority(priority);
  }

  function selectStatus(status: VacancyStatus) {
    vacanciesStore.setStatus(status);
  }

  function isPriorityActive(priority: VacancyPriority): boolean {
    return vacanciesStore.filters.priority === priority;
  }

  function isStatusActive(status: VacancyStatus): boolean {
    return vacanciesStore.filters.status === status;
  }

  function clearPriority() {
    vacanciesStore.clearPriority();
  }

  function clearStatus() {
    vacanciesStore.clearStatus();
  }
</script>


<div class="flex items-center gap-2">
  <!-- Priority Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="triangle-alert" size={15} class="mr-1.5" />
        Priorité
        {#if vacanciesStore.filters.priority}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            1
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Priorité
      </DropdownMenu.Label>

      {#each VACANCY_PRIORITY_OPTIONS as priority}
        {@const active = isPriorityActive(priority.value)}
        <DropdownMenu.Item
          onclick={() => selectPriority(priority.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={priority.icon} size={16} class={priority.color} />
            {priority.label}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if vacanciesStore.filters.priority}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearPriority()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
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
        <AppIcon name="tag" size={15} class="mr-1.5" />
        Statut
        {#if vacanciesStore.filters.status}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            1
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut
      </DropdownMenu.Label>

      {#each VACANCY_STATUS_OPTIONS as status}
        {@const active = isStatusActive(status.value)}
        <DropdownMenu.Item
          onclick={() => selectStatus(status.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={status.icon} size={16} class={status.color} />
            {status.label}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if vacanciesStore.filters.status}
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
      onclick={() => vacanciesStore.resetFilters()}
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
    Nouveau besoin
  </Button>
</div>
