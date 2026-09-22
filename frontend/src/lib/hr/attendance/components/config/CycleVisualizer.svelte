<script lang="ts">
  import { attendanceStore } from "../../stores/attendance.svelte";
  import { get } from 'svelte/store';
  import { useAssignmentsQuery, getAssignmentTotalCount, useDeleteAssignmentMutation } from "../../queries/attendanceQueries";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { Button } from "@/components/ui/button";
  import type { WorkPolicy, PolicyAssignment } from "../../types/types";
  import { RECURRENCE_LABELS } from "../../constants/attendance.constants";
  import type { Employee } from "@/hr/employees/types/types";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import AssignmentSheet from "./sheets/shift/AssignmentSheet.svelte";
  import BulkAssignmentSheet from "./sheets/shift/BulkAssignmentSheet.svelte";
  import PolicyComparisonSheet from "./sheets/shift/PolicyComparisonSheet.svelte";
  import EmployeeCard from "./views/EmployeeCard.svelte";
  import { fade, fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";


  interface EmployeeWithAssignment extends Employee {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
    basePolicy?: WorkPolicy;
    overridePolicy?: WorkPolicy;
  }


  // Pagination state
  let page = $state(1);
  let perPage = $state(10);

  // TanStack Queries — read all filters/sort from the attendanceStore
  const assignmentsQuery = useAssignmentsQuery(
    () => page,
    () => perPage,
    () => attendanceStore.filters.search,
    () => attendanceStore.filters.orgUnit.join(','),
    () => attendanceStore.filters.recurrence.join(','),
    () => attendanceStore.sortBy,
    () => attendanceStore.sortOrder,
  );

  // Delete mutation
  const deleteAssignmentMutation = useDeleteAssignmentMutation();

  const assignmentTotalCount = $derived(getAssignmentTotalCount($assignmentsQuery.data));
  const totalPages = $derived(Math.ceil(assignmentTotalCount / perPage) || 1);

  const isLoading = $derived($assignmentsQuery.isLoading);
  const isError = $derived($assignmentsQuery.isError);

  let selectedEmployee = $state<EmployeeWithAssignment | null>(null);
  let showAssignmentSheet = $state(false);
  let showBulkAssignmentSheet = $state(false);
  let showComparisonSheet = $state(false);
  let deletingId = $state<string | null>(null);

  // Listen for the custom event dispatched by sheets after a successful save
  $effect(() => {
    function handleAssignmentsChanged() {
      get(assignmentsQuery).refetch();
    }
    document.addEventListener('assignments-changed', handleAssignmentsChanged);
    return () => document.removeEventListener('assignments-changed', handleAssignmentsChanged);
  });

  // Re-fetch quand les filtres, la recherche, le tri ou la pagination changent
  $effect(() => {
    attendanceStore.filters.search;
    attendanceStore.filters.orgUnit;
    attendanceStore.filters.recurrence;
    attendanceStore.sortBy;
    attendanceStore.sortOrder;
    page;
    perPage;
    get(assignmentsQuery).refetch();
  });

  // Build cards directly from the API response, deduplicated by employee_id
  const assignmentCards = $derived.by(() => {
    const schemes = $assignmentsQuery.data?.results ?? [];
    const map = new Map<string, EmployeeWithAssignment>();
    for (const scheme of schemes) {
      const emp = {
        id: scheme.employee_id,
        name: scheme.employee_name,
        first_name: scheme.first_name,
        last_name: scheme.last_name,
        middle_name: scheme.middle_name,
        profile_photo: scheme.profile_photo,
        jobTitle: scheme.job_title ?? '',
        orgUnit: scheme.org_unit_name ?? '',
        orgUnitId: scheme.org_unit_id ?? undefined,
        status: '',
        location: '',
        contractType: '',
        joinDate: '',
        phone: '',
        email: '',
        avatarUrl: scheme.profile_photo ?? '',
        role: '',
        current_status: scheme.current_status ? { status: scheme.current_status } as any : undefined,
        baseAssignment: {
          id: scheme.id,
          employeeId: scheme.employee_id,
          policyId: scheme.policy_id,
          startDate: scheme.valid_from,
          endDate: scheme.valid_until ?? undefined,
          recurrence: scheme.recurrence,
        } as PolicyAssignment,
        basePolicy: { id: scheme.policy_id, name: scheme.policy_name } as WorkPolicy,
        overrideAssignment: scheme.override_policy_id ? {
          id: scheme.id,
          employeeId: scheme.employee_id,
          policyId: scheme.override_policy_id,
          startDate: scheme.override_valid_from ?? scheme.valid_from,
          endDate: scheme.override_valid_until ?? undefined,
          recurrence: scheme.override_recurrence,
          recurrenceCount: scheme.override_recurrence_count,
        } as PolicyAssignment : undefined,
        overridePolicy: scheme.override_policy_name
          ? { id: scheme.override_policy_id!, name: scheme.override_policy_name } as WorkPolicy
          : undefined,
      } as EmployeeWithAssignment;
      // Keep the latest scheme for each employee (dedup by employee id)
      map.set(scheme.employee_id, emp);
    }
    return Array.from(map.values());
  });

  // Client-side sort only — filtering is done server-side via query params
  const sortedEmployees = $derived.by(() => {
    const result = [...assignmentCards];
    const sortBy = attendanceStore.sortBy;
    const sortOrder = attendanceStore.sortOrder;

    result.sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'name') {
        comparison = a.name.localeCompare(b.name);
      } else if (sortBy === 'orgUnit') {
        comparison = (a.orgUnit || '').localeCompare(b.orgUnit || '');
      } else if (sortBy === 'policy') {
        comparison = (a.basePolicy?.name || '').localeCompare(b.basePolicy?.name || '');
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    
    return result;
  });

  // Labels personnalisés pour les filtres
  function getDisplayLabel(key: string, value: string): string {
    switch (key) {
      case 'orgUnit':
        const card = assignmentCards.find(c => c.orgUnitId === value);
        return card ? `Unité: ${card.orgUnit}` : `Unité: ${value}`;
      case 'recurrence':
        return RECURRENCE_LABELS[value] ?? value;
      default:
        return value;
    }
  }

  // If no results on current page, go back to page 1
  $effect(() => {
    if (sortedEmployees.length === 0 && page > 1) {
    page = 1;
    }
  });

  function handlePageChange(newPage: number) {
    page = newPage;
  }

  function handlePrevPage() {
    if (page > 1) page--;
  }

  function handleNextPage() {
    if (page < totalPages) page++;
  }

  function handlePerPageChange(newSize: number) {
    perPage = newSize;
    page = 1;
  }

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

  function openComparisonSheet(employee: EmployeeWithAssignment) {
    selectedEmployee = employee;
    showComparisonSheet = true;
  }

  async function removeAssignment(employee: EmployeeWithAssignment) {
    if (deletingId) return;
    const assignment = employee.baseAssignment || employee.overrideAssignment;
    if (!assignment) return;

    notification.confirm({
      title: "Suppression de l'affectation",
      message: `Êtes-vous sûr de vouloir supprimer l'affectation du modèle pour ${employee.name} ?`,
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: async () => {
        deletingId = assignment.id;
        try {
          await $deleteAssignmentMutation.mutateAsync(assignment.id);
          notification.toast.success('Affectation supprimée avec succès');
        } catch (err) {
          notification.toast.error('Erreur lors de la suppression de l\'affectation');
        } finally {
          deletingId = null;
        }
      }
    });
  }
</script>


<div class="flex h-full flex-col bg-white overflow-hidden min-h-0">
  {@render Header()}

  <div class="relative flex flex-1 flex-col overflow-hidden min-h-0">

      {#if isLoading}
        <div transition:fade={{ duration: 200 }} class="absolute inset-0 flex items-center justify-center">
          <AnimateSpin text="Chargement des affectations" />
        </div>

      {:else if isError}
        <div transition:fade={{ duration: 200 }} class="absolute inset-0 flex items-center justify-center p-8">
          <Empty
            title="Erreur de chargement"
            description={getFriendlyErrorMessage($assignmentsQuery.error)}
            icon="alert-circle"
            iconClass="text-red-400"
            iconSize={28}
            iconStrokeWidth={1.3}
            iconContainerClass="bg-red-50/30"
          >
            <Button onclick={() => {
              $assignmentsQuery.refetch();
            }} variant="outline" class="h-7 rounded-lg">
              <AppIcon name="refresh-cw" />
              Réessayer
            </Button>
          </Empty>
        </div>

      {:else if assignmentCards.length === 0 && !attendanceStore.filters.search && attendanceStore.filters.orgUnit.length === 0 && attendanceStore.filters.recurrence.length === 0}
        <div transition:fade={{ duration: 200 }} class="absolute inset-0 flex items-center justify-center">
          <Empty 
            title="Aucune affectation trouvée"
            description="Aucun employé n'a encore de modèle de travail assigné. Commencez par affecter un modèle."
            icon="calendar-days"
            iconSize={28}
            iconStrokeWidth={1.3}
            iconClass="text-slate-400"
          >
            <EmptyButton 
              labelElement="une affectation"
              onNew={() => showBulkAssignmentSheet = true}
            />
          </Empty>
        </div>

      {:else}
        <FilterChips 
          filters={{
            search: attendanceStore.filters.search ? [attendanceStore.filters.search] : [],
            orgUnit: attendanceStore.filters.orgUnit,
            recurrence: attendanceStore.filters.recurrence,
          }}
          activeFiltersCount={attendanceStore.activeFiltersCount + (attendanceStore.filters.search ? 1 : 0)}
          getDisplayLabel={(key, value) => key === 'search' ? `Recherche : ${value}` : getDisplayLabel(key, value)}
          onRemove={(key, value) => {
            if (key === 'search') { attendanceStore.filters.search = ''; }
            else { attendanceStore.toggleFilter(key as any, value); }
          }}
          onReset={() => { attendanceStore.resetFilters(); }}
          class="px-6 py-1 pt-0! border-b border-slate-50 shrink-0"
          badgeClass="bg-amber-50 text-amber-600 border-amber-100/50"
        />

        {#if sortedEmployees.length === 0}
          <div class="flex-1 flex items-center justify-center">
            <Empty 
              title="Aucun résultat trouvé" 
              description="Aucun employé avec un planning ne correspond à votre recherche."
              icon="search-x"
              iconSize={28}
              iconStrokeWidth={1.3}
              iconClass="text-slate-400"
            >
              <Button variant="ghost" onclick={() => attendanceStore.resetFilters()} class="h-7 bg-slate-50">
                <AppIcon name="x" size={16} class="text-slate-400" />
                Réinitialiser la recherche
              </Button>
            </Empty>
          </div>
        {:else}
          <div class="custom-scrollbar flex-1 overflow-auto p-6" style="--scrollbar-size: 6px">
            <div 
              class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
              in:fly={{ y: 20, duration: 400, delay: 100 }}
            >
              {#each sortedEmployees as employee (employee.id)}
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
          </div>

          {#if assignmentTotalCount > 0}
          <div class="px-6 py-0.5 border-t border-slate-100 bg-white sticky bottom-0 z-10">
            <DataPagination
              currentCount={sortedEmployees.length}
              totalCount={assignmentTotalCount}
              currentPage={page}
              {totalPages}
              perPage={perPage}
              onPageChange={handlePageChange}
              onPerPageChange={handlePerPageChange}
              onNext={handleNextPage}
              onPrev={handlePrevPage}
              unitLabel="employés"
            />
          </div>
          {/if}
        {/if}
      {/if}
  </div>
</div>


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
      
      <!-- Add Assignment Button -->
      <Button
        onclick={() => showBulkAssignmentSheet = true}
        variant="default"
        size="sm"
        class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
      >
        <AppIcon name="plus" size={15} />
        Affecter
      </Button>
    </div>
  </div>
{/snippet}


<!-- Sheets of affection -->
<AssignmentSheet bind:open={showAssignmentSheet} employee={selectedEmployee} />
<BulkAssignmentSheet bind:open={showBulkAssignmentSheet} />
<PolicyComparisonSheet bind:open={showComparisonSheet} employee={selectedEmployee} />

