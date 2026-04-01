<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { Button } from "@/components/ui/button";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/utilities/common/css";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { differenceInDays } from 'date-fns';
  import { recruitmentStore } from "../../stores/recruitment.svelte";
  import type { Interview } from "../../types/types";
  import { notification } from '@/stores/notification.svelte';
  import { goto } from '$app/navigation';
  import InterviewTimeline from "./elements/InterviewTimeline.svelte";
  import CandidateScorecard from "./elements/CandidateScorecard.svelte";
  import ResumeViewer from "./elements/ResumeViewer.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import InterviewSheet from "../shared/sheets/interview/InterviewSheet.svelte";
  import OfferSheet from "../shared/sheets/candidate/OfferSheet.svelte";
  import CandidateSheet from "../shared/sheets/candidate/CandidateSheet.svelte";
  import EvaluationSheet from "../shared/sheets/candidate/EvaluationSheet.svelte";
  import FeedbackSheet from "../shared/sheets/interview/FeedbackSheet.svelte";

  let { candidateId } = $props<{ candidateId: string }>();

  // Get candidate data from store
  const candidate = $derived(
    recruitmentStore.candidates.find(c => c.id === candidateId)
  );

  const interviews = $derived(
    recruitmentStore.interviews.filter(i => i.candidateId === candidateId)
  );

  const offers = $derived(
    recruitmentStore.offers.filter(o => o.candidateId === candidateId)
  );

  // Sheet states
  let isInterviewSheetOpen = $state(false);
  let isOfferSheetOpen = $state(false);
  let isEditSheetOpen = $state(false);
  let isEvaluationSheetOpen = $state(false);
  let isFeedbackSheetOpen = $state(false);
  let selectedInterview = $state<Interview | null>(null);

  // Redirect if candidate not found
  $effect(() => {
    if (!candidate) {
      goto('/recruitment/pipeline');
      notification.toast.error('Candidat non trouvé');
    }
  });

  // Configurations
  const priorityConfig: Record<string, { label: string, color: string }> = {
    'HIGH':   { label: 'Urgente', color: 'bg-red-50 text-red-600 border-red-100' },
    'MEDIUM': { label: 'Normale', color: 'bg-amber-50 text-amber-600 border-amber-100' },
    'LOW':    { label: 'Faible',  color: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
  };

  const stageConfig: Record<string, { label: string, color: string, icon: string }> = {
    'SCREENING':  { label: 'Tri',        color: 'bg-blue-50 text-blue-600 border-blue-100',      icon: 'filter' },
    'SHORTLIST':  { label: 'Shortlist',  color: 'bg-amber-50 text-amber-600 border-amber-100',    icon: 'star' },
    'INTERVIEW':  { label: 'Entretien',  color: 'bg-purple-50 text-purple-600 border-purple-100',  icon: 'users' },
    'OFFER':      { label: 'Offre',      color: 'bg-emerald-50 text-emerald-600 border-emerald-100', icon: 'send' },
    'REJECTED':   { label: 'Rejeté',     color: 'bg-red-50 text-red-600 border-red-100',         icon: 'x' }
  };

  const sourceConfig: Record<string, { label: string, icon: string }> = {
    'LINKEDIN':     { label: 'LinkedIn',     icon: 'briefcase' },
    'CAREER_SITE':  { label: 'Site Carrière', icon: 'globe' },
    'REFERRAL':     { label: 'Cooptation',   icon: 'users' },
    'DIRECT':       { label: 'Direct',       icon: 'mail' }
  };

  // Calculate derived values
  const palette = $derived(candidate ? getAvatarPalette(`${candidate.firstName} ${candidate.lastName}`) : null);
  const priCfg = $derived(candidate ? priorityConfig[candidate.priority] ?? priorityConfig.MEDIUM : null);
  const stCfg = $derived(candidate ? stageConfig[candidate.currentStage] ?? stageConfig.SCREENING : null);
  const srcCfg = $derived(candidate ? sourceConfig[candidate.source] ?? sourceConfig.DIRECT : null);
  
  const daysInStage = $derived(
    candidate ? differenceInDays(new Date(), new Date(candidate.lastStageChange)) : 0
  );

  // Action handlers
  function handleEdit() {
    isEditSheetOpen = true;
  }

  function handleScheduleInterview() {
    isInterviewSheetOpen = true;
  }

  function handleCreateOffer() {
    isOfferSheetOpen = true;
  }
</script>


{#if candidate}
  <div class="min-h-screen">
    {@render Header()}
    
    <!-- Main Content -->
    <div class="mx-auto px-2 py-2">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Left Column - Main Info -->
        <div class="lg:col-span-2 space-y-6">
          {@render BasicInfoCard()}
          {@render SkillsCard()}
          {@render ResumeCard()}
          {@render InterviewTimelineCard()}
        </div>
        
        <!-- Right Column - Status & Actions -->
        <div class="space-y-6 mr-4">
          {@render StatusCard()}
          {@render ScorecardCard()}
        </div>
      </div>
    </div>
  </div>
{/if}


<InterviewSheet bind:open={isInterviewSheetOpen} candidate={candidate ?? null} interview={selectedInterview} />
<OfferSheet bind:open={isOfferSheetOpen} candidate={candidate ?? null} />
<CandidateSheet bind:open={isEditSheetOpen} candidate={candidate ?? null} campaignId={candidate?.campaignId || ''} />
<EvaluationSheet bind:open={isEvaluationSheetOpen} candidate={candidate ?? null} />
<FeedbackSheet bind:open={isFeedbackSheetOpen} interview={selectedInterview} />


{#snippet Header()}
  <div class="bg-white border-b border-slate-200 sticky top-0 z-10">
    <div class="mx-auto px-3 pr-9">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex items-center gap-2">
            <Avatar class="h-11 w-11 border border-slate-300">
              <AvatarImage src={candidate?.avatarUrl} alt={`${candidate?.firstName} ${candidate?.lastName}`} />
              <AvatarFallback class={cn("text-[1rem] font-bold", palette?.bg, palette?.text)}>
                {getInitials(`${candidate?.firstName} ${candidate?.lastName}`)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h1 class="text-[1rem] font-semibold text-slate-900">
                {candidate?.firstName} {candidate?.lastName}
              </h1>
              <p class="text-[0.85rem] text-slate-500">{candidate?.email}</p>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" onclick={handleEdit} class="rounded-lg text-[0.85rem] h-7.5">
            <AppIcon name="edit" size={16} class="text-slate-500" />
            Modifier
          </Button>
          <Button size="sm" onclick={handleScheduleInterview} class="h-7.5 rounded-lg text-[0.85rem]">
            <AppIcon name="calendar" size={16} />
            Programmer entretien
          </Button>
          {#if candidate?.currentStage === 'INTERVIEW' || candidate?.currentStage === 'SHORTLIST'}
            <Button size="sm" onclick={handleCreateOffer} class="h-7.5 rounded-lg text-[0.85rem]">
              <AppIcon name="send" size={16} />
              Créer offre
            </Button>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/snippet}


{#snippet BasicInfoCard()}
  <Card class="border shadow-none gap-2.5">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 font-bold">
        <AppIcon name="user" size={20} strokeWidth={1.3} />
        Informations générales
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Téléphone</div>
          <p class="text-sm text-slate-900">{candidate?.phone || 'Non renseigné'}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Localisation</div>
          <p class="text-sm text-slate-900">{candidate?.location || 'Non renseigné'}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Poste visé</div>
          <p class="text-sm text-slate-900">{candidate?.position || 'Non renseigné'}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Expérience</div>
          <p class="text-sm text-slate-900">{candidate?.experience || 'Non renseigné'}</p>
        </div>
      </div>
      
      <Separator />
      
      <div>
        <div class="text-sm font-medium text-slate-500">Résumé</div>
        <p class="text-sm text-slate-700 mt-1">
          {candidate?.summary || 'Aucun résumé disponible'}
        </p>
      </div>
    </CardContent>
  </Card>
{/snippet}


{#snippet SkillsCard()}
  <Card class="border shadow-none gap-2.5">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 font-bold">
        <AppIcon name="code" size={20} strokeWidth={1.3} />
        Compétences
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="flex flex-wrap gap-2">
        {#if candidate?.skills && candidate?.skills.length > 0}
          {#each candidate?.skills as skill}
            <Badge variant="outline" class="text-xs border-slate-200">
              {skill}
            </Badge>
          {/each}
        {:else}
          <Empty 
            icon="code" 
            description="Aucune compétence listée" 
            class="py-4 w-full"
            iconSize={24}
          />
        {/if}
      </div>
    </CardContent>
  </Card>
{/snippet}


{#snippet ResumeCard()}
  <Card class="border shadow-none gap-2.5">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 font-bold">
        <AppIcon name="file-text" size={20} strokeWidth={1.3} />
        CV
      </CardTitle>
    </CardHeader>
    <CardContent>
      <ResumeViewer resumeUrl={candidate?.resumeUrl} />
    </CardContent>
  </Card>
{/snippet}


{#snippet InterviewTimelineCard()}
  <Card class="border shadow-none gap-2.5">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 font-bold">
        <AppIcon name="clock" size={20} strokeWidth={1.3} />
        Entretiens
      </CardTitle>
    </CardHeader>
    <CardContent>
      <InterviewTimeline interviews={interviews} />
    </CardContent>
  </Card>
{/snippet}


{#snippet StatusCard()}
  <Card class="border shadow-none gap-2.5">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 font-bold">
        <AppIcon name="info" size={20} strokeWidth={1.3} />
        Statut
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-500">Statut actuel</span>
        <Badge variant="outline" class={cn("text-xs border", stCfg?.color)}>
          <AppIcon name={stCfg?.icon || "info"} size={15} />
          {stCfg?.label}
        </Badge>
      </div>
      
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-500">Priorité</span>
        <Badge variant="outline" class={cn("text-xs border", priCfg?.color)}>
          {priCfg?.label}
        </Badge>
      </div>
      
      <div class="flex items-center justify-between">
        <span class="text-sm text-slate-500">Source</span>
        <div class="flex items-center gap-1">
          <AppIcon name={srcCfg?.icon || "info"} size={17} class="text-slate-400" />
          <span class="text-[0.81rem] text-slate-600">{srcCfg?.label}</span>
        </div>
      </div>
      
      <Separator />
      
      <div class="text-center">
        <div class="text-lg font-bold text-slate-900">{daysInStage}</div>
        <div class="text-[0.81rem] text-slate-500">
          {daysInStage <= 1 ? 'jour' : 'jours'} dans cette étape
        </div>
      </div>
    </CardContent>
  </Card>
{/snippet}


{#snippet ScorecardCard()}
  <Card class="border shadow-none gap-2.5">
    <CardHeader>
      <CardTitle class="flex items-center justify-between gap-2 font-bold">
        <div class="flex items-center gap-2">
          <AppIcon name="star" size={20} />
          Évaluation    
        </div>
        <Button variant="outline" size="sm" onclick={() => isEvaluationSheetOpen = true} class="h-7 bg-slate-50 text-[0.8rem]">
          <AppIcon name="edit" size={15} class="text-gray-500" />
          Modifier
        </Button>
      </CardTitle>
    </CardHeader>
    <CardContent>
      <CandidateScorecard 
        candidate={candidate ?? null} 
        onEditScores={() => isEvaluationSheetOpen = true} 
      />
    </CardContent>
  </Card>
{/snippet}
