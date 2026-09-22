<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { bankingStore } from "@/hr/modules/banking/stores/banking.svelte";
  import { useSeedBanksMutation } from "@/hr/modules/banking/queries/bankingQueries";
  import SeedBanksDialog from "./SeedBanksDialog.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import type { FilterDef } from "@/hr/actions/types";

  let { filterState = bankingStore, onAdd } = $props<{ filterState?: any; onAdd?: () => void }>();
  let isSeedDialogOpen = $state(false);
  const seedMutation = useSeedBanksMutation();
  async function handleSeed(codes?: string[]) { await $seedMutation.mutateAsync(codes); }

  const filterDefs = $derived<FilterDef[]>([
    { key: 'type', label: "Type d'entité", icon: 'bank', mode: 'multi', options: [{ value: 'bank', label: 'Banques' }, { value: 'mobile_money', label: 'Mobile Money' }] },
    { key: 'isActive', label: 'Statut', icon: 'power', mode: 'single', options: [{ value: 'true', label: 'Actifs' }, { value: 'false', label: 'Inactifs' }] },
  ]);

  const fs = $derived({
    get filters() { return { type: filterState.institutionFilters?.type ?? [], isActive: filterState.institutionFilters?.isActive !== null ? [String(filterState.institutionFilters.isActive)] : [] }; },
    get activeFiltersCount() { return (filterState.institutionFilters?.type.length ?? 0) + (filterState.institutionFilters?.search ? 1 : 0) + (filterState.institutionFilters?.isActive !== null ? 1 : 0); },
    toggleFilter: (k: string, v: string) => {
      if(k==='type') filterState.toggleInstitutionType(v);
      else if(k==='isActive') filterState.institutionFilters.isActive = filterState.institutionFilters.isActive === (v==='true') ? null : (v==='true');
    },
    resetFilters: () => filterState.resetInstitutionFilters()
  });
</script>

<ActionBar>
  <Button variant="ghost" size="sm" onclick={() => isSeedDialogOpen = true} class="h-7 px-2.5 text-[0.84rem] text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50">
    <AppIcon name="plus" size={15} class="mr-1.5" /> Institutions par défaut
  </Button>
  <FilterMenu filterDefs={filterDefs} filterState={fs} />
  {#if fs.activeFiltersCount > 0}
    <button onclick={() => fs.resetFilters()} class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer">
      <span class="text-[0.8rem]">{fs.activeFiltersCount} filtre{fs.activeFiltersCount > 1 ? 's' : ''}</span><AppIcon name="x" size={13} />
    </button>
  {/if}
  {#if onAdd}<button onclick={onAdd} class="h-7 px-3 bg-primary text-white rounded-lg text-[0.84rem] flex items-center gap-1"><AppIcon name="plus" size={14}/> Ajouter</button>{/if}
</ActionBar>
<SeedBanksDialog bind:open={isSeedDialogOpen} onSeed={handleSeed} />
