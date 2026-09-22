<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { payrollStore } from '@/hr/payroll/stores/payroll.svelte';
  import { RUN_LIST_STATUS_LABELS } from '@/hr/payroll/types/types';
  import { orgService } from '@/hr/jobs/services/org.service';
  import { goToActiveOrNewPayroll } from '@/hr/payroll/utils/goToActiveOrNewPayroll';


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

  const activeFiltersCount = $derived(payrollStore.activeCycleFiltersCount);

  // ── Période : plage de dates avec brouillon local + bouton Appliquer ──
  let draftStart = $state(payrollStore.cycleFilters.periodStart || '');
  let draftEnd = $state(payrollStore.cycleFilters.periodEnd || '');
  let periodOpen = $state(false);

  // Quand le dropdown s'ouvre, resync le brouillon sur le store (ex: après reset externe)
  $effect(() => {
    if (periodOpen) {
      draftStart = payrollStore.cycleFilters.periodStart || '';
      draftEnd = payrollStore.cycleFilters.periodEnd || '';
    }
  });

  const hasPeriodFilter = $derived(!!payrollStore.cycleFilters.periodStart || !!payrollStore.cycleFilters.periodEnd || !!payrollStore.cycleFilters.period);
  const draftHasValue = $derived(!!draftStart || !!draftEnd);
  const draftIsValid = $derived(!draftStart || !draftEnd || draftStart <= draftEnd);

  function formatFR(iso: string): string {
    if (!iso) return '';
    const d = new Date(iso + 'T00:00:00');
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  function periodChipLabel(): string {
    const s = payrollStore.cycleFilters.periodStart;
    const e = payrollStore.cycleFilters.periodEnd;
    if (s && e) return `${formatFR(s)} → ${formatFR(e)}`;
    if (s) return `Depuis ${formatFR(s)}`;
    if (e) return `Jusqu'au ${formatFR(e)}`;
    if (payrollStore.cycleFilters.period) return payrollStore.cycleFilters.period;
    return '';
  }

  function applyPeriod() {
    // Nettoie l'ancien filtre exact `period` au profit de la plage
    if (payrollStore.cycleFilters.period) payrollStore.setCycleFilter('period', '');
    payrollStore.setCycleFilter('periodStart', draftStart);
    // petit délai pour que le store batch correctement ; on set les deux d'affilée
    payrollStore.setCycleFilter('periodEnd', draftEnd);
    periodOpen = false;
  }

  function clearPeriod() {
    draftStart = '';
    draftEnd = '';
    payrollStore.setCycleFilter('period', '');
    payrollStore.setCycleFilter('periodStart', '');
    payrollStore.setCycleFilter('periodEnd', '');
    periodOpen = false;
  }

  function isStatusActive(value: string): boolean {
    return payrollStore.cycleFilters.status === value;
  }

  function toggleStatus(status: string) {
    if (payrollStore.cycleFilters.status === status) {
      payrollStore.setCycleFilter('status', 'all' as any);
    } else {
      payrollStore.setCycleFilter('status', status as any);
    }
  }

  function clearStatus() {
    payrollStore.setCycleFilter('status', 'all' as any);
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
      <DropdownMenu.Label class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
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
          <span class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[0.82rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
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

  <!-- Period Filter Button — plage de dates -->
  <DropdownMenu.Root bind:open={periodOpen}>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="calendar" size={15} class="mr-1.5" />
        Période
        {#if hasPeriodFilter}
          <span class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[0.82rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-80 p-3 z-100">
      <div class="flex items-center justify-between mb-2">
        <span class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider">Période</span>
        {#if hasPeriodFilter}
          <span class="text-[0.82rem] text-slate-400 truncate max-w-38">{periodChipLabel()}</span>
        {/if}
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div class="flex flex-col gap-1">
          <Label class="text-[0.82rem] font-medium text-slate-600">Début</Label>
          <Input type="date" bind:value={draftStart} class="h-8 text-[0.82rem]" />
        </div>
        <div class="flex flex-col gap-1">
          <Label class="text-[0.82rem] font-medium text-slate-600">Fin</Label>
          <Input type="date" bind:value={draftEnd} class="h-8 text-[0.82rem]" />
        </div>
      </div>

      {#if !draftIsValid}
        <p class="mt-2 text-[0.82rem] text-rose-600">La date de début doit être ≤ date de fin.</p>
      {/if}

      <div class="mt-3 flex items-center justify-between gap-2">
        <Button variant="ghost" size="sm" class="h-7 text-[0.82rem] text-slate-500" onclick={clearPeriod}>
          Réinitialiser
        </Button>
        <Button size="sm" class="h-7 text-[0.82rem]" disabled={!draftHasValue || !draftIsValid} onclick={applyPeriod}>
          Appliquer
        </Button>
      </div>

      {#if hasPeriodFilter}
        <p class="mt-2 text-[0.82rem] text-slate-400">Filtre actif : {periodChipLabel()}</p>
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
          <span class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[0.82rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
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
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.82rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.82rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <!-- New Cycle Button -->
  <Button
    onclick={() => goToActiveOrNewPayroll()}
    variant="default"
    size="sm"
    class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
  >
    <AppIcon name="plus" size={15} />
    Nouvelle paie
  </Button>
</div>

