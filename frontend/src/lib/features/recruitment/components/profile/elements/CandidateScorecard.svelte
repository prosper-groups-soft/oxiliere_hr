<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Progress } from "@/components/ui/progress";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/utilities/common/css";
  import type { CandidateApplication, EvaluationCriterion } from "../../../types/types";

  
  let { 
    application = null,
    evaluationTemplate = null,
    onEdit = null
  } = $props<{ 
    application: CandidateApplication | null,
    evaluationTemplate?: EvaluationCriterion[] | null,
    onEdit?: (() => void) | null
  }>();

  // Build a lookup map from template: criterionName -> { weight, source }
  const templateMap = $derived.by(() => {
    const map: Record<string, { weight: number; source: 'requirement' | 'skill' }> = {};
    (evaluationTemplate || []).forEach((c: EvaluationCriterion) => {
      map[c.name] = { weight: c.weight, source: c.source };
    });
    return map;
  });

  // Iterate over ACTUAL saved scores (not template), enrich with template metadata
  const evaluationCriteria = $derived.by(() => {
    const saved = (application?.scores || {}) as Record<string, number>;
    return (Object.entries(saved) as [string, number][])
      .filter(([, score]) => score > 0) // only show criteria with actual scores
      .map(([name, score]) => {
        const tpl = templateMap[name] || { weight: 0, source: 'requirement' as const };
        return {
          name,
          weight: tpl.weight,
          score,
          source: tpl.source,
        };
      });
  });

  // Calculate weighted average
  const overallScore = $derived.by(() => {
    if (evaluationCriteria.length === 0) return 0;
    const totalWeight = evaluationCriteria.reduce((sum: number, c) => sum + c.weight, 0);
    if (totalWeight === 0) return 0;
    const weightedSum = evaluationCriteria.reduce((sum: number, c) => sum + (c.score * c.weight), 0);
    return Math.round(weightedSum / totalWeight);
  });

  // Get score color
  function getScoreColor(score: number): string {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 60) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  }

  function getScoreLabel(score: number): string {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Bon';
    if (score >= 40) return 'Moyen';
    return 'À améliorer';
  }

  // Has any actual evaluation been submitted?
  const hasEvaluation = $derived(
    evaluationTemplate != null 
    && evaluationTemplate.length > 0 
    && application?.scores != null 
    && Object.keys(application.scores).length > 0
  );

  // Has evaluation criteria been configured (even if no scores yet)?
  const hasTemplate = $derived(
    evaluationTemplate != null && evaluationTemplate.length > 0
  );

</script>

{#if application}
  <div class="space-y-4">
    {#if hasEvaluation}
      <!-- Overall Score -->
      <div class="text-center p-4 bg-slate-50 rounded-lg">
        <div class="text-xl font-bold text-slate-900 mb-1">
          {overallScore}/100
        </div>
        <Badge variant="outline" class={cn(
          "text-xs font-medium border-none",
          getScoreColor(overallScore)
        )}>
          {getScoreLabel(overallScore)}
        </Badge>
      </div>

      <Separator />

      <!-- Detailed Scores -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-medium text-slate-700">Évaluation détaillée</h4>
          {#if onEdit}
            <button 
              onclick={() => onEdit()} 
              class="text-[0.8rem] text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1 cursor-pointer bg-transparent border-none"
            >
              <AppIcon name="edit" size={14} />
              Modifier
            </button>
          {/if}
        </div>
        
        {#each evaluationCriteria as criterion}
          <div class="space-y-2 mb-6">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-slate-900">{criterion.name}</span>
                  <span class="text-sm text-slate-600">{criterion.score}/100</span>
                </div>
                <span class="text-[0.7rem] px-1 py-0 rounded font-medium {criterion.source === 'requirement' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}">{criterion.source === 'requirement' ? 'req' : 'skill'}</span>
              </div>
            </div>
            
            <div class="space-y-1">
              <div class="relative">
                <Progress 
                  value={criterion.score} 
                  max={100} 
                  class="h-2 rounded-full"
                />
                <div 
                  class="absolute top-0 left-0 h-full rounded-l-full pointer-events-none transition-all duration-300"
                  class:bg-emerald-500={criterion.score >= 80}
                  class:bg-amber-500={criterion.score >= 60 && criterion.score < 80}
                  class:bg-red-500={criterion.score < 60}
                  style="width: {criterion.score}%"
                ></div>
              </div>
              <div class="flex items-center justify-between text-slate-500">
                <span class="text-[0.81rem]">Poids: {criterion.weight}%</span>
                <span class="text-[0.81rem]">Contribution: {Math.round(criterion.score * criterion.weight / 100)} pts</span>
              </div>
            </div>
          </div>
        {/each}
      </div>

      <!-- Evaluation Notes -->
      {#if application?.evaluationNotes}
        <Separator />
        <div class="space-y-3">
          <h4 class="text-sm font-medium text-slate-700">Notes d'évaluation</h4>
          <div class="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
            {application.evaluationNotes}
          </div>
        </div>
      {/if}
    {:else if hasTemplate}
      <div class="text-center py-6">
        <p class="text-sm text-slate-400 mb-2">Ce candidat n'a pas encore été évalué</p>
        {#if onEdit}
          <button 
            onclick={() => onEdit()} 
            class="text-[0.8rem] text-indigo-600 hover:text-indigo-700 font-medium cursor-pointer bg-transparent border-none"
          >
            Commencer l'évaluation
          </button>
        {/if}
      </div>
    {:else}
      <div class="text-center py-6">
        <p class="text-sm text-slate-400">Aucun critère d'évaluation configuré</p>
      </div>
    {/if}
  </div>
{/if}

