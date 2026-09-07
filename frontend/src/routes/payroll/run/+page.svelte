<script lang="ts">
  import { goto } from "$app/navigation";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { notification } from "@/stores/notification.svelte";
  import PayrollStepper from "@/features/payroll/components/run/PayrollStepper.svelte";
  import PreparationStep from "@/features/payroll/components/run/steps/PreparationStep.svelte";
  import CalculationStep from "@/features/payroll/components/run/steps/CalculationStep.svelte";
  import ReviewStep from "@/features/payroll/components/run/steps/ReviewStep.svelte";
  import ApprovalStep from "@/features/payroll/components/run/steps/ApprovalStep.svelte";
  import PaymentStep from "@/features/payroll/components/run/steps/PaymentStep.svelte";
  import { fade } from "svelte/transition";
  import StepHeader from "@/features/payroll/components/run/shared/StepHeader.svelte";
  import { ui } from "@/stores/ui.svelte";
  import KickoffStep from "@/features/payroll/components/run/steps/KickoffStep.svelte";


  const hasCurrentRun = $derived(payrollStore.hasActiveRun);
  const hasCurrentRunTab = $derived(payrollStore.hasCurrentRunTab);
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  const isKickoff = $derived(payrollStore.currentStep === 'kickoff');

  let isCreating = $state(false);
  let isCalculating = $state(false);
  let isReviewing = $state(false);
  let isApproving = $state(false);
  let isPaying = $state(false);

  let kickoffSubmit = $state<(() => void) | undefined>(undefined);
  let canSubmitKickoff = $state(false);

  function formatAmount(amount: number): string {
    return (amount ?? 0).toLocaleString('fr-FR', { style: 'currency', currency: 'USD' });
  }

  async function handleCalculate() {
    if (isCalculating) return;
    isCalculating = true;
    try {
      const ok = await payrollStore.calculatePayroll();
      if (ok) notification.toast.success('Calcul de la paie terminé');
      else notification.toast.error('Échec du calcul de la paie');
    } catch (e: any) {
      notification.toast.error(e?.message ?? 'Échec du calcul de la paie');
    } finally {
      isCalculating = false;
    }
  }

  async function handleReview() {
    if (isReviewing) return;
    isReviewing = true;
    try {
      const ok = await payrollStore.reviewPayroll();
      if (ok) notification.toast.success('Paie envoyée en révision');
      else notification.toast.error('Échec de la révision');
    } finally {
      isReviewing = false;
    }
  }

  function handleApprove() {
    if (isApproving) return;
    notification.confirm({
      title: 'Confirmer l\'approbation',
      message: `Vous allez approuver la paie de ${payrollStore.currentPeriod} pour un montant net total de ${formatAmount(payrollStore.totalNetPay)}`,
      type: 'warning',
      yesText: 'Approuver',
      noText: 'Annuler',
      onYes: async () => {
        isApproving = true;
        try {
          const ok = await payrollStore.approvePayroll();
          if (ok) notification.toast.success('Paie approuvée avec succès');
          else notification.toast.error('Échec de l\'approbation');
        } finally {
          isApproving = false;
        }
      }
    });
  }

  function handlePayment() {
    if (isPaying) return;
    notification.confirm({
      title: 'Confirmer le paiement',
      message: `Vous allez procéder au paiement de la paie de ${payrollStore.currentPeriod} pour un montant total de ${formatAmount(payrollStore.totalNetPay)}`,
      type: 'warning',
      yesText: 'Confirmer',
      noText: 'Annuler',
      onYes: async () => {
        isPaying = true;
        try {
          const ok = await payrollStore.processPayment();
          if (ok) notification.toast.success('Paiement effectué avec succès');
          else notification.toast.error('Échec du paiement');
        } finally {
          isPaying = false;
        }
      }
    });
  }

  const stepHeaderConfigs = $derived({
    kickoff: {
      title: "Création de la paie",
      icon: "plus"
    },
    preparation: {
      title: "Préparation de la paie",
      icon: "file-plus"
    },
    calculation: {
      title: "Calcul de la paie",
      icon: "calculator"
    },
    review: {
      title: "Révision des fiches de paie",
      icon: "eye"
    },
    approval: {
      title: "Approbation finale",
      icon: "circle-check"
    },
    payment: {
      title: "Paiement de la paie",
      icon: "banknote"
    }
  });

  const currentHeaderConfig = $derived(stepHeaderConfigs[payrollStore.currentStep]);

  $effect(() => {
    if (!hasCurrentRun) {
      ui.addActions('payroll-new-run', ActionsSnippet);
      return () => ui.removeActions('payroll-new-run');
    }
  });
</script>


<svelte:head>
  <title>Oxiliere HR - {hasCurrentRun ? `Paie ${payrollStore.currentRun?.period}` : 'Démarrer une nouvelle paie'}</title>
</svelte:head>

{#snippet ActionsSnippet()}
  <!-- Actions go here -->
{/snippet}


<div class="flex flex-col h-full overflow-hidden bg-slate-50/30">
  {#if hasCurrentRunTab}
    <header class="shrink-0 border-b border-slate-100 bg-white">
      <PayrollStepper 
        currentStep={payrollStore.currentStep}
        onStepClick={(step) => payrollStore.goToStep(step)}
      />
    </header>
    
    <main class="flex-1 overflow-y-auto w-full mx-auto p-3 min-h-105 max-w-5xl">
      <StepHeader
        title={currentHeaderConfig.title}
        icon={currentHeaderConfig.icon}
        status={currentStatus}
        currentStep={payrollStore.currentStep}
        hasCurrentRun={hasCurrentRun}
        {isCreating}
        {isCalculating}
        {isReviewing}
        {isApproving}
        {isPaying}
        {canSubmitKickoff}
        onCancelKickoff={() => { payrollStore.cancelNewRun(); goto('/payroll'); }}
        onSubmitKickoff={() => kickoffSubmit?.()}
        onNew={handleCalculate}
        onCalculate={handleCalculate}
        onReview={handleReview}
        onApprove={handleApprove}
        onPay={handlePayment}
        onNextStep={() => payrollStore.goToNextStep()}
      />

      {#if isKickoff} 
        <div in:fade={{ duration: 200 }}>
          <KickoffStep 
            bind:submitForm={kickoffSubmit}
            bind:canSubmit={canSubmitKickoff}
            bind:isCreating
            onCreated={() => payrollStore.goToStep('preparation')} 
          />
        </div>
      {:else if payrollStore.currentStep === 'preparation'}
        <div in:fade={{ duration: 200 }}>
          <PreparationStep />
        </div>
      {:else if payrollStore.currentStep === 'calculation'}
        <div in:fade={{ duration: 200 }}>
          <CalculationStep />
        </div>
      {:else if payrollStore.currentStep === 'review'}
        <div in:fade={{ duration: 200 }}>
          <ReviewStep />
        </div>
      {:else if payrollStore.currentStep === 'approval'}
        <div in:fade={{ duration: 200 }}>
          <ApprovalStep />
        </div>
      {:else if payrollStore.currentStep === 'payment'}
        <div in:fade={{ duration: 200 }}>
          <PaymentStep />
        </div>
      {/if}
    </main>
  {/if}
</div>

