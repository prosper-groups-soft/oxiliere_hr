<script lang="ts">
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { format } from 'date-fns';
  import { fr } from 'date-fns/locale';
  import { cn } from '@/hr/utilities/common/css';
  import type { Candidate, CandidateApplication } from '../../../../types/types';
  import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import { getInitials } from '@/hr/utilities/common/string';
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { fade } from "svelte/transition";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { useUploadCandidatePhotoMutation } from '@/hr/modules/recruitment/queries/recruitmentQueries';
  import { CANDIDATE_SOURCE_LABELS, CANDIDATE_PRIORITY_LABELS, STAGE_CONFIG, CANDIDATE_GENDER_LABELS } from '@/hr/modules/recruitment/constants/recruitment';
import { recruitmentStore } from '@/hr/modules/recruitment/stores/recruitment.svelte';


  let { 
    candidate,
    onScheduleInterview,
    onEdit,
    onDelete,
    onViewProfile
  } = $props<{
    candidate: Candidate;
    onScheduleInterview?: (candidate: Candidate) => void;
    onEdit?: (candidate: Candidate) => void;
    onDelete?: (candidate: Candidate) => void;
    onViewProfile?: (candidateId: string) => void;
  }>();
  

  const uploadPhotoMutation = useUploadCandidatePhotoMutation();

  // --- LOGIQUE DÉRIVÉE ---

  const fullName = $derived([candidate.lastName, candidate.middleName, candidate.firstName].filter(Boolean).join(' ') || '');

  const profilePhoto = $derived(getMediaUrl(candidate.avatarUrl));
  const palette = $derived(getAvatarPalette(fullName || ''));
  const summary = $derived(candidate.summary || candidate.notes || '');

  // Applications groupées
  const applications = $derived(candidate.applications || []);

  // Source
  const sourceLabel = $derived(CANDIDATE_SOURCE_LABELS[candidate.source] || candidate.source);

  // Helper pour calculer le score pondéré d'une candidature
  function computeWeightedScore(app: CandidateApplication): { score: number; totalScore: number; maxScore: number } | null {
    if (!app.scores || Object.keys(app.scores).length === 0) return null;
    const campaign = recruitmentStore.currentCampaign;
    const template = (campaign?.evaluationTemplate?.[app.positionId ?? ''] ?? []) as { name: string; weight: number }[];
    let totalWeighted = 0;
    let totalWeight = 0;
    if (template.length > 0) {
      // Pondéré : chaque critère note * weight / 100 (car note sur 100)
      for (const criterion of template) {
        const note = app.scores[criterion.name];
        if (note != null) {
          totalWeighted += note * criterion.weight;
          totalWeight += criterion.weight;
        }
      }
    } else {
      // Fallback : moyenne simple
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

  // Prio helpers
  function getPriorityLabel(p: string) {
    return CANDIDATE_PRIORITY_LABELS[p] || p;
  }
  function getPriorityColor(p: string) {
    return p === 'HIGH' ? 'text-rose-600' :
           p === 'MEDIUM' ? 'text-amber-600' :
           'text-slate-400';
  }

  // Skills (max 4)
  const displaySkills = $derived((candidate.skills || []).slice(0, 4));
  const remainingSkillsCount = $derived(Math.max(0, (candidate.skills?.length || 0) - 4));


  function handleViewCandidate(candidateId: string) {
    onViewProfile?.(candidateId);
  }

  function handleAvatarUpload(file: File) {
    $uploadPhotoMutation.mutate({ candidateId: candidate.id, file });
  }

</script>


<div 
  in:fade={{ duration: 300 }}
  role="link"
  tabindex="0"
  onclick={() => onEdit?.(candidate)}
  onkeydown={(e) => e.key === 'Enter' && onEdit?.(candidate)}
  class="group/row flex items-start py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
>
  <!-- Colonne 1: Avatar & Identité (21%) -->
  <div class="w-[21%] flex items-center gap-3 min-w-0 pt-0.5">
    <div role="none" onclick={(e) => e.stopPropagation()} class="shrink-0">
      <AvatarGallery
        name={fullName || ''}
        src={profilePhoto}
        onUpload={handleAvatarUpload}
        iconSize={16}
        iconStroke={2}
        class="h-10 w-10 rounded-full shadow-fine"
      >
        <Avatar class="h-full w-full border border-slate-200">
          <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
          <AvatarFallback class={cn("font-bold text-[0.85rem]", palette.bg, palette.text)}>
            {getInitials(candidate.lastName, candidate.middleName, candidate.firstName)}
          </AvatarFallback>
        </Avatar>
      </AvatarGallery>
    </div>
    <div class="flex flex-col min-w-0 flex-1">
      <span class="font-semibold text-[0.85rem] text-slate-800 truncate leading-tight group-hover/row:text-indigo-600 transition-colors">
        {fullName}
      </span>
      <div class="flex items-center gap-1 mt-0.5">
        <AppIcon name="mail" size={16} class="text-slate-400 shrink-0" />
        <span class="text-[0.85rem] text-slate-500 truncate">{candidate.email}</span>
      </div>
    </div>
  </div>

  <!-- Colonne 2: Source & Expérience (8%) -->
  <div class="w-[10%] flex flex-col justify-center gap-1 min-w-0 pt-1">
    <div class="flex items-center gap-1.5">
      <AppIcon 
        name={candidate.source === 'REFERRAL' ? 'user-plus' : 'globe'} 
        size={16} 
        class="text-slate-400 shrink-0" 
      />
      <span class="text-[0.84rem] text-slate-500 truncate">{sourceLabel}</span>
    </div>
    {#if candidate.experience}
      <div class="flex items-center gap-1.5">
        <AppIcon name="clock" size={16} class="text-slate-400 shrink-0" />
        <span class="text-[0.84rem] text-slate-500 truncate">{candidate.experience}</span>
      </div>
    {/if}
    <div class="flex items-center gap-1.5">
      <AppIcon name="users" size={16} class="text-slate-400 shrink-0" />
      <span class="text-[0.84rem] text-slate-500 truncate">{CANDIDATE_GENDER_LABELS[candidate.gender] || 'Non spécifié'}</span>
    </div>
  </div>

  <!-- Colonne 3: Applications (38%) - chaque poste avec stage + priorité + score -->
  <div class="w-[38%] flex flex-col justify-center gap-1.5 min-w-0 pr-2">
    {#each applications as app}
      {@const weightInfo = computeWeightedScore(app)}
      <div class="grid grid-cols-5 gap-2 py-0.5 items-center">
        <!-- Poste visé -->
        <div class="flex items-center gap-1.5 min-w-0 col-span-1">
          <AppIcon name="crosshair" size={14} class="text-primary shrink-0" />
          {#if app.targetPositionName}
            <span class="text-[0.84rem] font-semibold text-slate-700 truncate">
              {app.targetPositionName}
            </span>
          {:else}
            <span class="text-slate-300 italic text-[0.78rem]">Non défini</span>
          {/if}
        </div>

        <!-- Score -->
        <div class="flex items-center gap-1.5 min-w-0">
          {#if weightInfo}
            <div class="flex items-center gap-1.5">
              <div class="h-1.5 w-12 bg-slate-100 rounded-full overflow-hidden shrink-0">
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
              <span class="text-[0.82rem] font-bold text-slate-600 shrink-0">
                {weightInfo.score}/100
              </span>
            </div>
          {:else}
            <span class="text-[0.82rem] text-slate-300">Pas de score</span>
          {/if}
        </div>

        <!-- Stage -->
        <div class="flex items-center min-w-0">
          <Badge 
            variant="outline" 
            class={cn(
              "w-fit text-[0.82rem] px-1.5 py-0 border-0 shadow-none rounded-full font-semibold",
              (STAGE_CONFIG[app.currentStage]?.color) || 'bg-slate-50 text-slate-600'
            )}
          >
            {STAGE_CONFIG[app.currentStage]?.label || app.currentStage}
          </Badge>
        </div>

        <!-- Priorité -->
        <div class="flex items-center gap-1 min-w-0">
          <AppIcon name="flag" size={14} class={cn("shrink-0", getPriorityColor(app.priority))} />
          <span class="text-[0.82rem] text-slate-500 truncate">
            {getPriorityLabel(app.priority)}
          </span>
        </div>

        <!-- Date -->
        <div class="flex items-center justify-end min-w-0">
          {#if app.appliedDate}
            <span class="text-[0.82rem] text-slate-500 text-right">
              {format(new Date(app.appliedDate), 'dd MMM yyy', { locale: fr })}
            </span>
          {:else}
            <span class="text-[0.82rem] text-slate-300">—</span>
          {/if}
        </div>
      </div>
    {:else}
      <div class="text-sm text-slate-400 px-1 flex gap-1.5 justify-center items-center pt-1">
        <AppIcon name="circle-x" size={16} class="text-slate-300"/>
        Aucune candidature
      </div>
    {/each}
  </div>

  <!-- Colonne 4: Skills & Summary (14%) -->
  <div class="w-[14%] flex flex-col gap-1 min-w-0">
    {#if displaySkills.length > 0}
      <div class="flex flex-wrap gap-1">
        {#each displaySkills as skill}
          <span class="inline-flex items-center gap-2 px-1.5 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[0.8rem] leading-tight">
            <AppIcon name="tag" size={16} />
            {skill}
          </span>
        {/each}
        {#if remainingSkillsCount > 0}
          <span class="inline-flex items-center px-1.5 py-0.5 rounded-md bg-slate-50 text-slate-400 text-[0.8rem] leading-tight">
            +{remainingSkillsCount}
          </span>
        {/if}
      </div>
    {:else if summary}
      <p class="text-[0.84rem] text-slate-500 line-clamp-2 leading-snug">
        {summary}
      </p>
    {:else}
      <div class="text-sm text-slate-400 px-1 flex gap-1.5 justify-start items-center pt-1">
        <AppIcon name="circle-x" size={16} class="text-slate-300"/>
        Aucune info
      </div>
    {/if}
  </div>

  <!-- Colonne 5: Localisation (10%) -->
  <div class="w-[10%] flex flex-col gap-1.5 min-w-0 pt-1">
    {#if candidate.location}
      <div class="flex items-center gap-1.5">
        <AppIcon name="map-pin" size={16} class="text-slate-400 shrink-0" />
        <span class="text-[0.84rem] text-slate-500 truncate">{candidate.location}</span>
      </div>
    {/if}
  </div>

  <!-- Colonne 6: Actions (3%) -->
  <div class="w-[3%] flex items-start justify-start pt-1 shrink-0">
    {@render ActionMenu()}
  </div>
</div>


{#snippet ActionMenu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger asChild>
      {#snippet child({ props })}
        <button 
          {...props}
          onclick={(e: Event) => e.stopPropagation()}
          class="p-1.5 hover:bg-slate-200/50 rounded-md transition-colors text-slate-800 cursor-pointer outline-none"
        >
          <AppIcon name="more-vertical" size={21} />
        </button>
      {/snippet}
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 w-44">
      <DropdownMenu.Item 
        onclick={() => { handleViewCandidate(candidate.id); }}
        class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600"
      >
        <AppIcon name="user" size={17} class="text-slate-500" />
        Détails du profil
      </DropdownMenu.Item>

      {#if candidate.resumeUrl}
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); window.open(getMediaUrl(candidate.resumeUrl), '_blank'); }}
          class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600"
        >
          <AppIcon name="file-text" size={17} class="text-slate-500" />
          Voir le CV
        </DropdownMenu.Item>
      {/if}

      {#if candidate.linkedinUrl}
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); window.open(candidate.linkedinUrl, '_blank'); }}
          class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600"
        >
          <AppIcon name="globe" size={17} class="text-slate-500" />
          Profil LinkedIn
        </DropdownMenu.Item>
      {/if}

      <DropdownMenu.Separator class="my-1 bg-slate-100" />

      <DropdownMenu.Item 
        onclick={() => onEdit?.(candidate)}
        class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600"
      >
        <AppIcon name="edit" size={17} class="text-slate-500" />
        Modifier
      </DropdownMenu.Item>

      <DropdownMenu.Separator class="my-1 bg-slate-100" />

      <DropdownMenu.Item 
        onclick={() => onDelete?.(candidate)}
        class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-red-500 hover:text-red-700! hover:bg-red-50/50!"
      >
        <AppIcon name="trash-2" size={17} class="text-red-500" />
        Supprimer
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

