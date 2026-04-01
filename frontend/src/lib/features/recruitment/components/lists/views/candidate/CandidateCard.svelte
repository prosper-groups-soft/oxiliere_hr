<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { cn } from "@/utilities/common/css";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { format, differenceInDays } from 'date-fns';
  import type { Candidate } from "../../../../types/types";
  import { recruitmentStore } from "../../../../stores/recruitment.svelte";
  import { notification } from "@/stores/notification.svelte";

  let { 
    candidate,
    onEdit,
    onDelete,
    onScheduleInterview,
    onViewProfile,
    onUpdateStage,
    dragDisabled = false 
  } = $props<{
    candidate: Candidate;
    onEdit?: (candidate: Candidate) => void;
    onDelete?: (candidate: Candidate) => void;
    onScheduleInterview?: (candidate: Candidate) => void;
    onViewProfile?: (candidate: Candidate) => void;
    onUpdateStage?: (candidate: Candidate, stage: string) => void;
    dragDisabled?: boolean;
  }>();

  const priorityConfig: Record<string, { label: string, color: string }> = {
    'HIGH':   { label: 'Urgente', color: 'bg-red-50 text-red-600 border-red-100' },
    'MEDIUM': { label: 'Normale', color: 'bg-amber-50 text-amber-600 border-amber-100' },
    'LOW':    { label: 'Faible',  color: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
  };

  const stageConfig: Record<string, { label: string, color: string, icon: string }> = {
    'SCREENING':  { label: 'Tri', color: 'bg-blue-50 text-blue-600 border-blue-100', icon: 'filter' },
    'SHORTLIST':  { label: 'Shortlist', color: 'bg-amber-50 text-amber-600 border-amber-100', icon: 'star' },
    'INTERVIEW':  { label: 'Entretien', color: 'bg-purple-50 text-purple-600 border-purple-100', icon: 'users' },
    'OFFER':      { label: 'Offre', color: 'bg-emerald-50 text-emerald-600 border-emerald-100', icon: 'send' },
    'REJECTED':   { label: 'Rejeté', color: 'bg-red-50 text-red-600 border-red-100', icon: 'x' }
  };

  const sourceConfig: Record<string, { label: string, icon: string }> = {
    'LINKEDIN':     { label: 'LinkedIn', icon: 'briefcase' },
    'CAREER_SITE':  { label: 'Site Carrière', icon: 'globe' },
    'REFERRAL':     { label: 'Cooptation', icon: 'users' },
    'DIRECT':       { label: 'Direct', icon: 'mail' }
  };

  const palette = $derived(getAvatarPalette(`${candidate.firstName} ${candidate.lastName}`));
  const priCfg = $derived(priorityConfig[candidate.priority] ?? priorityConfig.MEDIUM);
  const stCfg = $derived(stageConfig[candidate.currentStage] ?? stageConfig.SCREENING);
  const srcCfg = $derived(sourceConfig[candidate.source] ?? sourceConfig.DIRECT);
  
  const daysInStage = $derived(
    differenceInDays(new Date(), new Date(candidate.lastStageChange))
  );

  function handleStageChange(newStage: string) {
    onUpdateStage?.(candidate, newStage);
  }
</script>


<div 
  in:fly={{ y: 10, duration: 300, easing: cubicOut }}
  class={cn(
    "group/card bg-white border border-slate-200 rounded-lg p-3 shadow-none hover:shadow-fine transition-all duration-200 relative",
    dragDisabled ? "cursor-default" : "cursor-grab active:cursor-grabbing"
  )}
  onclick={() => onViewProfile?.(candidate)}
  role="none"
>
  <div class="flex items-start justify-between mb-3">
    <div class="flex items-center gap-1.5 min-w-0">
      <Avatar class="h-10 w-10 shrink-0 border">
        <AvatarImage src={candidate.avatarUrl} alt={`${candidate.firstName} ${candidate.lastName}`} />
        <AvatarFallback class={cn("text-sm font-medium", palette.bg, palette.text)}>
          {getInitials(`${candidate.firstName} ${candidate.lastName}`)}
        </AvatarFallback>
      </Avatar>
      
      <div class="min-w-0">
        <h3 class="font-semibold text-[0.85rem] text-slate-900 truncate group-hover/card:text-blue-600 transition-colors">
          {candidate.firstName} {candidate.lastName}
        </h3>
        <div class="flex items-center gap-2 mt-1">
          <span class="text-[0.8rem] text-slate-500 truncate">{candidate.email}</span>
          {#if candidate.score}
            <Badge variant="outline" class="h-5 px-1.5 text-[0.68rem] font-medium border-blue-200 text-blue-600 shrink-0">
              {candidate.score}/100
            </Badge>
          {/if}
        </div>
      </div>
    </div>

    <div 
      class="flex items-center" 
      onclick={(e) => e.stopPropagation()} 
      onpointerdown={(e) => e.stopPropagation()} 
      role="none"
    >
      {@render Actions()}
    </div>
  </div>

  <div class="flex items-center gap-2 mb-3">
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

  <div class="flex items-center justify-between mt-auto">
    <span class="text-[0.8rem] text-slate-700">
      Candidature: {format(new Date(candidate.appliedDate), 'dd MMM')}
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
          class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-400 hover:text-slate-600"              
        >
          <AppIcon name="more-vertical" size={17} />
        </button>
      {/snippet}
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="p-2 rounded-lg shadow-fine bg-white border-slate-100 z-1100">
      <DropdownMenu.Group>
        <DropdownMenu.Label class="px-3 py-2 text-[0.7rem]! font-bold text-slate-400 uppercase tracking-widest">
          Changer le statut
        </DropdownMenu.Label>
        {#each Object.entries(stageConfig) as [key, config]}
          <DropdownMenu.Item 
            onclick={() => handleStageChange(key)}
            class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!"
          >
            <AppIcon name={config.icon} size={17} class="text-slate-500" />
            {config.label}
          </DropdownMenu.Item>
        {/each}
      </DropdownMenu.Group>
      
      <DropdownMenu.Separator class="my-2 bg-slate-50" />

      <DropdownMenu.Group>
        <DropdownMenu.Item onclick={() => onScheduleInterview?.(candidate)} class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!">
          <AppIcon name="calendar" size={17} class="text-slate-500" />
          Programmer entretien
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => onEdit?.(candidate)} class="cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!">
          <AppIcon name="edit" size={17} class="text-slate-500" />
          Modifier
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => {
          recruitmentStore.removeFromPipeline(candidate.id);
          notification.toast.warning(`${candidate.firstName} ${candidate.lastName} retiré du pipeline`);
        }} class="text-red-600 hover:text-red-700! hover:bg-red-50! cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!">
          <AppIcon name="x" size={17} class="text-red-600" />
          Retirer du pipeline
        </DropdownMenu.Item>
      </DropdownMenu.Group>

      <DropdownMenu.Separator class="my-2 bg-slate-50" />

      <DropdownMenu.Group>
        <DropdownMenu.Item onclick={() => onDelete?.(candidate)} class="text-red-600 hover:text-red-700! hover:bg-red-50! cursor-pointer gap-2 py-1.5 px-3 text-[0.85rem]!">
          <AppIcon name="trash" size={17} class="text-red-600" />
          Supprimer
        </DropdownMenu.Item>
      </DropdownMenu.Group>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

