<script lang="ts">
  import { fade } from "svelte/transition";
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import EmployeeContract from '@/features/employees/components/mgmt/profile/contract/EmployeeContract.svelte';

  
  // Get the full employee profile from the store (loaded in layout)
  const employee = $derived(employeeStore.current);
</script>


{#if employee}
  <div class="animate-in fade-in duration-500" transition:fade={{ duration: 200 }}>
    <EmployeeContract {employee} />
  </div>
{/if}
