<script lang="ts">
  import { createDashboard } from '@/hr/dashboard/core/dashboard';
  import { headcount, leavesPending, recruitmentOpen, payrollMass, myLeaves, myPayslip } from '@/hr/dashboard/widgets/widgets';
  import DashboardView from '@/hr/dashboard/components/DashboardView.svelte';
  import { auth } from '@/hr/auth/stores/auth.svelte';

  // Rôle depuis l'auth (admin | hr | employee) — fallback hr pour la démo
  const role = $derived((auth.user?.role as any) ?? 'hr');

  const dashboard = $derived(createDashboard({
    role,
    widgets: [headcount(), leavesPending(), recruitmentOpen(), payrollMass(), myLeaves(), myPayslip()],
    layout: { type: 'grid', columns: 4 },
    refresh: { policy: 'poll', interval: 5 * 60 * 1000 }
  }));
</script>

<DashboardView {dashboard} />
