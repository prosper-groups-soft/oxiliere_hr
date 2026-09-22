import type { Payslip } from '../../types/types';
import { payrollRunStore } from '../runs/payrollRunStore.svelte';
import { get_api_base_origin } from '@/utilities/http/urls';


function num(v: any): number { const n = Number(v); return Number.isFinite(n) ? n : 0; }

function normalizePayslipRow(raw: any): Payslip {
  const hasEmployee = raw.employee && typeof raw.employee === 'object';
  const baseEmployee: any = hasEmployee ? raw.employee : { id: raw.contract ? String(raw.contract) : '', matricule: '', fullName: raw.employee_name || '', orgUnit: raw.org_unit || '', jobTitle: raw.job_title || '' };
  const avatarUrl = raw.photo_path ?? raw.avatar_url ?? baseEmployee.avatarUrl ?? null;
  return { ...raw, employee: { ...baseEmployee, avatarUrl }, summary: raw.summary ?? { grossSalary: num(raw.gross_amount), totalDeductions: 0, postNetDeductions: 0, netPay: num(raw.net_amount), employerCosts: 0, totalEmployerCost: 0 } } as Payslip;
}


export class PayslipsStore {
  payslips = $state<Payslip[]>([]);
  currentPeriod = $state<string>('');
  availablePeriods = $state<string[]>([]);
  error = $state<string | null>(null);

  // Filtres serveur (comme payrollRunStore.cycleFilters)
  search = $state('');
  orgUnit = $state('');
  runId = $state(''); // '' = tous les runs
  ordering = $state<string>('-createdAt');

  currentPage = $state(1);
  perPage = $state(10);
  totalCount = $state(0);
  isFetching = $state(false);

  totalPages = $derived(Math.ceil(this.totalCount / this.perPage) || 1);
  paginatedPayslips = $derived(this.payslips); // serveur déjà paginé
  filteredPayslips = $derived(this.payslips);
  activeFiltersCount = $derived((this.orgUnit ? 1 : 0) + (this.runId ? 1 : 0));
  // compat ancien +page.svelte qui lit payrollStore.* — exposés en alias
  filters = $derived({ search: this.search, status: [] as string[], orgUnit: this.orgUnit ? [this.orgUnit] : [], period: this.currentPeriod });
  totalNetPay = $derived(this.payslips.reduce((s, p) => s + (p.summary?.netPay ?? num((p as any).net_amount)), 0));
  totalGrossPay = $derived(this.payslips.reduce((s, p) => s + (p.summary?.grossSalary ?? num((p as any).gross_amount)), 0));

  private _timer: any = null;
  private _fetchId = 0;

  setSearch(v: string) { this.search = v; this.currentPage = 1; this._debouncedFetch(); }
  setOrgUnit(v: string) { this.orgUnit = v; this.currentPage = 1; this.fetchPayslips(); }
  setRunId(v: string) { this.runId = v; this.currentPage = 1; this.fetchPayslips(); }
  setOrdering(v: string) { this.ordering = v; this.fetchPayslips(); }
  setPage(p: number) { this.currentPage = Math.max(1, Math.min(p, this.totalPages)); this.fetchPayslips(); }
  setPerPage(n: number) { this.perPage = n; this.currentPage = 1; this.fetchPayslips(); }
  nextPage() { if (this.currentPage < this.totalPages) { this.currentPage++; this.fetchPayslips(); } }
  prevPage() { if (this.currentPage > 1) { this.currentPage--; this.fetchPayslips(); } }
  toggleFilter(_k: string, v: string) { this.setOrgUnit(this.orgUnit === v ? '' : v); }
  setPeriod(p: string) { this.currentPeriod = p; }
  resetFilters() { this.search = ''; this.orgUnit = ''; this.runId = ''; this.currentPage = 1; this.fetchPayslips(); }

  private _debouncedFetch() {
    clearTimeout(this._timer);
    this._timer = setTimeout(() => this.fetchPayslips(), 350);
  }

  async fetchPayslips(runId?: string) {
    if (runId !== undefined) this.runId = runId;
    if (payrollRunStore.availablePeriods.length) {
      this.availablePeriods = payrollRunStore.availablePeriods;
      if (!this.currentPeriod) this.currentPeriod = payrollRunStore.currentPeriod || this.availablePeriods[0];
    }
    const fid = ++this._fetchId;
    this.isFetching = true;
    try {
      const { fetchPayslipsGlobal } = await import('@/hr/payroll/queries/payroll');
      const res = await fetchPayslipsGlobal({ page: this.currentPage, pageSize: this.perPage, search: this.search || undefined, orgUnit: this.orgUnit || undefined, runId: this.runId || undefined, ordering: this.ordering || undefined });
      if (fid !== this._fetchId) return;
      this.payslips = (res?.results as any[] ?? []).map(normalizePayslipRow);
      this.totalCount = res?.count ?? this.payslips.length;
    } catch (e: any) {
      this.error = e?.message ?? 'Erreur chargement bulletins';
      throw e;
    } finally { if (fid === this._fetchId) this.isFetching = false; }
  }

  async generatePayslips(_period: string) { await this.fetchPayslips(); }
  markAsCalculated() { this.payslips = this.payslips.map(p => ({ ...p, status: 'calculated' as const })); }
  markAsPaid() { this.payslips = this.payslips.map(p => ({ ...p, status: 'paid' as const, paidAt: new Date().toISOString() })); }

  downloadPayslip(id: string) { window.open(`${get_api_base_origin()}/api/payroll/payslips/${id}/export/`, '_blank'); }
  downloadZip() { const q = this.runId ? `?run_id=${this.runId}` : ''; window.open(`${get_api_base_origin()}/api/payroll/payslips/export/zip/${q}`, '_blank'); }
}


export const payslipsStore = new PayslipsStore();

