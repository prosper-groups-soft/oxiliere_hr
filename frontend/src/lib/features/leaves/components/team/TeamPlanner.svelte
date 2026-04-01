<script lang="ts">
  import { leavesStore } from '../../stores/leaves.svelte';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { LEAVE_TYPE_COLORS, LEAVE_TYPE_LABELS } from '../../types/types';
  import type { LeaveType } from '../../types/types';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { cn } from '@/utilities/common/css';
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";

  // --- Month Navigation ---
  let currentMonth = $state(new Date(2026, 2, 1)); // March 2026

  const monthLabel = $derived(
    currentMonth.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
  );

  function prevMonth() {
    currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1);
  }
  function nextMonth() {
    currentMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1);
  }
  function goToday() {
    currentMonth = new Date(2026, 2, 1);
  }

  // --- Days of Month ---
  const daysInMonth = $derived.by(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    return new Date(year, month + 1, 0).getDate();
  });

  const days = $derived(Array.from({ length: daysInMonth }, (_, i) => {
    const d = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), i + 1);
    return {
      day: i + 1,
      weekday: d.toLocaleDateString('fr-FR', { weekday: 'narrow' }).toUpperCase(),
      isWeekend: d.getDay() === 0 || d.getDay() === 6,
      iso: d.toISOString().split('T')[0],
    };
  }));

  // --- Employees & Leaves Grid ---
  const employees = $derived(employeeStore.employees.slice(0, 12));

  function getLeaveForDay(employeeId: number, dayIso: string): { type: LeaveType; status: string } | null {
    const request = leavesStore.requests.find(r =>
      r.employeeId === employeeId &&
      r.status !== 'rejected' &&
      dayIso >= r.startDate &&
      dayIso <= r.endDate
    );
    if (!request) return null;
    return { type: request.type, status: request.status };
  }

  // --- Legend ---
  const legendItems: { type: LeaveType; label: string }[] = [
    { type: 'annual', label: 'Annuel' },
    { type: 'sick', label: 'Maladie' },
    { type: 'circumstantial', label: 'Circonstanciel' },
    { type: 'unpaid', label: 'Sans solde' },
  ];
</script>


{#snippet Header()}
  <div class="flex items-center justify-between px-6 py-3 border-b border-slate-100 pr-9">
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-1 bg-white border border-slate-200 rounded-lg shadow-fine overflow-hidden">
        <button onclick={prevMonth} class="h-7.5 w-7.5 flex items-center justify-center hover:bg-slate-50 transition-colors cursor-pointer">
          <AppIcon name="prev" size={16} class="text-slate-500" />
        </button>
        <button onclick={goToday} class="h-7.5 px-3 text-[0.84rem] font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer capitalize min-w-36 text-center">
          {monthLabel}
        </button>
        <button onclick={nextMonth} class="h-7.5 w-7.5 flex items-center justify-center hover:bg-slate-50 transition-colors cursor-pointer">
          <AppIcon name="next" size={16} class="text-slate-500" />
        </button>
      </div>

      <Button variant="outline" onclick={goToday} class="h-7.5 px-3 text-[0.84rem] rounded-lg shadow-fine border-slate-200">
        Aujourd'hui
      </Button>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-4">
      {#each legendItems as item}
        <div class="flex items-center gap-1.5">
          <div class={cn("h-2.5 w-2.5 rounded-sm", LEAVE_TYPE_COLORS[item.type].dot)}></div>
          <span class="text-[0.8rem] text-slate-500">{item.label}</span>
        </div>
      {/each}
      <div class="flex items-center gap-1.5">
        <div class="h-2.5 w-2.5 rounded-sm bg-slate-200 border border-dashed border-slate-300"></div>
        <span class="text-[0.8rem] text-slate-500">En attente</span>
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


{#snippet LeaveIndicator(leave: { type: LeaveType; status: string })}
  <div 
    class={cn(
      "w-7 h-6 rounded-sm flex items-center justify-center",
      leave.status === 'pending'
        ? "bg-slate-100 border border-dashed border-slate-300"
        : LEAVE_TYPE_COLORS[leave.type].bg
    )}
    title={`${LEAVE_TYPE_LABELS[leave.type]} (${leave.status === 'pending' ? 'En attente' : 'Approuvé'})`}
  >
    {#if leave.status !== 'pending'}
      <div class={cn("h-1.5 w-1.5 rounded-full", LEAVE_TYPE_COLORS[leave.type].dot)}></div>
    {/if}
  </div>
{/snippet}


{#snippet EmployeeRow(emp: any)}
  {@const palette = getAvatarPalette(emp.name)}
  <div class="group flex border-b border-slate-50 hover:bg-slate-50/30 transition-colors">
    <div class="w-52 shrink-0 px-4 py-2.5 border-r border-slate-100 flex items-center gap-2.5">
      <div class={cn(
        "h-10 w-10 rounded-full flex items-center justify-center text-[0.7rem] font-bold shrink-0 uppercase",
        palette.bg,
        palette.text
      )}>
        {getInitials(emp.name)}
      </div>
      <div class="min-w-0">
        <p class="text-[0.83rem] font-medium text-slate-700 truncate group-hover:text-primary">{emp.name}</p>
        <p class="text-[0.8rem] text-slate-500 truncate">{emp.department}</p>
      </div>
    </div>
    <div class="flex flex-1">
      {#each days as d}
        {@const leave = getLeaveForDay(emp.id, d.iso)}
        <div class={cn(
          "flex-1 min-w-9 h-10 shrink-0 border-r border-slate-50 flex items-center justify-center",
          d.isWeekend ? "bg-slate-50/60" : "",
        )}>
          {#if leave}
            {@render LeaveIndicator(leave)}
          {/if}
        </div>
      {/each}
    </div>
  </div>
{/snippet}


<div class="flex h-full flex-col overflow-hidden">
  {@render Header()}

  <!-- Gantt Grid -->
  <div class="flex-1 overflow-auto custom-scrollbar">
    <div class="min-w-full w-max">
      {@render DaysHeader()}

      <!-- Employee Rows -->
      {#each employees as emp}
        {@render EmployeeRow(emp)}
      {/each}
    </div>
  </div>
</div>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

