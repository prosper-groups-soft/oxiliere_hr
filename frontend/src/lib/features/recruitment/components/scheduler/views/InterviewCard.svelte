<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/utilities/common/css";
  import { format } from 'date-fns';
  import type { Interview } from "@/features/recruitment/types/types";
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";

  let {
    interview,
    isToday,
    onClick
  } = $props<{
    interview: Interview;
    isToday: boolean;
    onClick: () => void;
  }>();

  const candidate = $derived(recruitmentStore.candidates.find(c => c.id === interview.candidateId));

  const interviewTypeConfig: Record<string, { label: string, icon: string, color: string, bg: string, border: string }> = {
    'PHONE':      { label: 'Tél.',   icon: 'phone',   color: 'text-blue-600',    bg: 'bg-blue-50',    border: 'border-blue-100' },
    'VIDEO':      { label: 'Vidéo',  icon: 'video',   color: 'text-purple-600',  bg: 'bg-purple-50',  border: 'border-purple-100' },
    'ONSITE':     { label: 'Site',   icon: 'map-pin', color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-100' },
    'TECHNICAL':  { label: 'Tech.',  icon: 'code',    color: 'text-amber-600',   bg: 'bg-amber-50',   border: 'border-amber-100' },
    'BEHAVIORAL': { label: 'Comp.',  icon: 'users',   color: 'text-indigo-600',  bg: 'bg-indigo-50',  border: 'border-indigo-100' }
  };

  const statusLabels: Record<string, { label: string, color: string }> = {
    'SCHEDULED':  { label: 'Planifié',  color: 'text-blue-600 bg-blue-50 border-blue-100' },
    'COMPLETED':  { label: 'Terminé',   color: 'text-emerald-600 bg-emerald-50 border-emerald-100' },
    'CANCELLED':  { label: 'Annulé',    color: 'text-red-600 bg-red-50 border-red-100' },
    'NO_SHOW':    { label: 'Absent',    color: 'text-amber-600 bg-amber-50 border-amber-100' }
  };

  const cfg = $derived(interviewTypeConfig[interview.type]);
</script>


<button 
  onclick={onClick}
  class={cn(
    "w-full text-left p-2 rounded-lg border transition-all group cursor-pointer flex flex-col items-stretch",
    interview.status === 'CANCELLED' 
      ? "opacity-40 border-slate-200 bg-white" 
      : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-fine"
  )}
>
  <!-- Time + Type -->
  <div class="flex items-center justify-between mb-1 w-full">
    <span class="text-[0.71rem] font-bold text-slate-500 flex-1">
      {format(new Date(interview.scheduledDate), 'HH:mm')}
    </span>
    {#if cfg}
      <div class={cn("h-5 w-5 rounded flex items-center justify-center shrink-0", cfg.bg)}>
        <AppIcon name={cfg.icon} size={15} class={cfg.color} />
      </div>
    {/if}
  </div>
  
  <!-- Candidate Name -->
  <h4 class="text-[0.79rem] font-bold text-slate-900 truncate leading-tight w-full">
    {candidate ? `${candidate.firstName} ${candidate.lastName}` : 'Inconnu'}
  </h4>
  
  <!-- Interviewer -->
  <div class="flex items-center gap-1 mt-0.5 w-full">
    <AppIcon name="user" size={15} class="text-slate-400 shrink-0" />
    <span class="text-[0.73rem] text-slate-500 font-medium truncate flex-1 leading-tight">{interview.interviewer || 'Non assigné'}</span>
  </div>

  <!-- Status badge for today's scheduled -->
  {#if interview.status === 'SCHEDULED' && isToday}
    <div class="mt-1.5 flex items-center gap-1">
      <span class="flex h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse shrink-0"></span>
      <span class="text-[0.6rem] font-bold text-blue-600 uppercase tracking-wider">Bientôt</span>
    </div>
  {/if}

  {#if interview.status === 'COMPLETED'}
    <div class="mt-1.5 self-start">
      <Badge variant="outline" class="text-[0.55rem] h-4 px-1 border-none bg-emerald-50 text-emerald-600 font-bold">
        Terminé
      </Badge>
    </div>
  {/if}
</button>
