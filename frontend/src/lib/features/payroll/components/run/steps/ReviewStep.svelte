<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { type Payslip } from "@/features/payroll/types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import ReviewEmployeeRow from "./views/review/ReviewEmployeeRow.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import PayslipDetailSheet from "@/features/payroll/components/payslips/sheets/PayslipDetailSheet.svelte";
  import { slide, fade, scale } from "svelte/transition";

  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  const payslips = $derived(payrollStore.payslips);

  const totalNet = $derived(payrollStore.totalNetPay);
  const employeeCount = $derived(payslips.length);
  const anomalies = $derived(payslips.filter(p => (p.netPay || 0) <= 0).length);
  
  // --- State des Filtres (Multi-sélection) ---
  let searchTerm = $state('');
  let selectedDepartments = $state<string[]>([]); 
  let showOnlyWithAnomalies = $state(false);
  
  const departmentsList = $derived(() => {
    const depts = new Set(payslips.map(p => p.department).filter(Boolean));
    return Array.from(depts).sort() as string[];
  });

  // --- Logique de Filtrage ---
  const filteredPayslips = $derived(() => {
    let filtered = payslips;
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(p => 
        p.employeeName.toLowerCase().includes(search) ||
        (p.department?.toLowerCase().includes(search))
      );
    }
    if (selectedDepartments.length > 0) {
      filtered = filtered.filter(p => selectedDepartments.includes(p.department));
    }
    if (showOnlyWithAnomalies) {
      filtered = filtered.filter(p => (p.netPay || 0) <= 0);
    }
    return filtered;
  });

  // --- Chips Logic ---
  const activeFilters = $derived(() => {
    const f: Record<string, string[]> = {};
    if (selectedDepartments.length > 0) f.department = selectedDepartments;
    if (showOnlyWithAnomalies) f.anomalies = ['Anomalies'];
    return f;
  });

  const activeCount = $derived(
    selectedDepartments.length + (showOnlyWithAnomalies ? 1 : 0)
  );

  // --- Actions Groupées ---
  function bulkMarkAsReviewed() {
    const targets = filteredPayslips();
    if (targets.length === 0) return;
    
    // Ici, on appelle la méthode du store pour mettre à jour les IDs filtrés
    const ids = targets.map(p => p.id);
    // payrollStore.markMultipleAsReviewed(ids); // Exemple d'appel API/Store
    console.log(`Action: Marquer ${ids.length} bulletins comme révisés.`);
  }

  function toggleDepartment(dept: string) {
    if (selectedDepartments.includes(dept)) {
      selectedDepartments = selectedDepartments.filter(d => d !== dept);
    } else {
      selectedDepartments = [...selectedDepartments, dept];
    }
  }

  function resetFilters() {
    selectedDepartments = [];
    showOnlyWithAnomalies = false;
    searchTerm = '';
  }

  // --- Sheet State ---
  let sheetOpen = $state(false);
  let selectedPayslip = $state<Payslip | null>(null);

  function openPayslipDetail(payslipId: string) {
    const payslip = payrollStore.payslips.find(p => p.id === payslipId);
    if (payslip) {
      selectedPayslip = payslip;
      sheetOpen = true;
    }
  }
</script>


<div class="mt-2 space-y-3">
  {@render HeaderStats()}
  {@render StatusInfoCards()}

  <Card class="border shadow-none border-slate-200 bg-white overflow-hidden py-3">
    <div class="flex flex-col bg-white border-b border-slate-100 pb-3">
      {@render SearchFilterBar()}
      {@render FilterChipsSection()}
    </div>

    {@render ReviewTable()}
  </Card>
</div>


{#snippet HeaderStats()}
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
    {@render StatCard('Total Bulletins', employeeCount + ' générés', 'users', 'text-slate-900', 'text-blue-500')}
    {@render StatCard('Net à payer global', totalNet.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' }), 'banknote', 'text-slate-900', 'text-emerald-500')}
    {@render StatCard('Anomalies détectées', anomalies === 0 ? 'Aucune' : anomalies + ' à vérifier', anomalies > 0 ? 'alert-circle' : 'shield-check', anomalies > 0 ? 'text-rose-600' : 'text-slate-900', anomalies > 0 ? 'text-rose-500' : 'text-emerald-500')}
  </div>
{/snippet}


{#snippet StatusInfoCards()}
  <div class="flex gap-1">
    {#if currentStatus === 'calculated'}
      {@render StatusCard('calculated', 'Révision détaillée requise', 'Vérifiez chaque ligne. Si tout est correct, cliquez sur <strong>Marquer comme révisé</strong> pour verrouiller les montants.', 'eye', 'Étape 3/4')}
    {:else if ['reviewed', 'approved', 'paid'].includes(currentStatus)}
      {@render StatusCard('completed', 'Révision terminée', 'Les données sont maintenant verrouillées. Toute modification nécessite une réinitialisation du cycle.', 'circle-check')}
    {/if}

    <div class="flex items-center justify-center gap-3 p-1.5 bg-slate-50/50 rounded-lg border border-slate-100 flex-1">      
      <div class="w-10 h-10 rounded-xl bg-white shadow-none flex items-center justify-center shrink-0 border border-blue-100 text-blue-600">
        <AppIcon name="check-shield" size={18} class="text-blue-500 mt-0.5" />
      </div>
      <div class="space-y-1">
        <p class="text-[0.82rem] text-slate-700 font-semibold">Vérification de conformité terminée</p>
        <p class="text-[0.82rem] text-slate-600 leading-relaxed">
          Cette étape génère l'historique de paie définitif. Assurez-vous que les primes et retenues (CNSS, IPR) sont correctes.
        </p>
      </div>
    </div>
  </div>
{/snippet}


{#snippet SearchFilterBar()}
  <div class="flex items-center justify-between px-4">
    <div class="flex-1 max-w-125">
      <SearchBar 
        bind:value={searchTerm} 
        placeholder="Rechercher un employé..." 
        class="w-full"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.88rem] bg-[#f5f6f7] border-transparent focus:bg-white focus:border-slate-200 transition-all shadow-none"
        iconSize={20}
        onClear={() => searchTerm = ""}
      />
    </div>

    <div class="flex items-center gap-1">
      
      {#if (activeCount > 0 || searchTerm) && filteredPayslips().length > 0 && currentStatus === 'calculated'}
        <button 
          onclick={bulkMarkAsReviewed}
          class="h-7.5 px-3 flex items-center gap-2 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-100 hover:bg-emerald-100 transition-all cursor-pointer mr-1"
          in:fade
        >
          <AppIcon name="check-check" size={14} />
          <span class="text-[0.84rem] font-medium text-nowrap text-emerald-700">Valider la sélection ({filteredPayslips().length})</span>
        </button>
      {/if}
    
      {#if activeCount > 0 || searchTerm}
        <button onclick={resetFilters} class="h-8 w-8 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-colors cursor-pointer" in:fade>
          <AppIcon name="rotate-ccw" size={16} />
        </button>
      {/if}

      {@render FilterDropdowns()}
    </div>
  </div>
{/snippet}


{#snippet FilterDropdowns()}
  <div class="relative">
    <TooltipWrapper content="Afficher les erreurs uniquement">
      {#snippet children(props)}
        <button 
          {...props}
          onclick={() => showOnlyWithAnomalies = !showOnlyWithAnomalies}
          class="h-7.5 px-3 flex items-center gap-2 rounded-lg border transition-all cursor-pointer shadow-fine
          {showOnlyWithAnomalies ? 'bg-rose-50 border-rose-200 text-rose-600' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'}"
        >
          <div class="relative">
            <AppIcon name="alert-circle" size={16} />
            {#if showOnlyWithAnomalies}
              <span class="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full border-2 border-rose-50" in:scale></span>
            {/if}
          </div>
          <span class="text-[0.84rem] font-medium">Anomalies</span>
        </button>
      {/snippet}
    </TooltipWrapper>
  </div>

  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      {#snippet child({ props })}
        <button 
          {...props} 
          class="h-7.5 px-4 flex items-center gap-2.5 bg-white border border-slate-200 rounded-lg shadow-fine hover:bg-slate-50 transition-all min-w-[160px] cursor-pointer outline-none"
        >
          <AppIcon name="layers" size={15} class="text-slate-400" />
          <span class="text-[0.84rem] text-slate-700 font-medium truncate flex-1 text-left">
            {#if selectedDepartments.length === 0}
              Départements
            {:else if selectedDepartments.length === 1}
              {selectedDepartments[0]}
            {:else}
              {selectedDepartments.length} départements
            {/if}
          </span>
          <AppIcon name="chevron-down" size={14} class="text-slate-400" />
        </button>
      {/snippet}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 min-w-[200px]">
      <DropdownMenu.Label class="px-2 py-1.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest">Entités</DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      
      <DropdownMenu.CheckboxItem 
        checked={selectedDepartments.length === departmentsList().length && departmentsList().length > 0}
        onCheckedChange={(checked) => {
          selectedDepartments = checked ? [...departmentsList()] : [];
        }}
        class="py-2 px-3 pl-7 rounded-md cursor-pointer text-[0.84rem] font-medium text-primary"
      >
        Tout sélectionner
      </DropdownMenu.CheckboxItem>
      
      <DropdownMenu.Separator class="my-1 bg-slate-50" />

      {#each departmentsList() as dept}
        <DropdownMenu.CheckboxItem 
          checked={selectedDepartments.includes(dept)}
          onCheckedChange={() => toggleDepartment(dept)}
          class="py-2 px-3 pl-7 rounded-md cursor-pointer text-[0.84rem]"
        >
          {dept}
        </DropdownMenu.CheckboxItem>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet FilterChipsSection()}
  {#if activeCount > 0}
    <div class="px-4 pb-2 pt-1" in:slide>
      <FilterChips 
        filters={activeFilters()}
        activeFiltersCount={activeCount}
        onRemove={(key, value) => {
          if (key === 'department') {
            selectedDepartments = selectedDepartments.filter(d => d !== value);
          } else {
            showOnlyWithAnomalies = false;
          }
        }}
        onReset={resetFilters}
        class="py-1"
      />
    </div>
  {/if}
{/snippet}


{#snippet ReviewTable()}
  <CardContent class="p-0">
    <div class="overflow-x-auto min-h-[300px]">
      <div class="divide-y divide-slate-100">
        {#each filteredPayslips() as payslip (payslip.id || payslip.employeeName)}
          <ReviewEmployeeRow {payslip} onClick={openPayslipDetail} />
        {:else}
          <div class="py-20 text-center flex flex-col items-center justify-center gap-2">
            <AppIcon name="search-slash" size={32} class="text-slate-200" />
            <p class="text-sm text-slate-400">Aucun bulletin ne correspond à vos filtres.</p>
          </div>
        {/each}
      </div>
    </div>
  </CardContent>
{/snippet}


{#snippet StatCard(title: string, value: string, icon: string, color: string, iconColor: string)}
  <Card class="border shadow-none border-slate-200 gap-1">
    <CardHeader class="pb-0 px-4 pt-0">
      <CardTitle class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
        <AppIcon name={icon} size={17} strokeWidth={1.5} class={iconColor} /> {title}
      </CardTitle>
    </CardHeader>
    <CardContent class="px-4 pb-0 py-0">
      <p class="text-[1rem] font-medium {color} uppercase tracking-tight">{value}</p>
    </CardContent>
  </Card>
{/snippet}


{#snippet StatusCard(status: string, title: string, description: string, icon: string, badge?: string)}
  <div class="border rounded-xl shadow-fine p-1.5 {status === 'calculated' ? 'border-blue-100 bg-blue-50/30' : 'border-emerald-100 bg-emerald-50/30'} flex-1 flex items-center justify-center">
    <div class="flex items-center justify-center gap-4">
      <div class="w-10 h-10 rounded-xl bg-white shadow-none flex items-center justify-center shrink-0 border {status === 'calculated' ? 'border-blue-100 text-blue-600' : 'border-emerald-100 text-emerald-600'}">
        <AppIcon name={icon} size={20} />
      </div>
      <div class="flex-1">
        <h3 class="text-sm font-semibold text-slate-800 flex items-center gap-2">
          {title}
          {#if badge}
            <span class="text-[0.6rem] bg-blue-600 text-white px-2 py-0.5 rounded-full font-bold uppercase">{badge}</span>
          {/if}
        </h3>
        <p class="text-[0.75rem] text-slate-600 leading-tight mt-1">
          {@html description}
        </p>
      </div>
    </div>
  </div>
{/snippet}


<PayslipDetailSheet bind:open={sheetOpen} payslip={selectedPayslip} />

