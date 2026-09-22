<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { Badge } from "@/components/ui/badge";
  import { PayrollApi } from "@/hr/payroll/api/payroll.endpoints";
  import PayslipList from "../shared/PayslipList.svelte";
  import type { RunListItem } from "../../../types/types";
  import { RUN_LIST_STATUS_LABELS, RUN_LIST_STATUS_COLORS, type Payslip } from "../../../types/types";
  import { cn } from "@/utilities/common/css";


  let { run = null as RunListItem | null, open = $bindable(false) }: {
    run: RunListItem | null;
    open: boolean;
  } = $props();

  type Detail = {
    id?: string; status?: string; period?: string; start_date?: string; end_date?: string;
    exchange_rate?: number | null; created_at?: string; updated_at?: string;
    stats?: { total_count?: number; processed_count?: number; pending_count?: number };
    financials?: { gross_total?: number; net_total?: number; total_tax_deductions?: number; employer_liability?: number };
    params_snapshot?: { selection?: { scope?: string } } | Record<string, unknown>;
  };
  type Summary = {
    payroll_run?: { id?: string; code?: string; period?: string; status?: string };
    summary?: {
      total_employees?: number; total_gross_salary?: number; total_net_salary?: number;
      total_ipr_to_pay?: number; total_cnss_employee?: number; total_cnss_employer?: number;
      total_inpp?: number; total_onem?: number; total_employer_liabilities?: number;
      total_cost_to_company?: number;
    };
  };

  type TabId = 'resume' | 'payslips' | 'meta';
  let activeTab = $state<TabId>('resume');

  const TABS: { id: TabId; label: string; icon: string }[] = [
    { id: 'resume', label: 'Résumé', icon: 'layout-dashboard' },
    { id: 'payslips', label: 'Bulletins', icon: 'file-text' },
    { id: 'meta', label: 'Période & paramètres', icon: 'settings' },
  ];

  let tabListEl = $state<HTMLElement | null>(null);
  let tabIndicatorStyle = $state('');
  $effect(() => {
    const el = tabListEl?.querySelector(`[data-tab="${activeTab}"]`) as HTMLElement | null;
    if (el) tabIndicatorStyle = `left: ${el.offsetLeft}px; width: ${el.offsetWidth}px;`;
  });
  let loading = $state(false);
  let error = $state(false);
  let detail = $state<Detail | null>(null);
  let summary = $state<Summary | null>(null);
  let payslips = $state<Payslip[]>([]);

  // Recharge quand on ouvre le sheet sur un nouveau run.
  $effect(() => {
    if (!open || !run) return;
    activeTab = 'resume';
    loading = true;
    error = false;
    detail = null;
    summary = null;
    payslips = [];
    let cancelled = false;
    const runId = run.id;
    const load = async () => {
      // On charge chaque source indépendamment : l'échec d'une (ex. summary)
      // ne doit pas faire tomber tout le détail. `error` n'apparaît que si
      // AUCUNE source n'aboutit.
      const [d, s, ps] = await Promise.allSettled([
        PayrollApi.runs.retrieve(runId) as unknown as Promise<Detail>,
        PayrollApi.runSummary.retrieve(runId) as unknown as Promise<Summary>,
        PayrollApi.runPayslips.list(runId) as unknown as Promise<{ results: any[] }>,
      ]);
      if (cancelled) return;
      const resolved = (r: PromiseSettledResult<any>) => r.status === 'fulfilled' ? r.value : null;
      detail = resolved(d);
      summary = resolved(s);
      payslips = ((resolved(ps) as any)?.results ?? []).map(normalizeRow);
      error = d.status === 'rejected' && s.status === 'rejected' && ps.status === 'rejected';
      loading = false;
    };
    load();
    return () => { cancelled = true; };
  });

  function num(v: any): number {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  }

  function money(v: number | null | undefined): string {
    return num(v).toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
  }

  function isoDate(v?: string): string {
    return v ? v.slice(0, 10) : '';
  }
  function fmtDay(v?: string): string {
    const raw = isoDate(v);
    if (!raw) return '—';
    const d = new Date(raw + 'T00:00:00');
    if (Number.isNaN(d.getTime())) return raw;
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }
  function monthLabel(start?: string): string {
    const raw = isoDate(start);
    const y = Number(raw.slice(0, 4));
    const m = Number(raw.slice(5, 7));
    if (raw && Number.isInteger(y) && Number.isInteger(m)) {
      return new Date(y, m - 1, 1).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
    }
    return run?.periodLabel || raw;
  }
  function periodDays(a?: string, b?: string): number {
    const s = isoDate(a), e = isoDate(b);
    if (!s || !e) return 0;
    const ms = (new Date(e + 'T00:00:00').getTime() - new Date(s + 'T00:00:00').getTime());
    return ms >= 0 ? Math.round(ms / 86400000) + 1 : 0;
  }

  // Reproduit normalizePayslipRow (stores/payslips) pour alimenter PayslipList.
  function normalizeRow(raw: any): Payslip {
    const hasEmployee = raw.employee && typeof raw.employee === 'object';
    const hasSummary = raw.summary && typeof raw.summary === 'object';
    const baseEmployee: any = hasEmployee ? raw.employee : {
      id: raw.contract ? String(raw.contract) : '',
      matricule: '',
      fullName: raw.employee_name || '',
      orgUnit: raw.org_unit || '',
      jobTitle: raw.job_title || '',
    };
    const avatarUrl = raw.photo_path ?? raw.avatar_url ?? baseEmployee.avatarUrl ?? baseEmployee.photo ?? null;
    return {
      ...raw,
      employee: { ...baseEmployee, avatarUrl },
      summary: hasSummary ? raw.summary : {
        grossSalary: num(raw.gross_amount),
        totalDeductions: 0,
        postNetDeductions: 0,
        netPay: num(raw.net_amount),
        employerCosts: 0,
        totalEmployerCost: 0,
      },
    } as Payslip;
  }

  const statusLabel = $derived(RUN_LIST_STATUS_LABELS[run?.status ?? 'draft'] ?? '—');
  const statusColors = $derived(RUN_LIST_STATUS_COLORS[run?.status ?? 'draft'] ?? RUN_LIST_STATUS_COLORS.draft);
  const selScope = $derived(
    (detail?.params_snapshot as any)?.selection?.scope
  );
  const selectionMode = $derived(
    selScope === 'employees' ? 'Sélection individuelle'
    : selScope === 'org_units' ? 'Par unité organisationnelle'
    : 'Tous les employés actifs'
  );
</script>


{#snippet Row(label: string, value: string, strong = false, tone: 'default' | 'emerald' | 'muted' = 'default')}
  <div class="flex items-center justify-between gap-3 py-1.5">
    <span class="text-sm text-slate-500">{label}</span>
    <span class={['whitespace-nowrap text-sm', strong ? 'font-bold text-slate-900' : 'font-semibold text-slate-800', tone === 'emerald' && 'text-emerald-600', tone === 'muted' && 'text-slate-500'].join(' ')}>{value}</span>
  </div>
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-220 p-0 flex flex-col bg-white h-full">
    {#if run}
      <Sheet.Header class="px-6 py-3 border-b bg-slate-50/60 flex items-start justify-between gap-3">
        <div class="min-w-0">
          <Sheet.Title class="text-base font-bold text-slate-900 text-left capitalize">
            Paie {monthLabel(run.periodLabel)}
          </Sheet.Title>
          <div class="flex items-center gap-2 mt-1">
            <span class={cn('inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold uppercase tracking-wider border', statusColors.bg, statusColors.text)}>
              {statusLabel}
            </span>
            {#if detail?.start_date}
              <span class="text-sm text-slate-500">{fmtDay(detail.start_date)} → {fmtDay(detail.end_date)}</span>
            {/if}
          </div>
        </div>
      </Sheet.Header>

      {#if loading}
        <div class="flex-1 flex items-center justify-center">
          <AnimateSpin text="Chargement du détail" />
        </div>
      {:else if error}
        <div class="flex-1 flex flex-col items-center justify-center gap-2 text-slate-500">
          <AppIcon name="circle-x" size={28} class="text-rose-500" />
          <p class="text-sm">Impossible de charger cette exécution de paie.</p>
        </div>
      {:else}
        <!-- Onglets — même langage visuel que PayrollTabs (icône + libellé, actif en
             primary, pastille de compteur, indicateur inférieur qui glisse). -->
        <div class="relative flex items-center pl-6 pr-8 border-b border-slate-100">
          <div bind:this={tabListEl} class="relative flex items-center gap-7">
            {#each TABS as t}
              <button
                data-tab={t.id}
                onclick={() => activeTab = t.id}
                class={cn(
                  'relative flex items-center gap-2 bg-transparent py-2.5 outline-none',
                  'font-bold cursor-pointer text-slate-800 transition-colors duration-300',
                  activeTab === t.id ? 'text-primary' : 'hover:text-slate-900'
                )}
              >
                <AppIcon name={t.icon} size={18} class={activeTab === t.id ? 'text-primary' : 'text-slate-500'} />
                <span class="text-sm tracking-tight">{t.label}</span>
                {#if t.id === 'payslips' && payslips.length > 0}
                  <span class={cn(
                    'flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-sm font-bold transition-colors',
                    activeTab === t.id ? 'bg-primary text-white' : 'bg-slate-100 text-slate-600'
                  )}>
                    {payslips.length}
                  </span>
                {/if}
              </button>
            {/each}

            <span
              class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10 pointer-events-none"
              style={tabIndicatorStyle}
            ></span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar px-6 py-4">
          {#if activeTab === 'resume'}
            <!-- Financial highlights -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              <div class="rounded-xl border border-slate-200 p-3">
                <p class="text-sm uppercase tracking-wide text-slate-500 font-semibold">Brut (masse)</p>
                <p class="text-sm font-bold text-slate-900 mt-1">{money(detail?.financials?.gross_total ?? (summary?.summary?.total_gross_salary ?? 0))}</p>
              </div>
              <div class="rounded-xl border border-emerald-200 bg-emerald-50/40 p-3">
                <p class="text-sm uppercase tracking-wide text-emerald-600 font-semibold">Net versé</p>
                <p class="text-sm font-bold text-emerald-700 mt-1">{money(detail?.financials?.net_total ?? (summary?.summary?.total_net_salary ?? 0))}</p>
              </div>
              <div class="rounded-xl border border-slate-200 p-3">
                <p class="text-sm uppercase tracking-wide text-slate-500 font-semibold">Employés</p>
                <p class="text-sm font-bold text-slate-900 mt-1">{run.employeeCount}<span class="font-medium text-slate-500 text-sm"> / {run.totalEmployeeCount}</span></p>
              </div>
              <div class="rounded-xl border border-slate-200 p-3">
                <p class="text-sm uppercase tracking-wide text-slate-500 font-semibold">CTC</p>
                <p class="text-sm font-bold text-slate-900 mt-1">{money(summary?.summary?.total_cost_to_company ?? 0)}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <p class="text-sm font-bold text-slate-700 uppercase tracking-wide mb-1 flex items-center gap-1.5">
                  <AppIcon name="landmark" size={14} class="text-rose-500" /> À reverser aux organismes
                </p>
                <div class="rounded-xl border border-slate-200 px-4 py-2 divide-y divide-slate-50">
                  {@render Row('IRPP (DGI)', money(summary?.summary?.total_ipr_to_pay))}
                  {@render Row('CNSS — part salariale', money(summary?.summary?.total_cnss_employee))}
                  {@render Row('CNSS — part patronale', money(summary?.summary?.total_cnss_employer))}
                  {@render Row('INPP', money(summary?.summary?.total_inpp))}
                  {@render Row('ONEM', money(summary?.summary?.total_onem))}
                  {@render Row('Charges employeur (total)', money(summary?.summary?.total_employer_liabilities ?? 0))}
                  {@render Row('Coût total entreprise (CTC)', money(summary?.summary?.total_cost_to_company), true)}
                </div>
              </div>

              <div>
                <p class="text-sm font-bold text-slate-700 uppercase tracking-wide mb-1 flex items-center gap-1.5">
                  <AppIcon name="activity" size={14} class="text-slate-500" /> Avancement de l'exécution
                </p>
                <div class="rounded-xl border border-slate-200 px-4 py-2 divide-y divide-slate-50">
                  {@render Row('Statut', statusLabel)}
                  {@render Row('Bulletins générés', `${payslips.length}`)}
                  {@render Row('Taxes retenues', money(detail?.financials?.total_tax_deductions), false, 'emerald')}
                </div>
              </div>
            </div>
          {:else if activeTab === 'payslips'}
            {#if payslips.length === 0}
              <div class="flex flex-col items-center justify-center gap-2 py-12 text-slate-500">
                <AppIcon name="file-text" size={28} class="text-slate-400" />
                <p class="text-sm">Aucun bulletin pour cette exécution.</p>
              </div>
            {:else}
              <PayslipList {payslips} title="Bulletins de l'exécution" icon="file-text" />
            {/if}
          {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <p class="text-sm font-bold text-slate-700 uppercase tracking-wide mb-1">Période</p>
                <div class="rounded-xl border border-slate-200 px-4 py-2 divide-y divide-slate-50">
                  {@render Row('Début', fmtDay(detail?.start_date))}
                  {@render Row('Fin', fmtDay(detail?.end_date))}
                  {@render Row('Jours calendaires', `${periodDays(detail?.start_date, detail?.end_date)}`)}
                  {@render Row('Libellé période', monthLabel(detail?.start_date))}
                </div>
              </div>
              <div>
                <p class="text-sm font-bold text-slate-700 uppercase tracking-wide mb-1">Paramètres</p>
                <div class="rounded-xl border border-slate-200 px-4 py-2 divide-y divide-slate-50">
                  {@render Row('Mode de sélection', selectionMode)}
                  {#if detail?.exchange_rate != null}
                    {@render Row('Taux de change (USD → CDF)', `1 USD = ${money(detail.exchange_rate).replace(' CDF', '')} CDF`)}
                  {/if}
                  {@render Row('Créé le', fmtDay(detail?.created_at))}
                  {@render Row('Mis à jour le', fmtDay(detail?.updated_at))}
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    {/if}
  </Sheet.Content>
</Sheet.Root>

