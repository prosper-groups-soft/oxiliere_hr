<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import EmployeeList from "@/features/employees/components/mngt/list/EmployeeList.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { scale } from "svelte/transition";
  import { cn } from "@/utilities/common/css";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";

  const sortLabels: Record<string, string> = {
    name: "Nom (A-Z)",
    joinDate: "Date d'embauche",
    status: "Statut"
  };
</script>


<svelte:head>
  <title>Oxiliere HR - Employés</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={employeeStore.filters}
      activeFiltersCount={employeeStore.activeFiltersCount}
      onRemove={(key, value) => employeeStore.toggleFilter(key as any, value)}
      onReset={() => employeeStore.resetFilters()}
      class="mb-2 py-1.5"
    />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <div class="flex-1 overflow-y-auto min-h-0">
        <EmployeeList 
          employees={employeeStore.paginatedEmployees} 
          viewMode={employeeStore.viewMode} 
        />
      </div>

      {#if employeeStore.totalCount > 0}
        <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
          <DataPagination 
            currentCount={employeeStore.paginatedEmployees.length}
            totalCount={employeeStore.totalCount}
            currentPage={employeeStore.currentPage}
            totalPages={employeeStore.totalPages}
            perPage={employeeStore.perPage}
            onPageChange={(p) => employeeStore.setPage(p)}
            onPerPageChange={(s) => employeeStore.setPerPage(s)}
            onNext={() => employeeStore.nextPage()}
            onPrev={() => employeeStore.prevPage()}
            unitLabel="profils"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8.5">
    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={employeeStore.searchQuery} 
          placeholder="Rechercher un profil..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => employeeStore.setSearchQuery("")}
        />
      </div>
      
      <div class="flex items-center gap-2">
        <div>
          <TooltipWrapper content={employeeStore.viewMode === 'list' ? "Passer en vue grille" : "Passer en vue liste"}>
            {#snippet children(props)}
              <button 
                {...props}
                onclick={() => employeeStore.toggleViewMode()}
                class="h-7.5 w-7.5 flex items-center justify-center bg-white border border-slate-300 rounded-lg shadow-fine hover:bg-slate-50 text-slate-600 transition-all cursor-pointer outline-none"
              >
                {#if employeeStore.viewMode === 'list'}
                  <div in:scale={{ duration: 150 }}>
                    <AppIcon name="layout-grid" size={17} />
                  </div>
                {:else}
                  <div in:scale={{ duration: 150 }}>
                    <AppIcon name="list" size={17} />
                  </div>
                {/if}
              </button>
            {/snippet}
          </TooltipWrapper>
        </div>

        {@render SortMenu()}
        {@render Actions()}
      </div>
    </div>
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
            
            <span class="text-[0.84rem] text-slate-700 w-26 font-medium truncate">
              {sortLabels[employeeStore.sortBy] || "Trier par"}
            </span>
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="start" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Critères
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
          <DropdownMenu.RadioGroup value={employeeStore.sortBy} onValueChange={(v) => employeeStore.setSort?.(v)}>
            <DropdownMenu.RadioItem value="name" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Nom (A-Z)
            </DropdownMenu.RadioItem>
            
            <DropdownMenu.RadioItem value="joinDate" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Date d'embauche
            </DropdownMenu.RadioItem>
            
            <DropdownMenu.RadioItem value="status" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Statut
            </DropdownMenu.RadioItem>
          </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <div class="w-8 h-7.5 shrink-0 flex items-center justify-center border-l border-slate-100 bg-slate-50/30">
      <TooltipWrapper content={employeeStore.sortOrder === 'asc' ? 'Ordre croissant' : 'Ordre décroissant'}>
        {#snippet children(props)}
          <button 
            {...props}
            onclick={() => employeeStore.toggleSortOrder?.()}
            class="w-full h-full flex items-center justify-center hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <div class={cn("transition-transform duration-300 flex items-center justify-center", employeeStore.sortOrder === 'desc' ? "rotate-180" : "rotate-0")}>
              <AppIcon name="arrow-up" size={15} class={employeeStore.sortOrder === 'desc' ? "text-blue-600" : "text-slate-400"} />
            </div>
          </button>
        {/snippet}
      </TooltipWrapper>
    </div>
  </div>
{/snippet}


{#snippet Actions()}
  <div class="flex items-center gap-3">
    <!-- Filtres -->
    <DropdownMenu.Root>
      <DropdownMenu.Trigger 
        class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all"
      >
        <AppIcon name="filter" size={16} class={employeeStore.activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
        <span class="text-[0.84rem] text-slate-700">Filtrer</span>
        {#if employeeStore.activeFiltersCount > 0}
          <div transition:scale={{ duration: 200, start: 0.8 }}>
            <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
              {employeeStore.activeFiltersCount}
            </Badge>
          </div>
        {/if}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="w-64 p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
        <div class="p-3 border-b border-slate-50 bg-slate-50/30">
          <input 
            type="text" 
            placeholder="Chercher un département..." 
            class="w-full text-[0.83rem] p-1.5 border rounded-md bg-white outline-none focus:border-blue-300"
          />
        </div>

        <div class="p-2 max-h-80 overflow-y-auto">
          {@render FilterSection("Département", ["Ingénierie", "Produit", "Vente"], "department")}
          <DropdownMenu.Separator class="my-2 bg-slate-50" />
          {@render FilterSection("Statut", ["Actif", "En intégration"], "status")}
        </div>

        {#if employeeStore.activeFiltersCount > 0}
          <div class="p-2 bg-slate-50/50 border-t border-slate-100">
            <Button variant="ghost" onclick={() => employeeStore.resetFilters()} class="w-full h-8 text-[0.84rem] bg-white text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
              Réinitialiser tout
            </Button>
          </div>
        {/if}
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <Button href="/employees/onboarding" class="bg-blue-600 hover:bg-blue-700 h-7.5 px-3 text-[0.84rem] text-white rounded-lg shadow-fine">
      <AppIcon name="plus" size={17} />
      Ajouter
    </Button>
  </div>
{/snippet}


{#snippet FilterSection(label: string, options: string[], filterKey: keyof typeof employeeStore.filters)}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={employeeStore.filters[filterKey].includes(option)}
      onCheckedChange={() => employeeStore.toggleFilter(filterKey, option)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {option}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}

