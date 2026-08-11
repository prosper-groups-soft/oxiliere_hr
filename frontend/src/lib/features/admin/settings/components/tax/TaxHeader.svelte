<script lang="ts">
  import { Button } from "@/components/ui/button";
  import CurrencyToggle from "@/components/ui/currency-toggle";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import type { CreateMutationResult } from '@tanstack/svelte-query';
  import { taxSettingsStore } from "../../stores/taxSettingsStore.svelte";
  import { notification } from "@/stores/notification.svelte";

  
  interface Props {
    saveMutation: CreateMutationResult<{ success: boolean }, Error, void, unknown>;
    resetMutation: CreateMutationResult<{ status: string; summary: Record<string, number> }, Error, void, unknown>;
    onSuccess?: () => void;
  }

  let { saveMutation, resetMutation, onSuccess }: Props = $props();

  const config = $derived(taxSettingsStore.config);
  const hasChanges = $derived(taxSettingsStore.hasChanges);
  const hasValidationErrors = $derived(Object.keys(taxSettingsStore.validationErrors).length > 0);
  const canSave = $derived(hasChanges && !hasValidationErrors);
  const isSaving = $derived($saveMutation.isPending);

  async function handleSave() {
    const changes = taxSettingsStore.getPendingChanges();
    if (!changes) {
      notification.toast.error('Veuillez corriger les erreurs de validation');
      return;
    }
    await $saveMutation.mutateAsync();
    onSuccess?.();
  }

  async function handleReset() {
    notification.confirm({
      title: 'Réinitialiser les paramètres ?',
      message: 'Cette action réinitialisera tous les paramètres fiscaux aux valeurs par défaut du système. Les données actuelles seront remplacées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      noText: 'Annuler',
      onYes: async () => {
        try {
          await $resetMutation.mutateAsync();
          onSuccess?.();
        } catch (err) {
          // Error handled by mutation
        }
      }
    });
  }
</script>


<div class="bg-white flex items-center justify-between px-6 py-2 pr-8 border-b border-slate-100">
  <div class="flex items-center gap-3">
    <div>
      <h3 class="font-semibold text-slate-900 text-[0.96rem]">
        Configuration fiscale IPR & Social
      </h3>
      <p class="text-[0.85rem] text-slate-500">
        Barème progressif IPR selon la législation fiscale RDC
      </p>
    </div>
  </div>
  <div class="flex gap-2 items-center">
    {#if canSave}
      <div transition:fade={{ duration: 300, easing: cubicOut }}>
        <Button onclick={handleSave} disabled={isSaving} class="bg-indigo-600 hover:bg-indigo-700 text-white shadow-fine h-7.5 whitespace-nowrap overflow-hidden transition-all">
          {#if isSaving}
            <AnimateSpin text="" class="border-white size-3" />
          {:else}
            <AppIcon name="check" size={17} />
          {/if}
          Enregistrer
        </Button>
      </div>
    {/if}
    <Button variant="outline" onclick={handleReset} disabled={isSaving} class="h-7.5 shadow-fine text-slate-600 hover:text-slate-800 hover:bg-slate-50 border-slate-200">
      <AppIcon name="rotate-ccw" size={16} />
      Rétablir
    </Button>
    
    <CurrencyToggle 
      currency={config.currency === 'CDF' ? 'CDF' : 'USD'} 
      onChange={(c) => taxSettingsStore.setCurrency(c)}
      size="sm"
    />
  </div>
</div>

<!-- Status badges -->
{#if hasChanges}
  {#if hasValidationErrors}
    <div class="px-6 py-1 bg-red-50 border-b border-red-100 hidden" transition:slide={{ duration: 300, easing: cubicOut }}>
      <span class="flex items-center gap-1.5 text-[0.8rem] text-red-600 font-medium">
        <AppIcon name="circle-x" size={15} />
        Veuillez corriger les erreurs de validation avant d'enregistrer
      </span>
    </div>
  {:else}
    <div class="px-6 py-1 bg-amber-50 border-b border-amber-100 hidden" transition:slide={{ duration: 300, easing: cubicOut }}>
      <span class="flex items-center gap-1.5 text-[0.8rem] text-amber-600 font-medium">
        <AppIcon name="circle-alert" size={15} />
        Modifications non sauvegardées
      </span>
    </div>
  {/if}
{/if}

