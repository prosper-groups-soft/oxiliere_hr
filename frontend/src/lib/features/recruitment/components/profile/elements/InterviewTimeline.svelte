<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import { Card, CardContent } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/utilities/common/css";
  import { format } from 'date-fns';
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import type { Interview } from "../../../types/types";

  let { 
    interviews = [],
    onReschedule = null,
    onAddFeedback = null
  } = $props<{ 
    interviews: Interview[],
    onReschedule?: (interview: Interview) => void,
    onAddFeedback?: (interview: Interview) => void
  }>();

  const statusConfig: Record<string, { label: string, color: string, icon: string }> = {
    'SCHEDULED':  { label: 'Planifié',    color: 'bg-blue-50 text-blue-600 border-blue-100', icon: 'calendar' },
    'COMPLETED':  { label: 'Terminé',    color: 'bg-green-50 text-green-600 border-green-100', icon: 'check' },
    'CANCELLED':  { label: 'Annulé',     color: 'bg-red-50 text-red-600 border-red-100', icon: 'x' },
    'NO_SHOW':    { label: 'Absent',     color: 'bg-amber-50 text-amber-600 border-amber-100', icon: 'alert' }
  };

  const typeConfig: Record<string, { label: string, icon: string }> = {
    'PHONE':      { label: 'Téléphonique', icon: 'phone' },
    'VIDEO':      { label: 'Visioconférence', icon: 'video' },
    'ONSITE':     { label: 'Présentiel', icon: 'map-pin' },
    'TECHNICAL':  { label: 'Technique', icon: 'code' },
    'BEHAVIORAL': { label: 'Comportemental', icon: 'users' }
  };

  // Sort interviews by date (most recent first)
  const sortedInterviews = $derived(
    [...interviews].sort((a, b) => new Date(b.scheduledDate).getTime() - new Date(a.scheduledDate).getTime())
  );

  function formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}min` : `${hours}h`;
  }

  function handleReschedule(interview: Interview) {
    onReschedule?.(interview);
  }

  function handleJoinVideo(interview: Interview) {
    if (interview.videoLink) {
      window.open(interview.videoLink, '_blank');
    }
  }

  function handleAddFeedback(interview: Interview) {
    onAddFeedback?.(interview);
  }
</script>


<div class="space-y-4">
  {#if sortedInterviews.length === 0}
    <Empty 
      icon="calendar" 
      title="Aucun entretien planifié" 
      description="Les entretiens apparaîtront ici une fois planifiés" 
      class="py-8"
    />
  {:else}
    {#each sortedInterviews as interview (interview.id)}
      <Card class={cn(
        "transition-all duration-200 shadow-none gap-2.5 p-0",
        interview.status === 'CANCELLED' && "opacity-60",
        interview.status === 'NO_SHOW' && "border-amber-200 bg-amber-50/30"
      )}>
        <CardContent class="p-4">
          <!-- Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <div class={cn(
                "h-10 w-10 rounded-lg flex items-center justify-center border",
                interview.status === 'SCHEDULED' && "bg-blue-50 border-blue-200",
                interview.status === 'COMPLETED' && "bg-green-50 border-green-200", 
                interview.status === 'CANCELLED' && "bg-red-50 border-red-200",
                interview.status === 'NO_SHOW' && "bg-amber-50 border-amber-200"
              )}>
                <AppIcon 
                  name={statusConfig[interview.status]?.icon || 'calendar'} 
                  size={16} 
                  class={statusConfig[interview.status]?.color || 'text-slate-600'}
                />
              </div>
              <div>
                <h6 class="font-semibold text-slate-900 text-[0.98rem]">
                  {typeConfig[interview.type]?.label || interview.type}
                </h6>
                <div class="flex items-center gap-1.5 mt-1">
                  <Badge variant="outline" class={cn(
                    "text-[0.75rem] shadow-fine rounded-lg",
                    interview.status === 'SCHEDULED' && "text-blue-600 bg-blue-50 border border-blue-200",
                    interview.status === 'COMPLETED' && "text-green-600 bg-green-50 border border-green-200",
                    interview.status === 'CANCELLED' && "text-red-600 bg-red-50 border border-red-200", 
                    interview.status === 'NO_SHOW' && "text-amber-600 bg-amber-50 border border-amber-200"
                  )}>
                    {statusConfig[interview.status]?.label}
                  </Badge>
                  {#if interview.interviewer}
                    <span class="text-[0.8rem] text-slate-500">
                      avec {interview.interviewer}
                    </span>
                  {/if}
                </div>
              </div>
            </div>
            
            <div class="flex items-center gap-1">
              {#if interview.status === 'SCHEDULED' && interview.videoLink}
                <Button variant="outline" size="sm" onclick={() => handleJoinVideo(interview)}>
                  <AppIcon name="video" size={17} />
                  Rejoindre
                </Button>
              {/if}
              {#if interview.status === 'SCHEDULED'}
                <Button variant="ghost" size="sm" onclick={() => handleReschedule(interview)}>
                  <AppIcon name="refresh" size={17} />
                </Button>
              {/if}
              {#if interview.status === 'COMPLETED' && !interview.feedback}
                <Button variant="ghost" size="sm" onclick={() => handleAddFeedback(interview)}>
                  <AppIcon name="edit" size={17} />
                </Button>
              {/if}
            </div>
          </div>

          <!-- Date and Time -->
          <div class="flex items-center gap-4 text-sm text-slate-600 mb-3">
            <div class="flex items-center gap-1">
              <AppIcon name="calendar" size={17} class="text-slate-400" />
              <span class="text-[0.87rem]">
                {format(new Date(interview.scheduledDate), 'dd MMM yyyy')}
              </span>
            </div>
            <div class="flex items-center gap-1">
              <AppIcon name="clock" size={17} class="text-slate-400" />
              <span class="text-[0.87rem]">
                {format(new Date(interview.scheduledDate), 'HH:mm')}
              </span>
            </div>
            {#if interview.duration}
              <div class="flex items-center gap-1">
                <AppIcon name="clock" size={17} class="text-slate-400" />
                <span class="text-[0.87rem]">
                  {formatDuration(interview.duration)}
                </span>
              </div>
            {/if}
          </div>

          <!-- Description -->
          {#if interview.description}
            <div class="text-sm text-slate-700 mb-3">
              {interview.description}
            </div>
          {/if}

          <!-- Feedback -->
          {#if interview.feedback}
            <Separator class="my-3" />
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <h5 class="text-sm font-medium text-slate-900">Feedback</h5>
                <div class="flex items-center gap-1">
                  {#if interview.rating}
                    <div class="flex items-center gap-1">
                      {#each Array.from({length: 5}) as _, i}
                        <AppIcon 
                          name="star" 
                          size={17} 
                          class={i < interview.rating ? "text-amber-400 fill-amber-400" : "text-slate-300"} 
                        />
                      {/each}
                      <span class="text-xs text-slate-600 ml-1">{interview.rating}/5</span>
                    </div>
                  {/if}
                </div>
              </div>
              <p class="text-sm text-slate-700">{interview.feedback}</p>
              {#if interview.nextSteps}
                <div class="mt-2">
                  <span class="text-xs font-medium text-slate-500">Prochaines étapes:</span>
                  <p class="text-sm text-slate-700 mt-1">{interview.nextSteps}</p>
                </div>
              {/if}
            </div>
          {/if}

          <!-- Video Link -->
          {#if interview.videoLink && interview.status !== 'CANCELLED'}
            <Separator class="my-3" />
            <div class="flex items-center gap-2 text-sm">
              <AppIcon name="video" size={17} class="text-slate-400" />
              <a 
                href={interview.videoLink} 
                target="_blank" 
                class="text-blue-600 hover:text-blue-700 underline text-[0.85rem]!"
              >
                Lien de la visioconférence
              </a>
            </div>
          {/if}

          <!-- Cancellation Reason -->
          {#if interview.status === 'CANCELLED' && interview.cancellationReason}
            <Separator class="my-3" />
            <div class="text-sm">
              <span class="font-medium text-slate-700">Raison d'annulation:</span>
              <p class="text-slate-600 mt-1">{interview.cancellationReason}</p>
            </div>
          {/if}
        </CardContent>
      </Card>
    {/each}
  {/if}
</div>
