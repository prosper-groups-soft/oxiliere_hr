<script lang="ts">
  import { recruitmentStore } from "../../stores/recruitment.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { 
    format, 
    startOfWeek, 
    endOfWeek, 
    eachDayOfInterval, 
    isSameDay 
  } from 'date-fns';
  import { fr } from 'date-fns/locale';
  import InterviewSheet from "../shared/sheets/interview/InterviewSheet.svelte";
  import SchedulerHeader from "./views/SchedulerHeader.svelte";
  import InterviewCard from "./views/InterviewCard.svelte";
  import type { Interview } from "../../types/types";

  // State
  let currentDate = $state(new Date());
  let selectedInterview = $state<Interview | null>(null);
  let isFormOpen = $state(false);

  // Derived
  const weekDays = $derived(
    eachDayOfInterval({
      start: startOfWeek(currentDate, { weekStartsOn: 1 }),
      end: endOfWeek(currentDate, { weekStartsOn: 1 })
    })
  );

  const interviews = $derived(recruitmentStore.interviews);


  // Actions
  function nextWeek() {
    const next = new Date(currentDate);
    next.setDate(next.getDate() + 7);
    currentDate = next;
  }

  function prevWeek() {
    const prev = new Date(currentDate);
    prev.setDate(prev.getDate() - 7);
    currentDate = prev;
  }

  function goToToday() {
    currentDate = new Date();
  }

  function handleSchedule() {
    selectedInterview = null;
    isFormOpen = true;
  }

  function handleEditInterview(interview: Interview) {
    selectedInterview = interview;
    isFormOpen = true;
  }

  function getInterviewsForDay(day: Date) {
    return interviews.filter(i => isSameDay(new Date(i.scheduledDate), day));
  }

  const weekInterviewCount = $derived(
    weekDays.reduce((sum, day) => sum + getInterviewsForDay(day).length, 0)
  );
</script>


<div class="h-full flex flex-col overflow-hidden">
  <!-- Compact Header -->
  <SchedulerHeader 
    {currentDate}
    {weekDays}
    {weekInterviewCount}
    onPrevWeek={prevWeek}
    onNextWeek={nextWeek}
    onGoToToday={goToToday}
    onSchedule={handleSchedule}
  />

  <!-- Calendar Grid -->
  {@render Calendar()}
</div>


{#snippet Calendar()}
  <div class="flex-1 overflow-y-auto min-h-0">
    <div class="grid grid-cols-7 h-full divide-x divide-slate-100">
      {#each weekDays as day}
        {@const dayInterviews = getInterviewsForDay(day)}
        {@const isToday = isSameDay(day, new Date())}
        
        <div class="flex flex-col min-h-0 min-w-[140px]">
          <!-- Day Header -->
          {@render DayHeader(day, dayInterviews, isToday)}
          <!-- Day Content -->
          {@render DayContent(day, dayInterviews, isToday)}
        </div>
      {/each}
    </div>
  </div>
{/snippet}


{#snippet DayHeader(day: Date, dayInterviews: any[], isToday: boolean)}
  <div class={cn(
    "px-2 py-2 border-b border-slate-100 flex items-center justify-center sticky top-0 z-10 bg-slate-50/50",
    isToday ? "bg-primary/5" : ""
  )}>
    <div class="flex items-center gap-1.5">
      <span class={cn(
        "h-6 w-6 flex items-center justify-center rounded-md text-[0.75rem] font-medium",
        isToday ? "bg-primary text-white shadow-fine" : "text-slate-900"
      )}>
        {format(day, 'd')}
      </span>
      <span class={cn(
        "text-[0.65rem] font-bold uppercase tracking-wider",
        isToday ? "text-primary" : "text-slate-400"
      )}>
        {format(day, 'EEE', { locale: fr })}
      </span>
    </div>
    {#if dayInterviews.length > 0}
      <div class="absolute right-2 top-1/2 -translate-y-1/2">
        <span class="flex h-4 min-w-4 items-center justify-center rounded-full bg-slate-100 border border-slate-200 px-1 text-[0.6rem] font-bold text-slate-500 shadow-none">
          {dayInterviews.length}
        </span>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet DayContent(day: Date, dayInterviews: any[], isToday: boolean)}
  <div class="flex-1 p-1.5 space-y-1.5 overflow-y-auto no-scrollbar">
    {#each dayInterviews as interview}
      <InterviewCard 
        {interview} 
        {isToday} 
        onClick={() => handleEditInterview(interview)} 
      />
    {/each}
    
    {#if dayInterviews.length === 0}
      <div class="h-full flex flex-col items-center justify-center opacity-15 pointer-events-none pb-20">
        <AppIcon name="calendar" size={22} strokeWidth={1.3} class="text-primary" />
      </div>
    {/if}
  </div>
{/snippet}


<InterviewSheet bind:open={isFormOpen} interview={selectedInterview} />


<style>
  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
</style>
