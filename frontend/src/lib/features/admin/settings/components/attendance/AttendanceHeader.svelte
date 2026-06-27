<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { attendanceSettingsStore } from "../../stores/attendanceSettingsStore.svelte";
  import { notification } from "@/stores/notification.svelte";


  const hasChanges = $derived(attendanceSettingsStore.isDirty);
  const isSaving = $derived(attendanceSettingsStore.isSaving);
  const isNotDefault = $derived(attendanceSettingsStore.isNotDefault);

  async function handleSave() {
    if (!hasChanges) return;
    await attendanceSettingsStore.save();
  }

  function handleReset() {
    notification.confirm({
      title: 'Réinitialiser les paramètres ?',
      message: 'Cette action rétablira les valeurs par défaut du système (5 min de grâce, 30 min d\'absence partielle, arrondi à 1 min). Les données actuelles seront remplacées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      noText: 'Annuler',
      onYes: () => {
        attendanceSettingsStore.resetToDefaults();
      }
    });
  }
</script>


<div class="bg-white flex items-center justify-between px-6 py-2 pr-8 border-b border-slate-100">
  <div class="flex items-center gap-3">
    <div>
      <h3 class="font-semibold text-slate-900 text-[0.96rem]">
        Règles de pointage
      </h3>
      <p class="text-[0.85rem] text-slate-500">
        Tolérances, seuils d'absence et précision d'arrondi
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
    {#if isNotDefault}
      <Button variant="outline" onclick={handleReset} disabled={isSaving} class="h-7.5 shadow-fine text-slate-600 hover:text-slate-800 hover:bg-slate-50 border-slate-200">
        <AppIcon name="rotate-ccw" size={16} />
        Rétablir
      </Button> 
    {/if}
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
