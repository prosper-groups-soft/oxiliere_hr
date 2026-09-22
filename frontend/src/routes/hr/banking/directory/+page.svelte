<script lang="ts">
  import { fly } from 'svelte/transition';
  import BankCard from "@/hr/modules/banking/components/directory/BankCard.svelte";
  import { Button } from "@/components/ui/button";
  import SearchBar from "@/hr/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/hr/components/shared/elements/FilterChips.svelte";
  import BankInstitutionSheet from "@/hr/modules/banking/components/directory/sheets/BankInstitutionSheet.svelte";
  import BankingActions from "@/hr/modules/banking/components/directory/BankingActions.svelte";
  import type { BankInstitution } from "@/hr/modules/banking/types/types";
  import { ui } from '@/hr/stores/ui.svelte';
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import { bankingService } from "@/hr/modules/banking/services/bankingService";

  let isSheetOpen = $state(false);
  let selectedInstitution = $state<BankInstitution | null>(null);

  const uiState = createFilterState<{ type: string[], isActive: string[] }>({ type: [], isActive: [] });

  const banksRes = useAsyncResource(
    () => ({
      queryKey: ['banking', 'institutions'],
      queryFn: () => bankingService.listInstitutions()
    }),
    {
      mapData: (d: any) => {
        let result: BankInstitution[] = Array.isArray(d) ? d : (d.results ?? d);
        const types = uiState.filters.type;
        if (types.length) result = result.filter(inst => types.includes(inst.type));
        const search = uiState.search.trim().toLowerCase();
        if (search) result = result.filter(inst => inst.name.toLowerCase().includes(search) || inst.shortName.toLowerCase().includes(search) || inst.country.toLowerCase().includes(search));
        const isActive = uiState.filters.isActive[0];
        if (isActive !== undefined) result = result.filter(inst => String(inst.isActive) === isActive);
        return { items: result, total: result.length };
      }
    }
  );

  const filtersWithSearch = $derived.by((): Record<string, string[]> => {
    const f: Record<string, string[]> = {};
    if (uiState.filters.type.length) f.type = uiState.filters.type;
    if (uiState.search) f.search = [uiState.search];
    if (uiState.filters.isActive.length) f.isActive = uiState.filters.isActive;
    return f;
  });

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche: "${value}"`;
    if (key === 'type') return value === 'bank' ? 'Banques' : 'Mobile Money';
    if (key === 'isActive') return value === 'true' ? 'Actifs' : 'Inactifs';
    return String(value);
  }
  function openNewSheet() { selectedInstitution = null; isSheetOpen = true; }
  function handleEdit(inst: BankInstitution) { selectedInstitution = inst; isSheetOpen = true; }
  async function handleDelete(instId: string) { await bankingService.deleteInstitution(instId); banksRes.refetch(); }
  $effect(() => { ui.addActions('banking-directory', BankingActionsSnippet); return () => ui.removeActions('banking-directory'); });
</script>

<div class="flex flex-col h-full bg-white">
  {@render Header()}
  <div class="flex flex-col flex-1 overflow-hidden">
    <FilterChips filters={filtersWithSearch} activeFiltersCount={uiState.activeFiltersCount + (uiState.search ? 1 : 0)} getDisplayLabel={getFilterDisplayLabel} onRemove={(k,v)=>k==='search'?uiState.setSearch(''):k==='isActive'?uiState.filters.isActive=[]:uiState.toggleFilter(k as any, v as string)} onReset={()=>uiState.resetFilters()} class="px-6 py-1.5 border-b border-slate-50 bg-white/50" />
    <AsyncView state={banksRes} loadingText="Chargement des institutions" emptyWhen={(d)=>d.total===0} isFiltered={uiState.activeFiltersCount>0 || !!uiState.search} searchQuery={uiState.search} onResetFilters={()=>uiState.resetFilters()} onCreate={openNewSheet} createLabel="Nouvelle institution">
      {#snippet children(data)}
        <div class="flex-1 overflow-y-auto p-5 scroll-smooth custom-scrollbar" in:fly={{ y: 15, duration: 300, delay: 80 }}>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each data.items as institution (institution.id)}<div in:fly={{ y: 20, duration: 400 }}><BankCard {institution} onEdit={handleEdit} onDelete={handleDelete} /></div>{/each}
          </div>
        </div>
      {/snippet}
    </AsyncView>
  </div>
</div>

{#snippet Header()}
  <div class="flex flex-col gap-3 py-2 border-b border-slate-100 pl-6 pr-9">
    <div class="flex items-center justify-between">
      <div class="flex-1 max-w-md"><SearchBar bind:value={uiState.search} placeholder="Rechercher une banque ou un service..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={() => uiState.setSearch("")} /></div>
      <Button variant="default" class="h-7.5 px-4 bg-primary text-white shadow-fine rounded-lg hover:bg-primary/90" onclick={openNewSheet}>Nouvelle institution</Button>
    </div>
  </div>
{/snippet}
{#snippet BankingActionsSnippet()}<BankingActions />{/snippet}

<BankInstitutionSheet bind:open={isSheetOpen} bind:institution={selectedInstitution} onCreate={async (d)=>{const r=await bankingService.createInstitution(d); banksRes.refetch(); return r;}} onUpdate={async (id,d)=>{await bankingService.updateInstitution(id,d); banksRes.refetch();}} onUploadLogo={async (id,f)=>{await bankingService.uploadLogo(id,f); banksRes.refetch();}} />
