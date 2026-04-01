<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { onboardingStore } from "@/features/employees/stores/onboarding.svelte";
  import OnboardingTabs from "@/features/employees/components/onboarding/nav/OnboardingTabs.svelte";
  import IdentityStep from "@/features/employees/components/onboarding/steps/IdentityStep.svelte";
  import AccountStep from "@/features/employees/components/onboarding/steps/AccountStep.svelte";
  import ContractStep from "@/features/employees/components/onboarding/steps/ContractStep.svelte";
  import DocumentsStep from "@/features/employees/components/onboarding/steps/DocumentsStep.svelte";
  import FamilyStep from "@/features/employees/components/onboarding/steps/FamilyStep.svelte";
  import { fade, fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { ui } from "@/stores/ui.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { onMount, untrack } from "svelte";
  import axios from "axios";

  let initialDataStr = $state("");
  let isInitialized = $state(false);
  let isSubmitting = $state(false);

  /**
   * GLOBAL ACTION REGISTRATION
   */
  $effect(() => {
    ui.addActions('onboarding-validate', ButtonValidateAction);
    return () => ui.removeActions('onboarding-validate');
  });

  /**
   * AUTO-SAVE TRIGGER & SMART IGNORE
   */
  $effect(() => {
    const currentDataStr = JSON.stringify(onboardingStore.data);
    const { isAutoSaveEnabled, isRestoring } = onboardingStore;
    
    untrack(() => {
      if (isRestoring || !isInitialized) return;

      if (isAutoSaveEnabled) {
        onboardingStore.triggerAutoSave();
      }
    });
  });

  onMount(() => {
    onboardingStore.reset();
    initialDataStr = JSON.stringify(onboardingStore.data);
    
    if (onboardingStore.hasDraft) {
      onboardingStore.loadDraft();
      notification.toast.success("Brouillon restauré automatiquement.");
    } else {
      onboardingStore.isAutoSaveEnabled = true;
    }
    isInitialized = true;
  });

  async function handleValidate() {
    if (onboardingStore.compliance.length > 0) {
      notification.toast.error("Veuillez corriger les erreurs avant de valider.");
      return;
    }

    isSubmitting = true;
    try {
      const data = onboardingStore.data;
      const payload = {
        ...data.identity,
        ...data.contract,
        create_account: data.account.createAccount,
        group_slug: data.account.groupSlug,
        // Flattening structure as expected by EmployeeCreate schema
        // Note: Backend schema uses snake_case
        first_name: data.identity.name.split(' ')[0],
        last_name: data.identity.name.split(' ').slice(1).join(' '),
        email: data.identity.email,
        phone: data.identity.phone,
        birth_date: data.identity.birthDate,
        job_title: data.contract.jobTitle,
        department_id: data.contract.departmentId,
        start_date: data.contract.startDate,
        contract_type: data.contract.contractType,
        base_salary: data.contract.salary
      };

      await axios.post('/api/employees/', payload);

      notification.toast.success("Dossier validé et employé créé avec succès !");
      onboardingStore.clearDraft();
    } catch (e: any) {
      notification.toast.error(e.response?.data?.detail || "Erreur lors de la création de l'employé");
    } finally {
      isSubmitting = false;
    }
  }
</script>


{#snippet ButtonValidateAction()}
  <Button 
    onclick={handleValidate}
    disabled={onboardingStore.compliance.length > 0 || isSubmitting} 
    class="bg-blue-600! hover:bg-blue-700 h-7 px-6 text-[0.8rem] font-medium shadow-soft transition-all"
  >
    {#if isSubmitting}
      <div class="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
      Traitement...
    {:else}
      <AppIcon name="check" size={16} />
      Valider le dossier
    {/if}
  </Button>
{/snippet}


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
            disabled={onboardingStore.compliance.length > 0}
            class="h-7.5 px-8 rounded-md font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-none text-sm transition-all"
          >
            <AppIcon name="check" size={16} class="mr-2" />
            Terminer le dossier
          </Button>
        {/if}
      </div>
    </div>
  </div>
{/snippet}

