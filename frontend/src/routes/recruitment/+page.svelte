<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import CampaignCard from "@/features/recruitment/components/lists/views/campaign/CampaignCard.svelte";
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";
  import { onMount } from 'svelte';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { scale } from 'svelte/transition';
  import { Badge } from "@/components/ui/badge";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import CampaignSheet from "@/features/recruitment/components/shared/sheets/campaign/CampaignSheet.svelte";
  import * as AlertDialog from "@/components/ui/alert-dialog";
  import { notification } from "@/stores/notification.svelte";
  import type { RecruitmentCampaign } from "@/features/recruitment/types/types";

  const campaigns = $derived(recruitmentStore.paginatedCampaigns);
  
  let isSheetOpen = $state(false);
  let selectedCampaign = $state<RecruitmentCampaign | null>(null);
  let isDeleteDialogOpen = $state(false);
  let campaignToDelete = $state<RecruitmentCampaign | null>(null);

  function openNewCampaign() {
    selectedCampaign = null;
    isSheetOpen = true;
  }

  function handleEdit(campaign: RecruitmentCampaign) {
    selectedCampaign = campaign;
    isSheetOpen = true;
  }

  function handleDelete(campaign: RecruitmentCampaign) {
    campaignToDelete = campaign;
    isDeleteDialogOpen = true;
  }

  async function confirmDelete() {
    if (campaignToDelete) {
      await recruitmentStore.deleteCampaign(campaignToDelete.id);
      notification.toast.success('Campagne supprimée');
      isDeleteDialogOpen = false;
      campaignToDelete = null;
    }
  }
  
  const sortLabels: Record<string, string> = {
    title: "Titre (A-Z)",
    jobName: "Poste",
    status: "Statut",
    openDate: "Date d'ouverture"
  };

  const statusOptions = [
    { value: 'OPEN', label: 'Ouvert' },
    { value: 'PAUSED', label: 'En pause' },
    { value: 'DRAFT', label: 'Brouillon' },
    { value: 'CLOSED', label: 'Fermé' }
  ];

  const jobNameOptions = [
    { value: 'Ingénierie', label: 'Ingénierie' },
    { value: 'Marketing', label: 'Marketing' },
    { value: 'Ventes', label: 'Ventes' },
    { value: 'RH', label: 'Ressources Humaines' }
  ];

  const typeOptions = [
    { value: 'FULL_TIME', label: 'Temps plein' },
    { value: 'PART_TIME', label: 'Temps partiel' },
    { value: 'CONTRACT', label: 'Contrat' },
    { value: 'INTERNSHIP', label: 'Stage' }
  ];
  
  onMount(() => {
    recruitmentStore.setActiveCampaign(null);
  });
</script>


<svelte:head>
  <title>Oxiliere HR - Campagnes de Recrutement</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={recruitmentStore.campaignFilters}
      activeFiltersCount={recruitmentStore.activeFiltersCount}
      onRemove={(key, value) => recruitmentStore.toggleCampaignFilter(key as any, value)}
      onReset={() => recruitmentStore.resetCampaignFilters()}
      class="mb-2 py-1.5"
    />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <div class="flex-1 overflow-y-auto min-h-0">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-4">
          {#each campaigns as campaign}
            <CampaignCard 
              {campaign} 
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          {/each}
        </div>
      </div>

      {#if recruitmentStore.totalCount > 0}
        <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea]">
          <DataPagination 
            currentCount={campaigns.length}
            totalCount={recruitmentStore.totalCount}
            currentPage={recruitmentStore.currentPage}
            totalPages={recruitmentStore.totalPages}
            perPage={recruitmentStore.perPage}
            onPageChange={(p) => recruitmentStore.setPage(p)}
            onPerPageChange={(s) => recruitmentStore.setPerPage(s)}
            onNext={() => recruitmentStore.nextPage()}
            onPrev={() => recruitmentStore.prevPage()}
            unitLabel="campagnes"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2 pt-2 border-b border-slate-100 px-4 mr-4">
    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={recruitmentStore.searchQuery} 
          placeholder="Rechercher une campagne..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => recruitmentStore.setSearchQuery("")}
        />
      </div>
      
      <div class="flex items-center gap-2">
        {@render FilterMenu()}
        {@render SortMenu()}
        {@render Actions()}
      </div>
    </div>
  </div>
{/snippet}


{#snippet FilterMenu()}
  <div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({ props })}
          <button 
            {...props} 
            class="h-7.5 px-3 flex items-center justify-start gap-2 cursor-pointer outline-none hover:bg-slate-50 transition-all border-none bg-transparent shadow-fine"
          >
            <div class="flex shrink-0 items-center justify-center">
              <AppIcon name="filter" size={16} class="text-slate-500" />
            </div>
            
            <span class="text-[0.84rem] text-slate-700 truncate">
              Filtres
            </span>
            
            {#if recruitmentStore.activeFiltersCount > 0}
              <div transition:scale={{ duration: 200, start: 0.8 }}>
                <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
                  {recruitmentStore.activeFiltersCount}
                </Badge>
              </div>
            {/if}
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="start" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 h-80">
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Statut
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
        {#each statusOptions as option}
          <DropdownMenu.CheckboxItem 
            checked={recruitmentStore.campaignFilters.status.includes(option.value)}
            onCheckedChange={(checked) => {
              if (checked) {
                recruitmentStore.toggleCampaignFilter('status', option.value);
              } else {
                recruitmentStore.toggleCampaignFilter('status', option.value);
              }
            }}
            class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!"
          >
            {option.label}
          </DropdownMenu.CheckboxItem>
        {/each}

        <DropdownMenu.Separator class="my-2 bg-slate-50" />
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Poste
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
        {#each jobNameOptions as option}
          <DropdownMenu.CheckboxItem 
            checked={recruitmentStore.campaignFilters.jobName.includes(option.value)}
            onCheckedChange={() => {
              recruitmentStore.toggleCampaignFilter('jobName', option.value);
            }}
            class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!"
          >
            {option.label}
          </DropdownMenu.CheckboxItem>
        {/each}

        <DropdownMenu.Separator class="my-2 bg-slate-50" />
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Type
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
        {#each typeOptions as option}
          <DropdownMenu.CheckboxItem 
            checked={recruitmentStore.campaignFilters.type.includes(option.value)}
            onCheckedChange={(checked) => {
              if (checked) {
                recruitmentStore.toggleCampaignFilter('type', option.value);
              } else {
                recruitmentStore.toggleCampaignFilter('type', option.value);
              }
            }}
            class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!"
          >
            {option.label}
          </DropdownMenu.CheckboxItem>
        {/each}
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}


{#snippet SortMenu()}
  <div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({ props })}
          <button 
            {...props} 
            class="h-7.5 px-3 flex items-center justify-start gap-2 cursor-pointer outline-none hover:bg-slate-50 transition-all min-w-35 max-w-50 border-none bg-transparent shadow-fine"
          >
            <div class="flex shrink-0 items-center justify-center">
              <AppIcon name="sort" size={16} class="text-slate-500" />
            </div>
            
            <span class="text-[0.84rem] text-slate-700 w-26 truncate">
              {sortLabels[recruitmentStore.sortBy] || "Trier par"}
            </span>
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="start" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Critères
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
          <DropdownMenu.RadioGroup value={recruitmentStore.sortBy} onValueChange={(v) => recruitmentStore.setSort(v)}>
            <DropdownMenu.RadioItem value="title" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Titre (A-Z)
            </DropdownMenu.RadioItem>
            
            <DropdownMenu.RadioItem value="jobName" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Poste
            </DropdownMenu.RadioItem>
            
            <DropdownMenu.RadioItem value="status" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Statut
            </DropdownMenu.RadioItem>
            
            <DropdownMenu.RadioItem value="openDate" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Date d'ouverture
            </DropdownMenu.RadioItem>
          </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <div class="w-8 h-7.5 shrink-0 flex items-center justify-center border-l border-slate-100 bg-slate-50/30">
      <TooltipWrapper content={recruitmentStore.sortOrder === 'asc' ? 'Ordre croissant' : 'Ordre décroissant'}>
        {#snippet children(props)}
          <button 
            {...props}
            onclick={() => recruitmentStore.toggleSortOrder()}
            class="w-full h-full flex items-center justify-center hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <AppIcon 
              name={recruitmentStore.sortOrder === 'asc' ? 'arrow-up' : 'arrow-up'} 
              size={15} 
              class={recruitmentStore.sortOrder === 'desc' ? "text-blue-600" : "text-slate-400"} 
            />
          </button>
        {/snippet}
      </TooltipWrapper>
    </div>
  </div>
{/snippet}


{#snippet Actions()}
  <Button 
    variant="default" 
    size="sm" 
    class="h-7.5 px-3 flex items-center shadow-fine text-[0.84rem]"
    onclick={openNewCampaign}
  >
    <AppIcon name="plus" size={17} />
    Nouvelle campagne
  </Button>
{/snippet}

<CampaignSheet bind:open={isSheetOpen} campaign={selectedCampaign} />

<AlertDialog.Root bind:open={isDeleteDialogOpen}>
  <AlertDialog.Content class="bg-white">
    <AlertDialog.Header>
      <AlertDialog.Title>Supprimer la campagne ?</AlertDialog.Title>
      <AlertDialog.Description>
        Cette action est irréversible. Cela supprimera également tous les candidats associés à cette campagne.
      </AlertDialog.Description>
    </AlertDialog.Header>
    <AlertDialog.Footer>
      <AlertDialog.Cancel>Annuler</AlertDialog.Cancel>
      <AlertDialog.Action onclick={confirmDelete} class="bg-red-600 hover:bg-red-700 text-white">
        Supprimer
      </AlertDialog.Action>
    </AlertDialog.Footer>
  </AlertDialog.Content>
</AlertDialog.Root>

