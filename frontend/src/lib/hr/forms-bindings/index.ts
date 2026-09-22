// Agrégateur MUET des bindings métier (avancement §2.1) : imports + init.
// Un module consomme un type via la factory déclarative + le registre (rempli
// par registerAllBusinessTypes à l'init), jamais via l'import du binding.
// `forms/` reste standalone : ce dossier est le seul point de couplage
// bindings ↔ endpoints/stores métier.
export { persist } from './persist.js';
export type { PersistConfig, PersistUpdateArgs } from './persist.js';
import { registerOrgTypes } from '@/hr/modules/jobs/forms/bindings/org-types.js';
import { registerEmployeeTypes } from '@/hr/modules/employees/forms/bindings/employee-type.js';
import { registerEnumTypes } from './enums.js';
import { registerGeoTypes } from './geo.js';
import { registerJobTypes } from '@/hr/modules/jobs/forms/bindings/job-types.js';
import { registerLeaveTypes } from '@/hr/modules/leaves/forms/bindings/leave-types.js';
import { registerPayrollTypes } from '@/hr/modules/payroll/forms/bindings/payroll-type.js';
import { registerAccessTypes } from '@/hr/modules/admin/access/forms/bindings/group-type.js';
import { registerBankTypes } from '@/hr/modules/banking/forms/bindings/bank-types.js';
import { registerTimelineType } from '@/hr/modules/leaves/forms/bindings/timeline-type.js';
import { registerPolicyGridType } from '@/hr/modules/attendance/forms/bindings/policy-grid-type.js';
import { registerScoringType } from '@/hr/modules/recruitment/forms/bindings/scoring-type.js';
import { registerRepaymentPlanType } from '@/hr/modules/payroll/forms/bindings/repayment-plan-type.js';
import { registerGoalEditorType } from '@/hr/modules/performance/forms/bindings/goal-editor-type.js';

let done = false;

/** Enregistre tous les types métier data-aware. Idempotent. */
export function registerAllBusinessTypes(): void {
	if (done) return;
	done = true;
	registerOrgTypes();
	registerJobTypes();
	registerEmployeeTypes();
	registerEnumTypes();
	registerGeoTypes();
	registerLeaveTypes();
	registerPayrollTypes();
	registerAccessTypes();
	registerBankTypes();
	registerTimelineType();
	registerPolicyGridType();
	registerScoringType();
	registerRepaymentPlanType();
	registerGoalEditorType();
}
