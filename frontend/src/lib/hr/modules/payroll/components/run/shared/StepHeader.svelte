<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { PayrollStatus, PayrollStep } from "../../../types/types";
  

  interface Props {
    title: string;
    icon?: string;
    status?: PayrollStatus | 'pending' | 'loading' | 'completed' | 'error';
    currentStep: PayrollStep;
    hasCurrentRun: boolean;
    isCreating?: boolean;
    isCalculating?: boolean;
    isReviewing?: boolean;
    isApproving?: boolean;
    isPaying?: boolean;
    isClosing?: boolean;
    canSubmitKickoff?: boolean;
    onNew?: () => void;
    onCalculate?: () => void;
    onReview?: () => void;
    onApprove?: () => void;
    onPay?: () => void;
    onCloseRun?: () => void;
    onCancelKickoff?: () => void;
    onSubmitKickoff?: () => void;
    onNextStep?: () => void;
  }

  let { 
    title, 
    icon = 'file-text', 
    status = 'pending',
    currentStep,
    hasCurrentRun,
    isCreating = false,
    isCalculating = false,
    isReviewing = false,
    isApproving = false,
    isPaying = false,
    isClosing = false,
    canSubmitKickoff = false,
    onNew,
    onCalculate,
    onReview,
    onApprove,
    onPay,
    onCloseRun,
    onCancelKickoff,
    onSubmitKickoff,
    onNextStep
  }: Props = $props();

  // Step-based colors for the icon container
  const stepColors: Record<PayrollStep, { bg: string; icon: string }> = {
    kickoff: { bg: 'bg-slate-100', icon: 'text-slate-600' },
    preparation: { bg: 'bg-slate-100', icon: 'text-slate-600' },
    calculation: { bg: 'bg-blue-100', icon: 'text-blue-600' },
    review: { bg: 'bg-amber-100', icon: 'text-amber-600' },
    approval: { bg: 'bg-emerald-100', icon: 'text-emerald-600' },
    payment: { bg: 'bg-purple-100', icon: 'text-purple-600' }
  };

  const currentStepColors = $derived(stepColors[currentStep]);

  const statusConfig = {
    draft: { icon: 'clock', color: 'text-slate-400', bg: 'bg-slate-100', label: 'Brouillon' },
    calculated: { icon: 'loader-2', color: 'text-blue-600', bg: 'bg-blue-100', label: 'Calculé' },
    reviewed: { icon: 'eye', color: 'text-amber-600', bg: 'bg-amber-100', label: 'Révisé' },
    approved: { icon: 'circle-check', color: 'text-emerald-600', bg: 'bg-emerald-100', label: 'Approuvé' },
    paid: { icon: 'banknote', color: 'text-purple-600', bg: 'bg-purple-100', label: 'Payé' },
    pending: { icon: 'clock', color: 'text-slate-400', bg: 'bg-slate-100', label: 'En attente' },
    loading: { icon: 'loader-2', color: 'text-blue-600', bg: 'bg-blue-100', label: 'En cours' },
    completed: { icon: 'circle-check', color: 'text-emerald-600', bg: 'bg-emerald-100', label: 'Terminé' },
    error: { icon: 'alert-circle', color: 'text-red-600', bg: 'bg-red-100', label: 'Erreur' }
  };

  const config = $derived(statusConfig[status as keyof typeof statusConfig] || statusConfig.pending);
</script>


{#snippet ActionButton(label: string, icon: string, onclick: (() => void) | undefined, className: string = "bg-primary", disabled: boolean = false)}
  <Button {onclick} disabled={disabled} class={cn("text-white h-7.5 px-4 text-[0.85rem]", className)} variant="default">
    <AppIcon name={icon} size={18} />
    {label}
  </Button>
{/snippet}


<header class="flex items-center justify-between pb-2 border-b border-slate-100 pt-0">
  <div class="flex items-center gap-3">
    <div class={cn("w-10 h-10 rounded-xl flex items-center justify-center shrink-0", currentStepColors.bg)}>
      <AppIcon name={icon} size={22} strokeWidth={1.2} />
    </div>

    <div class="flex flex-col gap-0.5">
      <h1 class="text-[0.95rem] font-bold text-slate-900 tracking-tight">{title}</h1>
      
      {#if hasCurrentRun}
        <div class={cn("inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.72rem] font-semibold leading-none w-fit", config.bg, config.color)}>
          <span class={cn(
            "h-1.5 w-1.5 rounded-full",
            status === 'loading' || status === 'calculated' ? "animate-pulse " + config.color.replace('text-', 'bg-') : config.color.replace('text-', 'bg-')
          )}></span>
          {config.label}
        </div>
      {/if}
    </div>
  </div>

  <div class="flex items-center gap-2">
    {#if currentStep === 'kickoff'}
      {#if onCancelKickoff}
        <Button 
          type="button"
          variant="outline" 
          size="sm" 
          onclick={onCancelKickoff} 
          class="h-7 text-[0.85rem] px-3.5 border-slate-200 text-slate-600 font-medium shadow-fine"
        >
          <AppIcon name="x" size={16} class="text-slate-500" />
          Annuler
        </Button>
      {/if}
      {@render ActionButton(
        isCreating ? "Traitement…" : (hasCurrentRun ? "Mettre à jour" : "Lancer l'exécution"),
        "play",
        onSubmitKickoff,
        "bg-primary",
        !canSubmitKickoff || isCreating
      )}

    {:else if !hasCurrentRun}
      {@render ActionButton(isCreating ? "Création…" : "Nouvelle paie", "plus", onNew, "bg-primary", isCreating)}
    
    {:else if currentStep === 'preparation' && status === 'draft'}
      {@render ActionButton(isCalculating ? "Calcul…" : "Passer au calcul", "calculator", () => {
        onCalculate?.();
      }, "bg-primary", isCalculating)}
    
    {:else if currentStep === 'calculation' && status === 'calculated'}
      {@render ActionButton(isReviewing ? "Passage à la révision…" : "Passer à la révision", "eye", () => {
        onReview?.();
      }, "bg-amber-500 hover:bg-amber-600", isReviewing)}
    
    {:else if currentStep === 'review' && status === 'reviewed'}
      {@render ActionButton(isApproving ? "Approbation…" : "Passer à l'approbation", "circle-check", () => {
        onApprove?.();
      }, "bg-emerald-600 hover:bg-emerald-700", isApproving)}
    
    {:else if currentStep === 'approval' && status === 'approved'}
      {@render ActionButton(isPaying ? "Paiement…" : "Passer au paiement", "banknote", () => {
        onPay?.();
      }, "bg-purple-600 hover:bg-purple-700", isPaying)}
    
    {:else if status === 'paid' && onCloseRun}
      {@render ActionButton(isClosing ? "Clôture…" : "Clôturer l'exécution", 'circle-check', onCloseRun, 'bg-slate-800 hover:bg-slate-900', isClosing)}
    {:else if status === 'paid'}
      <Button variant="outline" size="sm" class="h-7.5 text-[0.85rem] px-4 border-slate-200 text-slate-600 font-medium shadow-fine">
        <AppIcon name="download" size={16} />
        Télécharger les rapports
      </Button>
    {:else}
      <div class="flex items-center gap-2 px-3 py-1 bg-slate-50 border border-slate-100 rounded-lg">
        <AppIcon name="check" size={14} class="text-emerald-500" />
        <span class="text-[0.82rem] text-slate-500 font-medium">Action terminée</span>
      </div>
    {/if}
  </div>
</header>

