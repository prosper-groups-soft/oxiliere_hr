<script lang="ts">
  import { get } from 'svelte/store';
  import { useAllEmployees } from '@/features/employees/queries/employeeQueries';
  import { useTeamPlannerQuery } from '../../queries/leaveQueries';
  import { LEAVE_TYPE_COLORS, LEAVE_TYPE_LEGEND } from '../../constants/leaves';
  import { toFrontendCategory, toFrontendStatus } from '../../api/leaveRequests.endpoints';
  import type { LeaveType } from '../../types/types';
  import type { TeamPlannerEmployee } from '../../api/leaveRequests.endpoints';
  import TeamGanttRow from './views/TeamGanttRow.svelte';
  import * as Tooltip from "@/components/ui/tooltip";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { MONTHS } from '@/constants/locale';
  import { cn } from '@/utilities/common/css';


  // --- Month state ---
  let currentMonth = $state(new Date());
  const year = $derived(currentMonth.getFullYear());
  const month = $derived(currentMonth.getMonth() + 1);

  // --- Employees — fetch all for the team view ---
  const employeesQuery = useAllEmployees();
  const employees = $derived($employeesQuery.data ?? []);

  // --- Leaves for current month via dedicated endpoint ---
  const teamQuery = useTeamPlannerQuery(() => year, () => month);
  const teamData: TeamPlannerEmployee[] = $derived($teamQuery?.data ?? []);

  // Refetch query when month changes (même pattern que LeavesBoard)
  $effect(() => {
    year;
    month;
    get(teamQuery).refetch();
  });

  // Build a Map<employeeId, Map<dateIso, {type, status}>> for O(1) lookup
  const leaveMap = $derived.by(() => {
    const map = new Map<string, Map<string, { type: LeaveType; status: string }>>();
    for (const emp of teamData) {
      const dayMap = new Map<string, { type: LeaveType; status: string }>();
      for (const day of emp.days) {
        dayMap.set(day.date, { type: toFrontendCategory(day.type), status: toFrontendStatus(day.status) });
      }
      map.set(emp.employee_id, dayMap);
    }
    return map;
  });

  // --- Month Navigation ---
  let monthPickerOpen = $state(false);
  let monthIndicatorStyle = $state('');

  const monthLabel = $derived(
    currentMonth.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
  );

  const monthValue = $derived(
    `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}`
  );

  // Close picker on escape
  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') monthPickerOpen = false;
  }

  // Quick actions
  const monthQuickActions = [
    { label: 'Mois préc.', value: -1, key: 'prev' },
    { label: 'Ce mois', value: 0, key: 'today' },
    { label: 'Mois suiv.', value: 1, key: 'next' },
  ];

  const activeMonthKey = $derived.by(() => {
    for (const action of monthQuickActions) {
      const d = new Date();
      d.setMonth(d.getMonth() + action.value);
      const target = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      if (monthValue === target) return action.key;
    }
    return null;
  });

  $effect(() => {
    const key = activeMonthKey;
    if (!key) {
      monthIndicatorStyle = 'left: 0; width: 0;';
      return;
    }
    // Use rAF to ensure DOM layout is complete
    requestAnimationFrame(() => {
      const btn = document.querySelector(`[data-month-btn="${key}"]`) as HTMLElement | null;
      if (btn) {
        const parent = btn.closest('.month-btn-group') as HTMLElement | null;
        if (parent) {
          const parentRect = parent.getBoundingClientRect();
          const btnRect = btn.getBoundingClientRect();
          monthIndicatorStyle = `left: ${btnRect.left - parentRect.left}px; width: ${btnRect.width}px;`;
        }
      } else {
        monthIndicatorStyle = 'left: 0; width: 0;';
      }
    });
  });

  function openMonthPicker() {
    monthPickerOpen = true;
  }

  function handleQuickMonth(offset: number) {
    const d = new Date();
    d.setMonth(d.getMonth() + offset);
    currentMonth = new Date(d.getFullYear(), d.getMonth(), 1);
  }

  function selectMonth(m: number) {
    currentMonth = new Date(currentMonth.getFullYear(), m, 1);
    monthPickerOpen = false;
  }

  function handlePrevMonth() {
    currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1);
  }

  function handleNextMonth() {
    currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);
  }

  // --- Days of Month ---
  const daysInMonth = $derived.by(() => {
    const y = currentMonth.getFullYear();
    const m = currentMonth.getMonth();
    return new Date(y, m + 1, 0).getDate();
  });

  const days = $derived(Array.from({ length: daysInMonth }, (_, i) => {
    const d = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), i + 1);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(i + 1).padStart(2, '0');
    return {
      day: i + 1,
      weekday: d.toLocaleDateString('fr-FR', { weekday: 'narrow' }).toUpperCase(),
      isWeekend: d.getDay() === 0 || d.getDay() === 6,
      iso: `${y}-${m}-${day}`,
    };
  }));

  // --- Employees & Leaves Grid ---
  function getLeaveForDay(employeeId: string, dayIso: string): { type: LeaveType; status: string } | null {
    const empMap = leaveMap.get(employeeId);
    if (!empMap) return null;
    return empMap.get(dayIso) ?? null;
  }

  // --- Legend ---
  const legendItems = LEAVE_TYPE_LEGEND;

  // Count days by type and pending for the legend
  const typeDayCount = $derived.by(() => {
    const counts = new Map<string, number>();
    for (const emp of teamData) {
      for (const day of emp.days) {
        const t = toFrontendCategory(day.type);
        counts.set(t, (counts.get(t) ?? 0) + 1);
      }
    }
    return counts;
  });
  const pendingCount = $derived.by(() => {
    let count = 0;
    for (const emp of teamData) {
      for (const day of emp.days) {
        if (day.status === 'PENDING') count++;
      }
    }
    return count;
  });
</script>


{#snippet Header()}
  <div class="flex items-center justify-between px-4 pr-9 py-2.5 bg-white border-b border-slate-100">
    <div class="flex items-center gap-2 pr-2">
      <!-- Month Navigation -->
      <div class="flex items-center bg-indigo-50 p-0.5 rounded-xl border border-slate-200/40">

        <!-- Chevrons grouped together on the left -->
        <div class="flex items-center mr-1">
          <Button
            variant="ghost"
            size="icon"
            onclick={handlePrevMonth}
            class="h-7 w-7 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-white transition-all"
          >
            <AppIcon name="chevron-left" size={15} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onclick={handleNextMonth}
            class="h-7 w-7 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-white transition-all"
          >
            <AppIcon name="chevron-right" size={15} />
          </Button>
        </div>

        <div class="w-px h-4 bg-indigo-200"></div>

        <!-- Quick actions : Mois préc. / Ce mois / Mois suiv. with sliding indicator -->
        <div class="relative flex items-center month-btn-group">
          <div
            class="absolute h-7 rounded-lg bg-white shadow-fine border border-slate-200/50 transition-all duration-250 ease-in-out z-10"
            style={monthIndicatorStyle}
          ></div>

          {#each monthQuickActions as action}
            <Button
              data-month-btn={action.key}
              variant="ghost"
              onclick={() => handleQuickMonth(action.value)}
              class={cn(
                "relative h-7 px-2.5 rounded-lg transition-all z-20 flex items-center justify-center border-none shadow-none text-[0.84rem]",
                activeMonthKey === action.key
                  ? "text-slate-900 font-medium cursor-pointer"
                  : "text-slate-500 hover:text-slate-700 hover:bg-slate-200/50 cursor-pointer"
              )}
            >
              <span class="text-[0.84rem]">{action.label}</span>
            </Button>
          {/each}
        </div>

        <div class="w-px h-3.5 bg-indigo-200 mx-1"></div>

        <!-- Month picker -->
        <div class="relative h-7 w-7">
          <button 
            type="button"
            onclick={openMonthPicker}
            class="h-7 w-7 rounded-lg flex items-center justify-center hover:bg-white hover:shadow-fine transition-all cursor-pointer"
          >
            <AppIcon name="calendar-days" size={15} class="text-slate-500" />
          </button>

          {#if monthPickerOpen}
            <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
            <div 
              class="fixed inset-0 z-30"
              onclick={() => monthPickerOpen = false}
              role="none"
            ></div>
            <div 
              class="absolute top-full left-1/2 -translate-x-1/2 mt-1 z-40 bg-white rounded-lg shadow-xl border border-slate-200 p-1 w-40 max-h-60 overflow-y-auto custom-scrollbar"
              onkeydown={handleKeydown}
              role="none"
            >
              {#each MONTHS as label, i}
                <button
                  type="button"
                  onclick={() => selectMonth(i)}
                  class={cn(
                    "w-full text-left px-3 py-1.5 rounded-md text-[0.84rem] transition-colors hover:bg-indigo-50 hover:text-indigo-700 cursor-pointer",
                    i === currentMonth.getMonth() && "bg-indigo-50 font-medium text-indigo-700"
                  )}
                >
                  {label.charAt(0).toUpperCase() + label.slice(1)} {currentMonth.getFullYear()}

                </button>
              {/each}
            </div>
          {/if}
        </div>

        <div class="w-px h-4 bg-indigo-200 mx-1.5"></div>

        <!-- Month label (white pill rightmost) -->
        <div class="flex items-center gap-1.5 pl-2 pr-1.5 py-0.5 bg-white rounded-lg shadow-fine">
          <AppIcon name="calendar" size={14} class="text-slate-400" />
          <span class="text-[0.82rem] text-slate-700 font-medium whitespace-nowrap capitalize">
            {monthLabel}
          </span>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-4">
      {#each legendItems as item}
        <div class="flex items-center gap-1.5">
          <div class={cn("h-2.5 w-2.5 rounded-sm", LEAVE_TYPE_COLORS[item.type].dot)}></div>
          <span class="text-[0.8rem] text-slate-500">{item.label}</span>
          {#if (typeDayCount.get(item.type) ?? 0) > 0}
            <span class={cn(
              "text-[0.7rem] font-medium px-1.5 py-0.5 rounded-full",
              LEAVE_TYPE_COLORS[item.type].bg,
              LEAVE_TYPE_COLORS[item.type].text
            )}>
              {typeDayCount.get(item.type)}j
            </span>
          {/if}
        </div>
      {/each}
      <div class="flex items-center gap-1.5">
        <div class="h-2.5 w-2.5 rounded-sm bg-slate-200 border border-dashed border-slate-300"></div>
        <span class="text-[0.8rem] text-slate-500">En attente</span>
        {#if pendingCount > 0}
          <span class="text-[0.7rem] font-medium px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-700">
            {pendingCount}j
          </span>
        {/if}
      </div>
    </div>
  </div>
{/snippet}


{#snippet DaysHeader()}
  <div class="flex sticky top-0 z-20 border-b border-slate-100 bg-white">
    <div class="w-52 shrink-0 px-4 py-2 border-r border-slate-100 bg-slate-50/50">
      <span class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
    </div>
    <div class="flex flex-1">
      {#each days as d}
        <div class={cn(
          "flex-1 min-w-9 shrink-0 flex flex-col items-center py-1.5 border-r border-slate-50 text-center",
          d.isWeekend ? "bg-slate-50/80" : "bg-white"
        )}>
          <span class="text-[0.6rem] font-medium text-slate-400 uppercase">{d.weekday}</span>
          <span class={cn("text-[0.72rem] font-medium", d.isWeekend ? "text-slate-400" : "text-slate-600")}>{d.day}</span>
        </div>
      {/each}
    </div>
  </div>
{/snippet}


<div class="flex h-full flex-col overflow-hidden">
  {@render Header()}

  <!-- Overhead loading bar during refetch -->
  {#if $teamQuery.isFetching}
    <div class="h-0.5 bg-slate-100 overflow-hidden shrink-0">
      <div class="h-full bg-primary animate-[loadingSlide_1.2s_ease-in-out_infinite] rounded-full" style="width: 30%"></div>
    </div>
  {/if}

  <!-- Gantt Grid -->
  <Tooltip.Provider delayDuration={400}>
    <div class="flex-1 overflow-auto custom-scrollbar">
      <div class="min-w-full w-max">
        {@render DaysHeader()}

        <!-- Employee Rows -->
        {#each employees as emp}
          <TeamGanttRow employee={{
            id: String(emp.id),
            name: emp.name,
            jobTitle: emp.jobTitle,
            orgUnit: emp.orgUnit || '',
            orgUnitType: emp.orgUnitType,
            avatarUrl: emp.avatarUrl,
          }} days={days} {getLeaveForDay} />
        {/each}
      </div>
    </div>
  </Tooltip.Provider>
</div>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
  :global {
    @keyframes loadingSlide {
      0% { transform: translateX(-100%); }
      50% { transform: translateX(200%); }
      100% { transform: translateX(400%); }
    }
  }
</style>

