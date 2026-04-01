<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { payrollStore } from "../../stores/payroll.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import { 
    PAYROLL_STATUS_COLORS, 
    PAYROLL_STATUS_LABELS,
    DEPARTMENTS 
  } from "../../types/types";

  let sortColumn = $state<'employeeName' | 'grossPay' | 'netPay' | 'status'>('employeeName');
  let sortDirection = $state<'asc' | 'desc'>('asc');

  const sortedPayslips = $derived.by(() => {
    const sorted = [...payrollStore.filteredPayslips];
    sorted.sort((a, b) => {
      let comparison = 0;
      switch (sortColumn) {
        case 'employeeName':
          comparison = a.employeeName.localeCompare(b.employeeName);
          break;
        case 'grossPay':
          comparison = a.grossPay - b.grossPay;
          break;
        case 'netPay':
          comparison = a.netPay - b.netPay;
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
      }
      return sortDirection === 'asc' ? comparison : -comparison;
    });
    return sorted;
  });

  function toggleSort(column: typeof sortColumn) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
  }

  function toggleDepartmentFilter(dept: string) {
    payrollStore.toggleFilter('department', dept);
  }
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  <!-- Filters -->
  <div class="px-6 py-4 flex items-center justify-between gap-6 border-b border-slate-50">
    <SearchBar 
      bind:value={payrollStore.filters.search} 
      placeholder="Rechercher un employé..." 
      class="w-full max-w-sm"
      inputClass="h-10 rounded-xl bg-slate-50/50 border-slate-200 focus:bg-white transition-all shadow-none"
      iconSize={18}
      onClear={() => payrollStore.setSearch("")}
    />

    <div class="flex items-center gap-2 overflow-hidden">
      <div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
        {#each DEPARTMENTS as dept}
          <button
            onclick={() => toggleDepartmentFilter(dept)}
            class={cn(
              "px-3.5 py-1.5 text-[0.78rem] font-bold rounded-full transition-all border shrink-0 uppercase tracking-tight",
              payrollStore.filters.department.includes(dept)
                ? "bg-primary text-white border-primary shadow-sm"
                : "bg-white text-slate-500 border-slate-200 hover:border-primary/40 hover:text-primary transition-all cursor-pointer"
            )}
          >
            {dept}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <FilterChips 
    filters={{ department: payrollStore.filters.department }}
    activeFiltersCount={payrollStore.filters.department.length}
    onRemove={(key, value) => toggleDepartmentFilter(value)}
    onReset={() => payrollStore.resetFilters()}
    class="py-2.5 bg-slate-50/30 border-b border-slate-50"
  />

  <!-- Table -->
  <div class="flex-1 overflow-auto">
    <table class="w-full border-separate border-spacing-0">
      <thead class="bg-slate-50/80 sticky top-0 z-10 backdrop-blur-sm">
        <tr>
          <th class="px-6 py-3.5 text-left border-b border-slate-100">
            <button
              onclick={() => toggleSort('employeeName')}
              class="flex items-center gap-1.5 text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest hover:text-slate-900 transition-colors"
            >
              Employé
              <AppIcon name="sort" size={14} class={cn(sortColumn === 'employeeName' ? "text-primary" : "opacity-0 group-hover:opacity-100")} />
            </button>
          </th>
          <th class="px-6 py-3.5 text-left text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest border-b border-slate-100">Département</th>
          <th class="px-6 py-3.5 text-right border-b border-slate-100">
            <button
              onclick={() => toggleSort('grossPay')}
              class="flex items-center gap-1.5 justify-end w-full text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest hover:text-slate-900 transition-colors"
            >
              Salaire Brut
              <AppIcon name="sort" size={14} class={cn(sortColumn === 'grossPay' ? "text-primary" : "opacity-0")} />
            </button>
          </th>
          <th class="px-6 py-3.5 text-right border-b border-slate-100">
            <button
              onclick={() => toggleSort('netPay')}
              class="flex items-center gap-1.5 justify-end w-full text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest hover:text-slate-900 transition-colors"
            >
              Montant Net
              <AppIcon name="sort" size={14} class={cn(sortColumn === 'netPay' ? "text-primary" : "opacity-0")} />
            </button>
          </th>
          <th class="px-6 py-3.5 text-center border-b border-slate-100">
            <button
              onclick={() => toggleSort('status')}
              class="flex items-center gap-1.5 justify-center w-full text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest hover:text-slate-900 transition-colors"
            >
              Statut
              <AppIcon name="sort" size={14} class={cn(sortColumn === 'status' ? "text-primary" : "opacity-0")} />
            </button>
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-50">
        {#each sortedPayslips as payslip (payslip.id)}
          <tr class="group hover:bg-slate-50/50 transition-colors cursor-pointer">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-2xl bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600 group-hover:bg-primary group-hover:text-white transition-all">
                  {payslip.employeeName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                </div>
                <div class="flex flex-col">
                  <span class="text-[0.92rem] font-bold text-slate-800 tracking-tight group-hover:text-primary transition-colors">{payslip.employeeName}</span>
                  <span class="text-[0.7rem] text-slate-400 font-medium tracking-tight">ID: {payslip.id.slice(-6)}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="text-[0.85rem] font-semibold text-slate-500 bg-slate-100/50 px-2 py-1 rounded-md">{payslip.department}</span>
            </td>
            <td class="px-6 py-4 text-right">
              <span class="text-[0.9rem] font-bold text-slate-700">
                {payslip.grossPay.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <span class="text-[0.95rem] font-extrabold text-emerald-600">
                {payslip.netPay.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}
              </span>
            </td>
            <td class="px-6 py-4 text-center">
              <span class={cn(
                "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[0.72rem] font-bold uppercase tracking-wider",
                PAYROLL_STATUS_COLORS[payslip.status].bg,
                PAYROLL_STATUS_COLORS[payslip.status].text
              )}>
                <span class={cn("w-1.5 h-1.5 rounded-full", PAYROLL_STATUS_COLORS[payslip.status].dot)}></span>
                {PAYROLL_STATUS_LABELS[payslip.status]}
              </span>
            </td>
          </tr>
        {:else}
          <tr>
            <td colspan="5" class="px-6 py-20 text-center">
              <div class="flex flex-col items-center gap-3">
                <div class="w-16 h-16 rounded-full bg-slate-50 flex items-center justify-center text-slate-300">
                  <AppIcon name="file-text" size={32} />
                </div>
                <div>
                  <p class="text-[0.95rem] font-bold text-slate-600">Aucun bulletin de paie</p>
                  <p class="text-[0.85rem] text-slate-400">Aucun enregistrement ne correspond à vos critères de recherche.</p>
                </div>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>

