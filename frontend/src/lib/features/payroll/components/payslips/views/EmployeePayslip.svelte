<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { PAYROLL_STATUS_COLORS, PAYROLL_STATUS_LABELS, type Payslip } from "@/features/payroll/types/types";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";

  type Props = {
    payslip: Payslip;
    onClick: (payslipId: string) => void;
  };

  let { payslip, onClick }: Props = $props();

  /** Palette de couleurs pour l'avatar, dérivée du nom complet */
  const palette = $derived(getAvatarPalette(payslip.employee.fullName));
</script>


<div
  onclick={() => onClick(payslip.id)}
  class="group flex items-center px-6 py-2.5 border-b border-slate-50 hover:bg-slate-50/50 transition-colors cursor-pointer"
  role="none"
>
  <!-- Colonne employé : avatar + nom + département -->
  <div class="w-[35%] flex items-center gap-3 min-w-0">
    <Avatar class="h-10 w-10 border border-slate-200 shadow-fine shrink-0">
      <AvatarImage src="" alt={payslip.employee.fullName} />
      <AvatarFallback class={cn("font-bold text-[0.7rem] uppercase tracking-wider", palette.bg, palette.text)}>
        {getInitials(...payslip.employee.fullName.split(' '))}
      </AvatarFallback>
    </Avatar>
    <div class="min-w-0">
      <p class="text-[0.875rem] font-medium text-slate-800 truncate leading-tight group-hover:text-primary">{payslip.employee.fullName}</p>
      <p class="text-[0.75rem] text-slate-500 truncate">{payslip.employee.orgUnit}</p>
    </div>
  </div>

  <!-- Colonne identifiant du bulletin -->
  <div class="w-[20%]">
    <p class="text-[0.875rem] text-slate-700">Bulletin #{payslip.id}</p>
    <p class="text-[0.8rem] text-slate-500">Net payé</p>
  </div>

  <!-- Colonne statut -->
  <div class="w-[20%]">
    <span class={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.75rem] font-medium",
      PAYROLL_STATUS_COLORS[payslip.status].bg,
      PAYROLL_STATUS_COLORS[payslip.status].text
    )}>
      <span class={cn("h-1.5 w-1.5 rounded-full", PAYROLL_STATUS_COLORS[payslip.status].dot)}></span>
      {PAYROLL_STATUS_LABELS[payslip.status]}
    </span>
  </div>

  <!-- Colonne montant net -->
  <div class="w-[15%] text-right">
    <p class="text-[0.875rem] font-semibold text-slate-800">
      {payslip.summary.netPay.toLocaleString('fr-FR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}
    </p>
  </div>

  <!-- Colonne action (chevron) -->
  <div class="w-[10%] flex items-center justify-end">
    <div class="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 transition-colors group-hover:border-primary/30 group-hover:text-primary">
      <AppIcon name="chevron-right" size={16} />
    </div>
  </div>
</div>

