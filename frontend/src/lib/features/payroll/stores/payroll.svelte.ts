/**
 * payroll.svelte.ts — Façade de rétrocompatibilité
 *
 * Ce fichier ne contient plus de logique métier. Il réexporte
 * l'instance `payrollStore` qui délègue vers les 4 stores SRP :
 *
 *   - advancesStore      → cycle de vie des avances sur salaire
 *   - payrollConfigStore → configuration légale & taux de change
 *   - payrollRunStore    → runs de paie & wizard de traitement (S1-S7)
 *   - payslipsStore      → bulletins de paie, filtres & pagination
 *
 * Les composants existants continuent d'importer `payrollStore` sans
 * modification. Les nouveaux composants peuvent importer directement
 * le store spécialisé correspondant.
 */

import type { Advance, AdvanceCreatePayload } from '../types/types';

import { advancesStore }       from './advances/advancesStore.svelte';
import { payrollConfigStore }  from './configuration/payrollConfigStore.svelte';
import { payrollRunStore }     from './runs/payrollRunStore.svelte';
import { payslipsStore }       from './payslips/payslipsStore.svelte';

// Re-export individual stores for new code that imports them directly
export { advancesStore }       from './advances/advancesStore.svelte';
export { payrollConfigStore }  from './configuration/payrollConfigStore.svelte';
export { payrollRunStore }     from './runs/payrollRunStore.svelte';
export { payslipsStore }       from './payslips/payslipsStore.svelte';


/**
 * PayrollStore — Façade unifiée (rétrocompatibilité)
 *
 * Toutes les propriétés et méthodes sont des accesseurs qui
 * délèguent vers le store SRP approprié.
 */
class PayrollStoreFacade {

	// ─── payrollConfigStore ───────────────────────────────────────────────────

	get exchangeRateInfo()         { return payrollConfigStore.exchangeRateInfo; }
	get exchangeRate()             { return payrollConfigStore.exchangeRate; }
	get configuration()            { return payrollConfigStore.configuration; }
	get smigRates()                { return payrollConfigStore.smigRates; }
	get taxBrackets()              { return payrollConfigStore.taxBrackets; }
	get adjustments()              { return payrollConfigStore.adjustments; }
	get overtimeRules()            { return payrollConfigStore.overtimeRules; }
	get legalAllowances()          { return payrollConfigStore.legalAllowances; }
	get socialContributions()      { return payrollConfigStore.socialContributions; }
	get isSavingConfiguration()    { return payrollConfigStore.isSavingConfiguration; }
	get activeSMIG()               { return payrollConfigStore.activeSMIG; }

	syncConfiguration()            { return payrollConfigStore.syncConfiguration(); }
	saveConfiguration(data: any)   { return payrollConfigStore.saveConfiguration(data); }
	refreshExchangeRate()          { return payrollConfigStore.refreshExchangeRate(); }
	saveOvertimeRule(id: string, data: any)     { return payrollConfigStore.saveOvertimeRule(id, data); }
	saveLegalAllowance(id: string, data: any)   { return payrollConfigStore.saveLegalAllowance(id, data); }
	resetLegalAllowances()         { return payrollConfigStore.resetLegalAllowances(); }
	resetAdjustments()             { return payrollConfigStore.resetAdjustments(); }
	toggleAdjustmentActive(id: string, v: boolean) { return payrollConfigStore.toggleAdjustmentActive(id, v); }
	createAdjustment(data: any)    { return payrollConfigStore.createAdjustment(data); }
	updateAdjustment(id: string, data: any)     { return payrollConfigStore.updateAdjustment(id, data); }
	deleteAdjustment(id: string)   { return payrollConfigStore.deleteAdjustment(id); }

	// ─── payrollRunStore ──────────────────────────────────────────────────────

	get currentPeriod()            { return payrollRunStore.currentPeriod; }
	set currentPeriod(v: string)   { payrollRunStore.currentPeriod = v; }
	get availablePeriods()         { return payrollRunStore.availablePeriods; }
	get payrollRuns()              { return payrollRunStore.payrollRuns; }
	get currentRun()               { return payrollRunStore.currentRun; }
	get runList()                  { return payrollRunStore.runList; }
	get cycleFilters()             { return payrollRunStore.cycleFilters; }
	get cycleListPage()            { return payrollRunStore.cycleListPage; }
	get cycleListPerPage()         { return payrollRunStore.cycleListPerPage; }
	set cycleListPerPage(v: number) { payrollRunStore.cycleListPerPage = v; }
	get sortBy()                   { return payrollRunStore.sortBy; }
	get sortOrder()                { return payrollRunStore.sortOrder; }
	get filteredRunList()          { return payrollRunStore.filteredRunList; }
	get paginatedRunList()         { return payrollRunStore.paginatedRunList; }
	get runListTotalPages()        { return payrollRunStore.runListTotalPages; }
	get runListTotalItems()        { return payrollRunStore.runListTotalItems; }
	get runListPeriods()           { return payrollRunStore.runListPeriods; }
	get activeCycleFiltersCount()  { return payrollRunStore.activeCycleFiltersCount; }
	get currentStep()              { return payrollRunStore.currentStep; }
	get steps()                    { return payrollRunStore.steps; }
	get currentStepIndex()         { return payrollRunStore.currentStepIndex; }
	get canGoNext()                { return payrollRunStore.canGoNext; }
	get canGoPrev()                { return payrollRunStore.canGoPrev; }
	get isLastStep()               { return payrollRunStore.isLastStep; }
	get maxAccessibleStepIndex()   { return payrollRunStore.maxAccessibleStepIndex; }

	canAccessStep(i: number)       { return payrollRunStore.canAccessStep(i); }
	setCycleFilter<K extends Parameters<typeof payrollRunStore.setCycleFilter>[0]>(k: K, v: any) { payrollRunStore.setCycleFilter(k, v); }
	resetCycleFilters()            { payrollRunStore.resetCycleFilters(); }
	setCycleListPage(p: number)    { payrollRunStore.setCycleListPage(p); }
	setSort(by: any)               { payrollRunStore.setSort(by); }
	fetchRunList()                 { return payrollRunStore.fetchRunList(); }
	fetchRunDetail(id: string)     { return payrollRunStore.fetchRunDetail(id); }

	async createPayrollRun(period: string) {
		return payrollRunStore.createPayrollRun(period);
	}

	async createPayrollRunFromDates(startDate: string, endDate: string, exchangeRate?: number | null) {
		return payrollRunStore.createPayrollRunFromDates(startDate, endDate, exchangeRate);
	}

	async calculatePayroll() {
		return payrollRunStore.calculatePayroll();
	}

	async reviewPayroll()  { return payrollRunStore.reviewPayroll(); }
	async approvePayroll() { return payrollRunStore.approvePayroll(); }

	async processPayment() {
		return payrollRunStore.processPayment();
	}

	nextStep()              { payrollRunStore.nextStep(); }
	prevStep()              { payrollRunStore.prevStep(); }
	goToStep(step: any)     { payrollRunStore.goToStep(step); }
	goToNextStep()          { payrollRunStore.nextStep(); }
	resetSteps()            { payrollRunStore.resetSteps(); }

	// ─── payslipsStore ────────────────────────────────────────────────────────

	get payslips()           { return payslipsStore.payslips; }
	get filters()            { return payslipsStore.filters; }
	get currentPage()        { return payslipsStore.currentPage; }
	get perPage()            { return payslipsStore.perPage; }
	get filteredPayslips()   { return payslipsStore.filteredPayslips; }
	get paginatedPayslips()  { return payslipsStore.paginatedPayslips; }
	get totalPages()         { return payslipsStore.totalPages; }
	get totalCount()         { return payslipsStore.totalCount; }
	get activeFiltersCount() { return payslipsStore.activeFiltersCount; }
	get totalNetPay()        { return payslipsStore.totalNetPay; }
	get totalGrossPay()      { return payslipsStore.totalGrossPay; }
	get totalContributions() { return payslipsStore.totalContributions; }
	get totalTax()            { return payslipsStore.totalTax; }
	get totalSocialSecurity() { return payslipsStore.totalContributions; }
	get activeEmployeesCount()    { return payslipsStore.activeEmployeesCount; }
	get totalBaseSalary()         { return payslipsStore.totalBaseSalary; }
	get averageSalary()           { return payslipsStore.averageSalary; }
	get completeProfilesCount()   { return payslipsStore.completeProfilesCount; }
	get completionRate()          { return payslipsStore.completionRate; }
	get orgUnitDistribution()     { return payslipsStore.orgUnitDistribution; }

	generatePayslips(period: string) { payslipsStore.generatePayslips(period); }
	toggleFilter(category: any, value: string) { payslipsStore.toggleFilter(category, value); }
	setSearch(value: string)         { payslipsStore.setSearch(value); }
	setPeriod(period: string)        { payslipsStore.setPeriod(period); }
	resetFilters()                   { payslipsStore.resetFilters(); }
	setPage(page: number)            { payslipsStore.setPage(page); }
	setPerPage(size: number)         { payslipsStore.setPerPage(size); }
	nextPage()                       { payslipsStore.nextPage(); }
	prevPage()                       { payslipsStore.prevPage(); }

	// ─── advancesStore ────────────────────────────────────────────────────────

	get advances()               { return advancesStore.advances; }
	get pendingAdvances()        { return advancesStore.pendingAdvances; }
	get pendingAdvancesCount()   { return advancesStore.pendingAdvancesCount; }
	get pendingAdvancesAmount()  { return advancesStore.pendingAdvancesAmount; }
	get highRiskAdvancesCount()  { return advancesStore.highRiskAdvancesCount; }

	get variablesDetected() {
		return {
			primes: 3,
			avances: advancesStore.advances.filter(a => a.status === 'APPROVED' || a.status === 'ACTIVE').length
		};
	}

	get excludedEmployees() { return [{ employeeName: 'Jean Marc', reason: 'Fin de contrat', orgUnit: 'Admin' }, { employeeName: 'Marie Claire', reason: 'En congé prolongé', orgUnit: 'RH' }]; }
	get excludedEmployeesCount() { return this.excludedEmployees.length; }

	requestAdvance(payload: AdvanceCreatePayload): Promise<Advance | null> {
		return advancesStore.requestAdvance(payload);
	}
	
	approveAdvance(id: string)                 { advancesStore.approveAdvance(id); }
	rejectAdvance(id: string, reason = '')     { return advancesStore.rejectAdvance(id, reason); }
	submitAdvance(id: string)                  { return advancesStore.submitAdvance(id); }
	activateAdvance(id: string)                { return advancesStore.activateAdvance(id); }
	updateAdvanceConfig(id: string, data: any) { return advancesStore.updateAdvanceConfig(id, data); }
	updateAdvanceFields(id: string, data: Partial<AdvanceCreatePayload>) { return advancesStore.updateAdvance(id, data); }

	// ─── Sync générique (legacy) ──────────────────────────────────────────────

	async syncFromApi(source: 'runList' | 'runDetail' | 'payslips' | 'advances' | 'configuration', params?: Record<string, any>) {
		switch (source) {
			case 'runList':        return payrollRunStore.fetchRunList();
			case 'runDetail':      return payrollRunStore.fetchRunDetail(params?.runId as string);
			case 'payslips':       return payslipsStore.fetchPayslips(params?.runId as string);
			case 'advances':       return advancesStore.syncFromApi(params);
			case 'configuration':  return payrollConfigStore.syncConfiguration();
		}
	}
}


export const payrollStore = new PayrollStoreFacade();

