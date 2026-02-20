<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import EmployeeList from "@/features/employees/components/list/EmployeeList.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
</script>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 gap-8 overflow-hidden min-h-0">
    <!-- Main Content: List -->
    <main class="flex flex-1 flex-col overflow-hidden pb-2 min-h-0">
      <!-- Employee List Container -->
      <div class="flex-1 overflow-y-auto min-h-0">
        <EmployeeList employees={employeeStore.paginatedEmployees} />
      </div>

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
    </main>
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-6 mb-2 border-b border-slate-100">

    <div class="flex items-center gap-3 p-0.75">
      <div class="flex-1">
        {@render SearchBar()}
      </div>
      
      <div class="flex items-center gap-2">
        {@render SortMenu()}
        {@render Actions()}
      </div>
    </div>
  </div>
{/snippet}


{#snippet SearchBar()}
  <div class="relative group w-125 shrink-0">
    <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-all">
      <AppIcon name="search" size={22} />
    </div>
    <Input 
      type="text" 
      placeholder="Rechercher un profil..." 
      class="h-9.5 w-full pl-10 pr-9 bg-[#f5f6f7] border-slate-100 rounded-[18px] focus:bg-white focus:border-none focus:ring-4 focus:ring-primary/5 transition-all text-[0.9rem] placeholder:text-slate-500 placeholder:text-[0.89rem] shadow-none hover:bg-slate-100/50"
      bind:value={employeeStore.searchQuery}
    />
    {#if employeeStore.searchQuery}
      <button 
        class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-all cursor-pointer"
        onclick={() => employeeStore.setSearchQuery("")}
      >
        <AppIcon name="x" size={20} />
      </button>
    {/if}
  </div>
{/snippet}


{#snippet Actions()}
  <div class="ml-auto flex items-center gap-3">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger 
        class="inline-flex items-center justify-center shadow-soft whitespace-nowrap transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-slate-100/80 text-slate-600 border rounded-lg h-7.5 px-3 gap-1.5 relative cursor-pointer"
      >
        <AppIcon name="filter" size={18} class="text-slate-500" />
        <span class="text-[0.86rem] font-medium text-slate-700">Filtrer</span>
        
        {#if employeeStore.activeFiltersCount > 0}
          <Badge 
            variant="default" 
            class="absolute -top-1.5 -right-1.5 size-5 p-0 bg-indigo-600 text-[0.65rem] font-bold rounded-full border-2 border-indigo-600 flex items-center justify-center pointer-events-none shadow-sm"
          >
            {employeeStore.activeFiltersCount}
          </Badge>
        {/if}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="w-64 p-0 rounded-xl shadow-xl border-slate-100 flex flex-col overflow-hidden">
        <div class="px-2 py-2 max-h-80 overflow-y-auto">
          {@render FilterSection("Département", ["Ingénierie", "Produit", "Vente", "Marketing", "Ressources Humaines", "Finance"], "department")}
          
          <DropdownMenu.Separator class="my-1.5 bg-slate-50" />
          {@render FilterSection("Statut", ["Actif", "En intégration", "Suspendu", "Terminé"], "status")}
          
          <DropdownMenu.Separator class="my-1.5 bg-slate-50" />
          {@render FilterSection("Lieu", ["Siège Paris", "Télétravail", "Agence Lyon", "Hub Bordeaux"], "location")}
        </div>

        {#if employeeStore.activeFiltersCount > 0}
          <div class="p-1.5 border-t border-slate-50 bg-slate-50/50">
            <DropdownMenu.Item 
              onclick={() => employeeStore.resetFilters()}
              class="font-semibold text-red-500 hover:text-red-600! hover:bg-red-50! rounded-lg justify-center py-2 transition-colors cursor-pointer bg-white border border-slate-100"
            >
              Effacer les filtres
            </DropdownMenu.Item>
          </div>
        {/if}
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <Button 
      href="/employees/onboarding" 
      class="bg-primary hover:bg-primary/95 h-7.5 px-3 transition-all text-[0.85rem]"
    >
      <AppIcon name="plus" size={18} />
      Ajouter
    </Button>
  </div>
{/snippet}


{#snippet SortMenu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="h-7.5 px-3 shadow-soft border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-1.5 bg-white cursor-pointer outline-none">
      <AppIcon name="sort" size={18} class="text-slate-500" />
      <span class="text-[0.86rem] font-medium text-slate-700">Trier par</span>
    </DropdownMenu.Trigger>
    
    <DropdownMenu.Content align="end" class="w-48 rounded-xl shadow-lg border-slate-100 p-1">
      <DropdownMenu.Label class="text-[0.75rem] text-slate-500 uppercase font-bold tracking-wider px-2 py-1.5">
        Critères
      </DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      
      <DropdownMenu.RadioGroup 
        value={employeeStore.sortBy} 
        onValueChange={(v) => employeeStore.setSort(v)}
      >
        <DropdownMenu.RadioItem value="name" class="rounded-lg py-2 cursor-pointer transition-colors">
          Nom (A-Z)
        </DropdownMenu.RadioItem>
        <DropdownMenu.RadioItem value="joinDate" class="rounded-lg py-2 cursor-pointer transition-colors">
          Date d'embauche
        </DropdownMenu.RadioItem>
        <DropdownMenu.RadioItem value="status" class="rounded-lg py-2 cursor-pointer transition-colors">
          Statut
        </DropdownMenu.RadioItem>
      </DropdownMenu.RadioGroup>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet FilterSection(label: string, options: string[], filterKey: keyof typeof employeeStore.filters)}
  <DropdownMenu.Label class="text-[0.8rem]! font-semibold text-slate-500 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={employeeStore.filters[filterKey].includes(option)}
      onCheckedChange={() => employeeStore.toggleFilter(filterKey, option)}
      class="rounded-lg py-1.5"
    >
      {option}
    </DropdownMenu.CheckboxItem>
  {/each}
{/snippet}

