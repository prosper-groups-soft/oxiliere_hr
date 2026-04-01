<script lang="ts">
  import { attendanceStore } from "../../stores/attendance.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { 
    WorkPolicy, 
    PolicyAssignment 
  } from "../../types/types";
  import type { Employee } from "@/features/employees/types/types";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { notification } from "@/stores/notification.svelte";
  import AssignmentSheet from "./sheets/shift/AssignmentSheet.svelte";
  import BulkAssignmentSheet from "./sheets/shift/BulkAssignmentSheet.svelte";
  import PolicyComparisonSheet from "./sheets/shift/PolicyComparisonSheet.svelte";
  import EmployeeCard from "./views/EmployeeCard.svelte";
  
  import { fade, fly, scale } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import { cn } from "@/utilities/common/css";

  interface EmployeeWithAssignment extends Employee {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
    basePolicy?: WorkPolicy;
    overridePolicy?: WorkPolicy;
  }

  const sortLabels: Record<string, string> = {
    name: "Nom (A-Z)",
    department: "Département",
    policy: "Modèle"
  };

  let selectedEmployee = $state<EmployeeWithAssignment | null>(null);
  let showAssignmentSheet = $state(false);
  let showBulkAssignmentSheet = $state(false);
  let showComparisonSheet = $state(false);

  const employeesWithAssignments = $derived.by(() => {
    return employeeStore.employees
      .map(emp => {
        const baseAssignment = attendanceStore.policyAssignments.find(pa => pa.employeeId === emp.id && !pa.isOverride);
        const overrideAssignment = attendanceStore.policyAssignments.find(pa => pa.employeeId === emp.id && pa.isOverride);
        
        const basePolicy = baseAssignment ? attendanceStore.policies.find(p => p.id === baseAssignment.policyId) : undefined;
        const overridePolicy = overrideAssignment ? attendanceStore.policies.find(p => p.id === overrideAssignment.policyId) : undefined;
        
        return {
          ...emp,
          baseAssignment,
          overrideAssignment,
          basePolicy,
          overridePolicy
        } as EmployeeWithAssignment;
      })
      .filter(emp => emp.basePolicy || emp.overridePolicy); 
  }); 

  const filteredEmployees = $derived.by(() => {
    let result = [...employeesWithAssignments];
    
    // Filter
    if (attendanceStore.filters.search) {
      const search = attendanceStore.filters.search.toLowerCase();
      result = result.filter(emp => 
        emp.name.toLowerCase().includes(search) ||
        emp.department.toLowerCase().includes(search) ||
        emp.email?.toLowerCase().includes(search)
      );
    }
    
    if (attendanceStore.filters.department.length > 0) {
      result = result.filter(emp => attendanceStore.filters.department.includes(emp.department));
    }
    
    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      if (attendanceStore.sortBy === 'name') {
        comparison = a.name.localeCompare(b.name);
      } else if (attendanceStore.sortBy === 'department') {
        comparison = a.department.localeCompare(b.department);
      } else if (attendanceStore.sortBy === 'policy') {
        const policyA = a.basePolicy?.name || '';
        const policyB = b.basePolicy?.name || '';
        comparison = policyA.localeCompare(policyB);
      }
      return attendanceStore.sortOrder === 'asc' ? comparison : -comparison;
    });
    
    return result;
  });

  function openAssignmentSheet(employee: EmployeeWithAssignment) {
    selectedEmployee = employee;
    showAssignmentSheet = true;
  }

  function handleEditEmployee(employee: EmployeeWithAssignment) {
    openAssignmentSheet(employee);
  }

  function handleRemoveEmployee(employee: EmployeeWithAssignment) {
    removeAssignment(employee);
  }

  function openBulkAssignmentSheet() {
    showBulkAssignmentSheet = true;
  }

  function openComparisonSheet(employee: EmployeeWithAssignment) {
    selectedEmployee = employee;
    showComparisonSheet = true;
  }

  function removeAssignment(employee: EmployeeWithAssignment) {
    notification.confirm({
      title: "Suppression de l'affectation",
      message: `Êtes-vous sûr de vouloir supprimer l'affectation du modèle pour ${employee.name} ?`,
      onYes: () => {
        const index = attendanceStore.policyAssignments.findIndex(pa => pa.employeeId === employee.id);
        if (index !== -1) {
          attendanceStore.policyAssignments.splice(index, 1);
          attendanceStore.policyAssignments = [...attendanceStore.policyAssignments];
        }
      }
    });
  }
</script>


<div class="flex h-full flex-col bg-white overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={attendanceStore.filters}
      activeFiltersCount={attendanceStore.activeFiltersCount}
      onRemove={(key, value) => attendanceStore.toggleFilter(key as any, value)}
      onReset={() => attendanceStore.resetFilters()}
      class="px-6 py-2 border-b border-slate-50"
    />

    <div class="custom-scrollbar flex-1 overflow-auto p-6">
      {#if filteredEmployees.length === 0}
        <div in:fade={{ duration: 200 }}>
          <Empty 
            title="Aucun planning trouvé" 
            description="Aucun employé avec un planning ne correspond à votre recherche."
            icon="calendar-days"
            iconSize={32}
            iconStrokeWidth={1.2}
            iconClass="text-primary"
          />
        </div>
      {:else}
        <div 
          class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
          in:fly={{ y: 20, duration: 400, delay: 100 }}
        >
          {#each filteredEmployees as employee (employee.id)}
            <div animate:flip={{ duration: 400 }}>
              <EmployeeCard 
                {employee} 
                onEdit={handleEditEmployee}
                onRemove={handleRemoveEmployee}
                onViewDetail={openComparisonSheet}
              />
            </div>
          {/each} 
        </div>
      {/if}
    </div>
  </div>
</div>


<!-- Sheets of affection -->
<AssignmentSheet bind:open={showAssignmentSheet} employee={selectedEmployee} />
<BulkAssignmentSheet bind:open={showBulkAssignmentSheet} />
<PolicyComparisonSheet bind:open={showComparisonSheet} employee={selectedEmployee} />


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8.5">
    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={attendanceStore.filters.search} 
          placeholder="Rechercher un employé ou un département..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => attendanceStore.filters.search = ""}
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
  <div class="flex items-center bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden">
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
            
            <span class="text-[0.84rem] text-slate-700 w-26 font-medium truncate">
              {sortLabels[attendanceStore.sortBy] || "Trier par"}
            </span>
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="start" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Label class="px-2 py-1.5 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Critères
        </DropdownMenu.Label>
        <DropdownMenu.Separator class="my-1 bg-slate-50" />
          <DropdownMenu.RadioGroup value={attendanceStore.sortBy} onValueChange={(v) => attendanceStore.setSort(v)}>
            <DropdownMenu.RadioItem value="name" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Nom (A-Z)
            </DropdownMenu.RadioItem>
            
            <DropdownMenu.RadioItem value="department" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Département
            </DropdownMenu.RadioItem>

            <DropdownMenu.RadioItem value="policy" class="py-2 pr-3 pl-7 rounded-lg cursor-pointer text-[0.84rem]!">
              Modèle
            </DropdownMenu.RadioItem>
          </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <div class="w-8 h-7.5 shrink-0 flex items-center justify-center border-l border-slate-100 bg-slate-50/30">
      <TooltipWrapper content={attendanceStore.sortOrder === 'asc' ? 'Ordre croissant' : 'Ordre décroissant'}>
        {#snippet children(props)}
          <button 
            {...props}
            onclick={() => attendanceStore.toggleSortOrder()}
            class="w-full h-full flex items-center justify-center hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <div class={cn("transition-transform duration-300 flex items-center justify-center", attendanceStore.sortOrder === 'desc' ? "rotate-180" : "rotate-0")}>
              <AppIcon name="arrow-up" size={15} class={attendanceStore.sortOrder === 'desc' ? "text-blue-600" : "text-slate-400"} />
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
        <AppIcon name="filter" size={16} class={attendanceStore.activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
        <span class="text-[0.84rem] text-slate-700">Filtrer</span>
        {#if attendanceStore.activeFiltersCount > 0}
          <div transition:scale={{ duration: 200, start: 0.8 }}>
            <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
              {attendanceStore.activeFiltersCount}
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
          {@render FilterSection("Département", ["Ingénierie", "Produit", "Vente", "RH"], "department")}
        </div>

        {#if attendanceStore.activeFiltersCount > 0}
          <div class="p-2 bg-slate-50/50 border-t border-slate-100">
            <Button variant="ghost" onclick={() => attendanceStore.resetFilters()} class="w-full h-8 text-[0.84rem] bg-white text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
              Réinitialiser tout
            </Button>
          </div>
        {/if}
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <Button
      onclick={openBulkAssignmentSheet}
      size="sm"
      variant="default"
      class="bg-blue-600 hover:bg-blue-700 h-7.5 px-3 text-[0.84rem] text-white rounded-lg shadow-fine"
    >
      <AppIcon name="plus" size={17} />
      Affecter
    </Button>
  </div>
{/snippet}


{#snippet FilterSection(label: string, options: string[], filterKey: 'status' | 'department' | 'policy')}
  <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
    {label}
  </DropdownMenu.Label>
  {#each options as option}
    <DropdownMenu.CheckboxItem 
      checked={(attendanceStore.filters[filterKey] as any[]).includes(option)}
      onCheckedChange={() => attendanceStore.toggleFilter(filterKey, option)}
      class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
    >
      {option}
    </DropdownMenu.CheckboxItem>
  {/each}
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

