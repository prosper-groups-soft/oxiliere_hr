<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { 
    Avatar, 
    AvatarFallback, 
    AvatarImage 
  } from "@/components/ui/avatar";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import { cn } from "@/utilities/common/css";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import {
    ADVANCE_STATUS_LABELS,
    ADVANCE_STATUS_COLORS,
    ADVANCE_RISK_LABELS,
    type Advance
  } from "@/features/payroll/types/types";
  import { formatDate } from "date-fns";

  let {
    advance,
    showActions = false,
    onApprove,
    onReject,
    onClick
  }: {
    advance: Advance;
    showActions?: boolean;
    onApprove?: (id: string) => void;
    onReject?: (id: string) => void;
    onClick?: (advance: Advance) => void;
  } = $props();

  function getRiskColor(risk: Advance['riskLevel']) {
    switch (risk) {
      case 'low': return 'text-emerald-600 bg-emerald-50 border-emerald-100';
      case 'medium': return 'text-amber-600 bg-amber-50 border-amber-100';
      case 'high': return 'text-rose-600 bg-rose-50 border-rose-100';
    }
  }

  function getRiskIcon(risk: Advance['riskLevel']) {
    switch (risk) {
      case 'high': return 'alert-circle';
      case 'medium': return 'alert-triangle';
      case 'low': return 'shield-check';
    }
  }

  function getProgress(advance: Advance): number {
    return ((advance.amount - advance.remainingAmount) / advance.amount) * 100;
  }

  const palette = $derived(getAvatarPalette(advance.employeeName));
  const progress = $derived(getProgress(advance));
</script>


<div
  class="group bg-white rounded-xl border border-slate-200 p-4 hover:shadow-fine hover:border-slate-300 transition-all cursor-pointer"
  onclick={() => onClick?.(advance)}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && onClick?.(advance)}
>

  <div class="flex justify-between mb-1.5">
    <div class="flex items-start gap-3">
      <Avatar class="h-11 w-11 border border-slate-200 shrink-0">
        <AvatarImage src="" alt={advance.employeeName} />
        <AvatarFallback class={cn("font-bold text-[0.8rem] uppercase tracking-wider", palette.bg, palette.text)}>
          {getInitials(...advance.employeeName.split(' '))}
        </AvatarFallback>
      </Avatar>
      <div class="flex-1 min-w-0">
        <p class="text-[0.85rem] font-semibold text-slate-800 truncate group-hover:text-primary transition-colors">
          {advance.employeeName}
        </p>
        <p class="text-[0.77rem] text-slate-500 truncate">ID: {advance.employeeId}</p>
      </div>
    </div>

    <div class="text-right">
      <p class="text-[0.87rem] font-bold text-slate-800">
        {advance.amount.toLocaleString('fr-FR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}
      </p>
      <p class="text-[0.79rem] text-muted-foreground mt-0.5 leading-tight">{advance.reason}</p>
    </div>
  </div>

  {#if advance.status === 'approved'}
    <div class="mb-1.5">
      <div class="flex items-center justify-between mb-1.5">
        <span class="text-[0.82rem] text-slate-600">Remboursement</span>
        <span class="text-[0.82rem] font-medium text-slate-700">{Math.round(progress)}%</span>
      </div>
      <div class="h-1 bg-slate-100 rounded-full overflow-hidden">
        <div
          class="h-full bg-emerald-500 rounded-full transition-all"
          style="width: {progress}%"
        ></div>
      </div>
      <div class="flex justify-between mt-1.5 text-slate-600">
        <span class="text-[0.82rem]">Reste: {advance.remainingAmount.toLocaleString('fr-FR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}</span>
        <span class="text-[0.82rem]">{advance.monthlyDeduction.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}/m</span>
      </div>
    </div>
  {/if}

  <div class="flex items-center gap-1.5 text-slate-500 mb-1.5">
    <AppIcon name="calendar" size={14} />
    <span class="text-[0.84rem]">Demande du {formatDate(new Date(advance.requestDate), "dd/MM/yyyy")}</span>
  </div>

  <div class="flex items-center justify-between pt-1.5 border-t border-slate-100">
    <div class="flex items-center gap-2">
      <span class={cn(
        "inline-flex items-center px-2 py-0.5 rounded-full text-[0.8rem] font-medium",
        ADVANCE_STATUS_COLORS[advance.status].bg,
        ADVANCE_STATUS_COLORS[advance.status].text
      )}>
        {ADVANCE_STATUS_LABELS[advance.status]}
      </span>
      <span class={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[0.8rem] font-medium border",
        getRiskColor(advance.riskLevel)
      )}>
        <AppIcon name={getRiskIcon(advance.riskLevel)} size={13} />
        {ADVANCE_RISK_LABELS[advance.riskLevel]}
      </span>
    </div>

    {#if showActions && onApprove && onReject && advance.status === 'pending'}
      <div class="flex items-center gap-3">
        
        <div class="inline-block">
          <Button
            variant="link"
            size="sm"
            onclick={(e) => { e.stopPropagation(); onReject(advance.id); }}
            class="h-auto p-0 text-rose-500 hover:text-rose-700 font-medium text-[0.8rem] decoration-transparent hover:no-underline flex items-center gap-1 transition-colors"
          >
            <AppIcon name="x" size={14} />
            Rejeter
          </Button>
        </div>
        <div class="inline-block">
          <Button
            variant="link"
            size="sm"
            onclick={(e) => { e.stopPropagation(); onApprove(advance.id); }}
            class="h-auto p-0 text-emerald-600 hover:text-emerald-800 font-bold text-[0.8rem] decoration-transparent hover:no-underline flex items-center gap-1 transition-colors"
          >
            <AppIcon name="check" size={14} />
            Approuver
          </Button>
        </div>

      </div>
    {/if}
  </div>
</div>

