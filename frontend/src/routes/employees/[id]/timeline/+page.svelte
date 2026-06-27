<script lang="ts">
  import { fade } from "svelte/transition";
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { timelineEventStore } from '@/features/employees/stores/timelinevent.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import EmployeeTimeline from '@/features/employees/components/mgmt/profile/timeline/EmployeeTimeline.svelte';

  // Get the full employee profile from the store (loaded in layout)
  const employee = $derived(employeeStore.current);

  // Fetch timeline data when employee is available
  $effect(() => {
    if (employee?.id) {
      timelineEventStore.fetchTimeline(employee.id);
    }
  });
</script>


{#if employee}
  {#if timelineEventStore.isLoading}
    <div class="h-full flex items-center justify-center" transition:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement du timeline" />
    </div>
  {:else}
    <EmployeeTimeline events={timelineEventStore.events} />
  {/if}
{/if}
