<script lang="ts">
  import { page } from '$app/state';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { timelineEventStore } from '@/features/employees/stores/timelinevent.svelte';
  
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import EmployeeGeneralInfo from '@/features/employees/components/mngt/details/info/EmployeeGeneralInfo.svelte';
  import EmployeeTimeline from '@/features/employees/components/mngt/details/info/EmployeeTimeline.svelte';

  // Get the employee ID from the URL params
  const employeeId = $derived(page.params.id);
	
  // Get the employee from the store
  const employee = $derived(employeeId ? employeeStore.getById(employeeId) : null);
</script>


{#if employee}
  <div class="grid grid-cols-1 lg:grid-cols-8 gap-2 animate-in fade-in duration-500">
    <!-- Main Content Area -->
    <div class="lg:col-span-4 space-y-6 h-100">
      <EmployeeGeneralInfo {employee} />
    </div>

    <!-- Sidebar / Timeline Area -->
    <div class="lg:col-span-4 space-y-6">
      <EmployeeTimeline events={timelineEventStore.getTimelineEvents()} />
    </div>
  </div>
{:else}
  <div class="h-full flex items-center justify-center">
    <AnimateSpin text="Chargement du profil..." />
  </div>
{/if}

