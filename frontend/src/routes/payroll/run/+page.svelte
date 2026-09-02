<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { notification } from "@/stores/notification.svelte";
  import PayrollStepper from "@/features/payroll/components/run/PayrollStepper.svelte";

  import PreparationStep from "@/features/payroll/components/run/steps/PreparationStep.svelte";
  import CalculationStep from "@/features/payroll/components/run/steps/CalculationStep.svelte";
  import ReviewStep from "@/features/payroll/components/run/steps/ReviewStep.svelte";
  import ApprovalStep from "@/features/payroll/components/run/steps/ApprovalStep.svelte";
  import PaymentStep from "@/features/payroll/components/run/steps/PaymentStep.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import Button from "@/components/ui/button/button.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { fade } from "svelte/transition";
  import StepHeader from "@/features/payroll/components/run/shared/StepHeader.svelte";
  import { goto } from "$app/navigation";


  const hasCurrentRun = $derived(payrollStore.currentRun !== null);
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');

  let isCreating = $state(false);
  let isCalculating = $state(false);
  let isReviewing = $state(false);
  let isApproving = $state(false);
  let isPaying = $state(false);

  function formatAmount(amount: number): string {
    return (amount ?? 0).toLocaleString('fr-FR', { style: 'currency', currency: 'USD' });
  }

  async function handleNewPayroll() {
    if (isCreating) return;
    isCreating = true;
    try {
      const run = await payrollStore.createPayrollRun(payrollStore.currentPeriod);
      if (!run) {
        notification.toast.error('Impossible de créer la paie');
        return;
      }
      payrollStore.goToStep('preparation');
      notification.toast.success('Nouvelle paie créée');
      await payrollStore.fetchRunList();
      await goto('/payroll/run');
    } finally {
      isCreating = false;
    }
  }

  async function handleCalculate() {
    if (isCalculating) return;
    isCalculating = true;
    try {
      const ok = await payrollStore.calculatePayroll();
      if (ok) notification.toast.success('Calcul de la paie lancé');
      else notification.toast.error('Échec du calcul de la paie');
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

  const stepComponents = {
    preparation: PreparationStep,
    calculation: CalculationStep,
    review: ReviewStep,
    approval: ApprovalStep,
    payment: PaymentStep
  };

  const CurrentStep = $derived(stepComponents[payrollStore.currentStep]);
</script>


<!-- bg-slate-50/30 -->
<div class="flex flex-col h-full overflow-hidden bg-slate-50/30">
  {#if hasCurrentRun}
    <div class="shrink-0 border-b border-slate-100 bg-white">
      <PayrollStepper 
        currentStep={payrollStore.currentStep}
        onStepClick={(step) => payrollStore.goToStep(step)}
      />
    </div>
    
    <main class="flex-1 overflow-y-auto min-h-0">
      <div class="max-w-5xl mx-auto py-2">
        <div class="p-1 min-h-105">
          <StepHeader
            title={currentHeaderConfig.title}
            icon={currentHeaderConfig.icon}
            status={currentStatus}
            currentStep={payrollStore.currentStep}
            {hasCurrentRun}
            {isCreating}
            {isCalculating}
            {isReviewing}
            {isApproving}
            {isPaying}
            onNew={handleNewPayroll}
            onCalculate={handleCalculate}
            onReview={handleReview}
            onApprove={handleApprove}
            onPay={handlePayment}
            onNextStep={() => payrollStore.goToNextStep()}
          />
          {#if CurrentStep}
            {#key payrollStore.currentStep}
              <div in:fade={{ duration: 200 }}>
                <CurrentStep />
              </div>
            {/key}
          {/if}
        </div>
      </div>
    </main>
    
  {:else}
    <div class="flex flex-1 items-center justify-center">
      <!-- Reusing the new-run form logic here -->
      <div class="w-full max-w-2xl px-6">
        <h2 class="text-xl font-bold text-slate-800 mb-6">Démarrer une nouvelle paie</h2>
        <!-- Form code from new-run/+page.svelte goes here -->
        <p class="text-slate-500 mb-6">Veuillez configurer la période pour commencer.</p>
        <Button variant="default" size="sm" onclick={handleNewPayroll} disabled={isCreating} class="shadow-fine bg-primary text-white text-[0.83rem] hover:text-white rounded-lg">
          <AppIcon name="play-circle" size={17} />
          {isCreating ? 'Création…' : 'Commencer la paie'}
        </Button>
      </div>
    </div>
  {/if}
</div>


