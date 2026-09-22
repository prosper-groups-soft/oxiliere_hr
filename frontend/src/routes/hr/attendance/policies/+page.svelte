<script lang="ts">
  import PolicyManager from "@/hr/attendance/components/config/PolicyManager.svelte";
  import PoliciesActions from "@/hr/attendance/components/config/actions/PoliciesActions.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { attendanceStore } from "@/hr/attendance/stores/attendance.svelte";
  import { usePoliciesQuery } from "@/hr/attendance/queries/attendanceQueries";
  import { backendToWorkPolicy } from "@/hr/attendance/constants/attendance.helpers";
  import type { ShiftPolicyOut } from "@/hr/attendance/api/attendance.endpoints";


  // TanStack Query avec recherche et tri déportés dans le store
  const policiesQuery = usePoliciesQuery(
    () => attendanceStore.policySearch,
    () => {
      const order = attendanceStore.policySortOrder === 'desc' ? '-' : '';
      return `${order}${attendanceStore.policySortBy}`;
    }
  );

  // Synchroniser le store avec les données de la query
  $effect(() => {
    const data = $policiesQuery.data as ShiftPolicyOut[] | undefined;
    if (data) {
      attendanceStore.policies = data.map(backendToWorkPolicy);
    }
    attendanceStore.policiesLoading = $policiesQuery.isLoading as boolean;
    attendanceStore.policiesError = $policiesQuery.isError
      ? ($policiesQuery.error as Error)?.message || 'Erreur de chargement'
      : null;
  });

  // Re-fetch quand les filtres changent
  $effect(() => {
    attendanceStore.policySearch;
    attendanceStore.policySortBy;
    attendanceStore.policySortOrder;

    $policiesQuery.refetch();
  });


  // Enregistrer les actions dans l'en-tête via le store ui
  $effect(() => {
    ui.addActions('policies-actions', AttendancePoliciesActions);
    return () => ui.removeActions('policies-actions');
  });
</script>


{#snippet AttendancePoliciesActions()}
  <PoliciesActions />
{/snippet}


<div class="h-full">
  <PolicyManager />
</div>

