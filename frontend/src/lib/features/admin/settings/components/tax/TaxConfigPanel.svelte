<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { taxSettingsStore } from "../../stores/taxSettingsStore.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import type { CreateMutationResult } from '@tanstack/svelte-query';
  
  // Sub-components
  import TaxHeader from "./TaxHeader.svelte";
  import TaxLegalBanner from "./TaxLegalBanner.svelte";
  import IPRSection from "./sections/IPRSection.svelte";
  import LegalAllowancesSection from "./sections/LegalAllowancesSection.svelte";
  import OvertimeRulesSection from "./sections/OvertimeRulesSection.svelte";
  import SocialContributionsSection from "./sections/SocialContributionsSection.svelte";
  import CurrencyConfigSection from "./sections/CurrencyConfigSection.svelte";
  import LeaveAttendanceSection from "./sections/LeaveAttendanceSection.svelte";
  import IPRCalculatorSheet from "./sheets/IPRCalculatorSheet.svelte";

  interface Props {
    saveMutation: CreateMutationResult<{ success: boolean }, Error, void, unknown>;
    resetMutation: CreateMutationResult<{ status: string; summary: Record<string, number> }, Error, void, unknown>;
    onSuccess?: () => void;
  }

  let { saveMutation, resetMutation, onSuccess }: Props = $props();

  const hasLoaded = $derived(taxSettingsStore.hasLoaded);
  const hasChanges = $derived(taxSettingsStore.hasChanges);
  const hasValidationErrors = $derived(Object.keys(taxSettingsStore.validationErrors).length > 0);

  let showCalculatorSheet = $state(false);

  // Register header badges
  $effect(() => {
    ui.addActions('tax-settings-header', saveStatusBadge);
    return () => ui.removeActions('tax-settings-header');
  });
</script>


{#snippet saveStatusBadge()}
  {#if hasChanges}
    {#if hasValidationErrors}
      <span class="flex items-center justify-center gap-1.5 text-[0.8rem] text-red-600 bg-red-50 px-2.5 py-1 rounded-full font-medium whitespace-nowrap w-44" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
        <AppIcon name="circle-x" size={15} />
        Erreurs de validation
      </span>
    {:else}
      <span class="flex items-center justify-center gap-1.5 text-[0.8rem] text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full font-medium whitespace-nowrap w-44" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
        <AppIcon name="circle-alert" size={15} />
        Non sauvegardé
      </span>
    {/if}
  {/if}
{/snippet}


<div class="sticky top-0 z-10 bg-white">
  <TaxHeader {saveMutation} {resetMutation} {onSuccess} />
  <TaxLegalBanner />
</div>


{#if hasLoaded}
  <div class="mt-6 space-y-6 mb-6" transition:fade={{ duration: 300, easing: cubicOut }}>
    <IPRSection />
    <LegalAllowancesSection />
    <OvertimeRulesSection />
    <SocialContributionsSection />
    <CurrencyConfigSection />
    <LeaveAttendanceSection />
  </div>
{:else}
  <div class="mt-12 flex items-center justify-center" transition:fade={{ duration: 200, easing: cubicOut }}>
    <div class="flex items-center gap-3 text-slate-400">
      <AnimateSpin text="Chargement des paramètres" class="size-3" />
    </div>
  </div>
{/if}


<!-- IPR Calculator Sheet -->
<IPRCalculatorSheet bind:open={showCalculatorSheet} />

