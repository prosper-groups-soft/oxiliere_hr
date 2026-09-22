<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { currencySettingsStore } from "../../stores/currencySettingsStore.svelte";
  import { notification } from "@/stores/notification.svelte";

  const hasChanges = $derived(currencySettingsStore.hasChanges);
  const isSaving = $derived(currencySettingsStore.isSaving);
  const hasValidationErrors = $derived(false); // TODO: add validation

  async function handleSave() {
    await currencySettingsStore.saveSettings();
  }

  function handleReset() {
    notification.confirm({
      title: 'Réinitialiser les paramètres ?',
      message: 'Cette action réinitialisera tous les paramètres aux valeurs par défaut du système. Les données actuelles seront remplacées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      noText: 'Annuler',
      onYes: () => {
        currencySettingsStore.resetToDefaults();
      }
    });
  }
</script>


<div class="bg-white flex items-center justify-between px-6 py-2 pr-8 border-b border-slate-100">
  <div class="flex items-center gap-3">
    <div>
      <h3 class="font-semibold text-slate-900 text-[0.96rem]">
        Mon entreprise
      </h3>
      <p class="text-[0.85rem] text-slate-500">
        Configuration des informations légales et sites de travail
      </p>
    </div>
  </div>
  <div class="flex gap-2 items-center">
    {#if hasChanges}
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
    <Button variant="outline" onclick={handleReset} disabled={isSaving} class="h-7.5 shadow-fine text-slate-600 hover:text-slate-800 hover:bg-slate-50 border-slate-200 hidden">
      <AppIcon name="rotate-ccw" size={16} />
      Rétablir
    </Button> 
  </div>
</div>

<!-- Status badges -->
{#if hasChanges}
  <div class="px-6 py-1 bg-amber-50 border-b border-amber-100 hidden">
    <span class="flex items-center gap-1.5 text-[0.8rem] text-amber-600 font-medium" transition:slide={{ duration: 300, easing: cubicOut, axis: 'y' }}>
      <AppIcon name="circle-alert" size={15} />
      Modifications non sauvegardées
    </span>
  </div>
{/if}
