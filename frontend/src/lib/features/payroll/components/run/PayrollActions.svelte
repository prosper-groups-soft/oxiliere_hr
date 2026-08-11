<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { payrollStore } from '@/features/payroll/stores/payroll.svelte';
  import { RUN_LIST_STATUS_LABELS } from '@/features/payroll/types/types';

  import { orgService } from '@/features/jobs/services/org.service';

  // Unités organisationnelles chargées depuis le backend (/api/organization/units)
  let orgUnits = $state<string[]>([]);
  let isLoadingOrgUnits = $state(true);

  $effect(() => {
    let cancelled = false;
    orgService.listOrgUnits(1, 200)
      .then((res) => {
        if (cancelled) return;
        orgUnits = (res.results || []).map(u => u.name).sort((a, b) => a.localeCompare(b));
      })
      .catch(() => {})
      .finally(() => { if (!cancelled) isLoadingOrgUnits = false; });
    return () => { cancelled = true; };
  });


  let { onAdd, onExport }: { onAdd?: () => void; onExport?: () => void } = $props();


  const activeFiltersCount = $derived(payrollStore.activeCycleFiltersCount);

  // Périodes disponibles depuis la vraie liste d'exécutions
  const availablePeriods = $derived(
    [...new Set(payrollStore.runList.map(r => r.periodLabel))]
  );

  function isStatusActive(value: string): boolean {
    return payrollStore.cycleFilters.status === value;
  }

  function isPeriodActive(period: string): boolean {
    return payrollStore.cycleFilters.period === period;
  }

  function toggleStatus(status: string) {
    if (payrollStore.cycleFilters.status === status) {
      payrollStore.setCycleFilter('status', 'all' as any);
    } else {
      payrollStore.setCycleFilter('status', status as any);
    }
  }

  function togglePeriod(period: string) {
    if (payrollStore.cycleFilters.period === period) {
      payrollStore.setCycleFilter('period', '');
    } else {
      payrollStore.setCycleFilter('period', period);
    }
  }

  function clearStatus() {
    payrollStore.setCycleFilter('status', 'all' as any);
  }

  function clearPeriod() {
    payrollStore.setCycleFilter('period', '');
  }

  function isSortActive(by: string): boolean {
    return payrollStore.sortBy === by;
  }

  function isOrgUnitActive(unit: string): boolean {
    return payrollStore.cycleFilters.orgUnit === unit;
  }

  function toggleOrgUnit(unit: string) {
    if (payrollStore.cycleFilters.orgUnit === unit) {
      payrollStore.setCycleFilter('orgUnit', '');
    } else {
      payrollStore.setCycleFilter('orgUnit', unit);
    }
  }

  function clearOrgUnit() {
    payrollStore.setCycleFilter('orgUnit', '');
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

      <DropdownMenu.Item
        onclick={() => payrollStore.setSort('period')}
        class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", isSortActive('period') && "bg-slate-50 font-medium"]}
      >
        <span class="text-[0.86rem]">Période</span>
        {#if isSortActive('period')}
          <AppIcon name={payrollStore.sortOrder === 'asc' ? 'arrow-up' : 'arrow-down'} size={14} class="text-slate-600" />
        {/if}
      </DropdownMenu.Item>

      <DropdownMenu.Item
        onclick={() => payrollStore.setSort('status')}
        class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", isSortActive('status') && "bg-slate-50 font-medium"]}
      >
        <span class="text-[0.86rem]">Statut</span>
        {#if isSortActive('status')}
          <AppIcon name={payrollStore.sortOrder === 'asc' ? 'arrow-up' : 'arrow-down'} size={14} class="text-slate-600" />
        {/if}
      </DropdownMenu.Item>

      <DropdownMenu.Item
        onclick={() => payrollStore.setSort('employeeCount')}
        class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", isSortActive('employeeCount') && "bg-slate-50 font-medium"]}
      >
        <span class="text-[0.86rem]">Employés</span>
        {#if isSortActive('employeeCount')}
          <AppIcon name={payrollStore.sortOrder === 'asc' ? 'arrow-up' : 'arrow-down'} size={14} class="text-slate-600" />
        {/if}
      </DropdownMenu.Item>

      <DropdownMenu.Item
        onclick={() => payrollStore.setSort('grossTotal')}
        class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", isSortActive('grossTotal') && "bg-slate-50 font-medium"]}
      >
        <span class="text-[0.86rem]">Masse salariale</span>
        {#if isSortActive('grossTotal')}
          <AppIcon name={payrollStore.sortOrder === 'asc' ? 'arrow-up' : 'arrow-down'} size={14} class="text-slate-600" />
        {/if}
      </DropdownMenu.Item>
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
        <AppIcon name="circle" size={15} class="mr-1.5" />
        Statut
        {#if payrollStore.cycleFilters.status !== 'all'}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut du cycle
      </DropdownMenu.Label>

      {#each Object.entries(RUN_LIST_STATUS_LABELS) as [value, label]}
        {@const active = isStatusActive(value)}
        <DropdownMenu.Item
          onclick={() => toggleStatus(value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if payrollStore.cycleFilters.status !== 'all'}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={clearStatus}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Period Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="calendar" size={15} class="mr-1.5" />
        Période
        {#if payrollStore.cycleFilters.period}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Période
      </DropdownMenu.Label>

      {#each availablePeriods as period}
        {@const active = isPeriodActive(period)}
        <DropdownMenu.Item
          onclick={() => togglePeriod(period)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{period}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if payrollStore.cycleFilters.period}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={clearPeriod}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Org Unit Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="building-2" size={15} class="mr-1.5" />
        Unité
        {#if payrollStore.cycleFilters.orgUnit}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Unité organisationnelle
      </DropdownMenu.Label>

      {#if isLoadingOrgUnits}
        <div class="px-2 py-1.5 text-[0.82rem] text-slate-400">Chargement…</div>
      {:else if orgUnits.length === 0}
        <div class="px-2 py-1.5 text-[0.82rem] text-slate-400">Aucune unité</div>
      {:else}
        {#each orgUnits as unit}
          {@const active = isOrgUnitActive(unit)}
          <DropdownMenu.Item
            onclick={() => toggleOrgUnit(unit)}
            class={[
              "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
              active && "bg-slate-50 font-medium"
            ]}
          >
            <span class="text-[0.86rem]">{unit}</span>
            {#if active}
              <AppIcon name="check" size={14} class="text-slate-600" />
            {/if}
          </DropdownMenu.Item>
        {/each}
      {/if}

      {#if payrollStore.cycleFilters.orgUnit}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={clearOrgUnit}
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
      onclick={() => payrollStore.resetCycleFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>

  <!-- Export CSV Button -->
  {#if onExport}
    <Button
      variant="ghost"
      size="sm"
      onclick={onExport}
      class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
    >
      <AppIcon name="download" size={15} class="mr-1.5" />
      CSV
    </Button>
  {/if}

  <!-- New Cycle Button -->
  <Button
    onclick={onAdd}
    variant="default"
    size="sm"
    class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
  >
    <AppIcon name="plus" size={15} />
    Nouveau cycle
  </Button>
</div>

