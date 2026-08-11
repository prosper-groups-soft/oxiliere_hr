<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { get } from 'svelte/store';
  import { bankingStore } from "@/features/banking/stores/banking.svelte";
  import AccountCard from "@/features/banking/components/accounts/AccountCard.svelte";
  import BankAccountSheet from "@/features/banking/components/accounts/sheets/BankAccountSheet.svelte";
  import { Button } from "@/components/ui/button";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import LoadingBar from '@/components/layout/elements/LoadingBar.svelte';
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import type { BankAccount } from "@/features/banking/types/types";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import BankingAccountsActions from "@/features/banking/components/accounts/BankingAccountsActions.svelte";
  import { ui } from '@/stores/ui.svelte';
  import { useAccountsQuery, useBanksQuery, syncAccountsStore } from "@/features/banking/queries/bankingQueries";


  // --- TanStack Query ---
  const banksQuery = useBanksQuery();
  const accountsQuery = useAccountsQuery(
    () => bankingStore.currentPage,
    () => bankingStore.accountsPerPage,
    () => bankingStore.filters.search,
    () => ({
      currency: bankingStore.filters.currency,
      status: bankingStore.filters.status,
      institutionId: bankingStore.filters.institutionId,
    }),
    () => bankingStore.sortBy,
    () => bankingStore.sortOrder,
  );

  // Sync query data into the store
  $effect(() => {
    syncAccountsStore($accountsQuery);
  });

  $effect(() => {
    const institutions = $banksQuery.data;
    if (institutions) {
      bankingStore.updateInstitutions(institutions);
    }
  });

  // Re-fetch when filters, sort or page change
  $effect(() => {
    bankingStore.filters.search;
    bankingStore.filters.status;
    bankingStore.filters.currency;
    bankingStore.filters.institutionId;
    bankingStore.sortBy;
    bankingStore.sortOrder;
    bankingStore.currentPage;
    bankingStore.accountsPerPage;
    get(accountsQuery).refetch();
  });

  // --- State ---
  let isSheetOpen = $state(false);
  let selectedAccount = $state<BankAccount | null>(null);

  const accounts = $derived(bankingStore.accounts);
  const totalCount = $derived(bankingStore.totalCount);
  const activeFiltersCount = $derived(bankingStore.activeFiltersCount);

  // Build a filters object that includes search for FilterChips
  const filtersWithSearch = $derived.by((): Record<string, string[]> => {
    const f: Record<string, string[]> = {};
    if (bankingStore.filters.status.length > 0) {
      f.status = bankingStore.filters.status;
    }
    if (bankingStore.filters.currency.length > 0) {
      f.currency = bankingStore.filters.currency;
    }
    if (bankingStore.filters.institutionId.length > 0) {
      f.institutionId = bankingStore.filters.institutionId;
    }
    if (bankingStore.filters.search) {
      f.search = [bankingStore.filters.search];
    }
    return f;
  });

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche: "${value}"`;
    if (key === 'status') {
      const labels: Record<string, string> = { verified: 'Vérifié', pending: 'En attente', rejected: 'Rejeté', blocked: 'Bloqué' };
      return labels[value as string] || String(value);
    }
    if (key === 'currency') return String(value);
    if (key === 'institutionId') {
      const inst = bankingStore.getInstitutionById(value as string);
      return inst?.name || String(value);
    }
    return String(value);
  }

  function openNewSheet() {
    selectedAccount = null;
    isSheetOpen = true;
  }

  // Register actions in the UI store (like LeavesBoard)
  $effect(() => {
    ui.addActions('accounts', AccountsActionsSnippet);
    return () => {
      ui.removeActions('accounts');
    };
  });
</script>


<!-- WRAPPER FOR ui.addActions -->
{#snippet AccountsActionsSnippet()}
  <BankingAccountsActions />
{/snippet}


{#snippet Header()}
  <div class="flex flex-col gap-3 py-2 border-b border-slate-100 pl-6 pr-9">
    <div class="flex items-center justify-between">
      <div class="flex-1 max-w-md">
        <SearchBar 
          bind:value={bankingStore.filters.search} 
          placeholder="Rechercher un employé ou un compte..."
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => bankingStore.filters.search = ""}
        />  
      </div>
      <!-- Add Button -->
      <Button
        onclick={openNewSheet}
        variant="default"
        size="sm"
        class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all ml-3"
      >
        <AppIcon name="plus" size={15} />
        Nouveau compte
      </Button>
    </div>
  </div>
{/snippet}


<div class="flex flex-col h-full">
  {@render Header()}

  <div class="flex flex-col flex-1 overflow-hidden">
    <FilterChips 
      filters={filtersWithSearch}
      activeFiltersCount={activeFiltersCount}
      getDisplayLabel={getFilterDisplayLabel}
      onRemove={(key, value) => {
        if (key === 'search') {
          bankingStore.filters.search = '';
        } else {
          bankingStore.toggleFilter(key as any, value as string);
        }
      }}
      onReset={() => bankingStore.resetFilters()}
      class="px-6 py-2 border-b border-slate-50 bg-white/50"
    />

    <!-- Overhead loading bar during refetch -->
    <LoadingBar loading={$accountsQuery.isFetching} class="shrink-0" />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      {#if $accountsQuery.isPending}
        <div class="flex-1 flex items-center justify-center" in:fade>
          <AnimateSpin text="Chargement des comptes" />
        </div>
      {:else if $accountsQuery.error}
        <div class="flex-1 flex items-center justify-center" in:fade>
          <Empty 
            icon="alert-circle"
            title="Erreur de chargement"
            iconClass="text-rose-400"
            description="Impossible de charger la liste des comptes bancaires."
            iconSize={28}
            iconStrokeWidth={1.3}
          >
            <Button onclick={() => get(accountsQuery).refetch()} class="h-7">
              <AppIcon name="refresh" size={15} />
              Réessayer
            </Button>
          </Empty>
        </div>
      {:else if accounts.length === 0}
        <div class="flex-1 flex items-center justify-center" in:fade>
          <Empty 
            title="Aucun compte"
            description={activeFiltersCount > 0 || bankingStore.filters.search
              ? `Aucun compte bancaire ne correspond à vos critères${bankingStore.filters.search ? ' pour « ' + bankingStore.filters.search + ' »' : ''}.`
              : "Commencez par ajouter votre premier compte bancaire pour gérer vos transactions."}
            icon={activeFiltersCount > 0 ? "search-x" : "wallet"}
            iconSize={28}
            iconStrokeWidth={1.3}
            iconClass="text-slate-400"
          >
            {#if activeFiltersCount > 0}
              <Button variant="outline" onclick={() => bankingStore.resetFilters()} class="h-9 border-slate-200 shadow-fine cursor-pointer">
                <AppIcon name="x" size={16} class="text-slate-400" />
                Réinitialiser les filtres
              </Button>
            {:else}
              <Button onclick={openNewSheet} class="h-7 cursor-pointer">
                <AppIcon name="plus" size={15} />
                Nouveau compte
              </Button>
            {/if}
          </Empty>
        </div>
      {:else}
        <div class="flex-1 overflow-y-auto p-5 scroll-smooth custom-scrollbar" in:fly={{ y: 15, duration: 300, delay: 80 }}>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
            {#each accounts as account (account.id)}
              <div in:fly={{ y: 20, duration: 400 }}>
                <AccountCard 
                  {account} 
                  onEdit={(acc) => {
                    selectedAccount = acc;
                    isSheetOpen = true;
                  }}
                />
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if totalCount > 0}
        <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
          <DataPagination 
            currentCount={accounts.length}
            totalCount={totalCount}
            currentPage={bankingStore.currentPage}
            totalPages={bankingStore.totalPages}
            perPage={bankingStore.accountsPerPage}
            onPageChange={(p) => bankingStore.setPage(p)}
            onPerPageChange={(s) => bankingStore.setAccountsPerPage(s)}
            onNext={() => bankingStore.nextPage()}
            onPrev={() => bankingStore.prevPage()}
            unitLabel="comptes"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


<BankAccountSheet bind:open={isSheetOpen} bind:account={selectedAccount} />




