<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { format } from 'date-fns';
  import { fr } from 'date-fns/locale';
  import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";

  let {
    currentDate,
    weekDays,
    weekInterviewCount,
    onPrevWeek,
    onNextWeek,
    onGoToToday,
    applications = [],
    onSchedule
  } = $props<{
    currentDate: Date;
    weekDays: Date[];
    weekInterviewCount: number;
    onPrevWeek: () => void;
    onNextWeek: () => void;
    onGoToToday: () => void;
    applications: Array<{
      applicationId: string;
      candidateName: string;
      positionName: string;
      candidate?: any;
    }>;
    onSchedule: (applicationId: string, candidate: any) => void;
  }>();
</script>


<div class="px-4 pr-8 py-1.5 border-b border-slate-100 flex items-center justify-between bg-white">
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

    {#if applications.length > 0}
      <DropdownMenu>
        <DropdownMenuTrigger>
          <Button class="bg-primary text-white h-7.5 px-4 shadow-fine hover:bg-primary/90 transition-all text-[0.84rem] cursor-pointer">
            <AppIcon name="plus" size={17} />
            Programmer
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent class="z-9999 w-72 p-1">
          <div class="px-2 py-1.5 text-[0.65rem] font-bold uppercase tracking-wider text-slate-400">
            Sélectionner une candidature
          </div>
          {#each applications as app}
            <DropdownMenuItem 
              onclick={() => onSchedule(app.applicationId, app.candidate)}
              class="flex items-center gap-2.5 px-2 py-2 cursor-pointer rounded-md"
            >
              <Avatar class="h-7 w-7 rounded-full shrink-0 border border-slate-100">
                <AvatarImage src={getMediaUrl(app.candidate?.avatarUrl || '')} alt={app.candidateName} />
                <AvatarFallback class={cn("text-[0.6rem] font-bold", getAvatarPalette(app.candidateName || '').bg, getAvatarPalette(app.candidateName || '').text)}>
                  {getInitials(
                    app.candidate?.lastName || app.candidate?.last_name || '',
                    app.candidate?.middleName || app.candidate?.middle_name || '',
                    app.candidate?.firstName || app.candidate?.first_name || ''
                  )}
                </AvatarFallback>
              </Avatar>
              <div class="flex flex-col min-w-0 flex-1">
                <span class="text-[0.82rem] font-semibold text-slate-900 truncate">{app.candidateName}</span>
                <span class="text-[0.82rem] text-slate-500 truncate flex items-center gap-1">
                  <AppIcon name="briefcase" size={15} class="text-slate-400 shrink-0" />
                  {app.positionName}
                </span>
              </div>
            </DropdownMenuItem>
          {/each}
        </DropdownMenuContent>
      </DropdownMenu>
    {:else}
      <Button 
        disabled
        class="bg-primary/60 text-white h-7.5 px-4 shadow-fine text-[0.84rem] cursor-not-allowed"
      >
        <AppIcon name="plus" size={17} />
        Programmer
      </Button>
    {/if}
  </div>
</div>
