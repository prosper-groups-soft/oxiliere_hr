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


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #f1f5f9;
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #e2e8f0;
  }
</style>
