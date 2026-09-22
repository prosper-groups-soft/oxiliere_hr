<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { onboardingStore } from "@/hr/employees/stores/onboarding.svelte";
  import OnboardingTabs from "@/hr/employees/components/onboarding/nav/OnboardingTabs.svelte";
  import ArchiveModal from "@/hr/employees/components/onboarding/modals/ArchiveModal.svelte";
  import IdentityStep from "@/hr/employees/components/onboarding/steps/IdentityStep.svelte";
  import AccountStep from "@/hr/employees/components/onboarding/steps/AccountStep.svelte";
  import ContractStep from "@/hr/employees/components/onboarding/steps/ContractStep.svelte";
  import DocumentsStep from "@/hr/employees/components/onboarding/steps/DocumentsStep.svelte";
  import FamilyStep from "@/hr/employees/components/onboarding/steps/FamilyStep.svelte";
  import EducationStep from "@/hr/employees/components/onboarding/steps/EducationStep.svelte";
  import { fade, fly, slide } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { ui } from "@/stores/ui.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { onMount } from "svelte";
  import { onboardingService } from "@/hr/employees/services/onboarding.service";
  import { useQueryClient } from "@tanstack/svelte-query";

  let initialDataStr = $state("");
  let isInitialized = $state(false);
  let isSubmitting = $state(false);
  let showArchiveModal = $state(false);
  const queryClient = useQueryClient();

  /**
   * GLOBAL ACTION REGISTRATION
   */
  $effect(() => {
    ui.addActions('onboarding-validate', ButtonValidateAction);
    return () => ui.removeActions('onboarding-validate');
  });

  
  onMount(() => {
    // Vérifier s'il y a un brouillon à restaurer avant de réinitialiser
    const hasDraft = onboardingStore.hasDraft;
    if (!hasDraft) {
      onboardingStore.reset();
    }
    initialDataStr = JSON.stringify(onboardingStore.data);
    onboardingStore.isAutoSaveEnabled = true;
    isInitialized = true;
  });

  function openArchiveModal() {
    showArchiveModal = true;
  }

  async function handleValidate() {
    if (onboardingStore.compliance.length > 0) {
      notification.toast.error("Veuillez corriger les erreurs avant de valider.");
      return;
    }

    const data = onboardingStore.data;
    
    isSubmitting = true;
    try {
      const submitData: any = {
        identity: {
          ...data.identity,
          gender: data.identity.gender || undefined,
          marital_status: data.identity.marital_status || undefined,
          work_site: data.identity.work_site || undefined
        },
        contract: data.contract,
        documents: data.documents || [],
        family: {
          emergency_contacts: data.family.emergencyContacts,
          children: data.family.children
        },
        education: {
          educations: data.education.educations
        }
      };

      // N'inclure le compte que si create_account est true
      if (data.account?.create_account) {
        submitData.account = data.account;
      }

      const result = await onboardingService.submitFullOnboarding(submitData, queryClient);

      // Si succès : supprimer le brouillon (plus besoin)
      // Si échec : garder le brouillon pour continuer plus tard
      if (result.success) {
        onboardingStore.clearDraft(); // Supprime le brouillon actuel
      }
    } catch (e: any) {
      // Error handling is already done in the service
      console.error('Validation error:', e);
    } finally {
      isSubmitting = false;
    }
  }
</script>


{#snippet ButtonValidateAction()}
  <div class="flex items-center justify-center gap-1">
    <Button 
      variant="ghost" 
      onclick={openArchiveModal}
      class="h-7 px-4 text-[0.8rem] transition-all"
    >
      <AppIcon name="archive" size={16} class="text-slate-500" />
      Brouillons
    </Button>
    <div class="w-px h-5 bg-slate-200 mx-1"></div>
    <Button 
      onclick={handleValidate}
      disabled={onboardingStore.compliance.length > 0 || isSubmitting} 
      class="bg-indigo-600! hover:bg-indigo-700 h-7 px-6 text-[0.8rem] font-medium shadow-soft transition-all"
    >
      {#if isSubmitting}
        <AnimateSpin text="" class="size-3 border-white" />
      {:else}
        <AppIcon name="check" size={16} />
      {/if}
      Terminer l'onboarding
    </Button>
  </div>
  
{/snippet}


<!-- Modale d'archive des brouillons -->
<ArchiveModal 
  show={showArchiveModal} 
  onClose={() => showArchiveModal = false} 
/>


<div class="h-full flex flex-col bg-white overflow-hidden">
  <OnboardingTabs />

  <div class="flex-1 overflow-y-auto">
    <div class="grid grid-cols-1 lg:grid-cols-6 gap-12 items-start px-4">
      <main class="lg:col-start-2 lg:col-span-4 mt-3">
        {@render StepContent()}
      </main>
    </div>
  </div>

  {@render NavigationFooter()}
</div>


{#snippet StepContent()}
  <div class="grid grid-cols-1 items-start">
    {#if onboardingStore.currentStep === 'identity'}
      <div class="col-start-1 row-start-1" in:fly={{ y: 8, duration: 400, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }}>
        <IdentityStep />
      </div>
    {/if}
    {#if onboardingStore.currentStep === 'account'}
      <div class="col-start-1 row-start-1" in:fly={{ y: 8, duration: 400, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }}>
        <AccountStep />
      </div>
    {/if}
    {#if onboardingStore.currentStep === 'contract'}
      <div class="col-start-1 row-start-1" in:fly={{ y: 8, duration: 400, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }}>
        <ContractStep />
      </div>
    {/if}
    {#if onboardingStore.currentStep === 'documents'}
      <div class="col-start-1 row-start-1" in:fly={{ y: 8, duration: 400, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }}>
        <DocumentsStep />
      </div>
    {/if}
    {#if onboardingStore.currentStep === 'family'}
      <div class="col-start-1 row-start-1" in:fly={{ y: 8, duration: 400, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }}>
        <FamilyStep />
      </div>
    {/if}
    {#if onboardingStore.currentStep === 'education'}
      <div class="col-start-1 row-start-1" in:fly={{ y: 8, duration: 400, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }}>
        <EducationStep />
      </div>
    {/if}
  </div>
{/snippet}


{#snippet NavigationFooter()}
  <div class="bg-white/80 py-4 grid grid-cols-1 lg:grid-cols-6 gap-12 px-4 border-t border-slate-50">
    <div class="lg:col-start-2 lg:col-span-4 flex items-center justify-between">
      <div class="flex items-center gap-6">
        <Button 
          variant="outline" 
          onclick={() => onboardingStore.prevStep()}
          disabled={onboardingStore.currentStepIndex === 0}
          class="h-7.5 px-6 rounded-md border-slate-200 text-slate-700 shadow-soft hover:bg-slate-50 font-medium text-sm transition-all"
        >
          <AppIcon name="prev" size={16} class="mr-2" />
          Précédent
        </Button>
      </div>

      <div class="flex gap-3">
        {#if onboardingStore.currentStepIndex < onboardingStore.steps.length - 1}
          <Button 
            onclick={() => onboardingStore.nextStep()}
            class="h-7.5 px-8 text-white rounded-md bg-slate-900 hover:bg-slate-800 shadow-none font-medium text-sm transition-all"
          >
            Suivant
            <AppIcon name="next" size={16} class="ml-2" />
          </Button>
        {:else}
          <Button 
            onclick={handleValidate}
            disabled={onboardingStore.compliance.length > 0 || isSubmitting} 
            class="bg-indigo-600! hover:bg-indigo-700 h-7 px-6 text-[0.8rem] font-medium shadow-soft transition-all"
          >
            {#if isSubmitting}
              <AnimateSpin text="" class="size-3 border-white" />
            {:else}
              <AppIcon name="check" size={16} />
            {/if}
            Terminer l'onboarding
          </Button>
        {/if}
      </div>
    </div>
  </div>
{/snippet}

