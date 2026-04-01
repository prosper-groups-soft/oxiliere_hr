<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { bankingStore } from "@/features/banking/stores/banking.svelte";
  import BankCard from "@/features/banking/components/directory/BankCard.svelte";
  import { Button } from "@/components/ui/button";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import BankInstitutionSheet from "@/features/banking/components/directory/sheets/BankInstitutionSheet.svelte";
  import type { BankInstitution } from "@/features/banking/types/types";
  import { fade, fly, scale } from "svelte/transition";

  let isSheetOpen = $state(false);
  let selectedInstitution = $state<BankInstitution | null>(null);

  const institutions = $derived(bankingStore.filteredInstitutions);

  function openNewSheet() {
    selectedInstitution = null;
    isSheetOpen = true;
  }
</script>


{#snippet FilterSection(title: string, options: string[], filterKey: 'type')}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {title}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={bankingStore.institutionFilters[filterKey].includes(option as any)}
      onCheckedChange={() => {
         if (filterKey === 'type') bankingStore.toggleInstitutionType(option as any);
      }}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {option === 'bank' ? 'Banques' : 'Mobile Money'}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}


{#snippet Header()}
  <div class="flex flex-col gap-3 py-2 border-b border-slate-100 pl-6 pr-9">
    <div class="flex items-center justify-between">
      <div class="flex-1 max-w-md">
        <SearchBar 
          bind:value={bankingStore.institutionFilters.search} 
          placeholder="Rechercher une banque ou un service..."
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => bankingStore.institutionFilters.search = ""}
        />
      </div>
      
      <div class="flex items-center gap-2">
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
                  class={bankingStore.activeInstitutionFiltersCount > 0 ? "text-primary" : "text-slate-400"} 
                />
                <span class="text-[0.86rem]">Type</span>
                {#if bankingStore.activeInstitutionFiltersCount > 0}
                  <div transition:scale={{ duration: 200 }}>
                    <Badge class="h-4 min-w-4 p-0 flex items-center justify-center bg-primary text-white font-medium rounded-full text-[0.6rem] border-none">
                      {bankingStore.activeInstitutionFiltersCount}
                    </Badge>
                  </div>
                {/if}
              </Button>
            {/snippet}
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end" class="w-50 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
            <div class="p-2 max-h-80 overflow-y-auto">
              {@render FilterSection("Type d'entité", ["bank", "mobile_money"], "type")}
            </div>

            {#if bankingStore.activeInstitutionFiltersCount > 0}
              <div class="p-2 bg-slate-50/50 border-t border-slate-100">
                <Button variant="ghost" onclick={() => bankingStore.resetInstitutionFilters()} class="w-full h-8 text-[0.84rem] bg-white text-rose-500 hover:text-rose-600 hover:bg-rose-50! font-medium">
                  Réinitialiser
                </Button>
              </div>
            {/if}
          </DropdownMenu.Content>
        </DropdownMenu.Root>

        <Button 
          variant="default" 
          class="h-7.5 px-4 gap-2 bg-primary text-white shadow-fine rounded-lg hover:bg-primary/90 transition-all cursor-pointer"
          onclick={openNewSheet}
        >
          <AppIcon name="plus" size={16} />
          <span class="text-[0.86rem]">Nouvelle institution</span>
        </Button>
      </div>
    </div>
  </div>
{/snippet}


<div class="flex flex-col h-full bg-white">
  {@render Header()}

  <div class="flex flex-col flex-1 overflow-hidden">
    <FilterChips 
      filters={bankingStore.institutionFilters}
      activeFiltersCount={bankingStore.activeInstitutionFiltersCount}
      onRemove={(key, value) => {
        if (key === 'type') bankingStore.toggleInstitutionType(value as any);
      }}
      onReset={() => bankingStore.resetInstitutionFilters()}
      class="px-6 py-2 border-b border-slate-50 bg-white/50"
    />

    <div class="flex-1 overflow-y-auto p-5 scroll-smooth custom-scrollbar">
      {#if institutions.length > 0}
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {#each institutions as institution (institution.id)}
            <div in:fly={{ y: 20, duration: 400 }}>
              <BankCard 
                {institution} 
                onEdit={(inst) => {
                  selectedInstitution = inst;
                  isSheetOpen = true;
                }}
              />
            </div>
          {/each}
        </div>
      {:else}
        <div in:fade class="h-full">
          <Empty 
            icon="search"
            title="Aucune institution"
            iconClass="text-slate-300"
            description="Désolé, nous n'avons trouvé aucun établissement correspondant à votre recherche."
          >
            <Button 
              variant="outline" 
              class="border-slate-200 h-9 rounded-lg px-4 text-[0.83rem] shadow-fine"
              onclick={() => bankingStore.resetInstitutionFilters()}
            >
              Réinitialiser les filtres
            </Button>
          </Empty>
        </div>
      {/if}
    </div>
  </div>
</div>


<BankInstitutionSheet bind:open={isSheetOpen} bind:institution={selectedInstitution} />


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

