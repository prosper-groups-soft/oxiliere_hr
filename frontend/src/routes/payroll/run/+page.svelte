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

  const hasCurrentRun = $derived(payrollStore.currentRun !== null);
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');

  function handleNewPayroll() {
    payrollStore.createPayrollRun(payrollStore.currentPeriod);
    payrollStore.goToStep('preparation');
    notification.toast.success('Nouvelle paie créée');
  }

  function handleCalculate() {
    payrollStore.calculatePayroll();
  }

  function handleReview() {
    payrollStore.reviewPayroll();
  }

  function handleApprove() {
    notification.confirm({
      title: 'Confirmer l\'approbation',
      message: `Vous allez approuver la paie de ${payrollStore.currentPeriod} pour un montant net total de ${payrollStore.totalNetPay.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}`,
      type: 'warning',
      yesText: 'Approuver',
      noText: 'Annuler',
      onYes: () => {
        payrollStore.approvePayroll();
        notification.toast.success('Paie approuvée avec succès');
      }
    });
  }

  function handlePayment() {
    notification.confirm({
      title: 'Confirmer le paiement',
      message: `Vous allez procéder au paiement de la paie de ${payrollStore.currentPeriod} pour un montant total de ${payrollStore.totalNetPay.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}`,
      type: 'warning',
      yesText: 'Confirmer',
      noText: 'Annuler',
      onYes: () => {
        payrollStore.processPayment();
        notification.toast.success('Paiement effectué avec succès');
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
        <div class="p-1 min-h-[420px]">
          <StepHeader
            title={currentHeaderConfig.title}
            icon={currentHeaderConfig.icon}
            status={currentStatus}
            currentStep={payrollStore.currentStep}
            {hasCurrentRun}
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
      <Empty
        title="Démarrer une nouvelle paie"
        description="Créez une nouvelle période de paie pour commencer le processus de calcul et de paiement."
        icon="file-text"
      >
      <Button variant="default" size="sm" onclick={handleNewPayroll} class="shadow-fine bg-primary text-white text-[0.83rem] hover:text-white rounded-lg">
        <AppIcon name="play-circle" size={17} />
        Commencer la paie
      </Button>
      </Empty>
    </div>
  {/if}
</div>

