<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { bankingStore } from "@/features/banking/stores/banking.svelte";
  import AccountCard from "@/features/banking/components/accounts/AccountCard.svelte";
  import BankAccountSheet from "@/features/banking/components/accounts/sheets/BankAccountSheet.svelte";
  import { Button } from "@/components/ui/button";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { fade, fly, scale } from "svelte/transition";
  import type { BankAccount, BankingFilters } from "@/features/banking/types/types";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";

  // --- State ---
  let isSheetOpen = $state(false);
  let selectedAccount = $state<BankAccount | null>(null);

  const accounts = $derived(bankingStore.filteredAccounts);
</script>


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
      
      <div class="flex items-center gap-2">
        <!-- Filtres -->
        <DropdownMenu.Root>
          <DropdownMenu.Trigger>
            {#snippet child({ props })}
              <Button 
                {...props}
                variant="outline" 
                class="h-7.5 px-4 gap-2 text-slate-600 border-slate-200 shadow-fine"
              >
                <AppIcon 
                  name="filter" 
                  size={16} 
                  class={bankingStore.activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} 
                />
                <span class="text-[0.86rem]">Filtres</span>
                {#if bankingStore.activeFiltersCount > 0}
                  <div transition:scale={{ duration: 200 }}>
                    <Badge class="h-4 min-w-4 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.6rem] border-none">
                      {bankingStore.activeFiltersCount}
                    </Badge>
                  </div>
                {/if}
              </Button>
            {/snippet}
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end" class="w-64 h-100 overflow-y-scroll p-0 rounded-lg shadow-fine border-slate-100 bg-white">
            <div class="p-4 space-y-4">
              {@render FilterSection("Statut", ["verified", "pending", "blocked"], "status")}
              <DropdownMenu.Separator class="bg-slate-50" />
              {@render FilterSection("Devise", ["USD", "CDF", "EUR"], "currency")}
              <DropdownMenu.Separator class="bg-slate-50" />
              {@render FilterSection("Institution", bankingStore.institutions.map(i => i.id), "institutionId")}
            </div>

            {#if bankingStore.activeFiltersCount > 0}
              <div class="p-2 bg-slate-50/50 border-t border-slate-100">
                <Button variant="ghost" onclick={() => bankingStore.resetFilters()} class="w-full h-8 text-[0.8rem] bg-white text-rose-500 hover:text-rose-600 hover:bg-rose-50! font-medium">
                  Réinitialiser tout
                </Button>
              </div>
            {/if}
          </DropdownMenu.Content>
        </DropdownMenu.Root>
        
        <Button 
          class="h-7.5 px-4 gap-2 shadow-fine bg-blue-600 hover:bg-blue-700" 
          onclick={() => {
            selectedAccount = null;
            isSheetOpen = true;
          }}
        >
          <AppIcon name="plus" size={17} />
          <span class="text-[0.86rem]">Nouveau compte</span>
        </Button>
      </div>
    </div>
  </div>
{/snippet}


{#snippet FilterSection(label: string, options: string[], filterKey: keyof BankingFilters)}
  <div class="space-y-2">
    <span class="text-[0.65rem] font-bold uppercase tracking-widest text-slate-400 px-1">{label}</span>
    <div class="grid gap-1">
      {#each options as option}
        <DropdownMenu.CheckboxItem 
          checked={(bankingStore.filters[filterKey] as string[]).includes(option)}
          onCheckedChange={() => bankingStore.toggleFilter(filterKey, option)}
          class="rounded-md py-1.5 px-2 text-[0.82rem]! cursor-pointer pl-8"
        >
          {option === 'verified' ? 'Vérifié' : option === 'pending' ? 'En attente' : option === 'blocked' ? 'Bloqué' : option}
        </DropdownMenu.CheckboxItem>
      {/each}
    </div>
  </div>
{/snippet}


<div class="flex flex-col h-full">
  {@render Header()}

  <div class="flex flex-col flex-1 overflow-hidden">
    <FilterChips 
      filters={bankingStore.filters}
      activeFiltersCount={bankingStore.activeFiltersCount}
      onRemove={(key, value) => bankingStore.toggleFilter(key as any, value)}
      onReset={() => bankingStore.resetFilters()}
      class="px-6 py-2 border-b border-slate-50 bg-white/50"
    />

    <div class="flex-1 overflow-y-auto p-5 scroll-smooth custom-scrollbar">
      {#if accounts.length > 0}
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
      {:else}
        <div in:fade class="h-full">
          {#if bankingStore.accounts.length === 0}
            <Empty 
              icon="wallet"
              title="Aucun compte"
              iconClass="text-slate-300"
              description="Commencez par ajouter votre premier compte bancaire pour gérer vos transactions."
            >
              <EmptyButton 
                labelElement="un compte" 
                onNew={() => {
                  selectedAccount = null;
                  isSheetOpen = true;
                }} 
              />
            </Empty>
          {:else}
            <Empty 
              icon="search"
              title="Aucun résultat"
              iconClass="text-slate-300"
              description="Nous n'avons trouvé aucun compte correspondant à vos filtres actuels."
            >
              <Button 
                variant="outline" 
                class="border-slate-200 h-9 rounded-lg px-4 text-[0.83rem] shadow-fine"
                onclick={() => bankingStore.resetFilters()}
              >
                Réinitialiser les filtres
              </Button>
            </Empty>
          {/if}
        </div>
      {/if}
    </div>
  </div>
</div>


<BankAccountSheet bind:open={isSheetOpen} bind:account={selectedAccount} />


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

