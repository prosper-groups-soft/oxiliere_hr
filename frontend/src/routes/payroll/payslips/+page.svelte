<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { PAYROLL_STATUS_LABELS, type Payslip, DEPARTMENTS } from "@/features/payroll/types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { scale } from "svelte/transition";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import PayslipGroupList from '@/features/payroll/components/payslips/PayslipGroupList.svelte';
  import GroupHeader from '@/features/payroll/components/payslips/views/GroupHeader.svelte';
  import PayslipDetailSheet from '@/features/payroll/components/payslips/sheets/PayslipDetailSheet.svelte';

  type PayslipGroup = {
    period: string;
    label: string;
    payslips: Payslip[];
    count: number;
    totalNet: number;
  };

  function formatPeriodLabel(period: string) {
    const date = new Date(`${period}-01`);

    if (Number.isNaN(date.getTime())) {
      return period;
    }

    return new Intl.DateTimeFormat('fr-FR', {
      month: 'long',
      year: 'numeric'
    }).format(date);
  }

  function getPayslipGroups(payslips: Payslip[]): PayslipGroup[] {
    const groups = new Map<string, Payslip[]>();

    for (const payslip of payslips) {
      if (!groups.has(payslip.period)) {
        groups.set(payslip.period, []);
      }

      groups.get(payslip.period)?.push(payslip);
    }

    return Array.from(groups.entries())
      .sort(([left], [right]) => right.localeCompare(left))
      .map(([period, items]) => ({
        period,
        label: formatPeriodLabel(period),
        payslips: [...items].sort((a, b) => a.employeeName.localeCompare(b.employeeName)),
        count: items.length,
        totalNet: items.reduce((sum, payslip) => sum + payslip.netPay, 0)
    }));
  }

  const statusOptions = ['draft', 'calculated', 'reviewed', 'approved', 'paid'] as const;

  // Sheet state
  let sheetOpen = $state(false);
  let selectedPayslip = $state<Payslip | null>(null);

  function openPayslipDetail(payslipId: string) {
    const payslip = payrollStore.paginatedPayslips.find(p => p.id === payslipId);
    if (payslip) {
      selectedPayslip = payslip;
      sheetOpen = true;
    }
  }
</script>


<svelte:head>
  <title>Oxiliere HR - Bulletins de paie</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={payrollStore.filters}
      activeFiltersCount={payrollStore.activeFiltersCount}
      getDisplayLabel={(key, value) => key === 'status' ? PAYROLL_STATUS_LABELS[value as keyof typeof PAYROLL_STATUS_LABELS] : String(value)}
      onRemove={(key, value) => payrollStore.toggleFilter(key as any, value)}
      onReset={() => payrollStore.resetFilters()}
      class="mb-2 py-1.5"
    />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <div class="flex-1 overflow-y-auto min-h-0 {payrollStore.filteredPayslips.length === 0 ? 'px-4 py-4 pr-8.5' : ''}">
        {#if payrollStore.filteredPayslips.length === 0}
          <Empty 
            title="Aucun bulletin trouvé"
            description="Aucun bulletin ne correspond à vos critères de recherche."
            icon="file-text"
            iconSize={28}
          />
        {:else}
          <PayslipGroupList groups={getPayslipGroups(payrollStore.paginatedPayslips)} onSelect={openPayslipDetail} />
        {/if}
      </div>

      {#if payrollStore.totalCount > 0}
        <div class="bg-slate-50/80 border-t border-[#e9eaea] pr-10">
          <DataPagination 
            currentCount={payrollStore.paginatedPayslips.length}
            totalCount={payrollStore.totalCount}
            currentPage={payrollStore.currentPage}
            totalPages={payrollStore.totalPages}
            perPage={payrollStore.perPage}
            onPageChange={(p) => payrollStore.setPage(p)}
            onPerPageChange={(s) => payrollStore.setPerPage(s)}
            onNext={() => payrollStore.nextPage()}
            onPrev={() => payrollStore.prevPage()}
            unitLabel="bulletins"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8.5">

    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={payrollStore.filters.search} 
          placeholder="Rechercher un bulletin..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => payrollStore.setSearch('')}
        />
      </div>
      
      <div class="flex items-center gap-2">
        {#if payrollStore.paginatedPayslips.length > 0}
          {@const groups = getPayslipGroups(payrollStore.paginatedPayslips)}
          {#if groups.length > 0}
            <GroupHeader 
              label={groups[0].label} 
              count={groups[0].count} 
              totalNet={groups[0].totalNet} 
            />
          {/if}
        {/if}
        {@render PeriodSelector()}
        {@render FilterMenu()}
      </div>
    </div>
  </div>
{/snippet}


{#snippet PeriodSelector()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger 
      class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all"
    >
      <AppIcon name="calendar" size={16} class="text-slate-400" />
      <span class="text-[0.85rem] text-slate-700">{formatPeriodLabel(payrollStore.currentPeriod)}</span>
      <AppIcon name="chevron-down" size={14} class="text-slate-400" />
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
      <div class="p-1 max-h-80 overflow-y-auto">
        {#each payrollStore.availablePeriods as period}
          <DropdownMenu.Item 
            onclick={() => payrollStore.setPeriod(period)}
            class="rounded-md py-1.5 px-2 text-[0.879rem]! cursor-pointer {period === payrollStore.currentPeriod ? 'bg-blue-50 text-blue-600' : 'text-slate-700'}"
          >
            {formatPeriodLabel(period)}
          </DropdownMenu.Item>
        {/each}
      </div>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet FilterMenu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger 
      class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all"
    >
      <AppIcon name="filter" size={16} class={payrollStore.activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
      <span class="text-[0.84rem] text-slate-700">Filtrer</span>
      {#if payrollStore.activeFiltersCount > 0}
        <div transition:scale={{ duration: 200, start: 0.8 }}>
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {payrollStore.activeFiltersCount}
          </Badge>
        </div>
      {/if}
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-50 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
      <div class="p-2 max-h-80 overflow-y-auto">
        {@render FilterSection("Département", DEPARTMENTS, "department")}
        <DropdownMenu.Separator class="my-2 bg-slate-50" />
        {@render StatusFilterSection()}
      </div>

      {#if payrollStore.activeFiltersCount > 0}
        <div class="p-2 bg-slate-50/50 border-t border-slate-100">
          <Button variant="ghost" onclick={() => payrollStore.resetFilters()} class="w-full h-8 text-[0.84rem] bg-white text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
            Réinitialiser tout
          </Button>
        </div>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet FilterSection(label: string, options: string[], filterKey: 'department')}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={(payrollStore.filters[filterKey] as string[]).includes(option)}
      onCheckedChange={() => payrollStore.toggleFilter(filterKey, option)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {option}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}


{#snippet StatusFilterSection()}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    Statut
  </DropdownMenu.Label>
  {#each statusOptions as status}
    <DropdownMenu.CheckboxItem 
      checked={payrollStore.filters.status.includes(status)}
      onCheckedChange={() => payrollStore.toggleFilter('status', status)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {PAYROLL_STATUS_LABELS[status]}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}


<PayslipDetailSheet bind:open={sheetOpen} payslip={selectedPayslip} />

