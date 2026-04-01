<script lang="ts">
  import { page } from '$app/state';
  import { Button } from '@/components/ui/button';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { ui } from "@/stores/ui.svelte";
  
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import EmployeeDetailsHeader from '@/features/employees/components/mngt/details/header/EmployeeDetailsHeader.svelte';

  let { children } = $props();

  // Get reactive employee
  const employeeId = $derived(page.params.id);
  const employee = $derived(employeeId ? employeeStore.getById(employeeId) : null);

  /**
   * GLOBAL ACTION REGISTRATION
   * We use 'profile-global' to persist this action across all sub-tabs.
   */
  $effect(() => {
    ui.addActions('profile-global', exportAction);
    
    return () => ui.removeActions('profile-global');
  });
</script>


{#snippet exportAction()}
  <Button 
    variant="outline" 
    size="sm" 
    class="h-6 gap-2 px-3 bg-slate-100 hover:bg-slate-200 transition-colors border-0" 
    onclick={() => console.log('Exporting Profile for:', employee?.name)}
  >
    <AppIcon name="download" size={18} />
    <span class="hidden sm:inline text-sm font-medium text-slate-600">Exporter</span>
  </Button>
{/snippet}


{#if employee}
  <div class="space-y-2">

    <EmployeeDetailsHeader {employee} />
    
    <main class="h-full">
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

