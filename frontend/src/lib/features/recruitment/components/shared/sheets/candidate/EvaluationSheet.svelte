<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { useUpdateApplicationEvaluationMutation } from "@/features/recruitment/queries/recruitmentQueries";
  import type { CandidateApplication, EvaluationCriterion } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";

  let {
    open = $bindable(false),
    application = null,
    evaluationTemplate = null,
    onsaved = null
  } = $props<{
    open: boolean,
    application: CandidateApplication | null,
    evaluationTemplate?: EvaluationCriterion[] | null,
    onsaved?: (() => void) | null
  }>();

  const updateEvaluationMutation = useUpdateApplicationEvaluationMutation();

  // Dynamic scores: {criterionName: scoreValue}
  let scores = $state<Record<string, number>>({});
  let evaluationNotes = $state('');
  let isSaving = $state(false);

  $effect(() => {
    if (open && application) {
      // Build the full scores object locally first, then assign once
      const newScores: Record<string, number> = { ...(application.scores || {}) };
      // Ensure all template criteria have entries
      (evaluationTemplate || []).forEach((c: EvaluationCriterion) => {
        if (!(c.name in newScores)) {
          newScores[c.name] = 0;
        }
      });
      scores = newScores;
      evaluationNotes = application.evaluationNotes || '';
    }
  });

  async function handleSave() {
    if (!application) return;

    isSaving = true;
    try {
      await $updateEvaluationMutation.mutateAsync({
        applicationId: application.applicationId,
        data: {
          scores,
          evaluationNotes
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

  const criteria = $derived(evaluationTemplate || []);
  const activeCriteria = $derived(criteria.filter((c: EvaluationCriterion) => c.weight > 0));
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[0.99rem] font-bold text-slate-900 truncate">
            Évaluer le candidat
          </Sheet.Title>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-8" in:fade={{ duration: 200 }}>
        
        {#if activeCriteria.length > 0}
          <div class="space-y-5">
            <p class="text-[0.8rem] font-medium text-slate-500 uppercase tracking-wider">Critères</p>
            {#each activeCriteria as criterion (criterion.name)}
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <Label class="text-slate-900 text-[0.85rem]">{criterion.name}</Label>
                  <span class="text-[0.72rem] px-1.5 py-0.5 rounded font-medium {criterion.source === 'requirement' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}">
                    {criterion.source === 'requirement' ? 'requirement' : 'skill'}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <Input 
                    type="number" 
                    min="0" 
                    max="100"
                    value={scores[criterion.name] ?? 0}
                    oninput={(e) => scores[criterion.name] = parseInt((e.target as HTMLInputElement).value) || 0}
                    class="h-10 border-slate-200 shadow-fine w-20" 
                  />
                  <span class="text-[0.83rem] text-slate-400">/100 (Poids: {criterion.weight}%)</span>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="text-center py-8">
            <AppIcon name="star" size={40} class="text-slate-200 mx-auto mb-3" />
            <p class="text-[0.85rem] text-slate-400">Aucun critère d'évaluation défini pour ce poste.</p>
            <p class="text-[0.82rem] text-slate-400 mt-1">Configurez les critères dans la campagne.</p>
          </div>
        {/if}

        <div class="space-y-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Notes d'évaluation</Label>
            <Textarea 
              bind:value={evaluationNotes} 
              placeholder="Points forts, points faibles..." 
              class="min-h-32 border-slate-200 shadow-fine text-[0.85rem]"
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
          class="flex-1 bg-indigo-600 text-white h-9 shadow-fine shadow-indigo-600/20 hover:bg-indigo-700 transition-all disabled:opacity-70"
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



