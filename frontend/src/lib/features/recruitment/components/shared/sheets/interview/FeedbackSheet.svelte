<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger
  } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Interview, InterviewStatus } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";
  import { cn } from "@/utilities/common/css";

  let {
    open = $bindable(false),
    interview = null
  } = $props<{
    open: boolean,
    interview: Interview | null
  }>();

  // Form state
  let feedbackText = $state('');
  let nextSteps = $state('');
  let rating = $state(0);
  let status = $state<InterviewStatus>('COMPLETED');

  $effect(() => {
    if (open && interview) {
      if (interview.feedback) {
        feedbackText = interview.feedback.feedback || interview.feedback.notes || '';
        rating = interview.feedback.rating || 0;
        nextSteps = interview.feedback.nextSteps || interview.nextSteps || '';
      } else {
        feedbackText = '';
        rating = 0;
        nextSteps = interview.nextSteps || '';
      }
      status = interview.status;
    }
  });

  async function handleSave() {
    if (!interview) return;

    try {
      await recruitmentStore.updateInterview(interview.id, {
        status,
        nextSteps,
        feedback: {
          rating,
          feedback: feedbackText,
          notes: feedbackText,
          nextSteps,
          strengths: interview.feedback?.strengths || [],
          weaknesses: interview.feedback?.weaknesses || [],
          wouldHire: interview.feedback?.wouldHire ?? true
        }
      });

      notification.toast.success('Feedback enregistré avec succès');
      open = false;
    } catch (error) {
      notification.toast.error("Erreur lors de l'enregistrement");
    }
  }

  function setRating(val: number) {
    rating = val;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center shrink-0">
          <AppIcon name="message-square" size={20} />
        </div>
        <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
          Feedback d'entretien
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-8" in:fade={{ duration: 200 }}>
        
        <!-- Statut & Note -->
        <div class="grid grid-cols-2 gap-6">
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-bold">Statut</Label>
            <Select type="single" value={status} onValueChange={(v) => status = v as any}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
                <span class="truncate text-[0.85rem] font-medium">{status === 'COMPLETED' ? 'Terminé' : 'Absent'}</span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="COMPLETED" class="text-[0.85rem]">Terminé</SelectItem>
                <SelectItem value="NO_SHOW" class="text-[0.85rem]">Absent</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-2.5">
            <Label class="text-slate-900 font-bold">Note globale</Label>
            <div class="flex items-center gap-1.5 h-10">
              {#each Array.from({length: 5}) as _, i}
                <button 
                  type="button"
                  onclick={() => setRating(i + 1)}
                  class="transition-all hover:scale-110"
                >
                  <AppIcon 
                    name="star" 
                    size={22} 
                    class={cn(
                      "transition-colors",
                      (i < rating) ? "text-amber-400 fill-amber-400" : "text-slate-200"
                    )} 
                  />
                </button>
              {/each}
            </div>
          </div>
        </div>

        <!-- Feedback Text -->
        <div class="space-y-4">
          <h4 class="text-[0.7rem] font-black text-slate-400 uppercase tracking-widest border-b pb-2">Évaluation qualitative</h4>
          
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-bold">Notes de l'entretien</Label>
            <Textarea 
              bind:value={feedbackText} 
              placeholder="Qu'avez-vous pensé du candidat ? Points techniques, soft skills..." 
              class="min-h-32 border-slate-200 shadow-fine text-[0.85rem]"
            />
          </div>

          <div class="space-y-2.5">
            <Label class="text-slate-900 font-bold">Prochaines étapes conseillées</Label>
            <Textarea 
              bind:value={nextSteps} 
              placeholder="ex: Recommander pour un entretien technique, Envoyer un test..." 
              class="min-h-20 border-slate-200 shadow-fine text-[0.85rem]"
            />
          </div>
        </div>

      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-purple-600 text-white h-9 shadow-lg shadow-purple-600/20 hover:bg-purple-700 transition-all"
        >
          <AppIcon name="check" size={18} />
          Enregistrer le retour
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
