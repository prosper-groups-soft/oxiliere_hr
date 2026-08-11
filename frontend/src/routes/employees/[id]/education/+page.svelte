<script lang="ts">
  import EmployeeEducation from '@/features/employees/components/mgmt/profile/education/EmployeeEducation.svelte';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { fade } from 'svelte/transition';

  // Get the full employee profile from the store (loaded in layout)
  const employee = $derived(employeeStore.current);
</script>


{#if employee}
  <div class="h-full overflow-y-auto custom-scrollbar px-1" transition:fade>
    <EmployeeEducation {employee} />
  </div>
{/if}



