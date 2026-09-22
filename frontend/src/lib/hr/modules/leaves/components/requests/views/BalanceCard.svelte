<script lang="ts">
  import type { LeaveBalance } from '../../../types/types';
  import { LEAVE_TYPE_LABELS, LEAVE_TYPE_COLORS } from '../../../constants/leaves';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { cn } from '@/hr/utilities/common/css';


  let { balance }: { balance: LeaveBalance } = $props();

  const colors = $derived(LEAVE_TYPE_COLORS[balance.type]);
  const label = $derived(LEAVE_TYPE_LABELS[balance.type]);
  const percentage = $derived(balance.allocated > 0 ? Math.round((balance.taken / balance.allocated) * 100) : 0);
  const circumference = 2 * Math.PI * 28; // radius = 28
  const dashOffset = $derived(circumference - (percentage / 100) * circumference);

  const iconMap: Record<string, string> = {
    annual: 'sun',
    sick: 'heart-pulse',
    circumstantial: 'calendar-heart',
    unpaid: 'wallet',
  };
</script>


<div class="flex flex-col gap-3 p-4 bg-white border border-slate-100 rounded-xl hover:border-slate-200 transition-all">
  <div class="flex items-start justify-between">
    <div class="flex items-center gap-2.5">
      <div class={cn("h-8 w-8 rounded-lg flex items-center justify-center", colors.bg)}>
        <AppIcon name={iconMap[balance.type] ?? 'calendar'} size={16} class={colors.text} />
      </div>
      <div>
        <p class="text-[0.84rem] font-semibold text-slate-800">{label}</p>
        <p class="text-[0.72rem] text-slate-400">{balance.allocated} jours alloués</p>
      </div>
    </div>

    <!-- Circular Progress -->
    <div class="relative h-16 w-16 flex items-center justify-center">
      <svg class="transform -rotate-90" width="64" height="64">
        <circle cx="32" cy="32" r="28" stroke="#f1f5f9" stroke-width="4" fill="none" />
        <circle
          cx="32" cy="32" r="28"
          stroke={balance.type === 'annual' ? '#3b82f6' : balance.type === 'sick' ? '#f43f5e' : balance.type === 'circumstantial' ? '#f59e0b' : '#94a3b8'}
          stroke-width="4" fill="none"
          stroke-linecap="round"
          stroke-dasharray={circumference}
          stroke-dashoffset={dashOffset}
          class="transition-all duration-700 ease-out"
        />
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-[0.9rem] font-bold text-slate-800">{balance.remaining}</span>
        <span class="text-[0.55rem] text-slate-400 uppercase tracking-wider font-medium">restants</span>
      </div>
    </div>
  </div>

  <!-- Progress bar -->
  <div class="flex items-center gap-3 text-[0.72rem] text-slate-500">
    <div class="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
      <div 
        class={cn("h-full rounded-full transition-all duration-700 ease-out", colors.dot)}
        style="width: {percentage}%"
      ></div>
    </div>
    <span class="text-[0.7rem] font-medium text-slate-400 shrink-0">{balance.taken}/{balance.allocated}</span>
  </div>

  {#if balance.expiringDays && balance.expiringDays > 0}
    <div class="flex items-center gap-1.5 px-2.5 py-1.5 bg-amber-50 border border-amber-100 rounded-lg">
      <AppIcon name="alert-triangle" size={13} class="text-amber-500 shrink-0" />
      <span class="text-[0.7rem] text-amber-700 font-medium">
        {balance.expiringDays} jour{balance.expiringDays > 1 ? 's' : ''} de report expire{balance.expiringDays > 1 ? 'nt' : ''} le {new Date(balance.expiryDate!).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
      </span>
    </div>
  {/if}
</div>
