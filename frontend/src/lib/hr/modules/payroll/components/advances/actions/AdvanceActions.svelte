<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { advancesStore } from "@/hr/modules/payroll/stores/advances/advancesStore.svelte";
  import { ADVANCE_RISK_LABELS, ADVANCE_STATUS_LABELS, type AdvanceRiskLevel, type AdvanceStatus } from "@/hr/modules/payroll/types/types";

  
  let { onAdd }: { onAdd: () => void } = $props();

  // État partagé via le store (lu aussi par la page pour filtrer les avances)
  const riskLevelFilters = $derived(advancesStore.riskLevelFilters);
  const statusFilters = $derived(advancesStore.statusFilters);
  const activeFiltersCount = $derived(riskLevelFilters.length + statusFilters.length);

  const RISK_OPTIONS: { value: AdvanceRiskLevel; icon: string; iconClass: string }[] = [
    { value: 'LOW',    icon: 'shield-check',   iconClass: 'text-emerald-500' },
    { value: 'MEDIUM', icon: 'alert-triangle', iconClass: 'text-amber-500' },
    { value: 'HIGH',   icon: 'alert-circle',   iconClass: 'text-rose-500' },
  ];

  const STATUS_OPTIONS: { value: AdvanceStatus; icon: string; iconClass: string }[] = [
    { value: 'DRAFT',    icon: 'file-text',     iconClass: 'text-slate-500' },
    { value: 'PENDING',  icon: 'clock',        iconClass: 'text-amber-500' },
    { value: 'APPROVED', icon: 'check-circle',  iconClass: 'text-emerald-500' },
    { value: 'ACTIVE',   icon: 'zap',          iconClass: 'text-blue-500' },
    { value: 'REJECTED', icon: 'circle-x',     iconClass: 'text-rose-500' },
    { value: 'CLOSED',   icon: 'lock',         iconClass: 'text-slate-500' },
  ];

  function isRiskActive(level: AdvanceRiskLevel): boolean {
    return riskLevelFilters.includes(level);
  }

  function isStatusActive(status: AdvanceStatus): boolean {
    return statusFilters.includes(status);
  }
</script>


<div class="flex items-center gap-2">
  <!-- Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="filter" size={15} class="mr-1.5" />
        Risque
        {#if activeFiltersCount > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activeFiltersCount}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Niveau de risque
      </DropdownMenu.Label>

      {#each RISK_OPTIONS as option}
        {@const active = isRiskActive(option.value)}
        <DropdownMenu.Item
          onclick={() => advancesStore.toggleRiskLevel(option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={option.icon} size={16} class={option.iconClass} />
            {ADVANCE_RISK_LABELS[option.value]}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if activeFiltersCount > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => advancesStore.resetFilters()}
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
        <AppIcon name="list-filter" size={15} class="mr-1.5" />
        Statut
        {#if statusFilters.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {statusFilters.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut de la demande
      </DropdownMenu.Label>

      {#each STATUS_OPTIONS as option}
        {@const active = isStatusActive(option.value)}
        <DropdownMenu.Item
          onclick={() => advancesStore.toggleStatus(option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={option.icon} size={16} class={option.iconClass} />
            {ADVANCE_STATUS_LABELS[option.value]}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if statusFilters.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => advancesStore.statusFilters = []}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge (risque + statut cumulés) -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => advancesStore.resetFilters()}
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
    Nouvelle demande
  </Button>
</div>
