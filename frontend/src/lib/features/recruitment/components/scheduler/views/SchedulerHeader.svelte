<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { format } from 'date-fns';
  import { fr } from 'date-fns/locale';

  let {
    currentDate,
    weekDays,
    weekInterviewCount,
    onPrevWeek,
    onNextWeek,
    onGoToToday,
    onSchedule
  } = $props<{
    currentDate: Date;
    weekDays: Date[];
    weekInterviewCount: number;
    onPrevWeek: () => void;
    onNextWeek: () => void;
    onGoToToday: () => void;
    onSchedule: () => void;
  }>();
</script>


<div class="px-4 pr-8 py-3 border-b border-slate-100 flex items-center justify-between bg-white">
  <div class="flex items-center gap-4">
    <!-- Week Navigation -->
    <div class="flex items-center gap-1 bg-slate-50 border border-slate-100 p-0.5 rounded-lg">
      <Button variant="ghost" size="icon" onclick={onPrevWeek} class="h-7 w-7 text-slate-500 hover:bg-white hover:shadow-fine rounded-md">
        <AppIcon name="prev" size={14} />
      </Button>
      <Button variant="ghost" onclick={onGoToToday} class="h-7 px-2.5 text-[0.78rem] font-bold text-slate-700 hover:bg-white hover:shadow-fine rounded-md">
        Aujourd'hui
      </Button>
      <Button variant="ghost" size="icon" onclick={onNextWeek} class="h-7 w-7 text-slate-500 hover:bg-white hover:shadow-fine rounded-md">
        <AppIcon name="next" size={14} />
      </Button>
    </div>

    <!-- Period Label -->
    <div class="flex items-center gap-2">
      <span class="text-[0.88rem] font-bold text-slate-900 capitalize">
        {format(currentDate, 'MMMM yyyy', { locale: fr })}
      </span>
      <span class="text-[0.8rem] text-slate-400 font-medium">
        Sem. {format(weekDays[0], 'd', { locale: fr })}–{format(weekDays[6], 'd MMM', { locale: fr })}
      </span>
    </div>
  </div>

  <div class="flex items-center gap-3">
    <!-- Week Stats -->
    <div class="flex items-center gap-1.5 text-slate-500">
      <AppIcon name="calendar" size={17} strokeWidth={1.1} class="text-slate-400" />
      <span class="text-[0.8rem]">{weekInterviewCount} entretien{weekInterviewCount !== 1 ? 's' : ''} cette semaine</span>
    </div>

    <Button 
      onclick={onSchedule}
      class="bg-primary text-white h-7.5 px-4 shadow-fine hover:bg-primary/90 transition-all text-[0.84rem]"
    >
      <AppIcon name="plus" size={17} />
      Programmer
    </Button>
  </div>
</div>
