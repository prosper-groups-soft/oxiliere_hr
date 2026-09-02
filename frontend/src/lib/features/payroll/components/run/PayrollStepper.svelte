<script lang="ts">
  import TooltipWrapper from '@/components/shared/containers/TooltipWrapper.svelte';
  import { cn } from "@/utilities/common/css";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import type { PayrollStep } from "../../types/types";
  import { PAYROLL_STEPS, PAYROLL_STEP_LABELS, PAYROLL_STEP_DESCRIPTIONS } from "../../types/types";
  import { scale } from "svelte/transition";

  
  interface Props {
    currentStep: PayrollStep;
    onStepClick?: (step: PayrollStep) => void;
  }

  let { currentStep, onStepClick }: Props = $props();

  const steps: { id: PayrollStep; label: string; description: string }[] = PAYROLL_STEPS.map(step => ({
    id: step,
    label: PAYROLL_STEP_LABELS[step],
    description: PAYROLL_STEP_DESCRIPTIONS[step]
  }));

  const currentStepIndex = $derived(steps.findIndex(s => s.id === currentStep));
</script>


{#snippet navButton(direction: 'prev' | 'next', action: () => void, disabled: boolean)}
  <button
    onclick={action}
    {disabled}
    class={cn(
      "w-8 h-9 flex items-center justify-center transition-all cursor-pointer z-20",
      direction === 'prev' ? "rounded-l-lg border-r border-slate-200" : "rounded-r-lg border-l border-slate-200",
      !disabled ? "bg-slate-100 hover:bg-slate-200 text-slate-600" : "bg-slate-50 text-slate-300 cursor-not-allowed"
    )}
  >
    <AppIcon name={direction} size={17} />
  </button>
{/snippet}


{#snippet stepIndicator(index: number, isCompleted: boolean, isActive: boolean)}
  {@const stepColors = [
    "bg-slate-500",      // kickoff
    "bg-slate-400",      // preparation (draft)
    "bg-blue-500",       // calculation
    "bg-amber-500",      // review
    "bg-emerald-500",    // approval
    "bg-purple-500"      // payment
  ]}
  <div class={cn(
    "w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold transition-colors duration-300",
    isActive && "bg-primary text-white",
    isCompleted && "text-white",
    isCompleted && stepColors[index],
    !isActive && !isCompleted && "bg-slate-300 text-slate-600"
  )}>
    {#if isCompleted}
      <div in:scale={{ duration: 200 }}>
        <AppIcon name="check" size={10} strokeWidth={3} />
      </div>
    {:else}
      {index + 1}
    {/if}
  </div>
{/snippet}


<div class="relative bg-white">
  <div class="relative flex items-center justify-center px-6 py-1">
    
    {@render navButton('prev', () => payrollStore.prevStep(), !payrollStore.canGoPrev)}

    <div class="relative inline-grid grid-cols-6 bg-slate-100 w-auto overflow-hidden">
      <div class="absolute top-0.5 bottom-0.5 left-0.5 right-0.5 grid grid-cols-6 pointer-events-none">
        <div
          class="bg-white rounded-md shadow-fine border border-slate-200 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"
          style="transform: translateX({currentStepIndex * 100}%)"
        ></div>
      </div>

      {#each steps as step, index}
        {@const isActive = index === currentStepIndex}
        {@const isCompleted = index < currentStepIndex}
        {@const isAccessible = payrollStore.canAccessStep(index)}
        
        <TooltipWrapper content={step.description} side="top" asChild={true} delayDuration={100}>
          {#snippet children(props: Record<string, any>)}
            <button
              {...props}
              onclick={() => isAccessible && onStepClick?.(step.id)}
              disabled={!isAccessible}
              class={cn(
                "relative z-10 flex items-center justify-center gap-2 px-2 py-2 text-sm transition-colors outline-none",
                isActive ? "text-primary" : "text-slate-600",
                isAccessible ? "cursor-pointer hover:text-slate-800" : "cursor-not-allowed opacity-60"
              )}
            >
              {@render stepIndicator(index, isCompleted, isActive)}
              
              <span class="text-[0.81rem] whitespace-nowrap">{step.label}</span>
            </button>
          {/snippet}
        </TooltipWrapper>
      {/each}
    </div>

    {@render navButton('next', () => payrollStore.nextStep(), !payrollStore.canGoNext)}
  </div>
</div>

