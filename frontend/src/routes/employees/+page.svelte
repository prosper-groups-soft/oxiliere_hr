<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import EmployeeList from "@/features/employees/components/list/EmployeeList.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/utils";
</script>


<div class="flex h-full flex-col max-w-[1400px] overflow-hidden min-h-0 px-8">
  {@render Header()}

  <div class="flex flex-1 gap-8 overflow-hidden min-h-0">
    <!-- Main Content: List -->
    <main class="flex flex-1 flex-col overflow-hidden pb-2 min-h-0">
      <!-- Employee List Container -->
      <div class="flex-1 overflow-y-auto no-scrollbar min-h-0">
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
  <div class="flex items-center h-16 mb-4 border-b border-slate-100">
    <!-- Title: 120px anchor -->
    <div class="w-[120px] shrink-0">
      <h1 class="text-lg font-bold tracking-tight text-slate-900 line-clamp-1">Employés</h1>
    </div>

    <!-- Toolbar: Flex container -->
    <div class="flex items-center flex-1 min-w-0">
      <!-- Search Bar -->
      <div class="relative group w-[500px] shrink-0">
        <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-all">
          <AppIcon name="search" size={15} />
        </div>
        <Input 
          type="text" 
          placeholder="Rechercher un profil..." 
          class="h-[38px] w-full pl-10 pr-9 bg-[#F9FAFB] border-slate-100 rounded-[10px] focus:bg-white focus:border-primary/40 focus:ring-4 focus:ring-primary/5 transition-all text-[13px] placeholder:text-slate-400 shadow-none hover:bg-slate-100/50"
          bind:value={employeeStore.searchQuery}
        />
        {#if employeeStore.searchQuery}
          <button 
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-all cursor-pointer"
            onclick={() => employeeStore.setSearchQuery("")}
          >
            <AppIcon name="x" size={14} />
          </button>
        {/if}
      </div>

      <!-- Actions: Right aligned -->
      <div class="ml-auto flex items-center gap-3">
        <DropdownMenu.Root>
          <DropdownMenu.Trigger>
            <Button 
              variant="ghost"
              class="h-9 px-3 rounded-[10px] text-slate-600 hover:bg-slate-100/80 text-[13px] font-medium relative"
            >
              <AppIcon name="filter" size={14} class="mr-2" />
              Filtrer
              {#if employeeStore.activeFiltersCount > 0}
                <Badge 
                  variant="default" 
                  class="absolute -top-1.5 -right-1.5 size-5 p-0 bg-indigo-600 text-[10px] font-bold rounded-full border-2 border-indigo-600 flex items-center justify-center pointer-events-none shadow-sm"
                >
                  {employeeStore.activeFiltersCount}
                </Badge>
              {/if}
            </Button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end" class="w-64 p-0 rounded-xl shadow-xl border-slate-100 flex flex-col overflow-hidden">
            <!-- Scrollable Filter Area -->
            <div class="px-2 py-2 max-h-[320px] overflow-y-auto">
              <DropdownMenu.Label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 py-2">Département</DropdownMenu.Label>
              {#each ["Ingénierie", "Produit", "Vente", "Marketing", "Ressources Humaines", "Finance"] as dept}
                <DropdownMenu.CheckboxItem 
                  checked={employeeStore.filters.department.includes(dept)}
                  onCheckedChange={() => employeeStore.toggleFilter("department", dept)}
                  class="text-[13px] rounded-lg py-1.5"
                >
                  {dept}
                </DropdownMenu.CheckboxItem>
              {/each}

              <DropdownMenu.Separator class="my-1.5 bg-slate-50" />
              
              <DropdownMenu.Label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 py-2">Statut</DropdownMenu.Label>
              {#each ["Actif", "En intégration", "Suspendu", "Terminé"] as stat}
                <DropdownMenu.CheckboxItem 
                  checked={employeeStore.filters.status.includes(stat)}
                  onCheckedChange={() => employeeStore.toggleFilter("status", stat)}
                  class="text-[13px] rounded-lg py-1.5"
                >
                  {stat}
                </DropdownMenu.CheckboxItem>
              {/each}

              <DropdownMenu.Separator class="my-1.5 bg-slate-50" />
              
              <DropdownMenu.Label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-2 py-2">Lieu</DropdownMenu.Label>
              {#each ["Siège Paris", "Télétravail", "Agence Lyon", "Hub Bordeaux"] as loc}
                <DropdownMenu.CheckboxItem 
                  checked={employeeStore.filters.location.includes(loc)}
                  onCheckedChange={() => employeeStore.toggleFilter("location", loc)}
                  class="text-[13px] rounded-lg py-1.5"
                >
                  {loc}
                </DropdownMenu.CheckboxItem>
              {/each}
            </div>

            <!-- Fixed Footer Action -->
            {#if employeeStore.activeFiltersCount > 0}
              <div class="p-1.5 border-t border-slate-50 bg-slate-50/50">
                <DropdownMenu.Item 
                  onclick={() => employeeStore.resetFilters()}
                  class="text-[13px] font-semibold text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg justify-center py-2 transition-colors cursor-pointer bg-white border border-slate-100"
                >
                  Effacer les filtres
                </DropdownMenu.Item>
              </div>
            {/if}
          </DropdownMenu.Content>
        </DropdownMenu.Root>

        <Button 
          href="/employees/onboarding" 
          class="bg-primary hover:bg-primary/95 text-primary-foreground h-9 px-4 rounded-[10px] shadow-sm transition-all text-[13px] font-semibold"
        >
          <AppIcon name="plus" size={14} class="mr-2" />
          Ajouter
        </Button>
      </div>
    </div>
  </div>
{/snippet}

