<script lang="ts">
  import type { LeaveRequest } from '../../../types/types';
  import { 
    LEAVE_TYPE_LABELS, 
    LEAVE_TYPE_COLORS 
  } from '../../../types/types';
  import LeaveStatusBadge from '../../shared/LeaveStatusBadge.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { cn } from '@/utilities/common/css';
  import { leavesStore } from '../../../stores/leaves.svelte';
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";

  let { request }: { request: LeaveRequest } = $props();

  const typeColors = $derived(LEAVE_TYPE_COLORS[request.type]);
  const typeLabel = $derived(LEAVE_TYPE_LABELS[request.type]);
  const palette = $derived(getAvatarPalette(request.employeeName));

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  }

  function formatDateRange(start: string, end: string) {
    const s = formatDate(start);
    const e = formatDate(end);
    return s === e ? s : `${s} — ${e}`;
  }
</script>


<div class="group flex items-center px-6 py-3 border-b border-slate-50 hover:bg-slate-50/50 transition-colors cursor-pointer">
  <!-- Employee -->
  <div class="w-[25%] flex items-center gap-3 min-w-0">
    <Avatar class="h-10 w-10 border border-slate-200 shadow-fine shrink-0">
      <AvatarImage src="" alt={request.employeeName} />
      <AvatarFallback class={cn("font-bold text-[0.7rem] uppercase tracking-wider", palette.bg, palette.text)}>
        {getInitials(...request.employeeName.split(' '))}
      </AvatarFallback>
    </Avatar>
    <div class="min-w-0">
      <p class="text-[0.875rem] font-semibold text-slate-800 truncate group-hover:text-primary">{request.employeeName}</p>
      <p class="text-[0.75rem] text-slate-500 truncate">{request.department}</p>
    </div>
  </div>

  <!-- Type -->
  <div class="w-[15%]">
    <span class={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.75rem] font-medium",
      typeColors.bg, typeColors.text
    )}>
      <span class={cn("h-1.5 w-1.5 rounded-full", typeColors.dot)}></span>
      {typeLabel}
    </span>
  </div>

  <!-- Dates -->
  <div class="w-[20%]">
    <p class="text-[0.875rem] text-slate-700">{formatDateRange(request.startDate, request.endDate)}</p>
    <p class="text-[0.8rem] text-slate-500">{request.days} jour{request.days > 1 ? 's' : ''}</p>
  </div>

  <!-- Reason -->
  <div class="w-[20%] min-w-0">
    <p class="text-[0.85rem] text-slate-600 truncate">{request.reason || '—'}</p>
  </div>

  <!-- Status -->
  <div class="w-[10%]">
    <LeaveStatusBadge status={request.status} />
  </div>

  <!-- Actions -->
  <div class="w-[10%] flex items-center justify-end gap-2 pr-2">
    {#if request.status === 'pending'}
      <div class="flex items-center opacity-100 transition-opacity gap-2">
        <div class="relative">
          <TooltipWrapper content="Approuver">
            {#snippet children(props)}
              <Button
                {...props}
                variant="outline"
                size="sm"
              onclick={() => leavesStore.approveRequest(request.id)}
              class="h-7.5 w-7.5 p-0 border-emerald-200 text-emerald-600 hover:text-white hover:bg-emerald-500 hover:border-emerald-500 rounded-lg shadow-none transition-all cursor-pointer"
              >
                <AppIcon name="check" size={16} />
              </Button>
            {/snippet}
          </TooltipWrapper>
        </div>
        <div class="relative">
          <TooltipWrapper content="Refuser">
            {#snippet children(props)}
              <Button
                {...props}
                variant="outline"
                size="sm"
                onclick={() => leavesStore.rejectRequest(request.id)}
                class="h-7.5 w-7.5 p-0 border-rose-200 text-rose-500 hover:text-white hover:bg-rose-500 hover:border-rose-500 rounded-lg shadow-none transition-all cursor-pointer"
              >
                <AppIcon name="x" size={16} />
              </Button>
            {/snippet}
          </TooltipWrapper>
        </div>
      </div>
    {:else}
      <span class="text-[0.8rem] text-slate-400 font-medium truncate">{request.approver ?? ''}</span>
    {/if}
  </div>
</div>

