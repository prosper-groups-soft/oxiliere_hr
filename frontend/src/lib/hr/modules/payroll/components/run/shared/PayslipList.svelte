<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { fetchPayslipDetail } from "@/hr/modules/payroll/queries/payroll";
  import type { Payslip } from "@/hr/modules/payroll/types/types";

  
  interface Props {
    payslips: Payslip[];
    title?: string;
    icon?: string;
    hint?: string;
    emptyText?: string;
  }

  let {
    payslips,
    title = 'Bulletins de paie',
    icon = 'file-plus',
    hint = 'Cliquez sur un bulletin pour afficher son détail.',
    emptyText = 'Aucun bulletin chargé.'
  }: Props = $props();

  // Devise du run : celle des bulletins générés (CDF en pratique).
  const currency = $derived(payslips[0]?.currency ?? 'CDF');

  /** Formate un montant dans la devise des bulletins du run. */
  function money(value: number | null | undefined): string {
    const n = Number(value ?? 0);
    if (currency && currency.toUpperCase() !== 'CDF') {
      return n.toLocaleString('fr-FR', { maximumFractionDigits: 2 }) + ' ' + currency.toUpperCase();
    }
    return n.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
  }

  function num(value: any): number {
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  }

  /** Vue employé dérivée d'un bulletin (identité + avatar), sans hypothèse forte
   *  sur la forme exacte de `payslip.employee`. */
  function view(p: Payslip): { fullName: string; poste: string; photo: string | null; palette: ReturnType<typeof getAvatarPalette> } {
    const employee: any = (p && p.employee) || {};
    const fullName = employee.fullName || 'Employé';
    return {
      fullName,
      poste: employee.jobTitle || employee.orgUnit || 'Poste non défini',
      photo: employee.photo || employee.avatarUrl || null,
      palette: getAvatarPalette(fullName)
    };
  }

  // --- Détail déplié sous la ligne (chargé au clic depuis le backend) ---
  let expandedId = $state<string | null>(null);
  let detailMap = $state<Record<string, any>>({});
  let detailLoading = $state<string | null>(null);

  async function toggleRow(p: Payslip) {
    if (expandedId === p.id) {
      expandedId = null;
      return;
    }
    expandedId = p.id;
    if (!detailMap[p.id]) {
      detailLoading = p.id;
      try {
        const d = await fetchPayslipDetail(p.id);
        detailMap = { ...detailMap, [p.id]: d };
      } catch {
        detailMap = { ...detailMap, [p.id]: null };
      } finally {
        detailLoading = null;
      }
    }
  }
</script>

<div class="space-y-3">
  {#if title}
    <h3 class="text-sm font-bold text-slate-700 flex items-center gap-2 px-1">
      <AppIcon name={icon} size={18} strokeWidth={1.5} class="text-slate-400" />
      {title}
      {#if payslips.length > 0}
        <span class="ml-auto text-[0.78rem] font-semibold text-slate-400">{payslips.length}</span>
      {/if}
    </h3>
  {/if}

  {#if payslips.length > 0}
    <div class="space-y-1.5">
      {#each payslips as p (p.id)}
        {@const v = view(p)}
        <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
          <button
            type="button"
            onclick={() => toggleRow(p)}
            class="w-full text-left flex items-center justify-between gap-3 px-3 py-2.5 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <div class="flex items-center gap-2 min-w-0">
              <Avatar class="h-9 w-9 shrink-0 rounded-full border border-slate-200">
                {#if v.photo}
                  <AvatarImage src={getMediaUrl(v.photo)} alt={v.fullName} class="object-cover" />
                {/if}
                <AvatarFallback class={cn('font-bold text-[0.8rem]', v.palette.bg, v.palette.text)}>
                  {getInitials(...v.fullName.split(' '))}
                </AvatarFallback>
              </Avatar>
              <span class="text-sm font-medium text-slate-800 truncate">{v.fullName}</span>
            </div>

            <div class="flex items-center gap-3 shrink-0">
              <span class="text-[0.8rem] text-slate-400 hidden sm:inline truncate max-w-40">{v.poste}</span>
              <span class="text-[0.86rem] font-semibold text-slate-900 whitespace-nowrap">{money(p.summary?.netPay)}</span>
              <AppIcon name="chevron-down" size={15} class={cn('text-slate-300 transition-transform', expandedId === p.id && 'rotate-180')} />
            </div>
          </button>

          {#if expandedId === p.id}
            {@const d = detailMap[p.id]}
            {@const lines = Array.isArray(d?.lines) ? d.lines : []}
            {@const gains = lines.filter((ln: any) => (ln.adjustment_type ?? '') !== 'CONTRIBUTION')}
            {@const retenues = lines.filter((ln: any) => (ln.adjustment_type ?? '') === 'CONTRIBUTION')}
            <div class="px-4 py-3 border-t border-slate-100 bg-slate-50/40 space-y-3">
              {#if detailLoading === p.id}
                <div class="flex items-center justify-center py-2">
                  <AnimateSpin class="size-3" text="Chargement du détail" textPosition="right" />
                </div>
              {:else if d}
                <div class="flex items-end justify-between gap-3">
                  <div class="text-sm">
                    <span class="block text-[0.85rem] uppercase tracking-wide text-slate-400 font-semibold">Salaire net à payer</span>
                    <span class="text-sm font-bold text-emerald-600">{money(num(d.net_amount))}</span>
                  </div>
                  <div class="text-right text-[0.85rem] text-slate-400 leading-snug">
                    {#if d.worked_days > 0}
                      <span class="block text-[0.85rem]">{d.worked_days} jour{d.worked_days > 1 ? 's' : ''} travaillé{d.worked_days > 1 ? 's' : ''}</span>
                    {/if}
                    {#if d.paid_leave_days > 0}
                      <span class="block text-[0.85rem]">{d.paid_leave_days} jrs congés payés</span>
                    {/if}
                    {#if d.unpaid_leave_days > 0}
                      <span class="block text-amber-600 text-[0.85rem]">{d.unpaid_leave_days} jrs absences non payées</span>
                    {/if}
                  </div>
                </div>

                {#if gains.length > 0}
                  <div>
                    <p class="text-[0.72rem] uppercase tracking-wide text-slate-400 font-semibold mb-1">Éléments du salaire brut</p>
                    <div class="rounded-lg border border-slate-100 bg-white px-3 py-1 divide-y divide-slate-50">
                      {#each gains as ln (ln.id ?? ln.label)}
                        <div class="flex items-center justify-between gap-2 py-1">
                          <span class="text-slate-600 text-sm min-w-0 truncate">{ln.label ?? 'Ligne'}</span>
                          <span class="font-semibold text-sm whitespace-nowrap shrink-0 text-slate-800">{money(num(ln.amount))}</span>
                        </div>
                      {/each}
                      <div class="flex items-center justify-between gap-2 pt-1">
                        <span class="text-sm font-semibold text-slate-700">Salaire brut</span>
                        <span class="font-bold text-slate-900 text-sm">{money(num(d.gross_amount))}</span>
                      </div>
                    </div>
                  </div>
                {/if}

                {#if retenues.length > 0}
                  <div>
                    <p class="text-[0.72rem] uppercase tracking-wide text-slate-400 font-semibold mb-1">Retenues salariales</p>
                    <div class="rounded-lg border border-slate-100 bg-white px-3 py-1 divide-y divide-slate-50">
                      {#each retenues as ln (ln.id ?? ln.label)}
                        <div class="flex items-center justify-between gap-2 py-1">
                          <span class="text-slate-600 text-sm min-w-0 truncate">{ln.label ?? 'Ligne'}</span>
                          <span class="font-semibold text-sm whitespace-nowrap shrink-0 text-rose-600">− {money(num(ln.amount))}</span>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}

                {#if num(d.taxable_base) > 0}
                  <p class="text-sm text-slate-800 pt-0.5">
                    Base imposable IRPP : {money(num(d.taxable_base))}
                  </p>
                {/if}
              {:else}
                <div class="flex gap-1.5 items-center justify-center py-2">
                  <AppIcon name="circle-x" size={20} class="text-rose-600" />
                  <p class="text-rose-400 text-[0.86rem]">Impossible de charger le détail.</p>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
    {#if hint}
      <p class="text-[0.85rem] text-slate-400 px-1">{hint}</p>
    {/if}
  {:else}
    <div class="px-1 flex flex-col items-center justify-center gap-1.5">
      <AppIcon name="circle-x" size={16} strokeWidth={1.5} class="text-red-400" />
      <p class="text-sm text-red-500">{emptyText}</p>
    </div>
  {/if}
</div>

