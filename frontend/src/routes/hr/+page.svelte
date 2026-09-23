<script lang="ts">
  import { createDashboard } from '@/hr/dashboard/core/dashboard';
  import { headcount, leavesPending, recruitmentOpen, payrollMass, myLeaves, myPayslip, leavesChart, recruitmentChart, headcountChart, payrollChart, pendingLeavesList, recentCandidatesList, myLeavesList } from '@/hr/dashboard/widgets/widgets';
  import DashboardView from '@/hr/dashboard/components/DashboardView.svelte';
  import { auth } from '@/hr/auth/stores/auth.svelte';
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";

  const role = $derived((auth.user?.role as any) ?? 'hr');
  const periodState = createFilterState<{ period: string[] }>({ period: ['month'] });

  const dashboard = $derived(createDashboard({
    role,
    widgets: [headcount(), leavesPending(), recruitmentOpen(), payrollMass(), myLeaves(), myPayslip(), leavesChart(), recruitmentChart(), headcountChart(), payrollChart(), pendingLeavesList(), recentCandidatesList(), myLeavesList()],
    layout: { type: 'grid', columns: 4 },
    refresh: { policy: 'poll', interval: 5 * 60 * 1000 }
  }));
</script>

<DashboardView {dashboard} periodFilterState={periodState} />
