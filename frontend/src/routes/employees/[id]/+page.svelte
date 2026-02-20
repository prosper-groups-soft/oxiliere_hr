<script lang="ts">
	import { page } from '$app/state';
	import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import EmployeeGeneralInfo from '@/features/employees/components/details/info/EmployeeGeneralInfo.svelte';
  import EmployeeTimeline from '@/features/employees/components/details/info/EmployeeTimeline.svelte';
	import { timelineEventStore } from '@/features/employees/stores/timelinevent.svelte';

  // Get the employee ID from the URL params
  const employeeId  = $derived(page.params.id);
	
	// Get the employee from the store
  const employee = $derived(employeeId ? employeeStore.getById(employeeId) : null);

</script>


{#if employee}
  <div class="grid grid-cols-1 lg:grid-cols-6 gap-6 animate-in fade-in duration-500">
    
    <div class="lg:col-span-4 space-y-6 h-100">
        <EmployeeGeneralInfo
            employee={employee}
        />
    </div>

    <div class="lg:col-span-2 space-y-6">
        <EmployeeTimeline
            events={timelineEventStore.getTimelineEvents()}
        />
    </div>
</div>

{:else}
  <div class="h-full flex items-center justify-center">
    <AnimateSpin text="Chargement du profil..." />
  </div>
{/if}

