/**
 * payroll.client.svelte.ts — Façade de rétrocompatibilité (API layer)
 *
 * Ce fichier ne contient plus de logique. Il réexporte les 4 clients SRP :
 *
 *   - advancesApiStore      → /payroll/advances/*
 *   - payrollConfigApiStore → /payroll/configuration/*, /payroll/adjustments/*
 *   - payrollRunApiStore    → /payroll/runs/*
 *   - payslipsApiStore      → /payroll/payslips/*
 *
 * L'export `payrollApiStore` est maintenu pour la rétrocompatibilité avec
 * tout code qui l'importerait directement. Les nouveaux modules doivent
 * importer le client spécialisé correspondant.
 */

export { advancesApiStore }       from './advances/advances.client.svelte';
export { payrollConfigApiStore }  from './configuration/payrollConfig.client.svelte';
export { payrollRunApiStore }     from './runs/payrollRun.client.svelte';
export { payslipsApiStore }       from './payslips/payslips.client.svelte';
export type { AsyncState }        from './advances/advances.client.svelte';

// Façade unifiée legacy — agrège les 4 clients API SRP
import { advancesApiStore }       from './advances/advances.client.svelte';
import { payrollConfigApiStore }  from './configuration/payrollConfig.client.svelte';
import { payrollRunApiStore }     from './runs/payrollRun.client.svelte';
import { payslipsApiStore }       from './payslips/payslips.client.svelte';


/** @deprecated Préférez importer directement le client API spécialisé */
export const payrollApiStore = {
	// Advances
	fetchAdvances:   (...args: Parameters<typeof advancesApiStore.fetchAdvances>)      => advancesApiStore.fetchAdvances(...args),
	createAdvance:   (...args: Parameters<typeof advancesApiStore.createAdvance>)      => advancesApiStore.createAdvance(...args),
	approveAdvance:  (...args: Parameters<typeof advancesApiStore.approveAdvance>)     => advancesApiStore.approveAdvance(...args),
	rejectAdvance:   (...args: Parameters<typeof advancesApiStore.rejectAdvance>)      => advancesApiStore.rejectAdvance(...args),

	// Configuration
	fetchConfiguration:    ()            => payrollConfigApiStore.fetchConfiguration(),
	fetchSMIG:             ()            => payrollConfigApiStore.fetchSMIG(),
	fetchTaxBrackets:      ()            => payrollConfigApiStore.fetchTaxBrackets(),
	fetchAdjustmentTypes:  ()            => payrollConfigApiStore.fetchAdjustmentTypes(),
	fetchOvertimeRules:    ()            => payrollConfigApiStore.fetchOvertimeRules(),
	fetchLegalAllowances:  ()            => payrollConfigApiStore.fetchLegalAllowances(),
	fetchSocialContributions: ()         => payrollConfigApiStore.fetchSocialContributions(),
	fetchExchangeRate:     ()            => payrollConfigApiStore.fetchExchangeRate(),
	updateConfiguration:   (...args: Parameters<typeof payrollConfigApiStore.updateConfiguration>)   => payrollConfigApiStore.updateConfiguration(...args),
	toggleAdjustmentActive:(...args: Parameters<typeof payrollConfigApiStore.toggleAdjustmentActive>)=> payrollConfigApiStore.toggleAdjustmentActive(...args),
	createAdjustment:      (...args: Parameters<typeof payrollConfigApiStore.createAdjustment>)      => payrollConfigApiStore.createAdjustment(...args),
	updateAdjustment:      (...args: Parameters<typeof payrollConfigApiStore.updateAdjustment>)      => payrollConfigApiStore.updateAdjustment(...args),
	deleteAdjustment:      (...args: Parameters<typeof payrollConfigApiStore.deleteAdjustment>)      => payrollConfigApiStore.deleteAdjustment(...args),
	updateOvertimeRule:    (...args: Parameters<typeof payrollConfigApiStore.updateOvertimeRule>)     => payrollConfigApiStore.updateOvertimeRule(...args),
	updateLegalAllowance:  (...args: Parameters<typeof payrollConfigApiStore.updateLegalAllowance>)  => payrollConfigApiStore.updateLegalAllowance(...args),
	resetLegalAllowances:  ()            => payrollConfigApiStore.resetLegalAllowances(),
	resetAdjustments:      ()            => payrollConfigApiStore.resetAdjustments(),

	// Runs
	fetchRunList:   (...args: Parameters<typeof payrollRunApiStore.fetchRunList>)   => payrollRunApiStore.fetchRunList(...args),
	fetchRunDetail: (...args: Parameters<typeof payrollRunApiStore.fetchRunDetail>) => payrollRunApiStore.fetchRunDetail(...args),
	createRun:      (...args: Parameters<typeof payrollRunApiStore.createRun>)      => payrollRunApiStore.createRun(...args),
	updateRun:      (...args: Parameters<typeof payrollRunApiStore.updateRun>)      => payrollRunApiStore.updateRun(...args),
	processRun:     (...args: Parameters<typeof payrollRunApiStore.processRun>)     => payrollRunApiStore.processRun(...args),
	completeRun:    (...args: Parameters<typeof payrollRunApiStore.completeRun>)    => payrollRunApiStore.completeRun(...args),
	cancelRun:      (...args: Parameters<typeof payrollRunApiStore.cancelRun>)      => payrollRunApiStore.cancelRun(...args),

	// Payslips
	fetchPayslipList:   (...args: Parameters<typeof payslipsApiStore.fetchPayslipList>)   => payslipsApiStore.fetchPayslipList(...args),
	fetchPayslipDetail: (...args: Parameters<typeof payslipsApiStore.fetchPayslipDetail>) => payslipsApiStore.fetchPayslipDetail(...args),

	resetErrors() {
		advancesApiStore.resetErrors();
		payrollConfigApiStore.resetErrors();
		payrollRunApiStore.resetErrors();
		payslipsApiStore.resetErrors();
	},
};

