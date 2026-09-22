<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { format } from 'date-fns';
  import type { Interview } from "@/hr/recruitment/types/types";
  import { INTERVIEW_TYPE_CONFIG, INTERVIEW_STATUS_CONFIG } from "@/hr/recruitment/constants/recruitment";
  import { Button } from "@/components/ui/button";

  
  let {
    interview,
    isToday,
    onClick,
    onFeedback
  } = $props<{
    interview: Interview;
    isToday: boolean;
    onClick: () => void;
    onFeedback?: (() => void) | undefined;
  }>();

  const typeCfg = $derived(INTERVIEW_TYPE_CONFIG[interview.type]);
  const statusCfg = $derived(INTERVIEW_STATUS_CONFIG[interview.status]);
  const canGiveFeedback = $derived(interview.status === 'COMPLETED' || interview.status === 'NO_SHOW');
</script>


<div class={cn(
  "w-full text-left p-2 rounded-lg border transition-all group flex flex-col items-stretch relative",
  interview.status === 'CANCELLED' 
    ? "opacity-40 border-slate-200 bg-white" 
    : "border-slate-200 bg-white hover:border-slate-300"
)}>
  <button 
    onclick={onClick}
    class="w-full text-left flex flex-col items-stretch cursor-pointer"
  >
    <!-- Time + Duration + Type -->
    <div class="flex items-center justify-between mb-1.5 w-full">
      <div class="flex items-center gap-1.5">
        <span class="text-[0.71rem] font-bold text-slate-500">
          {format(new Date(interview.scheduledDate), 'HH:mm')}
        </span>
        <!-- Duration badge -->
        <span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-blue-50 text-[0.6rem] font-bold text-blue-700">
          <AppIcon name="clock" size={11} />
          {interview.duration} min
        </span>
      </div>
      {#if typeCfg}
        <div class="h-5 w-5 rounded flex items-center justify-center shrink-0 bg-slate-50/50" title={typeCfg.label}>
          <AppIcon name={typeCfg.icon} size={15} class={typeCfg.color} />
        </div>
      {/if}
    </div>
    
    <!-- Candidat -->
    <div class="flex flex-col gap-0.5 w-full">
      <div class="flex items-center gap-1 w-full">
        <AppIcon name="user" size={15} class="text-emerald-500 shrink-0" />
        <span class="text-[0.6rem] font-bold text-emerald-600 uppercase tracking-wider w-[4.8rem] shrink-0">Candidat</span>
        <span class="text-[0.79rem] font-bold text-slate-900 truncate leading-tight">{interview.candidateName || 'Inconnu'}</span>
      </div>
      
      <!-- Poste -->
      {#if interview.positionName}
        <div class="flex items-center gap-1 w-full">
          <AppIcon name="briefcase" size={15} class="text-violet-500 shrink-0" />
          <span class="text-[0.6rem] font-bold text-violet-600 uppercase tracking-wider w-[4.8rem] shrink-0">Poste</span>
          <span class="text-[0.73rem] text-violet-700 font-medium truncate flex-1 leading-tight">{interview.positionName}</span>
        </div>
      {/if}
      
      <!-- Interviewer -->
      <div class="flex items-center gap-1 w-full">
        <AppIcon name="user-check" size={15} class="text-slate-400 shrink-0" />
        <span class="text-[0.6rem] font-bold text-slate-400 uppercase tracking-wider w-[4.8rem] shrink-0">Interv.</span>
        <span class="text-[0.73rem] text-slate-500 font-medium truncate flex-1 leading-tight">{interview.interviewer || 'Non assigné'}</span>
      </div>
    </div>

    <!-- Status badge -->
    {#if statusCfg}
      <div class="mt-1.5 flex items-center gap-1 flex-wrap">
        <span class={cn("inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[0.6rem] font-bold uppercase tracking-wider", statusCfg.color)}>
          <AppIcon name={statusCfg.icon} size={12} />
          {statusCfg.label}
        </span>
        {#if interview.status === 'SCHEDULED' && isToday}
          <span class="flex h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse shrink-0"></span>
          <span class="text-[0.6rem] font-bold text-blue-600 uppercase tracking-wider">Bientôt</span>
        {/if}
      </div>
    {/if}
  </button>

  <!-- Feedback button (visible when status allows it) -->
  {#if canGiveFeedback && onFeedback}
    <div class="mt-1.5 pt-1.5 border-t border-slate-100">
      <Button 
        onclick={onFeedback}
        size="sm"
        variant="ghost"
        class="w-full h-6 text-[0.65rem] font-bold text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 transition-all cursor-pointer gap-1"
      >
        <AppIcon name="star" size={13} />
        {interview.feedback ? 'Modifier le feedback' : 'Donner un feedback'}
      </Button>
    </div>
  {/if}
</div>

