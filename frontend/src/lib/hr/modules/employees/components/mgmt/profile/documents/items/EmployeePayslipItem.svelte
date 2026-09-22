<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import TooltipWrapper from '@/hr/components/shared/containers/TooltipWrapper.svelte';
  import { formatDate } from '@/hr/utilities/common/date';
  import { get_api_base_origin } from '@/hr/utilities/http/urls';
  import { PAYROLL_STATUS_COLORS, PAYROLL_STATUS_LABELS } from '@/hr/modules/payroll/types/types';


  type PayslipLike = {
    id: string;
    payroll_run?: string;
    payroll_run_id?: string;
    status?: string;
    gross_amount?: number | string;
    net_amount?: number | string;
    currency?: string;
    created_at?: string;
    updated_at?: string;
    employee_name?: string;
    period_label?: string;
  };

  let { payslip, onPreview }: { payslip: PayslipLike; onPreview: (id: string) => void } = $props();

  const currency = $derived((payslip.currency as string) ?? 'CDF');

  function num(v: unknown): number {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }

  function fmtAmount(n: number, c = currency): string {
    try {
      return num(n).toLocaleString('fr-FR', { style: 'currency', currency: c as any, maximumFractionDigits: 0 });
    } catch {
      return `${num(n).toLocaleString('fr-FR')} ${c}`;
    }
  }

  function mapPayslipStatus(raw: string): keyof typeof PAYROLL_STATUS_COLORS {
    const s = (raw ?? '').toString().toUpperCase();
    if (s === 'PAID') return 'paid';
    if (s === 'CONFIRMED') return 'calculated';
    if (s === 'REVIEW' || s === 'CALCULATED') return 'calculated';
    if (s === 'CANCELED' || s === 'CANCELLED') return 'closed';
    const low = (raw ?? 'draft').toString().toLowerCase() as any;
    return (low in PAYROLL_STATUS_COLORS ? low : 'draft') as any;
  }

  const rawStatus = $derived(payslip.status ?? 'REVIEW');
  const statusKey = $derived(mapPayslipStatus(rawStatus));
  const statusColors = $derived(PAYROLL_STATUS_COLORS[statusKey] ?? PAYROLL_STATUS_COLORS.draft);
  const statusLabel = $derived(PAYROLL_STATUS_LABELS[statusKey] ?? rawStatus);

  const gross = $derived(num(payslip.gross_amount));
  const net = $derived(num(payslip.net_amount));
  const dateLabel = $derived(payslip.created_at ? formatDate(payslip.created_at, false, false) : '');

  function handleExport() {
    const url = `${get_api_base_origin()}/api/payroll/payslips/${payslip.id}/export/`;
    window.open(url, '_blank');
  }
</script>


{#snippet ActionButton(icon: string, label: string, onclick: () => void)}
  <TooltipWrapper content={label} side="top" asChild={true}>
    {#snippet children(props: Record<string, any>)}
      <Button
        {...props}
        variant="ghost"
        size="icon"
        class="h-8 w-8 rounded-lg border border-transparent hover:border-emerald-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-400 transition-colors"
        {onclick}
      >
        <AppIcon name={icon} size={18} />
      </Button>
    {/snippet}
  </TooltipWrapper>
{/snippet}


<div
  class="group flex items-center justify-between gap-3 p-3.5 rounded-xl bg-white border border-slate-200 shadow-fine hover:border-emerald-200 hover:shadow-sm transition-all cursor-pointer"
  onclick={() => onPreview(payslip.id)}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && onPreview(payslip.id)}
>
  <div class="flex items-center gap-3.5 min-w-0">
    <span class="h-9 w-9 shrink-0 rounded-lg border flex items-center justify-center bg-emerald-50 border-emerald-100 text-emerald-600 group-hover:bg-white transition-colors">
      <AppIcon name="receipt" size={16} />
    </span>

    <div class="min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <p class="font-bold text-[0.88rem] truncate text-slate-900 tracking-tight leading-tight">
          Bulletin
        </p>
        <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[0.75rem] font-semibold border {statusColors.bg} {statusColors.text} border-transparent">
          <span class="h-1.5 w-1.5 rounded-full {statusColors.dot}"></span>
          {statusLabel}
        </span>
      </div>
      <p class="text-slate-500 truncate flex items-center gap-1.5 mt-0.5">
        {#if dateLabel}
          <span class="inline-flex items-center gap-1 text-[0.88rem]">
            <AppIcon name="calendar" size={13} class="text-slate-400" />
            Émis le {dateLabel}
          </span>
          <span class="h-1 w-1 rounded-full bg-slate-300 shrink-0"></span>
        {/if}
        <span class="font-semibold text-[0.88rem] text-slate-700 tabular-nums">{fmtAmount(net)}</span>
        <span class="text-slate-400 text-[0.88rem]">· Brut {fmtAmount(gross)}</span>
      </p>
    </div>
  </div>

  <div class="flex items-center gap-1 shrink-0" onclick={(e) => e.stopPropagation()} role="none">
    <div class="flex items-center gap-1 pr-2 border-r border-slate-100">
      {@render ActionButton("eye", "Voir le détail", () => onPreview(payslip.id))}
      {@render ActionButton("download", "Exporter en PDF", handleExport)}
    </div>
    <!-- Pas de menu modifier/supprimer — lecture seule -->
    <span class="h-8 w-8 ml-1 inline-flex items-center justify-center rounded-lg text-slate-300">
      <AppIcon name="lock" size={16} />
    </span>
  </div>
</div>

