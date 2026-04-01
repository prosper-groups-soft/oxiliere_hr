<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { fade } from 'svelte/transition';

  let { payslip, onClick }: { payslip: any; onClick?: (payslipId: string) => void } = $props();

  // --- État Tooltip ---
  let tooltipPosition = $state<{ x: number; y: number } | null>(null);
  const palette = $derived(getAvatarPalette(payslip.employeeName));

  // --- Logique des montants ---
  const stats = $derived.by(() => {
    const gross = payslip.grossPay || 0;
    const net = payslip.netPay || 0;
    
    const taxes = payslip.lines?.filter((l: any) => l.type === 'deduction' && !l.label.toLowerCase().includes('avance'))
                  .reduce((sum: number, l: any) => sum + Math.abs(l.amount), 0) || 0;
    
    const advances = payslip.lines?.filter((l: any) => l.type === 'deduction' && l.label.toLowerCase().includes('avance'))
                     .reduce((sum: number, l: any) => sum + Math.abs(l.amount), 0) || 0;

    return { 
      gross, net, taxes, advances,
      netP: (net / gross) * 100,
      taxP: (taxes / gross) * 100,
      advP: (advances / gross) * 100
    };
  });

  // --- Fonctions Tooltip ---
  function updateTooltip(event: MouseEvent) {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    tooltipPosition = {
      x: rect.left + rect.width / 2,
      y: rect.top - 8
    };
  }

  function hideTooltip() {
    tooltipPosition = null;
  }
</script>


<div 
  in:fade={{ duration: 150 }}
  onclick={() => onClick?.(payslip.id)}
  class="group/row flex items-center h-16 px-6 bg-white border-b border-slate-100 hover:bg-slate-50/80 transition-colors cursor-pointer"
  role="none"
>
  <div class="flex items-center w-[30%] min-w-0">
    <Avatar class="h-10 w-10 shrink-0 rounded-full border border-slate-200">
      <AvatarImage src={payslip.avatarUrl} alt={payslip.employeeName} />
      <AvatarFallback class={cn("text-[0.7rem] font-bold", palette.bg, palette.text)}>
        {getInitials(...payslip.employeeName.split(' '))}
      </AvatarFallback>
    </Avatar>
    <div class="flex flex-col ml-3 min-w-0">
      <span class="text-[0.88rem] text-slate-900 font-medium truncate leading-tight">{payslip.employeeName}</span>
      <span class="text-[0.8rem] text-slate-400 truncate mt-0.5">{payslip.department}</span>
    </div>
  </div>

  <div class="flex items-center w-[20%] gap-2">
    {#if payslip.lines?.some((l: any) => l.label.toLowerCase().includes('prime'))}
      <div class="px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded text-[0.6rem] font-bold uppercase border border-emerald-100/50">
        Prime
      </div>
    {/if}
    {#if payslip.lines?.some((l: any) => l.label.toLowerCase().includes('avance'))}
      <div class="px-2 py-0.5 bg-amber-50 text-amber-600 rounded text-[0.6rem] font-bold uppercase border border-amber-100/50">
        Avance
      </div>
    {/if}
  </div>

  <div class="flex flex-col w-[25%] px-6 gap-2">
    <div 
      class="relative h-1.5 w-full bg-slate-100 rounded-full overflow-hidden flex cursor-help shadow-inner transition-all group-hover/row:h-2"
      onmouseenter={updateTooltip}
      onmouseleave={hideTooltip}
      role="none"
    >
      <div class="h-full bg-emerald-500 transition-all" style="width: {stats.netP}%"></div>
      <div class="h-full bg-rose-400/70 transition-all" style="width: {stats.taxP}%"></div>
      <div class="h-full bg-amber-400 transition-all" style="width: {stats.advP}%"></div>
    </div>
    
    <div class="flex items-center gap-3 opacity-0 group-hover/row:opacity-100 transition-opacity duration-300">
      <div class="flex items-center gap-1">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
        <span class="text-[0.6rem] text-slate-700 font-medium uppercase tracking-tighter">Net</span>
      </div>
      <div class="flex items-center gap-1">
        <div class="w-1.5 h-1.5 rounded-full bg-rose-400/70"></div>
        <span class="text-[0.6rem] text-slate-700 font-medium uppercase tracking-tighter">Taxes</span>
      </div>
      {#if stats.advances > 0}
        <div class="flex items-center gap-1">
          <div class="w-1.5 h-1.5 rounded-full bg-amber-400"></div>
          <span class="text-[0.6rem] text-slate-700 font-medium uppercase tracking-tighter">Avance</span>
        </div>
      {/if}
    </div>
  </div>

  <div class="flex items-center justify-end w-[25%] gap-6">
    <div class="text-right">
      <p class="text-[0.95rem] text-slate-900 font-medium tabular-nums leading-none tracking-tight">
        {stats.net.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}
      </p>
      <p class="text-[0.65rem] text-slate-400 font-bold mt-1.5 uppercase tracking-widest">Net versé</p>
    </div>
    
    <button class="p-2 rounded-lg text-slate-300 hover:text-primary hover:bg-white border border-transparent hover:border-slate-200 transition-all">
      <AppIcon name="chevron-right" size={18} />
    </button>
  </div>
</div>


{#if tooltipPosition}
  <div 
    class="fixed z-9999 pointer-events-none"
    style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px; transform: translateX(-50%) translateY(-100%);"
    transition:fade={{ duration: 100 }}
  >
    <div class="bg-slate-900 text-white rounded-lg p-3 shadow-2xl min-w-[230px] border border-slate-700">
      <div class="flex justify-between items-center mb-2 pb-2 border-b border-slate-700">
        <span class="text-[0.65rem] text-slate-400 uppercase font-black tracking-wider">Salaire Brut</span>
        <span class="font-mono text-xs font-bold">{stats.gross.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}</span>
      </div>
      
      <div class="space-y-2 mt-2">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500"></div>
            <span class="text-slate-400 text-[0.75rem]">Net à payer</span>
          </div>
          <span class="text-emerald-400 font-bold text-[0.75rem]">{stats.net.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}</span>
        </div>
        
        {#if stats.taxes > 0}
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <div class="w-1.5 h-1.5 rounded-full bg-rose-400"></div>
              <span class="text-slate-400 text-[0.75rem]">Détails taxes</span>
            </div>
            <span class="text-rose-400 text-[0.75rem] font-medium">-{stats.taxes.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}</span>
          </div>
        {/if}

        {#if stats.advances > 0}
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <div class="w-1.5 h-1.5 rounded-full bg-amber-400"></div>
              <span class="text-slate-400 text-[0.75rem]">Remb. avance</span>
            </div>
            <span class="text-amber-400 text-[0.75rem] font-medium">-{stats.advances.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}</span>
          </div>
        {/if}
      </div>

      <div class="w-2.5 h-2.5 bg-slate-900 border-r border-b border-slate-700 rotate-45 absolute -bottom-1 left-1/2 -translate-x-1/2"></div>
    </div>
  </div>
{/if}

