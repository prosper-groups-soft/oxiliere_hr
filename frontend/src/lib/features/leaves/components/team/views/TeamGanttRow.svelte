<script lang="ts">
  import { leavesStore } from '../../../stores/leaves.svelte';
  import { LEAVE_TYPE_COLORS, LEAVE_TYPE_LABELS } from '../../../types/types';
  import { cn } from '@/utilities/common/css';

  interface Props {
    employee: {
      id: number;
      name: string;
      department: string;
      avatarUrl?: string;
    };
    daysInMonth: Date[];
  }

  let { employee, daysInMonth }: Props = $props();

  // Get leaves for this employee in the current month
  const employeeLeaves = $derived.by(() => {
    return leavesStore.requests.filter(req => 
      req.employeeId === employee.id && 
      req.status === 'approved' &&
      isLeaveInMonth(req.startDate, req.endDate)
    );
  });

  // Check if a leave period overlaps with the current month
  function isLeaveInMonth(startDate: string, endDate: string): boolean {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const monthStart = daysInMonth[0];
    const monthEnd = daysInMonth[daysInMonth.length - 1];
    
    return !(end < monthStart || start > monthEnd);
  }

  // Check if a specific day has leave
  function getLeaveForDay(date: Date) {
    const dateStr = date.toISOString().split('T')[0];
    return employeeLeaves.find(leave => {
      return leave.startDate <= dateStr && leave.endDate >= dateStr;
    });
  }

  // Check if day is weekend
  function isWeekend(date: Date) {
    return date.getDay() === 0 || date.getDay() === 6;
  }
</script>


<div class="flex border-b border-slate-100 hover:bg-slate-50/30 transition-colors">
  <!-- Employee Info -->
  <div class="w-48 px-4 py-3 bg-white border-r border-slate-200">
    <div class="flex items-center gap-2">
      <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
        {#if employee.avatarUrl}
          <img src={employee.avatarUrl} alt={employee.name} class="w-full h-full rounded-full object-cover" />
        {:else}
          <span class="text-[0.7rem] font-medium text-slate-600">
            {employee.name.split(' ').map(n => n[0]).join('').toUpperCase()}
          </span>
        {/if}
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-[0.85rem] font-medium text-slate-800 truncate">{employee.name}</div>
        <div class="text-[0.7rem] text-slate-500 truncate">{employee.department}</div>
      </div>
    </div>
  </div>

  <!-- Day Cells -->
  {#each daysInMonth as day (day.toISOString())}
    {@const leave = getLeaveForDay(day)}
    {@const isWeekendDay = isWeekend(day)}
    
    <div 
      class={cn(
        "w-10 border-r border-slate-100 relative group transition-colors",
        isWeekendDay ? "bg-slate-50" : "bg-white",
        leave ? "cursor-pointer" : ""
      )}
    >
      {#if leave}
        <div 
          class={cn(
            "absolute inset-0.5 rounded-md border border-slate-200/50 flex items-center justify-center group-hover:border-slate-300 transition-all",
            LEAVE_TYPE_COLORS[leave.type].bg
          )}
          title={`${LEAVE_TYPE_LABELS[leave.type]} - ${leave.reason || 'Sans motif'}`}
        >
          <div class="flex items-center gap-1">
            <div class={cn("w-1.5 h-1.5 rounded-full", LEAVE_TYPE_COLORS[leave.type].dot)}></div>
            <div class={cn("text-[0.6rem] font-medium truncate", LEAVE_TYPE_COLORS[leave.type].text)}>
              {LEAVE_TYPE_LABELS[leave.type].charAt(0)}
            </div>
          </div>
        </div>
      {/if}
    </div>
  {/each}
</div>
