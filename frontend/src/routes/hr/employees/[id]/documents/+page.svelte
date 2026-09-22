<script lang="ts">
  import EmployeeDocuments from '@/hr/employees/components/mgmt/profile/documents/EmployeeDocuments.svelte';
  import { employeeStore } from '@/hr/employees/stores/employees.svelte';
  import { fade } from 'svelte/transition';

  // Get the full employee profile from the store (loaded in layout)
  const employee = $derived(employeeStore.current);
</script>


{#if employee}
  <div class="h-full overflow-y-auto custom-scrollbar px-1" transition:fade>
    <EmployeeDocuments {employee} />
  </div>
{/if}




