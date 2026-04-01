<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Candidate } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";

  let {
    open = $bindable(false),
    candidate = null
  } = $props<{
    open: boolean,
    candidate: Candidate | null
  }>();

  // Form state
  let technicalScore = $state(0);
  let experienceScore = $state(0);
  let communicationScore = $state(0);
  let cultureScore = $state(0);
  let notes = $state('');

  $effect(() => {
    if (open && candidate) {
      technicalScore = candidate.technicalScore || 0;
      experienceScore = candidate.experienceScore || 0;
      communicationScore = candidate.communicationScore || 0;
      cultureScore = candidate.cultureScore || 0;
      notes = candidate.notes || '';
    }
  });

  async function handleSave() {
    if (!candidate) return;

    try {
      await recruitmentStore.updateCandidate(candidate.id, {
        technicalScore,
        experienceScore,
        communicationScore,
        cultureScore,
        notes
      });

      notification.toast.success('Évaluation mise à jour');
      open = false;
    } catch (error) {
      notification.toast.error("Erreur lors de l'enregistrement");
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
          <AppIcon name="star" size={20} />
        </div>
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] font-bold text-slate-900 truncate">
            Évaluer le candidat
          </Sheet.Title>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-8" in:fade={{ duration: 200 }}>
        
        <div class="space-y-6">          
          <div class="grid grid-cols-2 gap-6">
            <div class="space-y-2.5">
              <Label class="text-slate-900">Technique</Label>
              <Input type="number" min="0" max="100" bind:value={technicalScore} class="h-10 border-slate-200 shadow-fine" />
            </div>
            <div class="space-y-2.5">
              <Label class="text-slate-900">Expérience</Label>
              <Input type="number" min="0" max="100" bind:value={experienceScore} class="h-10 border-slate-200 shadow-fine" />
            </div>
            <div class="space-y-2.5">
              <Label class="text-slate-900">Communication</Label>
              <Input type="number" min="0" max="100" bind:value={communicationScore} class="h-10 border-slate-200 shadow-fine" />
            </div>
            <div class="space-y-2.5">
              <Label class="text-slate-900">Culture</Label>
              <Input type="number" min="0" max="100" bind:value={cultureScore} class="h-10 border-slate-200 shadow-fine" />
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Notes d'évaluation</Label>
            <Textarea 
              bind:value={notes} 
              placeholder="Points forts, points faibles..." 
              class="min-h-32 border-slate-200 shadow-fine text-[0.85rem]"
            />
          </div>
        </div>

      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-amber-600 text-white h-9 shadow-fine shadow-amber-600/20 hover:bg-amber-700 transition-all"
        >
          <AppIcon name="check" size={18} />
          Enregistrer
        </Button>
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600">
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

