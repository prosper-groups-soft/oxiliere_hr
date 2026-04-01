<script lang="ts">
  import { goto } from '$app/navigation';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import { Button } from '@/components/ui/button';
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { format } from 'date-fns';
  import { cn } from '@/utilities/common/css';
  import type { Candidate } from '../../../../types/types';
  import { 
    Avatar, 
    AvatarFallback, 
    AvatarImage 
  } from '@/components/ui/avatar';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";
  import { getInitials } from '@/utilities/common/string';
  import { getAvatarPalette } from "@/utilities/common/func";

  let { 
    candidate,
    stageConfig,
    onScheduleInterview,
    onEdit,
    onDelete
  } = $props<{
    candidate: Candidate;
    stageConfig: Record<string, { label: string, color: string }>;
    onScheduleInterview?: (candidate: Candidate) => void;
    onEdit?: (candidate: Candidate) => void;
    onDelete?: (candidate: Candidate) => void;
  }>();

  const palette = $derived(getAvatarPalette(candidate.name));

  function handleViewCandidate(candidateId: string) {
    goto(`/recruitment/${candidate.campaignId}/candidates/${candidateId}`);
  }

  function handleAddToPipeline(candidateId: string) {
    recruitmentStore.addToPipeline(candidateId);
  }

  function handleRemoveFromPipeline(candidateId: string) {
    recruitmentStore.removeFromPipeline(candidateId);
  }

  function handleAvatarUpload(file: File) {
    // TODO: Implement avatar upload
    console.log('Avatar upload:', file);
  }

</script>


<div 
  class="group/row hover:bg-slate-50/80 bg-white border-b border-slate-100 rounded-none px-6 py-4 transition-all duration-200 cursor-pointer relative"
  onclick={() => handleViewCandidate(candidate.id)}
  role="none"
>
  <div class="flex items-center justify-between w-full gap-6">
    <!-- Colonne 1: Avatar et infos (35%) -->
    <div class="flex items-center gap-4 w-[35%] min-w-0">
      <div class="shrink-0">
        <div role="none" onclick={(e) => e.stopPropagation()}>
          <AvatarGallery 
            name={`${candidate.firstName} ${candidate.lastName}`}
            src={candidate.avatarUrl}
            onUpload={handleAvatarUpload}
            iconSize={16}
            iconStroke={2}
            class="h-12 w-12 rounded-full"
          >
            <Avatar class="h-12 w-12 border border-slate-300 shadow-none rounded-full">
              <AvatarImage src={candidate.avatarUrl} alt={`${candidate.firstName} ${candidate.lastName}`} />
              <AvatarFallback class={cn("font-bold text-[1rem]", palette.bg, palette.text)}>
                {getInitials(`${candidate.firstName} ${candidate.lastName}`)}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
        </div>
      </div>
      
      <div class="min-w-0 flex-1">
        <div class="font-bold text-[0.855rem] text-slate-900 truncate leading-tight group-hover/row:text-primary transition-colors">
          {candidate.firstName} {candidate.lastName}
        </div>
        <div class="flex items-center gap-1.5 mt-0.5">
           <AppIcon name="mail" size={16} class="text-slate-400" />
           <p class="text-[0.81rem] text-slate-500 truncate">{candidate.email}</p>
        </div>
      </div>
    </div>
    
    <!-- Colonne 2: Stage et poste (25%) -->
    <div class="flex flex-col items-start gap-1.5 w-[25%] min-w-0">
      <Badge variant="outline" class={cn("text-[0.75rem] px-2 py-0 border-transparent shadow-none", stageConfig[candidate.currentStage].color)}>
        {stageConfig[candidate.currentStage].label}
      </Badge>
      <div class="flex items-center gap-1.5 px-1 truncate w-full">
        <AppIcon name="briefcase" size={17} class="text-slate-400 shrink-0" />
        <span class="text-[0.8rem] text-slate-600 truncate font-medium">
          {candidate.position || 'Poste non spécifié'}
        </span>
      </div>
    </div>
    
    <!-- Colonne 3: Score et date (20%) -->
    <div class="w-[20%] min-w-0 flex flex-col gap-1">
      <div class="flex items-center gap-2">
        <div class="h-1.5 flex-1 bg-slate-100 rounded-full overflow-hidden max-w-20">
            <div 
              class={cn(
                "h-full rounded-full transition-all",
                (candidate.score || 0) > 80 ? "bg-emerald-500" : (candidate.score || 0) > 50 ? "bg-amber-500" : "bg-red-500"
              )} 
              style={`width: ${candidate.score || 0}%`}
            ></div>
        </div>
        <span class="text-[0.8rem] font-bold text-slate-700">{candidate.score || 0}</span>
      </div>
      <div class="flex items-center gap-1.5 text-slate-500">
        <AppIcon name="calendar" size={17} strokeWidth={1.2} />
        <span class="text-[0.81rem]">Postulé le {format(new Date(candidate.appliedDate), 'dd MMM yyyy')}</span>
      </div>
    </div>
    
    <!-- Colonne 4: Actions (20%) -->
    <div class="flex items-center justify-end gap-2.5 w-[20%] min-w-0">
      <div class="flex items-center gap-2">
        {#if candidate.inPipeline === false || candidate.currentStage === 'REJECTED'}
          <Button 
            variant="outline" 
            size="sm" 
            onclick={(e) => { e.stopPropagation(); handleAddToPipeline(candidate.id); }}
            class="h-7.5 bg-white border-slate-200 text-slate-600 hover:text-emerald-600 hover:border-emerald-200 text-[0.82rem] font-medium shadow-fine px-3"
          >
            Réactiver
          </Button>
        {:else}
          <Button 
            variant="outline" 
            size="sm" 
            onclick={(e) => { e.stopPropagation(); handleRemoveFromPipeline(candidate.id); }}
            class="h-7.5 bg-white border-slate-200 text-slate-600 hover:text-red-600 hover:border-red-200 text-[0.82rem] font-medium shadow-fine px-3"
          >
            Retirer
          </Button>
        {/if}
      </div>

      <div class="flex items-center gap-1">
        {@render ActionMenu()}
        <div class="h-8 w-8 rounded-full flex items-center justify-center bg-slate-50 text-slate-800 transition-all shadow-fine">
          <AppIcon name="arrow-right" size={16} />
        </div>
      </div>
    </div>
  </div>
</div>


{#snippet ActionMenu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger 
      class="h-8 w-8 rounded-full flex items-center justify-center bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-600 transition-all border border-slate-200 shadow-fine outline-none cursor-pointer"
      onclick={(e: Event) => e.stopPropagation()}
    >
      <AppIcon name="more-vertical" size={17} />
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-36 p-1 rounded-lg shadow-fine bg-white border-slate-100">
      <DropdownMenu.Item 
        onclick={() => onEdit?.(candidate)}
        class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-primary"
      >
        <AppIcon name="edit" size={17} />
        Modifier
      </DropdownMenu.Item>
      <DropdownMenu.Item 
        onclick={() => onDelete?.(candidate)}
        class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2  text-red-500 hover:text-red-700! hover:bg-red-50/50!"
      >
        <AppIcon name="trash-2" size={17} class="text-red-600 hover:text-red-700" />
        Supprimer
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

