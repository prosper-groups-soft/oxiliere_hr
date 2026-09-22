<script lang="ts">
  import { Button } from '@/components/ui/button';
  import * as Sheet from '@/components/ui/sheet';
  import * as Avatar from '@/components/ui/avatar';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import { Separator } from '@/components/ui/separator';
  import CurrencyConversionBanner from './CurrencyConversionBanner.svelte';
  import { PAYROLL_STATUS_COLORS, PAYROLL_STATUS_LABELS, type Payslip, type PayslipSection } from '@/hr/modules/payroll/types/types';
  import { cn } from '@/hr/utilities/common/css';
  import { getMediaUrl } from '@/hr/utilities/common/media';
  import { get_api_base_origin } from '@/hr/utilities/http/urls';

  
  interface Props {
    open: boolean;
    payslip: Payslip | null;
    currentIndex?: number;
    totalCount?: number;
    onPrevious?: () => void;
    onNext?: () => void;
    onAudit?: () => void;
  }

  let {
    open = $bindable(false),
    payslip,
    currentIndex,
    totalCount,
    onPrevious,
    onNext,
    onAudit
  }: Props = $props();

  /** Gestionnaire clavier : ← → pour navigation, Ctrl+A pour l'audit */
  function handleKeydown(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === 'ArrowLeft' && onPrevious) {
      e.preventDefault();
      onPrevious();
    } else if (e.key === 'ArrowRight' && onNext) {
      e.preventDefault();
      onNext();
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'a' && onAudit) {
      e.preventDefault();
      onAudit();
    }
  }

  /** Étiquette lisible du type de contrat — '' si inconnu (champ masqué) */
  const contractTypeLabel = $derived.by(() => {
    if (!payslip) return '';
    const t = (payslip as any).contract?.type ?? (payslip as any).contract_type ?? '';
    if (!t) return '';
    const labels: Record<string, string> = {
      CDI: 'CDI — Contrat à Durée Indéterminée',
      CDD: 'CDD — Contrat à Durée Déterminée',
      CTR: 'CTR — Contrat de Prestation',
    };
    return labels[t] ?? t;
  });

  /** Étiquette du régime — '' si inconnu */
  const workRegimeLabel = $derived.by(() => {
    if (!payslip) return '';
    const r = (payslip as any).contract?.workRegime ?? (payslip as any).contract?.work_regime ?? '';
    if (!r) return '';
    return r === 'TEMPS_PLEIN' ? 'Temps plein' : r === 'TEMPS_PARTIEL' ? 'Temps partiel' : r;
  });

  /** Formate un montant — retourne null si indisponible (permet de masquer la ligne) */
  function formatCurrency(amount: any): string | null {
    const n = Number(amount);
    if (!Number.isFinite(n)) 
      return null;
    const cur = (payslip as any)?.currency ?? (payslip as any)?.contract_currency ?? 'CDF';
    try { 
      return n.toLocaleString('fr-FR', { style: 'currency', currency: cur as any, maximumFractionDigits: 0 }); 
    }
    catch { 
      return `${n.toLocaleString('fr-FR')} ${cur}`; 
    }
  }
  
  function fmt(amount: any): string | null { return formatCurrency(amount); }
  const baseSalaryFmt = $derived(fmt((payslip as any)?.contract?.baseSalary ?? (payslip as any)?.base_salary_snapshot ?? (payslip as any)?.gross_amount ?? null));

  const safeSections = $derived((payslip as any)?.sections ?? []);
  const safeSummary = $derived((payslip as any)?.summary ?? null);

  /** Couleurs de fond pour chaque section */
  const sectionStyles: Record<PayslipSection['sectionType'], { heading: string; icon: string; iconName: string }> = {
    earning:  { heading: 'text-emerald-700', icon: 'text-emerald-500', iconName: 'plus-circle' },
    deduction: { heading: 'text-rose-700', icon: 'text-rose-500', iconName: 'minus-circle' },
  };

  function mapPayslipStatus(raw: any): keyof typeof PAYROLL_STATUS_COLORS {
    const s = String(raw ?? '').toUpperCase();
    if (s === 'PAID') return 'paid';
    if (s === 'CONFIRMED') return 'calculated';
    if (s === 'REVIEW' || s === 'CALCULATED') return 'calculated';
    if (s === 'CANCELED' || s === 'CANCELLED') return 'closed';
    const low = String(raw ?? 'draft').toLowerCase() as any;
    return (low in PAYROLL_STATUS_COLORS ? low : 'draft') as any;
  }
  
  const detailStatusKey = $derived(payslip ? mapPayslipStatus((payslip as any).status) : 'draft' as const);
  const detailStatusColors = $derived(PAYROLL_STATUS_COLORS[detailStatusKey] ?? PAYROLL_STATUS_COLORS.draft);
  const detailStatusLabel = $derived(payslip ? (PAYROLL_STATUS_LABELS[detailStatusKey] ?? String((payslip as any).status)) : '');
  function initials(name: string) { return name.split(/\s+/).filter(Boolean).slice(0,2).map(w=>w[0]?.toUpperCase()??'').join('') || '?'; }
  const _avatarSrc = $derived(getMediaUrl((payslip as any)?.photo_path ?? (payslip as any)?.employee?.avatarUrl ?? (payslip as any)?.avatar_url ?? null) ?? undefined);
  const _netFmt = $derived(fmt((payslip as any)?.summary?.netPay ?? (payslip as any)?.net_amount ?? (payslip as any)?.netAfterAdvances) ?? '—');
  const _grossNum = $derived(Number((payslip as any)?.summary?.grossSalary ?? (payslip as any)?.summary?.gross_salary ?? (payslip as any)?.gross_amount ?? (payslip as any)?.base_salary_snapshot ?? 0));
  const _grossFmt = $derived(fmt(_grossNum) ?? fmt((payslip as any)?.base_salary_snapshot));
  const _taxableBase = $derived((payslip as any)?.taxable_base ?? (payslip as any)?.taxableBase ?? (payslip as any)?.detail?.taxable_base ?? null);
  const _taxableBaseFmt = $derived(_taxableBase != null ? fmt(_taxableBase) : null);
  const _cnssRate = $derived((payslip as any)?.cnss_rate ?? (payslip as any)?.parametersFrozen?.cnssRate ?? 5);
  const _cnssNum = $derived(Number((payslip as any)?.cnss_amount ?? 0));
  const _irppNum = $derived(Number((payslip as any)?.ipr_amount ?? (payslip as any)?.irpp_amount ?? 0));
  const _brutLines = $derived.by(()=>{ const ls: any[] = (payslip as any)?.lines ?? (payslip as any)?.detail?.lines ?? []; if(!ls.length) return []; return ls.filter((l:any)=> String(l.adjustment_type ?? l.type ?? l.code ?? '').toLowerCase().includes('earning') || ['BASE_SALARY','PARTIAL_SALARY','HOUSING_ALLOWANCE','TRANSPORT_ALLOWANCE','RISK_BONUS','PERF_BONUS','FUNCTION_BONUS','OT_','SENIORITY','PRIME','ALLOCATION','INDEMNITE'].some(k=>String(l.code??l.adjustment_type??'').toUpperCase().includes(k)) || Number(l.amount) >= 0); });
  const _brutExtra = $derived.by(()=>{ if(!_grossNum) return null; const base = Number((payslip as any)?.base_salary_snapshot ?? 0); const sum = _brutLines.reduce((s:number,l:any)=> s + Number(l.amount||0), 0); const gap = _grossNum - (sum || base); if(Math.abs(gap) < 1) return null; if(_brutLines.length && Math.abs(gap) > 0) return gap; if(!_brutLines.length && base && gap !== 0) return gap; return null; });
  const _retenueLines = $derived.by(()=>{ const ls: any[] = (payslip as any)?.lines ?? (payslip as any)?.detail?.lines ?? []; if(!ls.length) return []; return ls.filter((l:any)=> Number(l.amount) < 0 || ['CNSS','IRPP','IPR','ONEM','INPP','RETENUE','DEDUCTION'].some(k=>String(l.code??l.adjustment_type??l.label??'').toUpperCase().includes(k))); });
  const _workedDays = $derived(Number((payslip as any)?.worked_days ?? 0));
  const _workedHours = $derived(Number((payslip as any)?.worked_hours ?? (payslip as any)?.workedHours ?? 0));
  const _paidLeaves = $derived(Number((payslip as any)?.paid_leave_days ?? 0));
  const _hasPresence = $derived(_workedDays > 0 || _workedHours > 0 || _paidLeaves > 0);
  const _hasProvenance = $derived(((payslip as any)?.base_salary_snapshot && (payslip as any)?.contract?.baseSalary && String((payslip as any).base_salary_snapshot) !== String((payslip as any).contract?.baseSalary)) || ((payslip as any)?.contract_currency && (payslip as any)?.contract_currency !== ((payslip as any).currency ?? 'CDF')));
  const _headerSub = $derived.by(()=>{ const job = (payslip as any)?.job_title ?? (payslip as any)?.employee?.jobTitle ?? (payslip as any)?.jobTitle ?? ''; const mat = (payslip as any)?.employee?.matricule ?? (payslip as any)?.matricule ?? ''; const s = (payslip as any)?.period?.start ?? ''; const e = (payslip as any)?.period?.end ?? ''; const period = s && e ? `${s} → ${e}` : s || e || ''; return [job, mat, period].filter(Boolean).join(' · '); });
  const _totalDedNum = $derived.by(()=>{ const v = Number((payslip as any)?.summary?.totalDeductions ?? (payslip as any)?.summary?.total_deductions ?? 0); if(v>0) return v; const sum = _cnssNum + _irppNum; return sum>0 ? sum : 0; });
  const _showEmployerCost = $derived(Number((payslip as any)?.summary?.employerCosts ?? (payslip as any)?.summary?.employer_costs ?? 0) > 0 || Number((payslip as any)?.summary?.totalEmployerCost ?? (payslip as any)?.summary?.total_employer_cost ?? 0) > 0);
</script>


<Sheet.Root bind:open>
  <Sheet.Content
    side="right"
    class="sm:max-w-180 flex flex-col h-full overflow-hidden p-0"
    onkeydown={handleKeydown}
  >
  {#if payslip}
    <div class="px-6 py-4 pr-12 border-b bg-white">
      <div class="flex items-center gap-3">
        <Avatar.Root class="h-11 w-11 border border-slate-200 shrink-0"><Avatar.Image src={_avatarSrc} alt={(payslip as any).employee?.fullName ?? (payslip as any).employee_name ?? ''} class="object-cover" /><Avatar.Fallback class="bg-slate-100 text-slate-700 text-[0.83rem] font-bold">{initials((payslip as any).employee?.fullName ?? (payslip as any).employee_name ?? '?')}</Avatar.Fallback></Avatar.Root>
        <div class="min-w-0 flex-1">
          <h2 class="font-bold text-[0.98rem] leading-none truncate">{(payslip as any).employee?.fullName ?? (payslip as any).employee_name ?? '—'}</h2>
          <p class="text-[0.83rem] text-slate-500 mt-1 truncate">{_headerSub}</p>
        </div>
        {#if totalCount != null && totalCount > 1}<div class="flex items-center gap-1 shrink-0"><span class="text-[0.83rem] text-slate-400 tabular-nums">{currentIndex != null ? currentIndex + 1 : '?'} / {totalCount}</span><button onclick={onPrevious} disabled={currentIndex == null || currentIndex <= 0} class="w-7 h-7 flex items-center justify-center rounded-md border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"><AppIcon name="chevron-left" size={14} /></button><button onclick={onNext} disabled={currentIndex == null || totalCount == null || currentIndex >= totalCount - 1} class="w-7 h-7 flex items-center justify-center rounded-md border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"><AppIcon name="chevron-right" size={14} /></button></div>{/if}
      </div>
    </div>
    <!-- Hero net — fond blanc -->
    <div class="mx-6 mt-4 rounded-xl bg-white border border-slate-200 p-4 flex items-center justify-between">
      <div><div class="text-[0.83rem] uppercase tracking-widest text-slate-400">Salaire net à payer</div><div class="text-[1.35rem] font-extrabold tracking-tight mt-1 text-slate-900">{_netFmt}</div>{#if _taxableBaseFmt}<div class="text-[0.83rem] text-slate-500 mt-1">Base imposable IRPP : {_taxableBaseFmt}</div>{/if}</div>
      <span class={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.83rem] font-medium", detailStatusColors.bg, detailStatusColors.text)}><span class={cn("h-1.5 w-1.5 rounded-full", detailStatusColors.dot)}></span>{detailStatusLabel}</span>
    </div>

      <div class="flex-1 overflow-y-auto px-6 py-4 space-y-6 custom-scrollbar">
        {#if _hasPresence}<div class="grid grid-cols-3 gap-2 text-center"><div class="rounded-lg bg-slate-50 border border-slate-100 py-2"><div class="text-[0.83rem] uppercase tracking-wide text-slate-400">Jours travaillés</div><div class="text-sm font-bold text-slate-800">{_workedDays || '—'}</div></div><div class="rounded-lg bg-slate-50 border border-slate-100 py-2"><div class="text-[0.83rem] uppercase tracking-wide text-slate-400">Heures</div><div class="text-sm font-bold text-slate-800">{_workedHours || '—'}</div></div><div class="rounded-lg bg-slate-50 border border-slate-100 py-2"><div class="text-[0.83rem] uppercase tracking-wide text-slate-400">Congés payés</div><div class="text-sm font-bold text-slate-800">{_paidLeaves || 0}</div></div></div>{/if}

        {#if ((payslip as any).employee?.fullName ?? (payslip as any).employee_name ?? '') || ((payslip as any).employee?.matricule ?? (payslip as any).matricule ?? '') || ((payslip as any).employee?.orgUnit ?? (payslip as any).org_unit ?? '') || (payslip as any).employee?.entryDate}
        <div class="space-y-3">
          <h4 class="text-[0.83rem] font-semibold text-slate-700 uppercase tracking-wider">Employé</h4>
          <div class="grid grid-cols-2 gap-4">
            {#if (payslip as any).employee?.matricule ?? (payslip as any).matricule}<div><div class="text-sm font-medium text-slate-500">Matricule</div><p class="text-sm text-slate-900">{(payslip as any).employee?.matricule ?? (payslip as any).matricule}</p></div>{/if}
            {#if (payslip as any).employee?.orgUnit ?? (payslip as any).org_unit}<div><div class="text-sm font-medium text-slate-500">Unité organisationnelle</div><p class="text-sm text-slate-900">{(payslip as any).employee?.orgUnit ?? (payslip as any).org_unit}</p></div>{/if}
            {#if (payslip as any).employee?.entryDate}<div><div class="text-sm font-medium text-slate-500">Date d'entrée</div><p class="text-sm text-slate-900">{(payslip as any).employee?.entryDate}</p></div>{/if}
          </div>
        </div>
        {/if}

        {#if contractTypeLabel || ((payslip as any).contract?.professionalCategory ?? (payslip as any).professional_category) || (payslip as any).contract?.grade || workRegimeLabel || ((payslip as any).contract?.currency ?? (payslip as any).currency ?? (payslip as any).contract_currency) || baseSalaryFmt}
        <div class="space-y-3">
          <h4 class="text-[0.83rem] font-semibold text-slate-700 uppercase tracking-wider">Contrat</h4>
          <div class="grid grid-cols-2 gap-4">
            {#if contractTypeLabel}<div><div class="text-sm font-medium text-slate-500">Type de contrat</div><p class="text-sm text-slate-900">{contractTypeLabel}</p></div>{/if}
            {#if (payslip as any).contract?.professionalCategory ?? (payslip as any).professional_category}<div><div class="text-sm font-medium text-slate-500">Catégorie</div><p class="text-sm text-slate-900">{(payslip as any).contract?.professionalCategory ?? (payslip as any).professional_category}</p></div>{/if}
            {#if (payslip as any).contract?.grade}<div><div class="text-sm font-medium text-slate-500">Grade</div><p class="text-sm text-slate-900">{(payslip as any).contract?.grade}</p></div>{/if}
            {#if workRegimeLabel}<div><div class="text-sm font-medium text-slate-500">Régime</div><p class="text-sm text-slate-900">{workRegimeLabel}</p></div>{/if}
            {#if (payslip as any).contract?.currency ?? (payslip as any).currency ?? (payslip as any).contract_currency}<div><div class="text-sm font-medium text-slate-500">Devise</div><p class="text-sm text-slate-900">{(payslip as any).contract?.currency ?? (payslip as any).currency ?? (payslip as any).contract_currency}</p></div>{/if}
            {#if baseSalaryFmt}<div><div class="text-sm font-medium text-slate-500">Salaire de base</div><p class="text-sm text-slate-900">{baseSalaryFmt}</p>{#if _hasProvenance}<p class="text-[0.83rem] text-slate-400 leading-tight mt-0.5">Snapshot au calcul{#if (payslip as any).base_salary_snapshot && (payslip as any).contract?.baseSalary && String((payslip as any).base_salary_snapshot) !== String((payslip as any).contract?.baseSalary)} · contrat {fmt((payslip as any).contract.baseSalary)} → proratisé{/if}{#if (payslip as any).contract_currency && (payslip as any).contract_currency !== ((payslip as any).currency ?? 'CDF')} · converti {(payslip as any).contract_currency}→{(payslip as any).currency}{/if}</p>{/if}</div>{/if}
          </div>
        </div>
        {/if}

        <Separator />

        <!-- Bannière taux de change (USD seulement) -->
        {#if (payslip as any).currency === 'USD' || (payslip as any).contract_currency === 'USD'}
          <CurrencyConversionBanner exchangeRate={payslip.exchangeRate} />
        {/if}

        <!-- Éléments du salaire brut (détail riche) -->
        {#if _brutLines.length || _grossFmt}<div class="space-y-2"><h4 class="text-[0.83rem] font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2"><AppIcon name="plus-circle" size={14} class="text-emerald-500" />Éléments du salaire brut</h4><div class="rounded-xl border border-slate-100 overflow-hidden divide-y divide-slate-50">{#each _brutLines as l}<div class="flex items-center justify-between px-3 py-2.5 bg-white"><span class="text-[0.84rem] text-slate-700">{l.label ?? l.code ?? l.adjustment_type}</span><span class="text-[0.84rem] font-semibold text-slate-900">{fmt(l.amount) ?? '—'}</span></div>{/each}{#if !_brutLines.length && (payslip as any).base_salary_snapshot}<div class="flex items-center justify-between px-3 py-2.5 bg-white"><span class="text-[0.84rem] text-slate-700">Salaire de Base</span><span class="text-[0.84rem] font-semibold">{fmt((payslip as any).base_salary_snapshot) ?? '—'}</span></div>{/if}{#if _brutExtra != null}<div class="flex items-center justify-between px-3 py-2.5 bg-white"><span class="text-[0.84rem] text-slate-700">Autres primes / ajustements</span><span class="text-[0.84rem] font-semibold text-slate-900">{fmt(_brutExtra) ?? '—'}</span></div>{/if}<div class="flex items-center justify-between px-3 py-2.5 bg-emerald-50/60 font-bold"><span class="text-[0.84rem] text-emerald-800">Salaire brut</span><span class="text-[0.84rem] text-emerald-700">{_grossFmt ?? '—'}</span></div></div></div>{/if}
        {#if _retenueLines.length || fmt((payslip as any).cnss_amount) || fmt((payslip as any).ipr_amount)}<div class="space-y-2"><h4 class="text-[0.83rem] font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2"><AppIcon name="minus-circle" size={14} class="text-rose-500" />Retenues salariales</h4><div class="rounded-xl border border-slate-100 overflow-hidden divide-y divide-slate-50">{#if fmt((payslip as any).cnss_amount)}<div class="flex items-center justify-between px-3 py-2.5 bg-white"><span class="text-[0.84rem] text-slate-700">CNSS ({_cnssRate}%)</span><span class="text-[0.84rem] font-semibold text-rose-600">− {fmt((payslip as any).cnss_amount)}</span></div>{/if}{#if fmt((payslip as any).ipr_amount ?? (payslip as any).irpp_amount)}<div class="flex flex-col px-3 py-2.5 bg-white"><div class="flex items-center justify-between"><span class="text-[0.84rem] text-slate-700">IRPP</span><span class="text-[0.84rem] font-semibold text-rose-600">− {fmt((payslip as any).ipr_amount ?? (payslip as any).irpp_amount)}</span></div>{#if _taxableBaseFmt}<span class="text-[0.83rem] text-slate-400 mt-1">Base imposable IRPP : {_taxableBaseFmt}</span>{/if}</div>{/if}{#each _retenueLines.filter((x:any)=> !String(x.code??x.adjustment_type??'').toUpperCase().match(/CNSS|IRPP|IPR/)) as l}<div class="flex items-center justify-between px-3 py-2.5 bg-white"><span class="text-[0.84rem] text-slate-700">{l.label ?? l.code}</span><span class="text-[0.84rem] font-semibold text-rose-600">{fmt(l.amount) ? (String(fmt(l.amount)).startsWith('-') ? fmt(l.amount) : `− ${fmt(l.amount)}`) : '—'}</span></div>{/each}</div></div>{/if}
        {#if safeSections.length && !_brutLines.length && !_grossFmt}
        {#each safeSections as section (section.code)}
          <div class="space-y-3">
            <h4 class={cn(
              "text-sm font-semibold uppercase tracking-wider flex items-center gap-2",
              sectionStyles[section.sectionType as keyof typeof sectionStyles]?.heading ?? 'text-slate-700'
            )}>
              <AppIcon name={sectionStyles[section.sectionType as keyof typeof sectionStyles]?.iconName ?? 'plus-circle'} size={15} class={sectionStyles[section.sectionType as keyof typeof sectionStyles]?.icon ?? 'text-slate-400'} />
              {section.label}
            </h4>
            <div class="space-y-2">
              {#each section.lines as line}
                {#if fmt(line.amount)}
                <div class="flex items-center justify-between py-1">
                  <span class="text-sm text-slate-700">{line.label}</span>
                  <span class={cn("text-sm font-medium", section.sectionType === 'earning' ? 'text-slate-900' : 'text-rose-600')}>
                    {section.sectionType === 'earning' ? '+' + fmt(line.amount) : '-' + fmt(line.amount)}
                  </span>
                </div>
                {/if}
              {/each}
            </div>
            {#if fmt(section.total)}
            <div class="flex items-center justify-between py-1.5 border-t border-slate-100">
              <span class="text-sm font-semibold text-slate-700">Total {section.label.toLowerCase()}</span>
              <span class={cn("text-sm font-bold", section.sectionType === 'earning' ? 'text-emerald-600' : 'text-rose-700')}>
                {section.sectionType === 'earning' ? fmt(section.total) : '-' + fmt(section.total)}
              </span>
            </div>
            {/if}
          </div>
        {/each}
        {/if}

        <Separator />

        {#if safeSummary}
          <div class="space-y-3">
            <h4 class="text-[0.83rem] font-semibold text-slate-700 uppercase tracking-wider">Résumé</h4>
            <div class="space-y-2.5">
              {#if fmt((payslip as any).summary?.grossSalary ?? (payslip as any).summary?.gross_salary ?? (payslip as any).gross_amount)}<div class="flex items-center justify-between py-1"><span class="text-sm font-medium text-slate-700">Salaire brut</span><span class="text-sm font-semibold text-slate-900">{fmt((payslip as any).summary?.grossSalary ?? (payslip as any).summary?.gross_salary ?? (payslip as any).gross_amount)}</span></div>{/if}
              {#if _totalDedNum > 0}<div class="flex items-center justify-between py-1"><span class="text-sm font-medium text-slate-700">Total retenues</span><span class="text-sm font-semibold text-rose-600">− {fmt(_totalDedNum)}</span></div>{/if}
              {#if fmt((payslip as any).summary?.postNetDeductions ?? (payslip as any).summary?.post_net_deductions) && Number((payslip as any).summary?.postNetDeductions ?? (payslip as any).summary?.post_net_deductions ?? 0) > 0}<div class="flex items-center justify-between py-1"><span class="text-sm font-medium text-slate-700">Déductions post-nette</span><span class="text-sm font-semibold text-rose-600">-{fmt((payslip as any).summary?.postNetDeductions ?? (payslip as any).summary?.post_net_deductions)}</span></div>{/if}
              {#if fmt((payslip as any).summary?.netPay ?? (payslip as any).summary?.net_pay ?? (payslip as any).net_amount)}<div class="flex items-center justify-between py-1.5 border-t border-slate-100"><span class="text-sm font-bold text-slate-800">Salaire net à payer</span><span class="text-sm font-bold text-emerald-600">{fmt((payslip as any).summary?.netPay ?? (payslip as any).summary?.net_pay ?? (payslip as any).net_amount)}</span></div>{/if}
            </div>
            {#if _showEmployerCost}
            <div class="mt-4 pt-3 border-t border-dashed border-slate-200 space-y-2.5">
              <h5 class="text-[0.83rem] font-semibold text-slate-500 uppercase tracking-wider">Coût employeur</h5>
              {#if Number((payslip as any).summary?.employerCosts ?? (payslip as any).summary?.employer_costs ?? 0) > 0}<div class="flex items-center justify-between py-1"><span class="text-sm font-medium text-slate-700">Cotisations employeur</span><span class="text-sm font-semibold text-slate-900">{fmt((payslip as any).summary?.employerCosts ?? (payslip as any).summary?.employer_costs)}</span></div>{/if}
              {#if Number((payslip as any).summary?.totalEmployerCost ?? (payslip as any).summary?.total_employer_cost ?? 0) > 0}<div class="flex items-center justify-between py-1.5 border-t border-dashed border-slate-100"><span class="text-sm font-bold text-slate-800">Coût total employeur</span><span class="text-sm font-bold text-indigo-600">{fmt((payslip as any).summary?.totalEmployerCost ?? (payslip as any).summary?.total_employer_cost)}</span></div>{/if}
            </div>
            {/if}
          </div>
        {/if}

        {#if payslip.immutableSnapshot}
          <Separator />
          <div class="space-y-2">
            <h4 class="text-[0.83rem] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <AppIcon name="shield-check" size={14} class="text-slate-400" />
              Snapshot d'audit
            </h4>
            <div class="bg-slate-50 rounded-lg p-3 space-y-1.5">
              {#if payslip.immutableSnapshot.signedAt}<div class="flex items-center justify-between text-[0.83rem]"><span class="text-slate-500">Signé le</span><span class="text-slate-700 font-mono">{payslip.immutableSnapshot.signedAt}</span></div>{/if}
              {#if payslip.immutableSnapshot.sha256}<div class="flex items-center justify-between text-[0.83rem]"><span class="text-slate-500">SHA-256</span><span class="text-slate-700 font-mono text-[0.83rem] truncate max-w-45" title={payslip.immutableSnapshot.sha256}>{payslip.immutableSnapshot.sha256}</span></div>{/if}
              {#if fmt(payslip.immutableSnapshot.parametersFrozen?.smig)}<div class="flex items-center justify-between text-[0.83rem]"><span class="text-slate-500">SMIG</span><span class="text-slate-700 font-mono">{fmt(payslip.immutableSnapshot.parametersFrozen?.smig)}</span></div>{/if}
              {#if payslip.immutableSnapshot.parametersFrozen?.cnssRate != null}<div class="flex items-center justify-between text-[0.83rem]"><span class="text-slate-500">Taux CNSS</span><span class="text-slate-700 font-mono">{payslip.immutableSnapshot.parametersFrozen.cnssRate}%</span></div>{/if}
              {#if payslip.immutableSnapshot.parametersFrozen?.exchangeRate != null}<div class="flex items-center justify-between text-[0.83rem]"><span class="text-slate-500">Taux de change</span><span class="text-slate-700 font-mono">{payslip.immutableSnapshot.parametersFrozen.exchangeRate}</span></div>{/if}
            </div>
          </div>
        {/if}
      </div>

      <!-- Pied de page avec boutons d'action -->
      <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
        <Button variant="outline" onclick={() => open = false} class="flex-1 h-9.5 text-sm">
          <AppIcon name="x" size={17} class="mr-1.5 text-slate-400" />
          Fermer
        </Button>
        <Button onclick={()=>window.open(`${get_api_base_origin()}/api/payroll/payslips/${(payslip as any).id}/export/`, '_blank')} class="flex-1 h-9.5 text-sm bg-blue-600 hover:bg-blue-700">
          <AppIcon name="download" size={17} class="mr-1.5" />
          Télécharger PDF
        </Button>
      </Sheet.Footer>
    {:else}
      <div class="flex flex-1 flex-col items-center justify-center gap-3 px-6 py-16">
        <AnimateSpin text="Chargement du bulletin"/>
      </div>
    {/if}
  </Sheet.Content>
</Sheet.Root>

