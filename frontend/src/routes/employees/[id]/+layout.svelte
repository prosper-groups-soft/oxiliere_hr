<script lang="ts">
  import { page } from '$app/state';
  import { Button } from '@/components/ui/button';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { ui } from "@/stores/ui.svelte";
  import { get_api_base_origin } from '@/utilities/http/urls';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import EmployeeProfileHeader from '@/features/employees/components/mgmt/profile/header/EmployeeProfileHeader.svelte';

  
  let { children } = $props();

  // Dérivations réactives pour suivre l'URL et le store
  const employeeId = $derived(page.params.id);
  const employee = $derived(employeeStore.current);

  /**
   * RÉACTIVITÉ DU CHARGEMENT
   * Cet effet se déclenche à chaque fois que 'employeeId' change.
   */
  $effect(() => {
    if (employeeId) {
      // On vide le profil actuel pour déclencher l'affichage du loader
      // si on passe d'un employé A à un employé B.
      employeeStore.setCurrent(null);
      employeeStore.getFullProfileById(employeeId);
    }
  });

  /**
   * ACTIONS GLOBALES (UI)
   */
  $effect(() => {
    ui.addActions('profile-global', ExportAction);
    return () => ui.removeActions('profile-global');
  });
</script>


{#snippet ExportAction()}
  <Button 
    variant="outline" 
    size="sm" 
    class="h-7.5 gap-2 px-3 hover:bg-slate-200 transition-colors border-0" 
    onclick={() => window.open(`${get_api_base_origin()}/api/employees/${employee?.id}/export/`, '_blank')}
  >
    <AppIcon name="download" size={18} class="text-slate-400" />
    <span class="hidden sm:inline text-[0.84rem] text-slate-600">Exporter</span>
  </Button>
{/snippet}


{#if employee}
  <div class="flex flex-col h-full">
    <EmployeeProfileHeader {employee} />
    
    <main class="flex-1 overflow-auto">
      {@render children()}
    </main>
  </div>
{:else}
  <div class="h-full flex items-center justify-center">
    <AnimateSpin text="Chargement du profil" />
  </div>
{/if}


<style>
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

