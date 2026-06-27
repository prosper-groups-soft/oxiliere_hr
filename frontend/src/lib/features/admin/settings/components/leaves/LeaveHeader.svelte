<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { leaveSettingsStore } from "../../stores/leaveSettingsStore.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { 
    useSaveLeaveSettingsMutation, 
    useInitializeDefaultsMutation 
  } from "../../queries/leaveQueries";


  interface Props {
    saveMutation: ReturnType<typeof useSaveLeaveSettingsMutation>;
    resetMutation: ReturnType<typeof useInitializeDefaultsMutation>;
    onSuccess?: () => void;
  }

  let { saveMutation, resetMutation, onSuccess }: Props = $props();

  const hasChanges = $derived(leaveSettingsStore.hasChanges);
  const hasValidationErrors = $derived(Object.keys(leaveSettingsStore.validationErrors).length > 0);
  const canSave = $derived(hasChanges && !hasValidationErrors);
  const isSaving = $derived($saveMutation.isPending);

  async function handleSave() {
    const changes = leaveSettingsStore.getPendingChanges();
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
      message: 'Cette action réinitialisera tous les paramètres aux valeurs par défaut du système. Les données actuelles seront remplacées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      noText: 'Annuler',
      onYes: async () => {
        try {
          await $resetMutation.mutateAsync();
          onSuccess?.();
        } catch (err) {
          // Error is managed by mutation
        }
      }
    });
  }
</script>


<div class="bg-white flex items-center justify-between px-6 py-2 pr-8 border-b border-slate-100">
  <div class="flex items-center gap-3">
    <div>
      <h3 class="font-semibold text-slate-900 text-[0.96rem]">
        Configuration des congés
      </h3>
      <p class="text-[0.85rem] text-slate-500">
        Paramétrage selon le Code du Travail RDC
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
  </div>
</div>

<!-- Status badges -->
{#if hasChanges}
  {#if hasValidationErrors}
    <div class="px-6 py-1 bg-red-50 border-b border-red-100 hidden">
      <span class="flex items-center gap-1.5 text-[0.8rem] text-red-600 font-medium" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
        <AppIcon name="circle-x" size={15} />
        Veuillez corriger les erreurs de validation avant d'enregistrer
      </span>
    </div>
  {:else}
    <div class="px-6 py-1 bg-amber-50 border-b border-amber-100 hidden">
      <span class="flex items-center gap-1.5 text-[0.8rem] text-amber-600 font-medium" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
        <AppIcon name="circle-alert" size={15} />
        Modifications non sauvegardées
      </span>
    </div>
  {/if}
{/if}
