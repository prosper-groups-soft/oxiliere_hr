<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import * as Select from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { calendarStore } from "@/features/calendar/stores/calendar.svelte";
  import type { EventType } from "../../types/types";
  import { fade } from "svelte/transition";

  let {
    open = $bindable(false)
  } = $props<{
    open: boolean
  }>();

  // State
  let sourceYear = $state(new Date().getFullYear());
  let targetYear = $state(new Date().getFullYear() + 1);
  let selectedTypes = $state<EventType[]>(['holiday', 'closure']);
  let isProcessing = $state(false);

  const eventTypes: { value: EventType; label: string }[] = [
    { value: 'holiday', label: 'Jours Fériés' },
    { value: 'closure', label: 'Fermetures Entreprise' },
    { value: 'training', label: 'Formations' }
  ];

  const yearOptions = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - 1 + i);

  function toggleType(type: EventType) {
    if (selectedTypes.includes(type)) {
      selectedTypes = selectedTypes.filter(t => t !== type);
    } else {
      selectedTypes = [...selectedTypes, type];
    }
  }

  async function handleReplicate() {
    if (sourceYear === targetYear) {
      notification.toast.error("L'année source et l'année cible doivent être différentes.");
      return;
    }
    
    if (selectedTypes.length === 0) {
      notification.toast.error("Veuillez sélectionner au moins un type d'événement.");
      return;
    }

    isProcessing = true;
    try {
      // Simulate/Trigger replication logic in store
      const count = calendarStore.replicateYear(sourceYear, targetYear, selectedTypes);
      
      if (count > 0) {
        notification.toast.success(`${count} événements ont été répliqués vers ${targetYear}.`);
        open = false;
      } else {
        notification.toast.warning("Aucun événement correspondant n'a été trouvé pour la réplication.");
      }
    } catch (error) {
      notification.toast.error("Erreur lors de la réplication.");
    } finally {
      isProcessing = false;
    }
  }
</script>

<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-2">
        <div class="h-10 w-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <AppIcon name="copy" size={20} />
        </div>
        <Sheet.Title class="text-[1rem] font-bold text-slate-900 truncate">
          Répliquer les événements
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <p class="text-[0.85rem] text-slate-500 leading-relaxed">
          Copiez vos événements récurrents (jours fériés, fermetures) d'une année à une autre. Les dates seront ajustées automatiquement.
        </p>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-slate-900">Année Source</Label>
            <Select.Root type="single" value={sourceYear.toString()} onValueChange={(v) => sourceYear = parseInt(v)}>
              <Select.Trigger class="h-10 w-full shadow-fine bg-white border-slate-200">
                <span class="truncate text-[0.85rem] font-medium">{sourceYear}</span>
              </Select.Trigger>
              <Select.Content>
                {#each yearOptions as year}
                  <Select.SelectItem value={year.toString()} class="text-[0.85rem]">{year}</Select.SelectItem>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>

          <div class="space-y-2">
            <Label class="text-slate-900">Année Cible</Label>
            <Select.Root type="single" value={targetYear.toString()} onValueChange={(v) => targetYear = parseInt(v)}>
              <Select.Trigger class="h-10 w-full shadow-fine bg-white border-slate-200">
                <span class="truncate text-[0.85rem] font-medium">{targetYear}</span>
              </Select.Trigger>
              <Select.Content>
                {#each yearOptions as year}
                  <Select.SelectItem value={year.toString()} class="text-[0.85rem]">{year}</Select.SelectItem>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>
        </div>

        <div class="space-y-3 pt-2">
          <Label class="text-slate-900">Types d'événements à répliquer</Label>
          <div class="space-y-3">
            {#each eventTypes as type}
              <div 
                class="flex items-center gap-3 cursor-pointer group"
                onclick={() => toggleType(type.value)}
                role="none"
              >
                <Checkbox 
                  checked={selectedTypes.includes(type.value)} 
                  class="data-[state=checked]:bg-primary data-[state=checked]:border-primary h-5 w-5"
                />
                <span class="text-[0.85rem] text-slate-600 group-hover:text-slate-900 transition-colors py-0.5">
                  {type.label}
                </span>
              </div>
            {/each}
          </div>
        </div>

        <div class="p-4 bg-blue-50/50 rounded-lg border border-blue-100 flex gap-3 text-blue-800">
          <AppIcon name="info" size={18} class="shrink-0 mt-0.5" />
          <p class="text-[0.8rem] leading-relaxed">
            Les événements existants dans l'année cible avec le même titre et la même date seront ignorés pour éviter les doublons.
          </p>
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleReplicate} 
          disabled={isProcessing}
          class="flex-1 bg-primary text-white h-9 shadow-fine hover:bg-primary/90 transition-all font-medium gap-2"
        >
          {#if isProcessing}
            <div class="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            En cours...
          {:else}
            <AppIcon name="check" size={18} />
            Répliquer
          {/if}
        </Button>
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium">
            Annuler
          </Button>
        </Sheet.Close>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>

<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
