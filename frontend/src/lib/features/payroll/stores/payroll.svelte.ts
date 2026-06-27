import type {
	PayrollRun,
	PayrollStep,
	Payslip,
	Advance,
	PayrollFilters,
	PayrollStatus,
	Currency,
	ExcludedEmployee
} from '../types/types';
import { PAYROLL_STEPS } from '../types/types';

const MOCK_EMPLOYEES = [
	{ id: 1, name: 'Jean-Paul Mabuso', orgUnit: 'IT', baseSalary: 2500, currency: 'USD' as Currency },
	{ id: 2, name: 'Merveille Kabamba', orgUnit: 'RH', baseSalary: 1800, currency: 'USD' as Currency },
	{ id: 3, name: 'Christian Luvambo', orgUnit: 'Finance', baseSalary: 2200, currency: 'USD' as Currency },
	{ id: 4, name: 'Grace Mbuyi', orgUnit: 'Commercial', baseSalary: 1500, currency: 'USD' as Currency },
	{ id: 5, name: 'Patrick Kalala', orgUnit: 'Production', baseSalary: 1200, currency: 'USD' as Currency },
	{ id: 6, name: 'Sophie Tshibola', orgUnit: 'Administration', baseSalary: 1600, currency: 'USD' as Currency }
];

const CURRENT_PERIOD = '2024-03';

export class PayrollStore {
	// --- Data ---
	currentPeriod = $state<string>(CURRENT_PERIOD);
	exchangeRate = $state<number>(2800); // USD to CDF

	// Available periods for selection
	availablePeriods = $state<string[]>(['2024-01', '2024-02', '2024-03', '2024-04']);

	payrollRuns = $state<PayrollRun[]>([
		{
			id: 'run-1',
			period: '2024-02',
			status: 'paid',
			totalGross: 11500,
			totalNet: 9200,
			totalContributions: 1725,
			totalTaxes: 575,
			totalAllocations: 0,
			employeeCount: 6,
			createdAt: '2024-02-25T08:00:00Z',
			calculatedAt: '2024-02-26T10:00:00Z',
			approvedAt: '2024-02-27T14:00:00Z',
			paidAt: '2024-02-28T09:00:00Z'
		}
	]);

	currentRun = $state<PayrollRun | null>(null);

	// --- Step Management ---
	currentStep = $state<PayrollStep>('preparation');
	steps = $state<PayrollStep[]>(PAYROLL_STEPS);

	currentStepIndex = $derived(
		this.steps.indexOf(this.currentStep)
	);

	canGoNext = $derived(
		this.currentStepIndex < this.steps.length - 1 && this.currentRun !== null
	);

	canGoPrev = $derived(
		this.currentStepIndex > 0
	);

	isLastStep = $derived(
		this.currentStepIndex === this.steps.length - 1
	);

	maxAccessibleStepIndex = $derived.by(() => {
		if (!this.currentRun) return -1;
		const statusToIndex: Record<PayrollStatus, number> = {
			'draft': 0,
			'calculated': 1,
			'reviewed': 2,
			'approved': 3,
			'paid': 4
		};
		return statusToIndex[this.currentRun.status] ?? 0;
	});

	canAccessStep(stepIndex: number) {
		// Allow access to completed steps or next step
		return stepIndex <= this.maxAccessibleStepIndex || stepIndex === this.currentStepIndex;
	}

	payslips = $state<Payslip[]>([]);

	advances = $state<Advance[]>([
		{
			id: 'adv-1',
			employeeId: 4,
			employeeName: 'Grace Mbuyi',
			amount: 500,
			remainingAmount: 200,
			monthlyDeduction: 100,
			requestDate: '2024-01-15',
			approvedDate: '2024-01-16',
			status: 'approved',
			reason: 'Urgence médicale',
			riskLevel: 'low'
		},
		{
			id: 'adv-2',
			employeeId: 5,
			employeeName: 'Patrick Kalala',
			amount: 800,
			remainingAmount: 800,
			monthlyDeduction: 200,
			requestDate: '2024-03-10',
			status: 'pending',
			reason: 'Réparation véhicule',
			riskLevel: 'high'
		}
	]);

	filters = $state<PayrollFilters>({
		search: '',
		status: [],
		orgUnit: [],
		period: CURRENT_PERIOD
	});

	// --- Statistics ---
	excludedEmployees = $state<ExcludedEmployee[]>([
		{ employeeName: 'Jean Marc', reason: 'Fin de contrat', orgUnit: 'Admin' },
		{ employeeName: 'Marie Claire', reason: 'En congé prolongé', orgUnit: 'RH' }
	]);

	// --- Derived ---
	activeEmployeesCount = $derived(
		this.payslips.length || MOCK_EMPLOYEES.length
	);

	excludedEmployeesCount = $derived(
		this.excludedEmployees.length
	);

	totalBaseSalary = $derived(
		this.payslips.reduce((sum, p) => sum + p.baseSalary, 0) || MOCK_EMPLOYEES.reduce((sum, e) => sum + e.baseSalary, 0)
	);

	averageSalary = $derived(
		this.activeEmployeesCount > 0 ? Math.round(this.totalBaseSalary / this.activeEmployeesCount) : 0
	);

	variablesDetected = $derived({
		primes: 3,
		avances: this.advances.filter(a => a.status === 'approved').length
	});

	completeProfilesCount = $derived(
		Math.round(this.activeEmployeesCount * 0.85) // 85% simulation
	);

	completionRate = $derived(
		this.activeEmployeesCount > 0 ? Math.round((this.completeProfilesCount / this.activeEmployeesCount) * 100) : 0
	);

	orgUnitDistribution = $derived(
		MOCK_EMPLOYEES.reduce((acc, emp) => {
			acc[emp.orgUnit] = (acc[emp.orgUnit] || 0) + 1;
			return acc;
		}, {} as Record<string, number>)
	);
	filteredPayslips = $derived.by(() => {
		return this.payslips.filter(p => {
			const matchesSearch = p.employeeName.toLowerCase().includes(this.filters.search.toLowerCase()) ||
				p.orgUnit.toLowerCase().includes(this.filters.search.toLowerCase());
			const matchesStatus = this.filters.status.length === 0 || this.filters.status.includes(p.status);
			const matchesOrgUnit = this.filters.orgUnit.length === 0 || this.filters.orgUnit.includes(p.orgUnit);
			return matchesSearch && matchesStatus && matchesOrgUnit;
		});
	});

	totalNetPay = $derived(
		this.payslips.reduce((sum, p) => sum + p.netPay, 0)
	);

	totalGrossPay = $derived(
		this.payslips.reduce((sum, p) => sum + p.grossPay, 0)
	);

	totalContributions = $derived(
		this.payslips.reduce((sum, p) => {
			const cnssLine = p.lines.find(l => l.label.includes('CNSS') || l.label.includes('INSS'));
			return sum + (cnssLine?.amount || 0);
		}, 0)
	);

	totalTax = $derived(
		this.payslips.reduce((sum, p) => {
			const taxLine = p.lines.find(l => l.label.includes('IRPP') || l.label.includes('Impôt'));
			return sum + Math.abs(taxLine?.amount || 0);
		}, 0)
	);

	totalSocialSecurity = $derived(
		this.payslips.reduce((sum, p) => {
			const cnssLine = p.lines.find(l => l.label.includes('CNSS') || l.label.includes('INSS'));
			return sum + Math.abs(cnssLine?.amount || 0);
		}, 0)
	);

	pendingAdvances = $derived(
		this.advances.filter(a => a.status === 'pending').length
	);

	pendingAdvancesAmount = $derived(
		this.advances
			.filter(a => a.status === 'pending')
			.reduce((sum, a) => sum + a.amount, 0)
	);

	highRiskAdvances = $derived(
		this.advances.filter(a => a.status === 'pending' && a.riskLevel === 'high').length
	);

	activeFiltersCount = $derived(
		this.filters.status.length + this.filters.orgUnit.length
	);

	// --- Pagination ---
	currentPage = $state<number>(1);
	perPage = $state<number>(8);

	paginatedPayslips = $derived.by(() => {
		const start = (this.currentPage - 1) * this.perPage;
		const end = start + this.perPage;
		return this.filteredPayslips.slice(start, end);
	});

	totalPages = $derived(
		Math.ceil(this.filteredPayslips.length / this.perPage) || 1
	);

	totalCount = $derived(this.filteredPayslips.length);

	// --- Actions ---
	createPayrollRun(period: string) {
		const newRun: PayrollRun = {
			id: `run-${Date.now()}`,
			period,
			status: 'draft',
			totalGross: 0,
			totalNet: 0,
			totalContributions: 0,
			totalTaxes: 0,
			totalAllocations: 0,
			employeeCount: MOCK_EMPLOYEES.length,
			createdAt: new Date().toISOString()
		};
		this.payrollRuns = [newRun, ...this.payrollRuns];
		this.currentRun = newRun;
		this.generatePayslips(period);
	}

	generatePayslips(period: string) {
		this.payslips = MOCK_EMPLOYEES.map(emp => {
			const baseSalary = emp.baseSalary;
			const cnss = baseSalary * 0.05; // 5% CNSS
			const inss = baseSalary * 0.03; // 3% INSS
			const tax = baseSalary * 0.02; // 2% tax

			// Check for advance deduction
			const activeAdvance = this.advances.find(
				a => a.employeeId === emp.id && a.status === 'approved' && a.remainingAmount > 0
			);
			const advanceDeduction = activeAdvance ? activeAdvance.monthlyDeduction : 0;

			const lines: Payslip['lines'] = [
				{ label: 'Salaire de base', amount: baseSalary, type: 'earning', formula: `${baseSalary} USD` },
				{ label: 'CNSS (5%)', amount: -cnss, type: 'deduction', formula: `${baseSalary} * 0.05` },
				{ label: 'INSS (3%)', amount: -inss, type: 'deduction', formula: `${baseSalary} * 0.03` },
				{ label: 'IRPP (2%)', amount: -tax, type: 'deduction', formula: `${baseSalary} * 0.02` }
			];

			if (advanceDeduction > 0) {
				lines.push({
					label: 'Remboursement avance',
					amount: -advanceDeduction,
					type: 'deduction',
					formula: `Mensualité avance`
				});
			}

			const grossPay = baseSalary;
			const netPay = baseSalary - cnss - inss - tax - advanceDeduction;

			return {
				id: `payslip-${emp.id}-${period}`,
				employeeId: emp.id,
				employeeName: emp.name,
				orgUnit: emp.orgUnit,
				period,
				baseSalary,
				lines,
				grossPay,
				netPay,
				status: 'draft' as const
			};
		});

		if (this.currentRun) {
			this.currentRun.totalGross = this.totalGrossPay;
			this.currentRun.totalNet = this.totalNetPay;
			this.currentRun.totalContributions = this.totalContributions;
		}
	}

	calculatePayroll() {
		if (!this.currentRun) return;
		this.currentRun.status = 'calculated';
		this.currentRun.calculatedAt = new Date().toISOString();
		this.payslips = this.payslips.map(p => ({ ...p, status: 'calculated' as const }));
	}

	reviewPayroll() {
		if (!this.currentRun) return;
		this.currentRun.status = 'reviewed';
	}

	approvePayroll() {
		if (!this.currentRun) return;
		this.currentRun.status = 'approved';
		this.currentRun.approvedAt = new Date().toISOString();
	}

	processPayment() {
		if (!this.currentRun) return;
		this.currentRun.status = 'paid';
		this.currentRun.paidAt = new Date().toISOString();
		this.payslips = this.payslips.map(p => ({ ...p, status: 'paid' as const, paidAt: new Date().toISOString() }));

		// Update advance remaining amounts
		this.advances = this.advances.map(a => {
			if (a.status === 'approved' && a.remainingAmount > 0) {
				const newRemaining = Math.max(0, a.remainingAmount - a.monthlyDeduction);
				return {
					...a,
					remainingAmount: newRemaining,
					status: newRemaining === 0 ? 'completed' as const : a.status,
					completedDate: newRemaining === 0 ? new Date().toISOString() : undefined
				};
			}
			return a;
		});
	}

	toggleFilter(category: keyof Omit<PayrollFilters, 'search' | 'period'>, value: string) {
		const current = this.filters[category] as string[];
		if (current.includes(value)) {
			this.filters[category] = current.filter(v => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
		this.currentPage = 1;
	}

	setSearch(value: string) {
		this.filters.search = value;
		this.currentPage = 1;
	}

	setPeriod(period: string) {
		this.currentPeriod = period;
		this.filters.period = period;
		this.currentPage = 1;
		// Regenerate payslips for the new period
		this.generatePayslips(period);
	}

	resetFilters() {
		this.filters = {
			search: '',
			status: [],
			orgUnit: [],
			period: this.currentPeriod
		};
		this.currentPage = 1;
	}

	setPage(page: number) {
		this.currentPage = Math.max(1, Math.min(page, this.totalPages));
	}

	setPerPage(size: number) {
		this.perPage = size;
		this.currentPage = 1;
	}

	nextPage() {
		if (this.currentPage < this.totalPages) {
			this.currentPage++;
		}
	}

	prevPage() {
		if (this.currentPage > 1) {
			this.currentPage--;
		}
	}

	// --- Advance Actions ---
	requestAdvance(employeeId: number, amount: number, reason: string) {
		const employee = MOCK_EMPLOYEES.find(e => e.id === employeeId);
		if (!employee) return;

		const riskLevel: Advance['riskLevel'] = amount > employee.baseSalary * 0.5 ? 'high' :
			amount > employee.baseSalary * 0.3 ? 'medium' : 'low';

		const newAdvance: Advance = {
			id: `adv-${Date.now()}`,
			employeeId,
			employeeName: employee.name,
			amount,
			remainingAmount: amount,
			monthlyDeduction: Math.ceil(amount / 5), // 5 months default
			requestDate: new Date().toISOString().split('T')[0],
			status: 'pending',
			reason,
			riskLevel
		};
		this.advances = [newAdvance, ...this.advances];
	}

	approveAdvance(id: string) {
		const index = this.advances.findIndex(a => a.id === id);
		if (index !== -1) {
			this.advances[index] = {
				...this.advances[index],
				status: 'approved',
				approvedDate: new Date().toISOString().split('T')[0]
			};
		}
	}

	rejectAdvance(id: string) {
		const index = this.advances.findIndex(a => a.id === id);
		if (index !== -1) {
			this.advances[index] = {
				...this.advances[index],
				status: 'rejected'
			};
		}
	}

	nextStep() {
		if (this.canGoNext) {
			this.currentStep = this.steps[this.currentStepIndex + 1];
		}
	}

	prevStep() {
		if (this.canGoPrev) {
			this.currentStep = this.steps[this.currentStepIndex - 1];
		}
	}

	goToStep(step: PayrollStep) {
		this.currentStep = step;
	}

	goToNextStep() {
		const currentIndex = this.steps.indexOf(this.currentStep);
		if (currentIndex < this.steps.length - 1) {
			this.currentStep = this.steps[currentIndex + 1];
		}
	}

	resetSteps() {
		this.currentStep = 'preparation';
	}

}


export const payrollStore = new PayrollStore();

