<script lang="ts">
  import { fly } from 'svelte/transition';
  import { get } from 'svelte/store';
  import { bankingStore } from "@/features/banking/stores/banking.svelte";
  import BankCard from "@/features/banking/components/directory/BankCard.svelte";
  import { Button } from "@/components/ui/button";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import LoadingBar from '@/components/layout/elements/LoadingBar.svelte';
  import BankInstitutionSheet from "@/features/banking/components/directory/sheets/BankInstitutionSheet.svelte";
  import BankingActions from "@/features/banking/components/directory/BankingActions.svelte";
  import type { BankInstitution } from "@/features/banking/types/types";
  import { useBanksQuery, useCreateBankMutation, useUpdateBankMutation, useDeleteBankMutation, useUploadBankLogoMutation } from "@/features/banking/queries/bankingQueries";
  import { ui } from '@/stores/ui.svelte';


  // --- UI State ---
  let isSheetOpen = $state(false);
  let selectedInstitution = $state<BankInstitution | null>(null);

  // Indicateur de filtrage local (pour afficher la barre de chargement)
  let isFiltering = $state(false);

  $effect(() => {
    // Tracker les changements de filtres
    bankingStore.institutionFilters.search;
    bankingStore.institutionFilters.type;
    bankingStore.institutionFilters.isActive;

    const timeout = setTimeout(() => {
      isFiltering = false;
    }, 400);

    const hasActiveFilters =
      bankingStore.institutionFilters.type.length
      + (bankingStore.institutionFilters.search ? 1 : 0)
      + (bankingStore.institutionFilters.isActive !== null ? 1 : 0);

    if (hasActiveFilters > 0) {
      isFiltering = true;
    }

    return () => clearTimeout(timeout);
  });

  // --- TanStack Query ---
  const banksQuery = useBanksQuery();
  const createMutation = useCreateBankMutation();
  const updateMutation = useUpdateBankMutation();
  const deleteMutation = useDeleteBankMutation();
  const uploadLogoMutation = useUploadBankLogoMutation();

  // Sync query data into the store
  $effect(() => {
    const data = $banksQuery.data;
    if (data) {
      bankingStore.updateInstitutions(data);
    }
  });

  // --- Derived ---
  const institutions = $derived.by(() => {
    const data = bankingStore.institutions;
    if (!data) return [];

    let result = data;

    const types = bankingStore.institutionFilters.type;
    if (types.length > 0) {
      result = result.filter(inst => types.includes(inst.type));
    }

    const search = bankingStore.institutionFilters.search.trim().toLowerCase();
    if (search) {
      result = result.filter(inst =>
        inst.name.toLowerCase().includes(search) ||
        inst.shortName.toLowerCase().includes(search) ||
        inst.country.toLowerCase().includes(search)
      );
    }

    const isActive = bankingStore.institutionFilters.isActive;
    if (isActive !== null) {
      result = result.filter(inst => inst.isActive === isActive);
    }

    return result;
  });

  // Construire un objet filters enrichi qui inclut la recherche textuelle
  // pour que FilterChips puisse l'afficher
  const filtersWithSearch = $derived.by((): Record<string, string[]> => {
    const f: Record<string, string[]> = {};
    if (bankingStore.institutionFilters.type.length > 0) {
      f.type = bankingStore.institutionFilters.type;
    }
    if (bankingStore.institutionFilters.search) {
      f.search = [bankingStore.institutionFilters.search];
    }
    if (bankingStore.institutionFilters.isActive !== null) {
      f.isActive = [bankingStore.institutionFilters.isActive.toString()];
    }
    return f;
  });

  const activeFiltersCount = $derived(
    bankingStore.institutionFilters.type.length
    + (bankingStore.institutionFilters.search ? 1 : 0)
    + (bankingStore.institutionFilters.isActive !== null ? 1 : 0)
  );

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche: "${value}"`;
    if (key === 'type') return value === 'bank' ? 'Banques' : 'Mobile Money';
    if (key === 'isActive') return value === 'true' ? 'Actifs' : 'Inactifs';
    return String(value);
  }

  function openNewSheet() {
    selectedInstitution = null;
    isSheetOpen = true;
  }

  function handleEdit(inst: BankInstitution) {
    selectedInstitution = inst;
    isSheetOpen = true;
  }

  // --- Mutation handlers ---
  async function handleCreate(data: {
    name: string;
    shortName: string;
    country: string;
    type: 'bank' | 'mobile_money';
    swiftCode: string;
    isActive: boolean;
  }): Promise<BankInstitution> {
    return await $createMutation.mutateAsync({
      name: data.name,
      code: data.shortName,
      swift_code: data.swiftCode || undefined,
      is_mobile_money: data.type === 'mobile_money',
      country_code: data.country,
      is_active: data.isActive,
    });
  }

  async function handleUpdate(id: string, data: {
    name: string;
    shortName: string;
    country: string;
    type: 'bank' | 'mobile_money';
    swiftCode: string;
    isActive: boolean;
  }) {
    await $updateMutation.mutateAsync({
      bankId: id,
      data: {
        name: data.name,
        code: data.shortName,
        swift_code: data.swiftCode || undefined,
        is_mobile_money: data.type === 'mobile_money',
        country_code: data.country,
        is_active: data.isActive,
      },
    });
  }

  async function handleDelete(instId: string) {
    await $deleteMutation.mutateAsync(instId);
  }

  async function handleUploadLogo(bankId: string, file: File) {
    await $uploadLogoMutation.mutateAsync({ bankId, file });
  }

  // Enregistrer les actions dans le store UI (comme les pages LeavesBoard/employés)
  $effect(() => {
    ui.addActions('banking-directory', BankingActionsSnippet);
    return () => {
      ui.removeActions('banking-directory');
    };
  });
</script>


<div class="flex flex-col h-full bg-white">
  {@render Header()}

  <div class="flex flex-col flex-1 overflow-hidden">
    <FilterChips 
      filters={filtersWithSearch}
      activeFiltersCount={activeFiltersCount}
      getDisplayLabel={getFilterDisplayLabel}
      onRemove={(key, value) => {
        if (key === 'search') {
          bankingStore.institutionFilters.search = '';
        } else if (key === 'isActive') {
          bankingStore.institutionFilters.isActive = null;
        } else {
          bankingStore.toggleInstitutionType(value as any);
        }
      }}
      onReset={() => bankingStore.resetInstitutionFilters()}
      class="px-6 py-1.5 border-b border-slate-50 bg-white/50"
    />

    <!-- Overhead loading bar during refetch -->
    <LoadingBar loading={$banksQuery.isFetching || isFiltering} class="shrink-0" />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      {#if $banksQuery.isPending}
        <div class="flex-1 flex items-center justify-center" in:fly={{ y: 15, duration: 300 }}>
          <AnimateSpin text="Chargement des institutions" />
        </div>
      {:else if $banksQuery.error}
        <div class="flex-1 flex items-center justify-center" in:fly={{ y: 15, duration: 300 }}>
          <Empty 
            title="Erreur de chargement"
            description="Impossible de charger la liste des institutions financières."
            icon="alert-circle"
            iconSize={28}
            iconStrokeWidth={1.3}
            iconClass="text-rose-300"
          >
            <Button onclick={() => get(banksQuery).refetch()} class="h-7">
              <AppIcon name="refresh" size={15} />
              Réessayer
            </Button>
          </Empty>
        </div>
      {:else if institutions.length === 0}
        <div class="flex-1 flex items-center justify-center" in:fly={{ y: 15, duration: 300 }}>
          <Empty 
            title="Aucune institution"
            description={activeFiltersCount > 0
              ? "Aucune institution ne correspond à vos critères."
              : "Aucune institution financière n'a encore été enregistrée."}
            icon={activeFiltersCount > 0 ? "search-x" : "bank"}
            iconSize={28}
            iconStrokeWidth={1.3}
            iconClass="text-slate-300"
          >
            {#if activeFiltersCount > 0}
              <Button variant="ghost" onclick={() => bankingStore.resetInstitutionFilters()} class="h-7 bg-slate-50">
                <AppIcon name="x" size={16} class="text-slate-400" />
                Réinitialiser les filtres
              </Button>
            {:else}
              <Button onclick={openNewSheet} class="h-7">
                <AppIcon name="plus" size={15} />
                Nouvelle institution
              </Button>
            {/if}
          </Empty>
        </div>
      {:else}
        <div class="flex-1 overflow-y-auto p-5 scroll-smooth custom-scrollbar" in:fly={{ y: 15, duration: 300, delay: 80 }}>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each institutions as institution (institution.id)}
              <div in:fly={{ y: 20, duration: 400 }}>
                <BankCard 
                  {institution} 
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                />
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </main>
  </div>
</div>


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
      
      <Button 
        variant="default" 
        class="h-7.5 px-4 bg-primary text-white shadow-fine rounded-lg hover:bg-primary/90 transition-all cursor-pointer"
        onclick={openNewSheet}
      >
        <AppIcon name="plus" size={17} />
        <span class="text-[0.86rem]">Nouvelle institution</span>
      </Button>
    </div>
  </div>
{/snippet}


<!-- WRAPPER FOR ui.addActions -->
{#snippet BankingActionsSnippet()}
  <BankingActions />
{/snippet}


<BankInstitutionSheet 
  bind:open={isSheetOpen} 
  bind:institution={selectedInstitution} 
  onCreate={handleCreate}
  onUpdate={handleUpdate}
  onUploadLogo={handleUploadLogo}
/>




