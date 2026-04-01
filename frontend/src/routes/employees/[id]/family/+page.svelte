<script lang="ts">
  import { page } from '$app/state';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import EmployeeEmergencyContacts from '@/features/employees/components/mngt/details/family/contacts/EmployeeEmergencyContacts.svelte';
  import EmployeeChildren from '@/features/employees/components/mngt/details/family/children/EmployeeChildren.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';

  const employeeId = $derived(page.params.id);
  const employee = $derived(employeeId ? employeeStore.getById(employeeId) : undefined);
</script>


{#if employee}
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch h-110 mt-2.5 px-3">
    <EmployeeEmergencyContacts {employee} />
    <EmployeeChildren {employee} />
  </div>
{:else}
  <div class="h-40 flex items-center justify-center">
    <AnimateSpin text="Chargement des données familiales..." />
  </div>
{/if}

