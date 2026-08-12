import type { PayrollRun, PayrollRunApiOut, PayrollRunDetailApiOut, PayrollRunSummaryApiOut, Payslip, Advance, AdvanceCreatePayload, AdvanceUpdatePayload, PayrollFilters, PayrollConfiguration, PayrollConfigurationUpdate, SMIGConfiguration, TaxBracketConfig, PayrollAdjustmentConfig, OvertimeRule, LegalAllowanceConfig, SocialContributionRate, ContractPayElementItem, ContractPayElementSummary, ProfessionalCategory } from '@/features/payroll/types/types';
import { PayrollApi } from '@/features/payroll/api/payroll.endpoints';
import { getStaleTime } from '@/api/queries/utils';


/** Réponse brute de l'endpoint /api/payroll/configuration/exchange-rate/ */
export interface ExchangeRateResponse {
  /** Valeur du taux (string — format Decimal côté backend) */
  rate: string;
  /** Source du taux : "bcc" (Banque Centrale du Congo) ou "config" (taux manuel) */
  source: 'bcc' | 'config' | string;
  /** Paire de devises concernée, ex. "USD/CDF" */
  currency_pair: string;
}

/** Filtres de la liste des avances (envoyés au backend) */
export interface AdvanceListFilters {
  search?: string;
  /** Statuts séparés par des virgules (PENDING,APPROVED...) */
  status?: string;
  /** Niveaux de risque séparés par des virgules (LOW,MEDIUM,HIGH) */
  risk_level?: string;
}


/* ─── Run List ─── */

export const payrollQueryOptions = {
  /** Cache-key root */
  all: () => ['payroll'] as const,

  /* ── Run list (S1) ── */
  runLists: () => [...payrollQueryOptions.all(), 'runs', 'list'] as const,
  runList: (filters: { page?: number; pageSize?: number; status?: string; period?: string; search?: string; orgUnit?: string }) => ({
    queryKey: [...payrollQueryOptions.runLists(), filters],
    queryFn: () => fetchRunList(filters),
    staleTime: getStaleTime(5),
  }),

  /* ── Run detail (S3) ── */
  runDetails: () => [...payrollQueryOptions.all(), 'runs', 'detail'] as const,
  runDetail: (runId: string) => ({
    queryKey: [...payrollQueryOptions.runDetails(), runId],
    queryFn: () => fetchRunDetail(runId),
    staleTime: getStaleTime(2),
  }),

  /* ── Run summary ── */
  runSummary: (runId: string) => ({
    queryKey: [...payrollQueryOptions.runDetails(), runId, 'summary'],
    queryFn: () => fetchRunSummary(runId),
    staleTime: getStaleTime(2),
  }),

  /* ── Payslips list (S4) ── */
  payslipLists: () => [...payrollQueryOptions.all(), 'payslips', 'list'] as const,
  payslipList: (runId: string, filters?: PayrollFilters) => ({
    queryKey: [...payrollQueryOptions.payslipLists(), runId, filters],
    queryFn: () => fetchPayslips(runId, filters),
    staleTime: getStaleTime(2),
  }),

  /* ── Payslip detail (S4) ── */
  payslipDetail: (payslipId: string) => ({
    queryKey: [...payrollQueryOptions.payslipLists(), 'detail', payslipId],
    queryFn: () => fetchPayslipDetail(payslipId),
    staleTime: getStaleTime(5),
  }),

  /* ── Advances (S6) ── */
  advanceLists: () => [...payrollQueryOptions.all(), 'advances', 'list'] as const,
  advanceList: (filters?: AdvanceListFilters) => ({
    queryKey: [...payrollQueryOptions.advanceLists(), filters],
    queryFn: () => fetchAdvances(filters),
    staleTime: getStaleTime(2),
  }),

  /* ── Configuration (S8) ── */
  configuration: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration'],
    queryFn: fetchConfiguration,
    staleTime: getStaleTime(15),
  }),

  /* ── SMIG rates (S8) ── */
  smigList: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'smig'],
    queryFn: fetchSMIG,
    staleTime: getStaleTime(15),
  }),

  /* ── Tax brackets (S8) ── */
  taxBrackets: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'tax-brackets'],
    queryFn: fetchTaxBrackets,
    staleTime: getStaleTime(15),
  }),

  /* ── Payroll adjustments / catalog (S8) ── */
  adjustments: () => ({
    queryKey: [...payrollQueryOptions.all(), 'adjustments', 'types'],
    queryFn: fetchAdjustments,
    staleTime: getStaleTime(15),
  }),

  /* ── Overtime rules (RDC) ── */
  overtimeRules: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'overtime'],
    queryFn: fetchOvertimeRules,
    staleTime: getStaleTime(15),
  }),

  /* ── Legal allowances (S8) ── */
  legalAllowances: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'allowances'],
    queryFn: fetchLegalAllowances,
    staleTime: getStaleTime(15),
  }),

  /* ── Social contribution rates (CNSS, ONEM, INPP) — read-only ── */
  socialContributions: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'contributions'],
    queryFn: fetchSocialContributions,
    staleTime: getStaleTime(60),
  }),

  /* ── Exchange rate (USD → CDF) ── */
  exchangeRate: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'exchange-rate'],
    queryFn: fetchExchangeRate,
    staleTime: getStaleTime(5),
  }),

  /* ── Contract pay elements (S10) ── */
  contractPayElements: (contractId: string) => ({
    queryKey: [...payrollQueryOptions.all(), 'contracts', contractId, 'pay-elements'],
    queryFn: () => fetchContractPayElements(contractId),
    staleTime: getStaleTime(5),
  }),

  /* ── Professional categories (S8) ── */
  professionalCategories: () => ({
    queryKey: [...payrollQueryOptions.all(), 'configuration', 'professional-categories'],
    queryFn: fetchProfessionalCategories,
    staleTime: getStaleTime(15),
  }),
};


/*
   API fetch functions
*/

/** Fetch paginated run list (raw PayrollRunOut objects — mapping to RunListItem happens in the store) */
async function fetchRunList(filters: {
  page?: number; pageSize?: number; status?: string; period?: string; search?: string; orgUnit?: string;
}): Promise<{ results: PayrollRunApiOut[]; count: number }> {
  const params: Record<string, any> = {};
  if (filters.page) params.page = filters.page;
  if (filters.pageSize) params.page_size = filters.pageSize;
  // Le filtrage statut/période est appliqué côté client (filteredRunList) :
  // le backend ne matche que des statuts exacts (DRAFT, PAID…), pas les valeurs RunListStatus.
  if (filters.search) params.search = filters.search;
  if (filters.orgUnit) params.org_unit = filters.orgUnit;
  return PayrollApi.runs.list(params);
}

/** Fetch a single payroll run (returns the raw service dict) */
async function fetchRunDetail(runId: string): Promise<PayrollRunDetailApiOut> {
  return PayrollApi.runs.retrieve(runId);
}

/** Fetch run financial summary */
async function fetchRunSummary(runId: string): Promise<PayrollRunSummaryApiOut> {
  return PayrollApi.runSummary.retrieve(runId);
}

/** Fetch payslips for a run */
async function fetchPayslips(runId: string, _filters?: PayrollFilters): Promise<{ results: Payslip[]; count: number }> {
  return PayrollApi.runPayslips.list(runId);
}

/** Fetch single payslip detail */
async function fetchPayslipDetail(payslipId: string): Promise<Payslip> {
  return PayrollApi.runPayslips.retrieve(payslipId);
}

/** Fetch salary advances (server-side filtering) */
async function fetchAdvances(filters?: AdvanceListFilters): Promise<{ results: Advance[]; count: number }> {
  const params: Record<string, any> = {};
  if (filters?.search) params.search = filters.search;
  if (filters?.status) params.status = filters.status;
  if (filters?.risk_level) params.risk_level = filters.risk_level;
  return PayrollApi.advances.list(params);
}

/** Fetch payroll configuration */
async function fetchConfiguration(): Promise<PayrollConfiguration> {
  return PayrollApi.configuration.retrieve();
}

/** Fetch SMIG rates (historical + active) */
async function fetchSMIG(): Promise<SMIGConfiguration[]> {
  const res = await PayrollApi.smig.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Fetch progressive tax brackets */
async function fetchTaxBrackets(): Promise<TaxBracketConfig[]> {
  const res = await PayrollApi.taxBrackets.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Fetch payroll adjustment templates (catalog) */
async function fetchAdjustments(): Promise<PayrollAdjustmentConfig[]> {
  const res = await PayrollApi.adjustments.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Fetch overtime rules (RDC multipliers) */
async function fetchOvertimeRules(): Promise<OvertimeRule[]> {
  const res = await PayrollApi.overtime.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Fetch the active USD → CDF exchange rate (BCC live rate → manual config → default) */
async function fetchExchangeRate(): Promise<ExchangeRateResponse> {
  return PayrollApi.exchangeRate.retrieve();
}

/** Fetch legal allowances (Logement, Transport) */
async function fetchLegalAllowances(): Promise<LegalAllowanceConfig[]> {
  const res = await PayrollApi.allowances.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Fetch social contribution rates (CNSS, ONEM, INPP) — read-only informational */
async function fetchSocialContributions(): Promise<SocialContributionRate[]> {
  const res = await PayrollApi.contributions.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Update an overtime rule multiplier */
export async function updateOvertimeRule(ruleId: string, data: Partial<OvertimeRule>): Promise<OvertimeRule> {
  return PayrollApi.overtime.partial_update(ruleId, data);
}

/** Update a legal allowance amount/percentage (PATCH /payroll/configuration/allowances/:id) */
export async function updateLegalAllowance(
  allowanceId: string,
  data: Partial<LegalAllowanceConfig>
): Promise<LegalAllowanceConfig> {
  return PayrollApi.allowances.partial_update(allowanceId, data);
}

/** Reset legal allowances from fixture (POST /payroll/configuration/allowances/reset/) */
export async function resetLegalAllowances(): Promise<{ status: string; reset_count: number }> {
  return PayrollApi.allowanceReset.create();
}

/** Reset payroll adjustment catalog from fixture (POST /payroll/adjustments/reset/) */
export async function resetPayrollAdjustments(): Promise<{ status: string; reset_count: number }> {
  return PayrollApi.adjustmentsReset.create();
}

/** Fetch contract pay elements (S10 — GET /payroll/contracts/:id/pay-elements) */
export async function fetchContractPayElements(contractId: string): Promise<ContractPayElementSummary> {
  return PayrollApi.contractPayElements.list(contractId) as unknown as ContractPayElementSummary;
}

/** Add a pay element to a contract (S10 — POST /payroll/contracts/:id/pay-elements) */
export async function createContractPayElement(
  contractId: string,
  data: Partial<ContractPayElementItem> & { adjustment: string; start_period: string; end_period?: string | null; custom_amount?: number | null; custom_percentage?: number | null; is_active?: boolean }
): Promise<ContractPayElementItem> {
  // IMPORTANT : le backend (ContractAdjustmentCreateIn) attend `start_date`/`end_date`,
  // pas `start_period`/`end_period` (noms S10 frontend). Mapping obligatoire sinon les
  // dates sont silencieusement ignorées → NOT NULL constraint failed sur start_date.
  const { start_period, end_period, ...rest } = data;
  const payload = {
    ...rest,
    start_date: start_period,
    end_date: end_period ?? null,
  };
  return PayrollApi.contractPayElements.create(contractId, payload) as unknown as ContractPayElementItem;
}

/** Update a contract pay element (S10 — PATCH /payroll/contracts/:id/pay-elements/:elementId) */
export async function patchContractPayElement(
  contractId: string,
  elementId: string,
  data: Partial<ContractPayElementItem>
): Promise<ContractPayElementItem> {
  return PayrollApi.contractPayElements.partial_update(contractId, elementId, data) as unknown as ContractPayElementItem;
}

/** Delete a contract pay element (S10 — DELETE /payroll/contracts/:id/pay-elements/:elementId) */
export async function deleteContractPayElement(
  contractId: string,
  elementId: string
): Promise<{ message: string }> {
  return PayrollApi.contractPayElements.destroy(contractId, elementId) as unknown as { message: string };
}

/** Fetch professional categories grid (S8 — GET /payroll/configuration/professional-categories) */
export async function fetchProfessionalCategories(): Promise<ProfessionalCategory[]> {
  const res = await PayrollApi.professionalCategories.list();
  return Array.isArray(res) ? res : (res?.results ?? []);
}

/** Update a professional category (S8 — PATCH /payroll/configuration/professional-categories/:id) */
export async function updateProfessionalCategory(
  categoryId: string,
  data: Partial<ProfessionalCategory>
): Promise<ProfessionalCategory> {
  return PayrollApi.professionalCategories.partial_update(categoryId, data) as unknown as ProfessionalCategory;
}

/** Reset professional categories from fixture (POST /payroll/configuration/professional-categories/reset/) */
export async function resetProfessionalCategories(): Promise<{ status: string; reset_count: number }> {
  return PayrollApi.professionalCategoriesReset.create();
}

/*
   Mutations
*/

/** Create a new payroll run (backend accepts start_date/end_date only) */
export async function createPayrollRun(data: {
  start_date: string; end_date: string; exchange_rate_applied?: number | null;
}): Promise<PayrollRunApiOut> {
  return PayrollApi.runs.create(data);
}

/** Update a payroll run */
export async function updatePayrollRun(runId: string, data: Partial<PayrollRun>): Promise<PayrollRun> {
  return PayrollApi.runs.partial_update(runId, data);
}

/** Process payroll (generate payslips) */
export async function processPayrollRun(runId: string): Promise<{ task_id: string; status: string }> {
  return PayrollApi.runProcess.create(runId);
}

/** Complete payroll (finalize) */
export async function completePayrollRun(runId: string): Promise<PayrollRunApiOut> {
  return PayrollApi.runComplete.create(runId);
}

/** Review payroll (VALIDATED → REVIEWED) */
export async function reviewPayrollRun(runId: string): Promise<PayrollRunApiOut> {
  return PayrollApi.runReview.create(runId);
}

/** Approve payroll (REVIEWED → APPROVED) */
export async function approvePayrollRun(runId: string): Promise<PayrollRunApiOut> {
  return PayrollApi.runApprove.create(runId);
}

/** Cancel payroll */
export async function cancelPayrollRun(runId: string): Promise<PayrollRunApiOut> {
  return PayrollApi.runCancel.create(runId);
}

/** Request an advance */
export async function requestAdvance(data: AdvanceCreatePayload): Promise<Advance> {
  return PayrollApi.advances.create(data);
}

/** Approve an advance (PATCH /payroll/advances/:id/approve) */
export async function approveAdvance(advanceId: string): Promise<Advance> {
  return PayrollApi.advanceApprove.partial_update(advanceId, {});
}

/** Activate an approved advance (PATCH /payroll/advances/:id/activate) */
export async function activateAdvance(advanceId: string): Promise<Advance> {
  return PayrollApi.advanceActivate.partial_update(advanceId, {});
}

/**
 * Update advance deduction configuration (PATCH /payroll/advances/:id/configuration)
 * This is the SINGLE route that modifies deduction settings at approval time.
 */
export async function updateAdvance(advanceId: string, data: AdvanceUpdatePayload): Promise<Advance> {
  const config = await PayrollApi.advanceConfiguration.partial_update(advanceId, data);
  return config as unknown as Advance;
}

/** Edit a draft advance fields (PATCH /payroll/advances/:id) — amount, reason */
export async function updateAdvanceFields(advanceId: string, data: Record<string, any>): Promise<Advance> {
  return PayrollApi.advances.partial_update(advanceId, data);
}

/** Reject an advance (PATCH /payroll/advances/:id/reject) — reason is mandatory */
export async function rejectAdvance(advanceId: string, reason = ''): Promise<Advance> {
  return PayrollApi.advanceReject.partial_update(advanceId, { reason });
}

/** Submit a draft advance (POST /payroll/advances/:id/submit) */
export async function submitAdvance(advanceId: string): Promise<Advance> {
  return PayrollApi.advanceSubmit.create(advanceId);
}

/** Update the global payroll configuration */
export async function updatePayrollConfiguration(data: PayrollConfigurationUpdate): Promise<PayrollConfiguration> {
  return PayrollApi.configuration.partial_update(data);
}

/** Toggle the active state of a payroll adjustment (catalog) */
export async function togglePayrollAdjustment(adjustmentId: string, isActive: boolean): Promise<PayrollAdjustmentConfig> {
  return PayrollApi.adjustments.partial_update(adjustmentId, { is_active: isActive });
}

/** Create a new payroll adjustment template (POST /payroll/adjustments/types) */
export async function createPayrollAdjustment(
  data: Partial<PayrollAdjustmentConfig>
): Promise<PayrollAdjustmentConfig> {
  return PayrollApi.adjustments.create(data);
}

/** Update a payroll adjustment template (PATCH /payroll/adjustments/:id) */
export async function updatePayrollAdjustment(
  adjustmentId: string,
  data: Partial<PayrollAdjustmentConfig>
): Promise<PayrollAdjustmentConfig> {
  return PayrollApi.adjustments.partial_update(adjustmentId, data);
}

/** Delete a payroll adjustment template (DELETE /payroll/adjustments/:id) */
export async function deletePayrollAdjustment(adjustmentId: string): Promise<{ message: string }> {
  return PayrollApi.adjustments.destroy(adjustmentId);
}

