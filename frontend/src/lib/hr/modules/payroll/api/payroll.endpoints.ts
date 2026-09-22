import APIEndPoint from '@/hr/utilities/http/rest';


/**
 * Payroll API endpoints.
 * Backend: Django-Ninja @api_controller('/payroll/runs'), etc.
 * Connected controllers: PayrollRunController, PayrollConfigurationController,
 *   SalaryAdvanceController, EmployeeContractController, PayrollAdjustmentsController.
 */
export const PayrollApi = {
  /** Payroll runs — /api/payroll/runs/ */
  runs: new APIEndPoint('/api/payroll/runs/', '/api/payroll/runs/:id/'),

  /** Payslips within a run — /api/payroll/runs/:runId/payslips */
  runPayslips: new APIEndPoint('/api/payroll/runs/:id/payslips/', '/api/payroll/runs/:id/payslips/:payslipId/'),

  /** Bulletins globaux paginés — /api/payroll/payslips/ (filtre run_id, tri ordering, recherche search) */
  payslips: new APIEndPoint('/api/payroll/payslips/', '/api/payroll/payslips/:id/'),

  /** Détail d'un bulletin — /api/payroll/runs/payslips/:payslipId/ (sans run_id) */
  payslipDetail: new APIEndPoint('/api/payroll/runs/payslips/:payslipId/', '/api/payroll/runs/payslips/:payslipId/'),

  /** Run summary — /api/payroll/runs/:id/summary */
  runSummary: new APIEndPoint('/api/payroll/runs/:id/summary/', '/api/payroll/runs/:id/summary/'),

  /** Aperçu de présence (préparation) — /api/payroll/runs/:id/presence */
  runPresence: new APIEndPoint('/api/payroll/runs/:id/presence/', '/api/payroll/runs/:id/presence/'),

  /** Run processing — /api/payroll/runs/:id/process */
  runProcess: new APIEndPoint('/api/payroll/runs/:id/process', '/api/payroll/runs/:id/process'),

  /** Run complete — /api/payroll/runs/:id/complete */
  runComplete: new APIEndPoint('/api/payroll/runs/:id/complete', '/api/payroll/runs/:id/complete'),

  /** Run review — /api/payroll/runs/:id/review */
  runReview: new APIEndPoint('/api/payroll/runs/:id/review', '/api/payroll/runs/:id/review'),

  /** Run approve — /api/payroll/runs/:id/approve */
  runApprove: new APIEndPoint('/api/payroll/runs/:id/approve', '/api/payroll/runs/:id/approve'),

  /** Run cancel — /api/payroll/runs/:id/cancel */
  runCancel: new APIEndPoint('/api/payroll/runs/:id/cancel', '/api/payroll/runs/:id/cancel'),

  /** Salary advances — /api/payroll/advances/ */
  advances: new APIEndPoint('/api/payroll/advances/', '/api/payroll/advances/:id'),

  /** Approve an advance — PATCH /api/payroll/advances/:id/approve */
  advanceApprove: new APIEndPoint('/api/payroll/advances/:id/approve', '/api/payroll/advances/:id/approve'),

  /** Activate an advance — PATCH /api/payroll/advances/:id/activate */
  advanceActivate: new APIEndPoint('/api/payroll/advances/:id/activate', '/api/payroll/advances/:id/activate'),

  /** Advance deduction configuration — PATCH /api/payroll/advances/:id/configuration */
  advanceConfiguration: new APIEndPoint('/api/payroll/advances/:id/configuration', '/api/payroll/advances/:id/configuration'),

  /** Reject an advance — PATCH /api/payroll/advances/:id/reject */
  advanceReject: new APIEndPoint('/api/payroll/advances/:id/reject', '/api/payroll/advances/:id/reject'),

  /** Submit a draft advance — POST /api/payroll/advances/:id/submit */
  advanceSubmit: new APIEndPoint('/api/payroll/advances/:id/submit', '/api/payroll/advances/:id/submit'),

  /** Payroll configuration — /api/payroll/configuration/ */
  configuration: new APIEndPoint('/api/payroll/configuration/', '/api/payroll/configuration/'),

  /** SMIG rates — /api/payroll/configuration/smig/ */
  smig: new APIEndPoint('/api/payroll/configuration/smig/', '/api/payroll/configuration/smig/:id/'),

  /** Tax brackets (IRPP / IPR) — /api/payroll/configuration/tax-brackets/ */
  taxBrackets: new APIEndPoint('/api/payroll/configuration/tax-brackets/', '/api/payroll/configuration/tax-brackets/:id/'),

  /** Social contribution rates (CNSS, ONEM, INPP) — /api/payroll/configuration/contributions/ */
  contributions: new APIEndPoint('/api/payroll/configuration/contributions/', '/api/payroll/configuration/contributions/:id/'),

  /** Overtime rules (RDC) — /api/payroll/configuration/overtime/ */
  overtime: new APIEndPoint('/api/payroll/configuration/overtime/', '/api/payroll/configuration/overtime/:id/'),

  /** Payroll adjustments (catalog) — /api/payroll/adjustments/types */
  adjustments: new APIEndPoint('/api/payroll/adjustments/types', '/api/payroll/adjustments/:id/'),

  /** Exchange rate (USD → CDF) — /api/payroll/configuration/exchange-rate/ */
  exchangeRate: new APIEndPoint('/api/payroll/configuration/exchange-rate/', '/api/payroll/configuration/exchange-rate/'),

  /** Legal allowances (Familiale, Logement, Transport) — /api/payroll/configuration/allowances/ */
  allowances: new APIEndPoint('/api/payroll/configuration/allowances/', '/api/payroll/configuration/allowances/:id/'),

  /** Reset legal allowances from fixture — POST /api/payroll/configuration/allowances/reset/ */
  allowanceReset: new APIEndPoint('/api/payroll/configuration/allowances/reset/', '/api/payroll/configuration/allowances/reset/'),

  /** Reset payroll adjustment catalog from fixture — POST /api/payroll/adjustments/reset/ */
  adjustmentsReset: new APIEndPoint('/api/payroll/adjustments/reset/', '/api/payroll/adjustments/reset/'),

  /** Contract pay elements */
  contractPayElements: new APIEndPoint('/api/payroll/contracts/:contractId/pay-elements', '/api/payroll/contracts/:contractId/pay-elements/:id'),

  /** Contract adjustments (S10) — même route que pay-elements (rétro-compat) */
  contractAdjustments: new APIEndPoint('/api/payroll/contracts/:contractId/pay-elements', '/api/payroll/contracts/:contractId/pay-elements/:id'),
} as const;

