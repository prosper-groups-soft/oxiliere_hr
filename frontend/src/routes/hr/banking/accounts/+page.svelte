<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import AccountCard from "@/hr/modules/banking/components/accounts/AccountCard.svelte";
  import BankAccountSheet from "@/hr/modules/banking/components/accounts/sheets/BankAccountSheet.svelte";
  import DataPagination from "@/hr/components/layout/elements/DataPagination.svelte";
  import SearchBar from "@/hr/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/hr/components/shared/elements/FilterChips.svelte";
  import type { BankAccount } from "@/hr/modules/banking/types/types";
  import BankingAccountsActions from "@/hr/modules/banking/components/accounts/BankingAccountsActions.svelte";
  import { ui } from '@/hr/stores/ui.svelte';
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import { bankingService } from "@/hr/modules/banking/services/bankingService";
  import { Button } from "@/components/ui/button";

  const uiState = createFilterState<{ currency: string[], status: string[], institutionId: string[] }>({ currency: [], status: [], institutionId: [] });

  const accountsRes = useAsyncResource(
    () => ({
      queryKey: ['banking', 'accounts', uiState.page, uiState.perPage, uiState.search, uiState.filters, uiState.sortBy, uiState.sortOrder],
      queryFn: () => bankingService.listAccounts({ page: uiState.page, perPage: uiState.perPage, search: uiState.search, filters: uiState.filters, sortBy: uiState.sortBy, sortOrder: uiState.sortOrder } as any)
    }),
    { mapData: (d: any) => ({ items: d.results ?? d, total: d.count ?? d.length, totalPages: Math.ceil((d.count ?? d.length) / uiState.perPage) }) }
  );

  let isSheetOpen = $state(false);
  let selectedAccount = $state<BankAccount | null>(null);

  const filtersWithSearch = $derived.by((): Record<string, string[]> => {
    const f: Record<string, string[]> = {};
    if (uiState.filters.status.length) f.status = uiState.filters.status;
    if (uiState.filters.currency.length) f.currency = uiState.filters.currency;
    if (uiState.filters.institutionId.length) f.institutionId = uiState.filters.institutionId;
    if (uiState.search) f.search = [uiState.search];
    return f;
  });

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche: "${value}"`;
    if (key === 'status') { const l: Record<string,string> = { verified: 'Vérifié', pending: 'En attente', rejected: 'Rejeté', blocked: 'Bloqué' }; return l[value as string] || String(value); }
    if (key === 'currency') return String(value);
    if (key === 'institutionId') return String(value);
    return String(value);
  }
  function openNewSheet() { selectedAccount = null; isSheetOpen = true; }
  $effect(() => { ui.addActions('accounts', AccountsActionsSnippet); return () => ui.removeActions('accounts'); });
</script>

{#snippet AccountsActionsSnippet()}<BankingAccountsActions />{/snippet}
{#snippet Header()}
  <div class="flex flex-col gap-3 py-2 border-b border-slate-100 pl-6 pr-9">
    <div class="flex items-center justify-between">
      <div class="flex-1 max-w-md"><SearchBar bind:value={uiState.search} placeholder="Rechercher un employé ou un compte..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={() => uiState.setSearch("")} /></div>
      <Button onclick={openNewSheet} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg ml-3">Nouveau compte</Button>
    </div>
  </div>
{/snippet}

<div class="flex flex-col h-full">
  {@render Header()}
  <div class="flex flex-col flex-1 overflow-hidden">
    <FilterChips filters={filtersWithSearch} activeFiltersCount={uiState.activeFiltersCount + (uiState.search ? 1 : 0)} getDisplayLabel={getFilterDisplayLabel} onRemove={(k,v)=>k==='search'?uiState.setSearch(''):uiState.toggleFilter(k as any, v as string)} onReset={()=>uiState.resetFilters()} class="px-6 py-2 border-b border-slate-50 bg-white/50" />
    <AsyncView state={accountsRes} loadingText="Chargement des comptes" emptyWhen={(d)=>d.total===0} isFiltered={uiState.activeFiltersCount>0 || !!uiState.search} searchQuery={uiState.search} onResetFilters={()=>uiState.resetFilters()} onCreate={openNewSheet} createLabel="Nouveau compte" emptyDescription="Commencez par ajouter votre premier compte bancaire pour gérer vos transactions.">
      {#snippet children(data)}
        <div class="flex-1 overflow-y-auto p-5 scroll-smooth custom-scrollbar" in:fly={{ y: 15, duration: 300, delay: 80 }}>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
            {#each data.items as account (account.id)}<div in:fly={{ y: 20, duration: 400 }}><AccountCard {account} onEdit={(acc)=>{selectedAccount=acc; isSheetOpen=true;}} /></div>{/each}
          </div>
        </div>
      {/snippet}
    </AsyncView>
    {#if accountsRes.data && accountsRes.data.total>0}
      <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
        <DataPagination currentCount={accountsRes.data.items.length} totalCount={accountsRes.data.total} currentPage={uiState.page} totalPages={accountsRes.data.totalPages} perPage={uiState.perPage} onPageChange={(p)=>uiState.setPage(p)} onPerPageChange={(s)=>uiState.setPerPage(s)} onNext={()=>uiState.nextPage()} onPrev={()=>uiState.prevPage()} unitLabel="comptes" />
      </div>
    {/if}
  </div>
</div>

<BankAccountSheet bind:open={isSheetOpen} bind:account={selectedAccount} />
