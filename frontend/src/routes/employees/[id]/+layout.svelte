<script lang="ts">
  import { page } from '$app/state';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import EmployeeDetailsHeader from '@/features/employees/components/details/header/EmployeeDetailsHeader.svelte';

  let { children } = $props();

  // Get reactive employee
  const employeeId = $derived(page.params.id);
  const employee = $derived(employeeId ? employeeStore.getById(employeeId) : null);
</script>


{#if employee}
  <div class="space-y-3">

    <EmployeeDetailsHeader {employee} />
    
    <main class="min-h-100">
      {@render children()}
    </main>

  </div>
{:else}
  <div class="h-full flex items-center justify-center">
    <AnimateSpin text="Chargement du profil..." />
  </div>
{/if}


<style>

  /* Animation of content when changing tabs */
  main {
    animation: slideUp 0.3s ease-out;
  }

  @keyframes slideUp {
    from { 
      opacity: 0; 
      transform: translateY(8px); 
    }
    to { 
      opacity: 1; 
      transform: translateY(0); 
    }
  }
</style>

