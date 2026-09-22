<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { cn } from "@/utilities/common/css";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { fade } from "svelte/transition";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import type { Advance, AdvanceRiskLevel, AdvanceStatus } from "@/hr/payroll/types/types";
  import { ADVANCE_STATUS_LABELS, ADVANCE_STATUS_COLORS, ADVANCE_RISK_LABELS } from "@/hr/payroll/types/types";


  let {
    advance,
    index = 0,
    onClick,
    onApprove,
    onReject,
    onActivate,
    onEdit,
    onSubmit,
    onViewDetail
  } = $props<{
    advance: Advance;
    onClick?: (advance: Advance) => void;
    onApprove?: (advance: Advance) => void;
    onReject?: (advance: Advance) => void;
    onActivate?: (id: string) => void;
    onEdit?: (advance: Advance) => void;
    onSubmit?: (advance: Advance) => void;
    onViewDetail?: (advance: Advance) => void;
    index?: number;
  }>();
  

  const RISK_STYLES: Record<AdvanceRiskLevel, string> = {
    LOW:    'bg-emerald-50 text-emerald-700 border-emerald-200',
    MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200',
    HIGH:   'bg-rose-50 text-rose-700 border-rose-200',
  };

  const statusColor = $derived(ADVANCE_STATUS_COLORS[advance.status as AdvanceStatus] ?? ADVANCE_STATUS_COLORS.PENDING);
  const statusLabel = $derived(ADVANCE_STATUS_LABELS[advance.status as AdvanceStatus] ?? ADVANCE_STATUS_LABELS.PENDING);
  const riskClass = $derived(RISK_STYLES[advance.risk_level as AdvanceRiskLevel] ?? RISK_STYLES.LOW);

  const displayDate = $derived(
    new Date(advance.requested_date || advance.created_at).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  );

  function fmtAmount(v: number): string {
    return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(v || 0);
  }

  // Avatar employé (objet enrichi) — fallback initiales + palette dérivée du nom
  const advanceAvatar = $derived(
    advance.employee && typeof advance.employee === 'object' && 'avatar_url' in advance.employee
      ? getMediaUrl(advance.employee.avatar_url ?? '')
      : undefined
  );
  const avatarPalette = $derived(getAvatarPalette(advance.employee_name || ''));

  // Poste de l'employé (objet enrichi) — secours si pas de motif
  const employeeJobTitle = $derived(
    advance.employee && typeof advance.employee === 'object' && 'job_title' in advance.employee
      ? advance.employee.job_title
      : null
  );
</script>


<div
  in:fade={{ duration: 200 }}
  class="group flex items-center px-6 py-3 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
  role="none"
  onclick={() => onClick?.(advance)}
>
  <!-- Employé -->
  <div class="w-[22%] flex items-center gap-2.5 min-w-0">
    <div class="relative shrink-0">
      <Avatar class="h-11 w-11 border border-slate-200">
        {#if advanceAvatar}
          <AvatarImage src={advanceAvatar} alt={advance.employee_name || ''} class="object-cover" />
        {/if}
        <AvatarFallback class={cn("font-bold text-[0.7rem]", avatarPalette.bg, avatarPalette.text)}>
          {getInitials(advance.employee_name || '??')}
        </AvatarFallback>
      </Avatar>
    </div>
    <div class="flex flex-col justify-center gap-0.5 min-w-0">
      <span class="text-sm font-medium text-slate-800 truncate">
        {advance.employee_name || 'Employé inconnu'}
      </span>
      <span class="text-[0.84rem] text-slate-400 truncate">
        {employeeJobTitle || 'Pas de poste'}
      </span>
      <span class="text-[0.84rem] text-slate-400 truncate flex items-center gap-1">
        <AppIcon name="message-square" size={13} class="text-slate-300 shrink-0" />
        {advance.reason || 'Pas de raison'}
      </span>
      {#if advance.status === 'REJECTED' && advance.rejection_reason}
        <span class="text-[0.84rem] text-rose-500 truncate flex items-center gap-1" title="Motif du rejet : {advance.rejection_reason}">
          <AppIcon name="circle-x" size={13} class="text-rose-400 shrink-0" />
          Rejet : {advance.rejection_reason}
        </span>
      {/if}
    </div>
  </div>

  <!-- Montant -->
  <div class="w-[15%] flex flex-col justify-center gap-0.5">
    <span class="text-[0.88rem] font-semibold text-slate-800 tabular-nums">
      {fmtAmount(advance.amount)} {advance.currency || 'CDF'}
    </span>
    {#if advance.status === 'DRAFT' || advance.status === 'PENDING' || advance.status === 'REJECTED'}
      <span class="text-[0.82rem] text-slate-400" title="Le pourcentage de retenue sur le salaire sera défini par la RH lors de l'approbation">
        Retenue définie à l'approbation
      </span>
    {:else}
      <span class="text-[0.82rem] text-slate-500 tabular-nums">
        {advance.repayment_percentage ?? 0}% / mois
      </span>
    {/if}
  </div>

  <!-- Statut -->
  <div class="w-[14%] flex items-center">
    <Badge
      variant="outline"
      class="{statusColor.bg} {statusColor.text} border-0 text-[0.78rem] font-semibold px-2.5 py-0.5 rounded-full whitespace-nowrap shadow-none"
    >
      {statusLabel}
    </Badge>
  </div>

  <!-- Risque -->
  <div class="w-[13%] flex items-center">
    <span class="text-[0.84rem] font-medium px-2.5 py-0.5 rounded-full border whitespace-nowrap {riskClass}">
      {ADVANCE_RISK_LABELS[advance.risk_level as AdvanceRiskLevel] ?? 'Inconnu'}
    </span>
  </div>

  <!-- Solde restant -->
  <div class="w-[13%] flex flex-col justify-center gap-0.5">
    <span class="text-[0.84rem] font-medium text-slate-700 tabular-nums">
      {fmtAmount(advance.remaining_balance ?? 0)} {advance.currency || 'CDF'}
    </span>
    {#if advance.is_closed}
      <span class="text-[0.84rem] text-emerald-500 font-medium">Soldée</span>
    {/if}
  </div>

  <!-- Date -->
  <div class="w-[11%] text-right flex flex-col justify-center">
    <span class="text-[0.84rem] font-medium text-slate-600 whitespace-nowrap">
      {displayDate}
    </span>
  </div>

  <!-- Actions — menu kebab -->
  <div role="none" class="w-[8%] flex items-center justify-end" onclick={(e) => e.stopPropagation()}>
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        class="p-1.5 rounded text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer! outline-none!"
        title="Actions"
      >
        <AppIcon name="more-vertical" size={17} />
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="w-56 p-1 z-50">
        <!-- Voir le détail — disponible pour tous les statuts -->
        <DropdownMenu.Item
          onclick={() => onViewDetail?.(advance)}
          class="text-[0.85rem] py-1.5 cursor-pointer"
        >
          <AppIcon name="file-text" size={15} class="text-slate-500" />
          Voir le détail
        </DropdownMenu.Item>
        <DropdownMenu.Separator />

        {#if advance.status === 'DRAFT'}
          <DropdownMenu.Item
            onclick={() => onSubmit?.(advance)}
            class="text-[0.85rem] py-1.5 cursor-pointer"
          >
            <AppIcon name="paper-plane" size={15} class="text-blue-500" />
            Soumettre pour approbation
          </DropdownMenu.Item>
          <DropdownMenu.Item
            onclick={() => onEdit?.(advance)}
            class="text-[0.85rem] py-1.5 cursor-pointer"
          >
            <AppIcon name="file-check" size={15} class="text-indigo-500" />
            Reprendre le brouillon
          </DropdownMenu.Item>
        {:else if advance.status === 'PENDING'}
          <DropdownMenu.Item
            onclick={() => onApprove?.(advance)}
            class="text-[0.85rem] py-1.5 cursor-pointer"
          >
            <AppIcon name="check-circle" size={15} class="text-emerald-500" />
            Approuver
          </DropdownMenu.Item>
          <DropdownMenu.Item
            variant="destructive"
            onclick={() => onReject?.(advance)}
            class="text-[0.85rem] py-1.5 cursor-pointer"
          >
            <AppIcon name="circle-x" size={15} />
            Rejeter
          </DropdownMenu.Item>
        {:else if advance.status === 'APPROVED'}
          <DropdownMenu.Item
            onclick={() => onActivate?.(advance.id)}
            class="text-[0.85rem] py-1.5 cursor-pointer"
          >
            <AppIcon name="circle-play" size={15} class="text-blue-500" />
            Activer (déductible)
          </DropdownMenu.Item>
        {/if}
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
</div>

