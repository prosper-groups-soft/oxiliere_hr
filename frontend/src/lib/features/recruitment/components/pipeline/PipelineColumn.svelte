<script lang="ts">
  import { dndzone, TRIGGERS, type DndEvent } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/utilities/common/css";
  import CandidateCard from "../lists/views/candidate/CandidateCard.svelte";
  import type { Candidate, CandidateStage } from "../../types/types";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { stageConfig } from "../../stores/recruitment.svelte";

  let { 
    stage,
    title,
    candidates = [],
    onCandidateEdit,
    onCandidateDelete,
    onScheduleInterview,
    onViewProfile,
    onUpdateStage,
    onDrop
  } = $props<{
    stage: CandidateStage;
    title: string;
    candidates: Candidate[];
    onCandidateEdit?: (candidate: Candidate) => void;
    onCandidateDelete?: (candidate: Candidate) => void;
    onScheduleInterview?: (candidate: Candidate) => void;
    onViewProfile?: (candidate: Candidate) => void;
    onUpdateStage?: (candidate: Candidate, newStage: string) => void;
    onDrop: (candidateId: string, newStage: CandidateStage) => void;
  }>();

  let items = $state<Candidate[]>([]);

  $effect(() => {
    items = [...candidates];
  });

  const flipDurationMs = 200;

  function handleDndConsider(e: CustomEvent<DndEvent<Candidate>>) {
    items = e.detail.items;
  }

  function handleDndFinalize(e: CustomEvent<DndEvent<Candidate>>) {
    const { items: newItems, info } = e.detail;
    items = newItems;
    
    if (info.trigger === TRIGGERS.DROPPED_INTO_ZONE) {
      onDrop(info.id, stage);
    }
  }

  const badgeConfig: Record<CandidateStage, { color: string, bgColor: string, borderColor: string }> = {
    'SCREENING':  { color: 'text-blue-700', bgColor: 'bg-blue-100', borderColor: 'border-blue-200' },
    'SHORTLIST':  { color: 'text-amber-700', bgColor: 'bg-amber-100', borderColor: 'border-amber-200' },
    'INTERVIEW':  { color: 'text-purple-700', bgColor: 'bg-purple-100', borderColor: 'border-purple-200' },
    'OFFER':      { color: 'text-emerald-700', bgColor: 'bg-emerald-100', borderColor: 'border-emerald-200' },
    'REJECTED':   { color: 'text-red-700', bgColor: 'bg-red-100', borderColor: 'border-red-200' }
  };

  const config = $derived(stageConfig[stage as CandidateStage]);
  const badgeCfg = $derived(badgeConfig[stage as CandidateStage]);
  
  // Calculate average time in stage
  function averageTimeInStage() {
    if (candidates.length === 0) return 0;
    const totalDays = candidates.reduce((sum: number, c: Candidate) => {
      const days = Math.floor((new Date().getTime() - new Date(c.lastStageChange).getTime()) / (1000 * 60 * 60 * 24));
      return sum + days;
    }, 0);
    return Math.round(totalDays / candidates.length);
  }
</script>


<div 
  in:fly={{ x: stage === 'SCREENING' ? -20 : stage === 'OFFER' ? 20 : 0, duration: 400, delay: 100, easing: cubicOut }}
  class={cn(
    "flex flex-col h-full bg-slate-50 rounded-lg border border-slate-200 overflow-hidden transition-all duration-200"
  )}
>
  {@render Header()}

  <div 
    class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[150px] outline-none"
    use:dndzone={{
      items, 
      flipDurationMs, 
      type: 'candidate',
      dropTargetStyle: { outline: 'none' } 
    }}
    onconsider={handleDndConsider}
    onfinalize={handleDndFinalize}
  >
    {#if items.length === 0}
      {@render Empty()}
    {:else}
      {#each items as candidate (candidate.id)}
        <div animate:flip={{ duration: flipDurationMs }}>
          <CandidateCard 
            {candidate}
            onEdit={onCandidateEdit}
            onDelete={onCandidateDelete}
            onScheduleInterview={onScheduleInterview}
            onViewProfile={onViewProfile}
            onUpdateStage={onUpdateStage}
          />
        </div>
      {/each}
    {/if}
  </div>

  {@render Footer()}
</div>


{#snippet Header()}
  <div class={cn("flex items-center justify-between p-2 py-1 border-b", config.borderColor, config.bgColor)}>
    <div class="flex items-center gap-1">
      <div class={cn("h-5 w-5 rounded-lg flex items-center justify-center", config.bgColor)}>
        <AppIcon name={config.icon} size={17} class={config.color} />
      </div>
      <h3 class="font-semibold text-[0.9rem] text-slate-900">{title}</h3>
    </div>
    <Badge variant="outline" class={cn("text-[0.68rem] font-medium shadow-none border px-1.5 py-0 rounded-md", badgeCfg.bgColor, badgeCfg.color, badgeCfg.borderColor)}>
      {items.length}
    </Badge>
  </div>
{/snippet}


{#snippet Empty()}
  <div class="flex flex-col items-center justify-center h-full min-h-[200px] text-center py-8 pointer-events-none">
    <AppIcon name={config.icon} size={24} class="text-slate-400 mb-3" strokeWidth={1} />
    <p class="text-[0.82rem] text-slate-500 font-medium">Aucun candidat</p>
    <p class="text-[0.75rem] text-slate-500 mt-1">Glissez-déposez ici</p>
  </div>
{/snippet}


{#snippet Footer()}
  <div class={cn("p-2 py-1 border-t", config.borderColor, "bg-white/50")}>
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <AppIcon name="info" size={14} class="text-slate-400" />
        <span class="text-[0.75rem] text-slate-500">
          {items.length} candidat{items.length !== 1 ? 's' : ''}
        </span>
      </div>
      {#if averageTimeInStage() > 7}
        <div class="flex items-center gap-1 text-amber-600">
          <AppIcon name="alert" size={12} />
          <span class="text-[0.7rem] font-medium">{averageTimeInStage()}j moy.</span>
        </div>
      {/if}
    </div>
  </div>
{/snippet}

