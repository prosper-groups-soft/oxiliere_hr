<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import { Card, CardContent } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/utilities/common/css";
  import { format } from 'date-fns';
  import { fr } from 'date-fns/locale';
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { useAllEmployees } from "@/features/employees/queries/employeeQueries";
  import type { Interview } from "../../../types/types";
  import { INTERVIEW_STATUS_CONFIG, INTERVIEW_TYPE_CONFIG } from "../../../constants/recruitment";

  
  let { 
    interviews = [],
    onReschedule = null,
    onAddFeedback = null,
    applicationId = '',
    loading = false
  } = $props<{ 
    interviews: Interview[],
    onReschedule?: (interview: Interview) => void,
    onAddFeedback?: (interview: Interview) => void,
    applicationId?: string,
    loading?: boolean
  }>();

  const statusConfig = INTERVIEW_STATUS_CONFIG;
  const typeConfig = INTERVIEW_TYPE_CONFIG;

  // Load employees to resolve interviewer names from IDs
  const employeesQuery = useAllEmployees();
  let allEmployees = $derived($employeesQuery.data || []);

  // Build a map from employee ID -> employee for quick lookup
  const employeeMap = $derived(
    new Map(allEmployees.map((emp: any) => [String(emp.id), emp]))
  );

  const filteredInterviews = $derived(
    applicationId 
      ? interviews.filter((i: Interview) => i.applicationId === applicationId)
      : interviews
  );

  const sortedInterviews = $derived(
    [...filteredInterviews].sort((a, b) => new Date(b.scheduledDate).getTime() - new Date(a.scheduledDate).getTime())
  );

  function formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}min` : `${hours}h`;
  }

  /** Format a UTC ISO date string in local time for display */
  function formatLocalDate(isoString: string, fmt: string): string {
    return format(new Date(isoString), fmt, { locale: fr });
  }

  /** Resolve interviewer display info from employee map or fallback to stored name */
  function getInterviewerInfo(interview: Interview): { name: string; photo: string; lastName: string; middleName: string; firstName: string } | null {
    if (interview.interviewer) {
      const emp = employeeMap.get(interview.interviewerId);
      if (emp) {
        return {
          name: interview.interviewer,
          photo: getMediaUrl(emp.profile_photo || emp.avatarUrl || '') || '',
          lastName: emp.last_name || '',
          middleName: emp.middle_name || '',
          firstName: emp.first_name || '',
        };
      }
      return {
        name: interview.interviewer,
        photo: '',
        lastName: '',
        middleName: '',
        firstName: '',
      };
    }
    const emp = employeeMap.get(interview.interviewerId);
    if (emp) {
      return {
        name: emp.name || `${emp.first_name || ''} ${emp.last_name || ''}`.trim(),
        photo: getMediaUrl(emp.profile_photo || emp.avatarUrl || '') || '',
        lastName: emp.last_name || '',
        middleName: emp.middle_name || '',
        firstName: emp.first_name || '',
      };
    }
    return null;
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


{#snippet StatusIcon(status: string)}
  <div class={cn(
    "h-10 w-10 rounded-lg flex items-center justify-center border",
    status === 'SCHEDULED' && "bg-blue-50 border-blue-200",
    status === 'COMPLETED' && "bg-green-50 border-green-200", 
    status === 'CANCELLED' && "bg-red-50 border-red-200",
    status === 'NO_SHOW' && "bg-amber-50 border-amber-200"
  )}>
    <AppIcon 
      name={statusConfig[status]?.icon || 'calendar'} 
      size={16} 
      class={statusConfig[status]?.color || 'text-slate-600'}
    />
  </div>
{/snippet}


{#snippet InterviewBadge(status: string)}
  <Badge variant="outline" class={cn(
    "text-[0.82rem] shadow-fine rounded-lg",
    status === 'SCHEDULED' && "text-blue-600 bg-blue-50 border border-blue-200",
    status === 'COMPLETED' && "text-green-600 bg-green-50 border border-green-200",
    status === 'CANCELLED' && "text-red-600 bg-red-50 border border-red-200", 
    status === 'NO_SHOW' && "text-amber-600 bg-amber-50 border border-amber-200"
  )}>
    {statusConfig[status]?.label}
  </Badge>
{/snippet}


{#snippet InterviewerAvatar(info: { name: string; photo: string; lastName: string; middleName: string; firstName: string })}
  <span class="flex items-center gap-1 text-[0.82rem] text-slate-500">
    <Avatar class="h-7 w-7 rounded-full border border-slate-200 shrink-0">
      <AvatarImage src={info.photo} alt={info.name} class="object-cover" />
      <AvatarFallback class={cn("text-[0.5rem] font-bold", getAvatarPalette(info.name).bg, getAvatarPalette(info.name).text)}>
        {getInitials(info.lastName, info.middleName, info.firstName)}
      </AvatarFallback>
    </Avatar>
    avec {info.name}
  </span>
{/snippet}


{#snippet InterviewTypeLabel(interview: Interview)}
  <div class="flex items-center gap-1.5 text-[0.88rem] cursor-pointer">
    <AppIcon 
      name={typeConfig[interview.type]?.icon || 'calendar'} 
      size={18} 
      class={cn(typeConfig[interview.type]?.color || 'text-slate-600', 'cursor-pointer')} 
    />
    {typeConfig[interview.type]?.label || interview.type}
    {#if interview.description}
      <TooltipWrapper content={interview.description} side="top" asChild={true}>
        {#snippet children(props)}
          <button {...props} class="text-slate-400 hover:text-slate-600 outline-none focus:outline-none flex items-center">
            <AppIcon name="info" size={15} />
          </button>
        {/snippet}
      </TooltipWrapper>
    {/if}
  </div>
{/snippet}


{#snippet InterviewMeta(interview: Interview)}
  <div class="flex items-center gap-4 text-sm text-slate-600 mb-3">
    <div class="flex items-center gap-1">
      <AppIcon name="calendar" size={17} class="text-slate-400" />
      <span class="text-[0.87rem]">
        {formatLocalDate(interview.scheduledDate, 'dd MMM yyyy')}
      </span>
    </div>
    <div class="flex items-center gap-1">
      <AppIcon name="clock" size={17} class="text-slate-400" />
      <span class="text-[0.87rem]">
        {formatLocalDate(interview.scheduledDate, 'HH:mm')}
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
    {#if interview.location}
      <div class="flex items-center gap-1">
        <AppIcon name="map-pin" size={17} class="text-slate-400" />
        <span class="text-[0.87rem]">
          {interview.location}
        </span>
      </div>
    {/if}
    {#if interview.notes}
      <TooltipWrapper content={interview.notes} side="top" asChild={true}>
        {#snippet children(props)}
          <button {...props} class="flex items-center gap-1 text-slate-400 hover:text-slate-600 outline-none focus:outline-none cursor-pointer">
            <AppIcon name="file-text" size={17} class="text-slate-400" />
            <span class="text-[0.87rem]">Notes</span>
          </button>
        {/snippet}
      </TooltipWrapper>
    {/if}
  </div>
{/snippet}


{#snippet InterviewActions(interview: Interview)}
  <div class="flex items-center gap-1">
    {#if interview.status === 'SCHEDULED' && interview.videoLink}
      <Button variant="outline" size="sm" onclick={() => handleJoinVideo(interview)}>
        <AppIcon name="video" size={17} />
        Rejoindre
      </Button>
    {/if}
    {#if interview.status !== 'CANCELLED'}
      <Button variant="ghost" size="sm" onclick={() => handleReschedule(interview)} class="text-[0.82rem]!">
        <AppIcon name="edit" size={17} />
        Modifier
      </Button>
    {/if}
    {#if interview.status !== 'CANCELLED'}
      <Button variant="ghost" size="sm" onclick={() => handleAddFeedback(interview)} class="text-[0.82rem]!">
        <AppIcon name="messaging" size={17} />
        {interview.feedback ? 'Modifier le feedback' : 'Feedback'}
      </Button>
    {/if}
  </div>
{/snippet}


{#snippet InterviewFeedback(interview: Interview)}
  {#if interview.feedback}
    <Separator class="my-3" />
    <div class="space-y-2">
      <div class="flex items-center justify-between">
        <h5 class="text-sm font-medium text-slate-900">Feedback</h5>
        {#if interview.feedback.rating}
          <div class="flex items-center gap-1">
            {#each Array.from({length: 5}) as _, i}
              <AppIcon 
                name="star" 
                size={17} 
                class={i < interview.feedback.rating ? "text-amber-400 fill-amber-400" : "text-slate-300"} 
              />
            {/each}
            <span class="text-[0.83rem] text-slate-600 ml-1">{interview.feedback.rating}/5</span>
          </div>
        {/if}
      </div>
      {#if interview.feedback.strengths && interview.feedback.strengths.length > 0}
        <div class="flex flex-wrap gap-1 mt-2">
          {#each interview.feedback.strengths as strength}
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.83rem] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <AppIcon name="thumbs-up" size={14} class="text-emerald-500" />
              {strength}
            </span>
          {/each}
        </div>
      {/if}
      {#if interview.feedback.weaknesses && interview.feedback.weaknesses.length > 0}
        <div class="flex flex-wrap gap-1 mt-2">
          {#each interview.feedback.weaknesses as weakness}
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.83rem] font-medium bg-amber-50 text-amber-700 border border-amber-200">
              <AppIcon name="trending-up" size={14} class="text-amber-500" />
              {weakness}
            </span>
          {/each}
        </div>
      {/if}
      {#if interview.feedback.feedback}
        <p class="text-sm text-slate-700 mt-2">{interview.feedback.feedback}</p>
      {/if}
      {#if interview.feedback.wouldHire !== undefined && interview.feedback.wouldHire !== null}
        <div class="mt-2 flex items-center gap-1.5">
          {#if interview.feedback.wouldHire}
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.83rem] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <AppIcon name="thumbs-up" size={12} class="text-emerald-500" />
              Recommandé à l'embauche
            </span>
          {:else}
            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.83rem] font-medium bg-red-50 text-red-700 border border-red-200">
              <AppIcon name="thumbs-down" size={12} class="text-red-500" />
              Non recommandé
            </span>
          {/if}
        </div>
      {/if}
      {#if interview.feedback.nextSteps}
        <div class="mt-2">
          <span class="text-xs font-medium text-slate-500">Prochaines étapes:</span>
          <p class="text-sm text-slate-700 mt-1">{interview.feedback.nextSteps}</p>
        </div>
      {/if}
    </div>
  {/if}

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

  {#if interview.status === 'CANCELLED' && interview.cancellationReason}
    <Separator class="my-3" />
    <div class="text-sm">
      <span class="font-medium text-slate-700">Raison d'annulation:</span>
      <p class="text-slate-600 mt-1">{interview.cancellationReason}</p>
    </div>
  {/if}
{/snippet}


{#snippet InterviewCard(interview: Interview)}
  {@const interviewerInfo = getInterviewerInfo(interview)}
  <Card class={cn(
    "transition-all duration-200 shadow-none gap-2.5 p-0",
    interview.status === 'CANCELLED' && "opacity-60",
    interview.status === 'NO_SHOW' && "border-amber-200 bg-amber-50/30"
  )}>
    <CardContent class="p-4">
      <!-- Header row -->
      <div class="flex items-start justify-between mb-3">
        <div class="flex items-center gap-3">
          {@render StatusIcon(interview.status)}
          <div>
            <h6 class="font-semibold text-slate-900 text-[0.88rem]">
              {@render InterviewTypeLabel(interview)}
            </h6>
            <div class="flex items-center gap-1.5 mt-1">
              {@render InterviewBadge(interview.status)}
              {#if interviewerInfo}
                {@render InterviewerAvatar(interviewerInfo)}
              {/if}
            </div>
          </div>
        </div>
        {@render InterviewActions(interview)}
      </div>

      <!-- Date, Time, Duration, Location -->
      {@render InterviewMeta(interview)}

      <!-- Feedback & extras -->
      {@render InterviewFeedback(interview)}
    </CardContent>
  </Card>
{/snippet}


{#snippet LoadingSkeleton()}
  <div class="space-y-4">
    {#each Array.from({length: 2}) as _}
      <Card class="shadow-none gap-2.5 p-0">
        <CardContent class="p-4">
          <div class="flex items-start justify-between mb-3 animate-pulse">
            <div class="flex items-center gap-3">
              <div class="h-10 w-10 rounded-lg bg-slate-200"></div>
              <div class="space-y-2">
                <div class="h-4 w-44 rounded bg-slate-200"></div>
                <div class="flex items-center gap-2">
                  <div class="h-5 w-20 rounded-lg bg-slate-200"></div>
                  <div class="h-5 w-28 rounded bg-slate-200"></div>
                </div>
              </div>
            </div>
            <div class="flex gap-1">
              <div class="h-8 w-20 rounded-lg bg-slate-200"></div>
              <div class="h-8 w-20 rounded-lg bg-slate-200"></div>
            </div>
          </div>
          <div class="flex items-center gap-4 animate-pulse">
            <div class="h-5 w-28 rounded bg-slate-200"></div>
            <div class="h-5 w-16 rounded bg-slate-200"></div>
            <div class="h-5 w-16 rounded bg-slate-200"></div>
          </div>
        </CardContent>
      </Card>
    {/each}
  </div>
{/snippet}


<div class="space-y-4">
  {#if loading}
    {@render LoadingSkeleton()}
  {:else if sortedInterviews.length === 0}
    <Empty 
      icon="calendar" 
      title="Aucun entretien planifié" 
      description="Les entretiens apparaîtront ici une fois planifiés" 
      class="py-8"
      iconSize={28}
      iconStrokeWidth={1.3}
    />
  {:else}
    {#each sortedInterviews as interview (interview.id)}
      {@render InterviewCard(interview)}
    {/each}
  {/if}
</div>

