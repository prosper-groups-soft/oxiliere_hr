<script lang="ts">
  import { fade } from "svelte/transition";
  import { employeeStore } from '@/hr/employees/stores/employees.svelte';
  import EmployeeProfile from '@/hr/employees/components/mgmt/profile/info/EmployeeProfile.svelte';

  
  // Get the full employee profile from the store (loaded in layout)
  const employee = $derived(employeeStore.current);
</script>


{#if employee}
  <div class="animate-in fade-in duration-500" transition:fade={{ duration: 200 }}>
    <EmployeeProfile {employee} />
  </div>
{/if}

