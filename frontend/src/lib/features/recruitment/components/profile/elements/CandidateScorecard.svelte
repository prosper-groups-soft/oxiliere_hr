<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import { Progress } from "@/components/ui/progress";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/utilities/common/css";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import type { Candidate } from "../../../types/types";

  let { 
    candidate = null,
    onEditScores = null
  } = $props<{ 
    candidate: Candidate | null,
    onEditScores?: () => void
  }>();

  // Mock evaluation criteria - in real app, this would come from a job posting or evaluation template
  const evaluationCriteria = $derived([
    { 
      id: 'technical', 
      name: 'Compétences techniques', 
      weight: 40, 
      score: candidate?.technicalScore || 0,
      description: 'Connaissances techniques, langages, frameworks'
    },
    { 
      id: 'experience', 
      name: 'Expérience pertinente', 
      weight: 25, 
      score: candidate?.experienceScore || 0,
      description: 'Années d\'expérience, projets pertinents'
    },
    { 
      id: 'communication', 
      name: 'Communication', 
      weight: 20, 
      score: candidate?.communicationScore || 0,
      description: 'Clarté, écoute, expression orale'
    },
    { 
      id: 'culture', 
      name: 'Culture d\'entreprise', 
      weight: 15, 
      score: candidate?.cultureScore || 0,
      description: 'Adéquation avec les valeurs de l\'entreprise'
    }
  ]);

  // Calculate weighted average
  const overallScore = $derived.by(() => {
    if (!candidate) return 0;
    
    const totalWeight = evaluationCriteria.reduce((sum, criterion) => sum + criterion.weight, 0);
    const weightedSum = evaluationCriteria.reduce((sum, criterion) => {
      return sum + (criterion.score * criterion.weight);
    }, 0);
    
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

  function handleEditScores() {
    onEditScores?.();
  }

  function handleGenerateReport() {
    console.log('Generate evaluation report for candidate:', candidate?.id);
    // TODO: Generate and download PDF report
  }
</script>


{#if candidate}
  <div class="space-y-4">
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
      <h4 class="text-sm font-medium text-slate-700">Évaluation détaillée</h4>
      
      {#each evaluationCriteria as criterion}
        <div class="space-y-2 mb-6">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-slate-900">{criterion.name}</span>
                <span class="text-sm text-slate-600">{criterion.score}/100</span>
              </div>
              <p class="text-[0.81rem] text-slate-500 mt-1">{criterion.description}</p>
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

    <Separator />

    <!-- Skills Assessment -->
    <div class="space-y-3">
      <h4 class="text-sm font-medium text-slate-700">Compétences évaluées</h4>
      <div class="flex flex-wrap gap-2">
        {#each candidate.skills || [] as skill}
          <Badge variant="secondary" class="text-xs">
            {skill}
          </Badge>
        {/each}
        {#if !candidate.skills || candidate.skills.length === 0}
          <span class="text-sm text-slate-400">Aucune compétence évaluée</span>
        {/if}
      </div>
    </div>

    <!-- Notes -->
    {#if candidate.notes}
      <div class="space-y-3">
        <h4 class="text-sm font-medium text-slate-700">Notes d'évaluation</h4>
        <div class="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
          {candidate.notes}
        </div>
      </div>
    {/if}

    <!-- Actions -->
    <div class="flex gap-2 pt-2">
      <Button variant="outline" size="sm" onclick={handleEditScores} class="shadow-fine rounded-lg">
        <AppIcon name="edit" size={16} class="text-gray-500" />
        Modifier scores
      </Button>
      <Button variant="outline" size="sm" onclick={handleGenerateReport} class="shadow-fine rounded-lg">
        <AppIcon name="download" size={16} class="text-gray-500" />
        Générer rapport
      </Button>
    </div>
  </div>
{:else}
  <Empty 
    icon="star" 
    description="Aucune évaluation disponible" 
    class="py-4"
  />
{/if}

