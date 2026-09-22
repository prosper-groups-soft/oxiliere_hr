<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { PAYROLL_STATUS_COLORS, PAYROLL_STATUS_LABELS, type Payslip } from "@/hr/modules/payroll/types/types";
  import { cn } from "@/hr/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { get_api_base_origin } from "@/hr/utilities/http/urls";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";


  type Props = {
    payslip: Payslip;
    onClick: (payslipId: string) => void;
  };

  let { payslip, onClick }: Props = $props();

  function mapPayslipStatus(raw: string): keyof typeof PAYROLL_STATUS_COLORS {
    const s = (raw ?? '').toString().toUpperCase();
    if (s === 'PAID') return 'paid';
    if (s === 'CONFIRMED') return 'calculated';
    if (s === 'REVIEW' || s === 'CALCULATED') return 'calculated';
    if (s === 'CANCELED' || s === 'CANCELLED') return 'closed';
    const low = (raw ?? 'draft').toString().toLowerCase() as any;
    return (low in PAYROLL_STATUS_COLORS ? low : 'draft') as any;
  }

  // Statut du bulletin (si disponible)
  const rawStatus = $derived((payslip as any).status ?? 'REVIEW');
  const statusKey = $derived(mapPayslipStatus(rawStatus));
  const statusColors = $derived(PAYROLL_STATUS_COLORS[statusKey] ?? PAYROLL_STATUS_COLORS.draft);
  const statusLabel = $derived(PAYROLL_STATUS_LABELS[statusKey] ?? rawStatus);

  // Le reste suit.
  const palette = $derived(getAvatarPalette(payslip.employee?.fullName ?? '?'));
  const photo = $derived(getMediaUrl((payslip as any).photo_path ?? (payslip as any).avatarUrl ?? (payslip.employee as any)?.avatarUrl ?? null));
  // Devise du RUN (config.currency figée dans payslip.currency à la génération) — prioritaire sur contract_currency
  const currency = $derived(((payslip as any).currency ?? (payslip as any).payroll_run_currency ?? (payslip as any).payrollRunCurrency ?? payslip.currency ?? 'CDF') as string);
  
  function num(v: any): number { 
    const n = Number(v); 
    return Number.isFinite(n) ? n : 0; 
  }
  
  const gross = $derived(num((payslip as any).gross_amount ?? (payslip as any).grossAmount ?? payslip.summary?.grossSalary ?? 0));
  const net = $derived(num((payslip as any).net_amount ?? (payslip as any).netAmount ?? payslip.summary?.netPay ?? 0));
  const cnss = $derived(num((payslip as any).cnss_amount ?? 0));
  const irpp = $derived(num((payslip as any).ipr_amount ?? (payslip as any).irpp_amount ?? 0));
  const workedDays = $derived(num((payslip as any).worked_days ?? 0));
  const jobTitle = $derived((payslip.employee as any)?.jobTitle ?? (payslip as any).job_title ?? '');
  const matricule = $derived((payslip.employee as any)?.matricule ?? '');
  
  function fmt(n: number, c = currency) { 
    try { 
      return num(n).toLocaleString('fr-FR', { style: 'currency', currency: c as any, maximumFractionDigits: 0 }); 
    } catch {
       return `${num(n).toLocaleString('fr-FR')} ${c}`; 
    } 
  }
</script>


<div
  onclick={() => onClick(payslip.id)}
  class="group flex items-center py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
  role="none"
>
  <!-- Employé : photo + identité -->
  <div class="w-[30%] flex items-center gap-3 min-w-0">
    <Avatar class="h-11 w-11 border border-slate-200 shadow-fine shrink-0">
      <AvatarImage src={photo} alt={payslip.employee?.fullName ?? ''} class="object-cover" />
      <AvatarFallback class={cn("font-bold text-[0.83rem] uppercase tracking-wider", palette.bg, palette.text)}>
        {getInitials(...(payslip.employee?.fullName ?? '?').split(' '))}
      </AvatarFallback>
    </Avatar>
    <div class="min-w-0">
      <p class="text-[0.85rem] font-semibold text-slate-800 truncate leading-tight group-hover:text-indigo-600 transition-colors">{payslip.employee?.fullName ?? '—'}</p>
      <p class="text-[0.83rem] text-slate-500 truncate">{jobTitle || 'Poste non défini'}{matricule ? ` • ${matricule}` : ''}</p>
    </div>
  </div>

  <!-- Unité -->
  <div class="w-[16%] flex items-center gap-1.5 min-w-0">
    <AppIcon name="building-2" size={16} class="text-slate-400 shrink-0" />
    <span class="text-[0.83rem] text-slate-600 truncate">{payslip.employee?.orgUnit ?? (payslip as any).org_unit ?? '—'}</span>
  </div>

  <!-- Brut / Net (devise du run) -->
  <div class="w-[22%] flex flex-col gap-0.5 text-right pr-2">
    <span class="text-[0.85rem] font-semibold text-slate-800 tabular-nums">{fmt(net)}</span>
    <span class="text-[0.83rem] text-slate-500 tabular-nums">Brut {fmt(gross)} • CNSS {fmt(cnss)} • IRPP {fmt(irpp)}</span>
  </div>

  <!-- Présence -->
  <div class="w-[12%] flex items-center gap-1.5 justify-center">
    <AppIcon name="calendar" size={14} class="text-slate-400" />
    <span class="text-[0.83rem] text-slate-600">{workedDays} j travaillés</span>
  </div>

  <!-- Statut -->
  <div class="w-[12%] flex items-center justify-end">
    <span class={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.83rem] font-medium", statusColors.bg, statusColors.text)}>
      <span class={cn("h-1.5 w-1.5 rounded-full", statusColors.dot)}></span>
      {statusLabel}
    </span>
  </div>

  <!-- Actions — menu comme EmployeeCard -->
  <div class="w-[8%] flex items-center justify-end" onclick={(e)=>e.stopPropagation()} role="none">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        {#snippet child({ props })}
          <button {...props} class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-400 hover:text-slate-600 outline-none cursor-pointer">
            <AppIcon name="more-vertical" size={18} />
          </button>
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Item onclick={()=>onClick(payslip.id)} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
          <AppIcon name="eye" size={18} class="text-slate-500" />
          Voir détail
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={()=>window.open(`${get_api_base_origin()}/api/payroll/payslips/${payslip.id}/export/`, '_blank')} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
          <AppIcon name="download" size={18} class="text-slate-500" />
          Télécharger PDF
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
</div>

