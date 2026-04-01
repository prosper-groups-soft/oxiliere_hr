<script lang="ts">
  import { attendanceStore } from "../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { WorkPolicy } from "../../types/types";
  import PolicySheet from "./sheets/policy/PolicySheet.svelte";
  import PolicyCard from "./views/PolicyCard.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import { cn } from "@/utilities/common/css";
  import { notification } from "@/stores/notification.svelte";
  
  // Important for animations
  import { fade, fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';

  type Policy = WorkPolicy;

  const sortLabels: Record<string, string> = {
    name: "Nom (A-Z)",
    created: "Date de création",
    activeDays: "Jours actifs"
  };

  let searchQuery = $state("");
  let sortBy = $state("name");
  let sortOrder = $state<"asc" | "desc">("asc");

  let showForm = $state(false);
  let editingPolicy = $state<Policy | null>(null);

  const filteredPolicies = $derived.by(() => {
    return attendanceStore.getFilteredPolicies(searchQuery, sortBy, sortOrder);
  });

  function openNewForm() {
    editingPolicy = {
      name: "",
      description: "",
      pattern: { 
        0: { isOff: true, periods: [] }, 
        1: { isOff: false, periods: [
          { id: "1", startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: "2", startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: "3", startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
        ]}, 
        2: { isOff: false, periods: [
          { id: "1", startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: "2", startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: "3", startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
        ]}, 
        3: { isOff: false, periods: [
          { id: "1", startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: "2", startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: "3", startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
        ]}, 
        4: { isOff: false, periods: [
          { id: "1", startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: "2", startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: "3", startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
        ]}, 
        5: { isOff: false, periods: [
          { id: "1", startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: "2", startTime: "12:00", endTime: "14:00", type: "break", name: "Pause déjeuner" },
          { id: "3", startTime: "14:00", endTime: "18:00", type: "work", name: "Après-midi" }
        ]}, 
        6: { isOff: true, periods: [] }, 
      },
    };
    showForm = true;
  }

  function toggleSortOrder() {
    sortOrder = sortOrder === "asc" ? "desc" : "asc";
  }

  function editPolicy(policy: Policy) {
    editingPolicy = JSON.parse(JSON.stringify(policy));
    showForm = true;
  }

  function deletePolicy(policy: Policy) {
    notification.confirm({
      title: "Suppression de la politique",
      message: `Êtes-vous sûr de vouloir supprimer la politique "${policy.name}" ?`,
      onYes: () => {
        console.log('Deleting policy:', policy);
      }
    });
  }
</script>


<div class="flex h-full flex-col bg-white overflow-hidden">
  {@render Header()}

  <div class="custom-scrollbar flex-1 overflow-auto p-6">
    {#if filteredPolicies.length === 0}
      <div in:fade={{ duration: 200 }}>
        <Empty 
          title="Aucun modèle de travail trouvé" 
          description="Commencez par créer votre premier modèle de travail pour organiser les horaires de vos employés."
          icon="briefcase"
          iconSize={32}
          iconStrokeWidth={1.2}
          iconClass="text-primary"
        >
          <EmptyButton 
            labelElement="un modèle" 
            onNew={openNewForm} 
          />
        </Empty>
      </div>
    {:else}
      <div 
        class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
        in:fly={{ y: 20, duration: 400, delay: 100 }}
      >
        {#each filteredPolicies as policy (policy.id)}
          <div animate:flip={{ duration: 400 }}>
            <PolicyCard 
              {policy} 
              onEdit={editPolicy}
              onDelete={deletePolicy}
            />
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>


<PolicySheet bind:open={showForm} bind:policy={editingPolicy} />


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8.5">
    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={searchQuery} 
          placeholder="Rechercher un modèle..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => searchQuery = ""}
        />
      </div>
      
      <div class="flex items-center gap-2">
        {@render SortMenu()}
        {@render Actions()}
      </div>
    </div>
  </div>
{/snippet}


{#snippet SortMenu()}
  <div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden h-7.5">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({ props })}
          <button 
            {...props} 
            class="h-7.5 px-3 flex items-center justify-start gap-2 cursor-pointer outline-none hover:bg-slate-50 transition-all min-w-35 max-w-50 border-none bg-transparent"
          >
            <div class="flex shrink-0 items-center justify-center">
              <AppIcon name="sort" size={16} class="text-slate-500" />
            </div>
            
            <span class="text-[0.84rem] text-slate-700 w-26 font-medium truncate text-left">
              {sortLabels[sortBy] || "Trier par"}
            </span>
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="start" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Critères
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
        
        <DropdownMenu.RadioGroup value={sortBy} onValueChange={(v) => sortBy = v}>
          {#each Object.entries(sortLabels) as [key, label]}
            <DropdownMenu.RadioItem value={key} class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              {label}
            </DropdownMenu.RadioItem>
          {/each}
        </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <div class="w-8 h-full shrink-0 flex items-center justify-center border-l border-slate-100 bg-slate-50/30">
      <TooltipWrapper content={sortOrder === 'asc' ? 'Ordre croissant' : 'Ordre décroissant'}>
        {#snippet children(props)}
          <button 
            {...props}
            onclick={toggleSortOrder}
            class="w-full h-full flex items-center justify-center hover:bg-slate-100 transition-colors cursor-pointer outline-none"
          >
            <div class={cn("transition-transform duration-300 flex items-center justify-center", sortOrder === 'desc' ? "rotate-180" : "rotate-0")}>
              <AppIcon name="arrow-up" size={15} class={sortOrder === 'desc' ? "text-blue-600" : "text-slate-400"} />
            </div>
          </button>
        {/snippet}
      </TooltipWrapper>
    </div>
  </div>
{/snippet}


{#snippet Actions()}
  <Button
    onclick={openNewForm}
    size="sm"
    variant="default"
    class="h-7.5 px-3 rounded-lg text-[0.84rem] shadow-fine transition-all"
  >
    <AppIcon name="plus" size={17} />
    Ajouter modèle
  </Button>
{/snippet}


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>

