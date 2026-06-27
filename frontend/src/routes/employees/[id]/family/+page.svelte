<script lang="ts">
  import { fade } from "svelte/transition";
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import EmployeeEmergencyContacts from '@/features/employees/components/mgmt/profile/family/contacts/EmployeeEmergencyContacts.svelte';
  import EmployeeChildren from '@/features/employees/components/mgmt/profile/family/children/EmployeeChildren.svelte';

  // Get the full employee profile from the store (loaded in layout)
  const employee = $derived(employeeStore.current);
</script>


{#if employee}
  <div class="grid grid-cols-1 md:grid-cols-2 items-stretch h-110 mt-2.5 px-3" transition:fade={{ duration: 200 }}>
    <EmployeeEmergencyContacts {employee} />
    <EmployeeChildren {employee} />
  </div>
{/if}

