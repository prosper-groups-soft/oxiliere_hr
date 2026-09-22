<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { cn } from "@/hr/utilities/common/css";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { format, differenceInDays } from 'date-fns';
  import { fr } from 'date-fns/locale';
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import type { PipelineApplicationItem, CandidateStage, CandidateApplication } from "../../../types/types";
  import { STAGE_CONFIG, CANDIDATE_PRIORITY_CONFIG, CANDIDATE_SOURCE_CONFIG, CANDIDATE_GENDER_LABELS } from "../../../constants/recruitment";
  import { recruitmentStore } from "../../../stores/recruitment.svelte";
  import TooltipWrapper from "@/hr/components/shared/containers/TooltipWrapper.svelte";

  
  let { 
    item,
    onEdit,
    onDelete,
    onScheduleInterview,
    onViewProfile,
    onUpdateStage,
    onFeedback,
    onEvaluate,
    dragDisabled = false 
  } = $props<{
    item: PipelineApplicationItem;
    onEdit?: (item: PipelineApplicationItem) => void;
    onDelete?: (item: PipelineApplicationItem) => void;
    onScheduleInterview?: (item: PipelineApplicationItem) => void;
    onViewProfile?: (item: PipelineApplicationItem) => void;
    onUpdateStage?: (item: PipelineApplicationItem, stage: string) => void;
    onFeedback?: (item: PipelineApplicationItem) => void;
    onEvaluate?: (item: PipelineApplicationItem) => void;
    dragDisabled?: boolean;
  }>();

  const candidate = $derived(item.candidate);
  const app = $derived(item.application);

  const palette = $derived(getAvatarPalette(`${candidate.firstName} ${candidate.lastName}`));
  const stCfg = $derived(STAGE_CONFIG[app.currentStage] ?? STAGE_CONFIG.SCREENING);
  const priCfg = $derived(CANDIDATE_PRIORITY_CONFIG[app.priority] ?? CANDIDATE_PRIORITY_CONFIG['MEDIUM']);
  const srcCfg = $derived(CANDIDATE_SOURCE_CONFIG[candidate.source] ?? CANDIDATE_SOURCE_CONFIG['DIRECT']);
  
  const daysInStage = $derived(
    differenceInDays(new Date(), new Date(app.lastStageChange))
  );

  // Afficher le salaire si OFFER ou ACCEPTED
  const showSalary = $derived(app.currentStage === 'OFFER' || app.currentStage === 'ACCEPTED');
  const salaryRange = $derived.by(() => {
    if (!app.salaryMin || !app.salaryMax) return null;
    const formatSalary = (val: number) => val.toLocaleString('fr-FR');
    return `${formatSalary(app.salaryMin)} - ${formatSalary(app.salaryMax)}`;
  });

  // Score pondéré (comme dans CandidateRow)
  function computeWeightedScore(app: CandidateApplication): { score: number; totalScore: number; maxScore: number } | null {
    if (!app.scores || Object.keys(app.scores).length === 0) return null;
    const campaign = recruitmentStore.currentCampaign;
    const template = (campaign?.evaluationTemplate?.[app.positionId ?? ''] ?? []) as { name: string; weight: number }[];
    let totalWeighted = 0;
    let totalWeight = 0;
    if (template.length > 0) {
      for (const criterion of template) {
        const note = app.scores[criterion.name];
        if (note != null) {
          totalWeighted += note * criterion.weight;
          totalWeight += criterion.weight;
        }
      }
    } else {
      const values = Object.values(app.scores).filter(v => v != null) as number[];
      if (values.length === 0) return null;
      return {
        score: Math.round(values.reduce((a, b) => a + b, 0) / values.length),
        totalScore: Math.round(values.reduce((a, b) => a + b, 0)),
        maxScore: values.length * 100
      };
    }
    if (totalWeight === 0) return null;
    return {
      score: Math.round(totalWeighted / totalWeight),
      totalScore: Math.round(totalWeighted),
      maxScore: totalWeight * 100
    };
  }

  const weightInfo = $derived(computeWeightedScore(app));

  function handleStageChange(newStage: string) {
    onUpdateStage?.(item, newStage);
  }

  // Ordre des étapes pour calculer l'étape suivante
  const STAGE_ORDER: CandidateStage[] = ['SCREENING', 'SHORTLIST', 'INTERVIEW', 'OFFER', 'ACCEPTED'];

  const nextStage = $derived.by(() => {
    const idx = STAGE_ORDER.indexOf(app.currentStage as CandidateStage);
    return idx >= 0 && idx < STAGE_ORDER.length - 1 ? STAGE_ORDER[idx + 1] : null;
  });

  const nextStageLabel = $derived.by(() => {
    if (!nextStage) return '';
    return STAGE_CONFIG[nextStage]?.label ?? nextStage;
  });

  const isTerminal = $derived(app.currentStage === 'ACCEPTED');
  const isScreening = $derived(app.currentStage === 'SCREENING');
  const isOfferStage = $derived(app.currentStage === 'OFFER');

  // Visibilité des actions selon le stage
  const canAdvance = $derived(nextStage !== null && !isTerminal);
  const canScheduleInterview = $derived(
    app.currentStage === 'SHORTLIST' || app.currentStage === 'INTERVIEW'
  );
  const canGiveFeedback = $derived(app.currentStage === 'INTERVIEW');
  const canEvaluate = $derived(
    (app.currentStage === 'INTERVIEW' || app.currentStage === 'OFFER')
  );
  const canReject = $derived(
    app.currentStage === 'SHORTLIST' || app.currentStage === 'INTERVIEW' || app.currentStage === 'OFFER'
  );
</script>


<div 
  in:fly={{ y: 10, duration: 300, easing: cubicOut }}
  class={cn(
    "group/card bg-white border border-slate-200 rounded-lg p-3 pt-1.5 shadow-none hover:shadow-fine transition-all duration-200 relative gap-1.5",
    dragDisabled ? "cursor-default" : "cursor-grab active:cursor-grabbing"
  )}
  onclick={() => onViewProfile?.(item)}
  role="none"
>
  <div class="flex flex-col items-start justify-between">
    <div 
      class="flex items-center justify-end w-full" 
      onclick={(e) => e.stopPropagation()} 
      onpointerdown={(e) => e.stopPropagation()} 
      role="none"
    >
      {#if isScreening}
        {@render ScreeningAdvance()}
      {:else}
        {@render Actions()}
      {/if}
    </div>
    <div class="flex items-center gap-1.5 min-w-0">
      <Avatar class="h-10 w-10 shrink-0 border">
        <AvatarImage src={getMediaUrl(candidate.avatarUrl)} alt={`${candidate.lastName} ${candidate.middleName} ${candidate.firstName}`} />
        <AvatarFallback class={cn("text-sm font-medium", palette.bg, palette.text)}>
          {getInitials(`${candidate.lastName} ${candidate.middleName} ${candidate.firstName}`)}
        </AvatarFallback>
      </Avatar>
      
      <div class="min-w-0">
        <TooltipWrapper content={`${candidate.lastName} ${candidate.middleName} ${candidate.firstName}`} side="top" asChild={true}>
          <h3
            class="font-semibold text-[0.85rem] text-slate-900 truncate group-hover/card:text-blue-600 transition-colors"
          >
            {candidate.lastName} {candidate.middleName} {candidate.firstName}
          </h3>
        </TooltipWrapper>
        <div class="flex items-center gap-1.5 mt-0.5">
          {#if app.targetPositionName}
            <span class="text-[0.78rem] text-slate-600 font-medium truncate max-w-35">
              {app.targetPositionName}
            </span>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <!-- Infos : genre + score -->
  <div class="flex items-center justify-between gap-3 mb-2 text-[0.8rem] text-slate-500">
    <div class="flex items-center gap-1">
      <AppIcon name="users" size={15} class="text-slate-400" />
      <span class="text-[0.8rem]">{CANDIDATE_GENDER_LABELS[candidate.gender] || 'Non spécifié'}</span>
    </div>

    {#if weightInfo}
      <div class="flex items-center gap-2">
        <div class="h-1.5 w-16 bg-slate-100 rounded-full overflow-hidden">
          <div
            class={cn(
              "h-full rounded-full transition-all",
              weightInfo.score >= 80 ? "bg-emerald-500" :
              weightInfo.score >= 50 ? "bg-amber-500" :
              "bg-red-500"
            )}
            style={`width: ${Math.min(weightInfo.score, 100)}%`}
          ></div>
        </div>
        <span class="font-bold text-slate-600 text-[0.8rem]">{weightInfo.score}/100</span>
      </div>
    {:else}
      <span class="text-slate-300 text-[0.8rem]">Pas de score</span>
    {/if}
  </div>

  <div class="flex items-center gap-2 mb-2">
    <Badge variant="outline" class={cn("w-fit h-5 px-2 text-[0.62rem] font-bold uppercase tracking-widest border-none", stCfg.color)}>
      <AppIcon name={stCfg.icon} size={14} class="mr-1" />
      {stCfg.label}
    </Badge>
    
    <Badge variant="outline" class={cn("w-fit h-5 px-2 text-[0.62rem] font-bold uppercase tracking-widest border-none", priCfg.color)}>
      {priCfg.label}
    </Badge>

    <div class="flex items-center gap-1 ml-auto">
      <AppIcon name={srcCfg.icon} size={15} class="text-slate-400" />
      <span class="text-[0.775rem] text-slate-500">{srcCfg.label}</span>
    </div>
  </div>

  {#if showSalary && salaryRange}
    <div class="mb-2 p-2 bg-linear-to-r from-emerald-50 to-green-50 rounded border border-emerald-100">
      <div class="flex items-center justify-between">
        <span class="text-[0.82rem] font-semibold text-emerald-900">Salaire proposé</span>
        <span class="text-[0.8rem] font-bold text-emerald-700">{salaryRange} {app.salaryCurrency || ''}</span>
      </div>
      {#if app.offerStartDate}
        <span class="text-[0.7rem] text-emerald-600 block mt-1">
          Démarrage: {format(new Date(app.offerStartDate), 'dd MMM yyyy', { locale: fr })}
        </span>
      {/if}
    </div>
  {/if}

  <div class="flex items-center justify-between mt-auto">
    <span class="text-[0.8rem] text-slate-700">
      Candidature: {format(new Date(app.appliedDate), 'dd MMM', { locale: fr })}
    </span>
    <div class="flex items-center gap-1">
      <AppIcon name="clock" size={15} class="text-slate-400" />
      <span class="text-[0.76rem] text-slate-700">
        {daysInStage} {daysInStage <= 1 ? 'jour' : 'jours'}
      </span>
    </div>
  </div>
</div>


{#snippet Actions()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger asChild>
      {#snippet child({ props })}
        <button 
          {...props}
          class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-600 hover:text-slate-600 cursor-pointer"              
        >
          <AppIcon name="more-horizontal" size={17} />
        </button>
      {/snippet}
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="p-2 rounded-lg shadow-fine bg-white border-slate-100 z-1100">
      <!-- Actions de progression -->
      {#if canAdvance}
        <DropdownMenu.Group>
          {#if isOfferStage}
            <DropdownMenu.Item 
              onclick={() => handleStageChange('ACCEPTED')}
              class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]! text-emerald-600 hover:text-emerald-700! hover:bg-emerald-50!"
            >
              <AppIcon name="check" size={17} class="text-emerald-600" />
              Accepter l'offre
            </DropdownMenu.Item>
          {:else}
            <DropdownMenu.Item 
              onclick={() => nextStage && handleStageChange(nextStage)}
              class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!"
            >
              <AppIcon name="arrow-right" size={17} class="text-blue-600" />
              Avancer vers {nextStageLabel}
            </DropdownMenu.Item>
          {/if}
        </DropdownMenu.Group>

        <DropdownMenu.Separator class="my-2 bg-slate-50" />
      {/if}

      <!-- Actions contextuelles -->
      <DropdownMenu.Group>
        {#if canScheduleInterview}
          <DropdownMenu.Item 
            onclick={() => onScheduleInterview?.(item)}
            class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!"
          >
            <AppIcon name="calendar" size={17} class="text-slate-500" />
            Programmer entretien
          </DropdownMenu.Item>
        {/if}
        {#if canEvaluate}
          <DropdownMenu.Item 
            onclick={() => onEvaluate?.(item)}
            class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!"
          >
            <AppIcon name="edit" size={17} class="text-slate-500" />
            Évaluer
          </DropdownMenu.Item>
        {/if}
        <DropdownMenu.Item onclick={() => onEdit?.(item)} class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!">
          <AppIcon name="user" size={17} class="text-slate-500" />
          Modifier le candidat
        </DropdownMenu.Item>
      </DropdownMenu.Group>

      <!-- Actions destructives -->
      {#if canReject}
        <DropdownMenu.Separator class="my-2 bg-slate-50" />

        <DropdownMenu.Group>
          <DropdownMenu.Item 
            onclick={() => handleStageChange('REJECTED')}
            class="text-red-600 hover:text-red-700! hover:bg-red-50! cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!"
          >
            <AppIcon name="x" size={17} class="text-red-600" />
            Rejeter
          </DropdownMenu.Item>
        </DropdownMenu.Group>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet ScreeningAdvance()}
  <button 
    onclick={() => nextStage && handleStageChange(nextStage)}
    class="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[0.77rem]! font-medium
           bg-blue-50 text-blue-600 border border-blue-200
           hover:bg-blue-100 hover:text-blue-700 hover:border-blue-300
           transition-all duration-150 cursor-pointer"
  >
    <AppIcon name="arrow-right" size={14} class="text-blue-500" />
    Shortlist
  </button>
{/snippet}


