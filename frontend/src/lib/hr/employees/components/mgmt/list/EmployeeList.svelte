<script lang="ts">
  import { flip } from 'svelte/animate';
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import EmployeeRow from './views/EmployeeRow.svelte';
  import EmployeeCard from './views/EmployeeCard.svelte';
  import { cn } from '@/utilities/common/css';
  import { Button } from "@/components/ui/button";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';


  let { 
    employees, 
    viewMode = 'list', 
    activeFiltersCount = 0, 
    searchQuery = '', 
    onResetFilters, 
    onAdd
  } = $props();
</script>


<div class="flex flex-col h-full">
  {#if employees.length === 0}
    <div in:fade={{ duration: 200 }} class="h-full">
      <Empty
        title="Aucun employé trouvé"
        description={activeFiltersCount > 0 || searchQuery
          ? "Aucun résultat ne correspond à vos critères de recherche."
          : "Aucun employé n'a été enregistré."}
        icon={activeFiltersCount > 0 || searchQuery ? "search-x" : "no-user"}
        iconClass="text-slate-300"
        iconSize={28}
        iconStrokeWidth={1.3}
      >
        {#if activeFiltersCount > 0 || searchQuery}
          <Button variant="ghost" onclick={onResetFilters} class="h-7 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Réinitialiser les filtres
          </Button>
        {:else}
          <Button variant="default" onclick={onAdd} class="h-7">
            <AppIcon name="plus" size={17} class="text-white" />
            Ajouter un employé
          </Button>
        {/if}
      </Empty>
    </div>
  {:else}
    <div class="relative h-full">
      {#key viewMode}
        {#if viewMode === 'list'}
          <!-- Headers -->
          <div class="sticky top-0 z-10 flex items-center h-8 px-6 bg-white border-b border-slate-100">
            <span class="w-[28%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
            <span class="w-[18%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Unité Org.</span>
            <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Contrat</span>
            <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Embauche</span>
            <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Localisation</span>
            <span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-4">Statut</span>
            <span class="w-[5%]"></span>
          </div>
        {/if}

        <div
          in:fly={{ y: 20, duration: 400, delay: 200, easing: cubicOut }}
          out:fade={{ duration: 200 }}
          class={cn(
            'w-full',
            viewMode === 'grid'
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 p-6'
              : 'flex flex-col'
          )}
        >
          {#each employees as employee (employee.id)}
            <div animate:flip={{ duration: 400, easing: cubicOut }}>
              {#if viewMode === 'list'}
                <EmployeeRow {employee} />
              {:else}
                <EmployeeCard {employee} />
              {/if}
            </div>
          {/each}
        </div>
      {/key}
    </div>
  {/if}
</div>

