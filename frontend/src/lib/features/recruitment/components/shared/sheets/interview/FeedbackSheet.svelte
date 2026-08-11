<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import { Input } from "@/components/ui/input";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { useSubmitInterviewFeedbackMutation } from "@/features/recruitment/queries/recruitmentQueries";
  import type { Interview, InterviewStatus } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";
  import { cn } from "@/utilities/common/css";

  let {
    open = $bindable(false),
    interview = null,
    onsaved = null
  } = $props<{
    open: boolean,
    interview: Interview | null,
    onsaved?: (() => void) | null
  }>();

  const submitFeedbackMutation = useSubmitInterviewFeedbackMutation();

  // Form state
  let feedbackText = $state('');
  let nextSteps = $state('');
  let rating = $state(0);
  let strengthsList = $state<string[]>([]);
  let weaknessesList = $state<string[]>([]);
  let wouldHire = $state<boolean | undefined>(undefined);
  let status = $state<InterviewStatus>('COMPLETED');
  let isSaving = $state(false);

  // Tag input for strengths/weaknesses
  let strengthInput = $state('');
  let weaknessInput = $state('');

  $effect(() => {
    if (open && interview) {
      if (interview.feedback) {
        feedbackText = interview.feedback.feedback || '';
        rating = interview.feedback.rating || 0;
        strengthsList = interview.feedback.strengths || [];
        weaknessesList = interview.feedback.weaknesses || [];
        wouldHire = interview.feedback.wouldHire ?? undefined;
        nextSteps = interview.feedback.nextSteps || interview.nextSteps || '';
      } else {
        feedbackText = '';
        rating = 0;
        strengthsList = [];
        weaknessesList = [];
        wouldHire = undefined;
        nextSteps = interview.nextSteps || '';
      }
      status = interview.status;
    }
  });

  async function handleSave() {
    if (!interview) return;

    isSaving = true;
    try {
      await $submitFeedbackMutation.mutateAsync({
        interviewId: interview.id,
        data: {
          score: rating,
          feedback: feedbackText || undefined,
          strengths: strengthsList.length > 0 ? strengthsList : undefined,
          weaknesses: weaknessesList.length > 0 ? weaknessesList : undefined,
          wouldHire: wouldHire ?? undefined,
          nextSteps: nextSteps || undefined,
          status
        }
      });

      onsaved?.();
      open = false;
    } catch (error) {
      console.error("Erreur lors de l'enregistrement:", error);
    } finally {
      isSaving = false;
    }
  }

  function setRating(val: number) {
    rating = val;
  }

  function addStrength() {
    const val = strengthInput.trim();
    if (val && !strengthsList.includes(val)) {
      strengthsList = [...strengthsList, val];
    }
    strengthInput = '';
  }

  function removeStrength(index: number) {
    strengthsList = strengthsList.filter((_, i) => i !== index);
  }

  function addWeakness() {
    const val = weaknessInput.trim();
    if (val && !weaknessesList.includes(val)) {
      weaknessesList = [...weaknessesList, val];
    }
    weaknessInput = '';
  }

  function removeWeakness(index: number) {
    weaknessesList = weaknessesList.filter((_, i) => i !== index);
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <Sheet.Title class="text-[0.98rem] font-bold text-slate-900 truncate">
          Feedback d'entretien
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 px-2 space-y-6" in:fade={{ duration: 200 }}>
        
        <!-- Statut & Note -->
        <div class="grid grid-cols-2 gap-6">
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-bold">Statut</Label>
            <Select type="single" value={status} onValueChange={(v) => status = v as any}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md cursor-pointer">
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
                  class="transition-all hover:scale-110 cursor-pointer"
                >
                  <AppIcon 
                    name="star" 
                    size={22} 
                    class={cn(
                      "transition-colors cursor-pointer",
                      (i < rating) ? "text-amber-400 fill-amber-400" : "text-slate-300"
                    )} 
                  />
                </button>
              {/each}
            </div>
          </div>
        </div>

        <!-- Feedback Sections -->
        <div class="space-y-4">
          <h4 class="text-[0.7rem] font-black text-slate-400 uppercase tracking-widest border-b pb-2">Évaluation qualitative</h4>

          <!-- Strengths (Points forts) -->
          <div class="space-y-2">
            <Label class="text-slate-900 font-bold">Points forts</Label>
            <div class="flex flex-wrap gap-1.5">
              {#each strengthsList as strength, i}
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.83rem] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                  {strength}
                  <button type="button" onclick={() => removeStrength(i)} class="hover:text-emerald-900 cursor-pointer">
                    <AppIcon name="x" size={15} />
                  </button>
                </span>
              {/each}
            </div>
            <div class="flex gap-1">
              <Input
                type="text"
                bind:value={strengthInput}
                onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addStrength())}
                placeholder="Ajouter un point fort..."
                class="flex-1 h-9.5 text-[0.875rem]"
              />
              <button type="button" onclick={addStrength} class="shrink-0 h-9.5 px-2 text-sm font-medium text-emerald-600 bg-emerald-50 border border-emerald-200 rounded-md hover:bg-emerald-100 cursor-pointer">
                <AppIcon name="plus" size={17} />
              </button>
            </div>
          </div>

          <!-- Weaknesses (Axes d'amélioration) -->
          <div class="space-y-2">
            <Label class="text-slate-900 font-bold">Axes d'amélioration</Label>
            <div class="flex flex-wrap gap-1.5">
              {#each weaknessesList as weakness, i}
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.83rem] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                  {weakness}
                  <button type="button" onclick={() => removeWeakness(i)} class="hover:text-amber-900 cursor-pointer">
                    <AppIcon name="x" size={15} />
                  </button>
                </span>
              {/each}
            </div>
            <div class="flex gap-1">
              <Input
                type="text"
                bind:value={weaknessInput}
                onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addWeakness())}
                placeholder="Ajouter un axe d'amélioration..."
                class="flex-1 h-9.5 text-[0.875rem]"
              />
              <button type="button" onclick={addWeakness} class="shrink-0 h-9.5 px-2 text-sm font-medium text-amber-600 bg-amber-50 border border-amber-200 rounded-md hover:bg-amber-100 cursor-pointer">
                <AppIcon name="plus" size={17} />
              </button>
            </div>
          </div>

          <!-- Would Hire -->
          <div class="space-y-2">
            <Label class="text-slate-900 font-bold">Recommandation</Label>
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="wouldHire" checked={wouldHire === true} onchange={() => wouldHire = true} class="cursor-pointer" />
                <span class="text-[0.85rem] text-emerald-700 font-medium">À embaucher</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="wouldHire" checked={wouldHire === false} onchange={() => wouldHire = false} class="cursor-pointer" />
                <span class="text-[0.85rem] text-red-600 font-medium">Ne pas embaucher</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="wouldHire" checked={wouldHire === undefined} onchange={() => wouldHire = undefined} class="cursor-pointer" />
                <span class="text-[0.85rem] text-slate-400">Non spécifié</span>
              </label>
            </div>
          </div>

          <!-- Feedback Text -->
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-bold">Notes de l'entretien</Label>
            <Textarea 
              bind:value={feedbackText} 
              placeholder="Qu'avez-vous pensé du candidat ? Points techniques, soft skills..." 
              class="min-h-24 border-slate-200 shadow-fine text-[0.85rem]"
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
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600">
            <AppIcon name="x" size={18} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={handleSave} 
          disabled={isSaving}
          class="flex-1 bg-indigo-700 text-white h-9 shadow-none hover:bg-indigo-800 transition-all disabled:opacity-70"
        >
          {#if isSaving}
            <AnimateSpin text="" class="size-3 border-white" />
          {:else}
            <AppIcon name="check" size={18} />
          {/if}
          Enregistrer
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


