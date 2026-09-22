<script lang="ts">
  import { goto } from "$app/navigation";
  import { payrollStore } from "@/hr/payroll/stores/payroll.svelte";
  import { notification } from "@/stores/notification.svelte";
  import PayrollStepper from "@/hr/payroll/components/run/PayrollStepper.svelte";
  import PreparationStep from "@/hr/payroll/components/run/steps/PreparationStep.svelte";
  import CalculationStep from "@/hr/payroll/components/run/steps/CalculationStep.svelte";
  import ReviewStep from "@/hr/payroll/components/run/steps/ReviewStep.svelte";
  import ApprovalStep from "@/hr/payroll/components/run/steps/ApprovalStep.svelte";
  import PaymentStep from "@/hr/payroll/components/run/steps/PaymentStep.svelte";
  import { fade } from "svelte/transition";
  import StepHeader from "@/hr/payroll/components/run/shared/StepHeader.svelte";
  import { ui } from "@/stores/ui.svelte";
  import KickoffStep from "@/hr/payroll/components/run/steps/KickoffStep.svelte";
  import { hr } from '@/constants/features/navigation';


  const hasCurrentRun = $derived(payrollStore.hasActiveRun);
  const hasCurrentRunTab = $derived(payrollStore.hasCurrentRunTab);
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  const isKickoff = $derived(payrollStore.currentStep === 'kickoff');

  // Redirige vers la liste des exécutions si on arrive sur /payroll/run sans
  // exécution en cours (ni création en cours). On attend isBootResolved pour ne
  // pas rediriger pendant la restauration du run ; et on garde l'écran de clôture
  // d'un run payé (currentRun non nul) visible.
  $effect(() => {
    if (
      payrollStore.isBootResolved &&
      !payrollStore.currentRun &&
      !payrollStore.isStartingNewRun
    ) {
      goto(hr('/payroll'));
    }
  });

  let isCreating = $state(false);
  let isCalculating = $state(false);
  let isReviewing = $state(false);
  let isApproving = $state(false);
  let isPaying = $state(false);
  let isClosing = $state(false);

  let kickoffSubmit = $state<(() => void) | undefined>(undefined);
  let canSubmitKickoff = $state(false);

  /** Nombre d'employés payés sur le run courant (source summary, sinon bulletins). */
  const paidEmployeeCount = $derived(payrollStore.currentRunSummary?.summary?.total_employees ?? payrollStore.payslips.length);

  /** Formate un montant dans la devise du run (CDF en pratique), sans USD. */
  function formatAmount(amount: number): string {
    return (amount ?? 0).toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
  }

  /** Libellé humain de la période du run (ex. « septembre 2026 ») au lieu de « 2026-09 ». */
  const periodLabel = $derived.by(() => {
    const start = payrollStore.currentRun?.periodStart;
    const raw = start || payrollStore.currentPeriod;
    const y = Number(raw?.slice(0, 4));
    const m = Number(raw?.slice(5, 7));
    if (!raw || !Number.isInteger(y) || !Number.isInteger(m)) {
      return payrollStore.currentRun?.period || payrollStore.currentPeriod || '';
    }
    return new Date(y, m - 1, 1).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
  });

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

  /** Clôture d'un run payé : petite temporisation (feedback) puis libère l'onglet
   *  et retourne aux exécutions. Désactive le bouton pour éviter les doubles clics. */
  function handleCloseRun() {
    if (isClosing) return;
    isClosing = true;
    setTimeout(() => {
      payrollStore.closeActiveRun();
      goto(hr('/payroll'));
    }, 450);
  }

  async function handleReview() {
    if (isReviewing) return;
    isReviewing = true;
    try {
      const ok = await payrollStore.reviewPayroll();
      if (ok) notification.toast.success('Paie envoyée en révision');
      else notification.toast.error('Échec de la révision');
    } catch (e: any) {
      notification.toast.error(e?.message ?? 'Échec de la révision');
    } finally {
      isReviewing = false;
    }
  }

  function handleApprove() {
    if (isApproving) return;
    notification.confirm({
      title: 'Confirmer l\'approbation',
      message: `Vous allez approuver la paie de ${periodLabel} (${paidEmployeeCount} employé${paidEmployeeCount > 1 ? 's' : ''}) pour un montant net total de ${formatAmount(payrollStore.totalNetPay)}. L'approbation verrouillera la paie pour le paiement.`,
      type: 'warning',
      yesText: 'Approuver',
      noText: 'Annuler',
      onYes: async () => {
        isApproving = true;
        try {
          const ok = await payrollStore.approvePayroll();
          if (ok) notification.toast.success('Paie approuvée avec succès');
          else notification.toast.error('Échec de l\'approbation');
        } catch (e: any) {
          notification.toast.error(e?.message ?? 'Échec de l\'approbation');
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
      message: `Vous allez procéder au paiement de la paie de ${periodLabel} (${paidEmployeeCount} employé${paidEmployeeCount > 1 ? 's' : ''}) pour un montant total de ${formatAmount(payrollStore.totalNetPay)}.`,
      type: 'warning',
      yesText: 'Confirmer',
      noText: 'Annuler',
      onYes: async () => {
        isPaying = true;
        try {
          const ok = await payrollStore.processPayment();
          if (ok) notification.toast.success('Paiement effectué avec succès');
          else notification.toast.error('Échec du paiement');
        } catch (e: any) {
          notification.toast.error(e?.message ?? 'Échec du paiement');
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
      title: "Révision de la paie",
      icon: "eye"
    },
    approval: {
      title: "Approbation de la paie",
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
        {isClosing}
        {canSubmitKickoff}
        onCloseRun={handleCloseRun}
        onCancelKickoff={() => { payrollStore.cancelNewRun(); goto(hr('/payroll')); }}
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

