import { DEFAULT_LEAVE_CONFIG } from '../types/leaveSettings.types';
import type { 
	LeaveConfig, 
	SpecialLeave, 
	SpecialLeaveType, 
	LeaveBalance 
} from '../types/leaveSettings.types';
import { leaveSettingsService } from '../services/leaveSettings.service';
import { notification } from '@/hr/stores/notification.svelte';
import { DEFAULT_COUNTRY_CODE } from '@/hr/constants';
import type { 
	LeavePolicy, 
	CircumstanceLeaveRule 
} from '../schemas/leaveSettings.schemas';
import { LeaveConfigValidationSchema } from '../schemas/leaveSettings.schemas';


const BACKEND_TO_FRONTEND_TYPE: Record<string, SpecialLeaveType> = {
	'MARRIAGE_EMPLOYEE': 'MARRIAGE',
	'BIRTH_SPOUSE': 'BIRTH',
	'DEATH_FIRST_DEGREE': 'DEATH_SPOUSE_CHILD',
	'DEATH_SECOND_DEGREE': 'DEATH_ANCESTOR',
	'CHILD_MARRIAGE': 'CHILD_MARRIAGE',
	'MOVING': 'MOVING',
	'CHILD_HOSPITALIZATION': 'CHILD_HOSPITALIZATION',
	'OTHER': 'OTHER'
};


const FRONTEND_TO_BACKEND_TYPE: Record<string, CircumstanceLeaveRule['type']> = {
	'MARRIAGE': 'MARRIAGE_EMPLOYEE',
	'BIRTH': 'BIRTH_SPOUSE',
	'DEATH_SPOUSE_CHILD': 'DEATH_FIRST_DEGREE',
	'DEATH_ANCESTOR': 'DEATH_SECOND_DEGREE',
	'CHILD_MARRIAGE': 'CHILD_MARRIAGE',
	'MOVING': 'MOVING',
	'CHILD_HOSPITALIZATION': 'CHILD_HOSPITALIZATION',
	'OTHER': 'OTHER'
};


const LEAVE_PRESENTATION: Record<SpecialLeaveType, { label: string; icon: string }> = {
	'MARRIAGE': { label: 'Mariage', icon: 'heart' },
	'BIRTH': { label: 'Naissance', icon: 'baby' },
	'DEATH_SPOUSE_CHILD': { label: 'Décès conjoint/enfant', icon: 'flower-2' },
	'DEATH_ANCESTOR': { label: 'Décès ascendant', icon: 'flower-2' },
	'CHILD_MARRIAGE': { label: 'Mariage enfant', icon: 'heart' },
	'MOVING': { label: 'Déménagement', icon: 'moving' },
	'CHILD_HOSPITALIZATION': { label: 'Hospitalisation enfant', icon: 'stethoscope' },
	'OTHER': { label: 'Autre circonstance', icon: 'file-plus' }
};


export class LeaveSettingsStore {
	// PUBLIC STATE
	config = $state<LeaveConfig>({ ...DEFAULT_LEAVE_CONFIG });
	isLoading = $state(false);
	isSaving = $state(false);
	hasChanges = $state(false);
	error = $state<string | null>(null);
	validationErrors = $state<Record<string, string>>({});
	
	// Backend refs
	currentPolicy = $state<LeavePolicy | null>(null);
	policyId = $state<string | null>(null);
	
	// Editing state
	editingLeaveType = $state<SpecialLeaveType | null>(null);
	editForm = $state<Partial<SpecialLeave>>({});
	
	// Rule mappings
	ruleIdMap = $state<Map<string, string>>(new Map());
	
	// DERIVED STATE
	annualLeaveDays = $derived(this.config.annualLeaveDays);
	specialLeaves = $derived(this.config.specialLeaves);
	seniorityBonus = $derived(this.config.seniorityBonus);
	totalSpecialLeaveDays = $derived(
		this.config.specialLeaves.reduce((sum, sl) => sum + sl.daysAllowed, 0)
	);
	
	maxAnnualDays = $derived(() => {
		if (!this.config.seniorityBonus.enabled) return this.config.annualLeaveDays;
		const maxYears = this.config.seniorityBonus.maxBonus
			? this.config.seniorityBonus.maxBonus * this.config.seniorityBonus.yearsPerBonus
			: 30;
		const maxBonus = Math.floor(maxYears / this.config.seniorityBonus.yearsPerBonus) *
			this.config.seniorityBonus.bonusDays;
		return this.config.annualLeaveDays + maxBonus;
	});

	// PRIVATE STATE (Sync tracking)
	#seniorityRuleId: string | null = null;
	#originalSeniorityYears: number | null = null;
	#originalSeniorityBonusDays: number | null = null;
	#seniorityRules: Array<{ id?: string; years_of_service: number; bonus_days: number }> = [];

	// Getter/Setter for seniorityRuleId (used by mutations)
	get seniorityRuleId(): string | null {
		return this.#seniorityRuleId;
	}
	
	set seniorityRuleId(value: string | null) {
		this.#seniorityRuleId = value;
	}
	
	#originalAnnualDays: number | null = null;
	#originalAllowsCarryOver: boolean | null = null;
	#originalMaxCarryOverDays: number | null = null;
	#originalCarryOverExpirationMonth: number | null = null;
	#originalMaxConsecutiveDays: number | null = null;
	#originalNoticePeriodDays: number | null = null;
	#originalLeaveDays = $state<Map<string, number>>(new Map());
	#originalIsPaid = $state<Map<string, boolean>>(new Map());
	#originalDescription = $state<Map<string, string>>(new Map());

	setAnnualLeaveDays(days: number, rawValue?: string) {
		// Si NaN ou valeur invalide, stocker l'erreur
		if (Number.isNaN(days) || rawValue === '' || !Number.isInteger(days)) {
			this.validationErrors['annualLeaveDays'] = 'Veuillez entrer un nombre entier';
			return;
		}
		if (days < 12 || days > 40) {
			this.validationErrors['annualLeaveDays'] = 'Doit être entre 12 et 40 jours';
			return;
		}
		delete this.validationErrors['annualLeaveDays'];
		this.config.annualLeaveDays = days;
		this.hasChanges = true;
	}

	updateSeniorityBonus(updates: Partial<typeof this.config.seniorityBonus>, fieldName?: string, rawValue?: string) {
		// Validation pour chaque champ
		if ('yearsPerBonus' in updates) {
			const val = updates.yearsPerBonus;
			if (val === undefined || Number.isNaN(val) || rawValue === '' || !Number.isInteger(val)) {
				this.validationErrors['seniorityBonus.yearsPerBonus'] = 'Entier requis';
				return;
			}
			if (val < 1 || val > 10) {
				this.validationErrors['seniorityBonus.yearsPerBonus'] = '1-10 ans';
				return;
			}
			delete this.validationErrors['seniorityBonus.yearsPerBonus'];
		}
		
		if ('bonusDays' in updates) {
			const val = updates.bonusDays;
			if (val === undefined || Number.isNaN(val) || rawValue === '' || !Number.isInteger(val)) {
				this.validationErrors['seniorityBonus.bonusDays'] = 'Entier requis';
				return;
			}
			if (val < 1 || val > 10) {
				this.validationErrors['seniorityBonus.bonusDays'] = '1-10 jours';
				return;
			}
			delete this.validationErrors['seniorityBonus.bonusDays'];
		}
		
		this.config.seniorityBonus = { ...this.config.seniorityBonus, ...updates };
		this.hasChanges = true;
	}

	toggleSeniorityBonus() {
		this.config.seniorityBonus.enabled = !this.config.seniorityBonus.enabled;
		this.hasChanges = true;
	}

	setAllowHalfDays(allow: boolean) { this.config.allowHalfDays = allow; this.hasChanges = true; }
	setRequireApproval(require: boolean) { this.config.requireApproval = require; this.hasChanges = true; }
	setMaxConsecutiveDays(days: number) { this.config.maxConsecutiveDays = days; this.hasChanges = true; }
	setNoticePeriodDays(days: number) { this.config.noticePeriodDays = days; this.hasChanges = true; }

	// Carry over settings
	setAllowsCarryOver(allows: boolean) { this.config.allowsCarryOver = allows; this.hasChanges = true; }
	
	setMaxCarryOverDays(days: number, rawValue?: string) {
		if (Number.isNaN(days) || rawValue === '' || !Number.isInteger(days)) {
			this.validationErrors['maxCarryOverDays'] = 'Entier requis';
			return;
		}
		if (days < 0 || days > 30) {
			this.validationErrors['maxCarryOverDays'] = '0-30 jours';
			return;
		}
		delete this.validationErrors['maxCarryOverDays'];
		this.config.maxCarryOverDays = days;
		this.hasChanges = true;
	}
	
	setCarryOverExpirationMonth(month: number, rawValue?: string) {
		if (Number.isNaN(month) || rawValue === '' || !Number.isInteger(month)) {
			this.validationErrors['carryOverExpirationMonth'] = 'Entier requis';
			return;
		}
		if (month < 1 || month > 12) {
			this.validationErrors['carryOverExpirationMonth'] = '1-12 mois';
			return;
		}
		delete this.validationErrors['carryOverExpirationMonth'];
		this.config.carryOverExpirationMonth = month;
		this.hasChanges = true;
	}

	updateSpecialLeave(type: SpecialLeaveType, updates: Partial<SpecialLeave>) {
		const index = this.config.specialLeaves.findIndex(sl => sl.type === type);
		if (index !== -1) {
			this.config.specialLeaves[index] = { ...this.config.specialLeaves[index], ...updates };
			this.hasChanges = true;
		}
	}

	startEditingLeave(type: SpecialLeaveType) {
		const leave = this.config.specialLeaves.find(sl => sl.type === type);
		if (leave) {
			this.editingLeaveType = type;
			this.editForm = { ...leave };
		}
	}

	saveLeaveEdit() {
		if (this.editingLeaveType && this.editForm) {
			this.updateSpecialLeave(this.editingLeaveType, this.editForm);
			this.editingLeaveType = null;
			this.editForm = {};
		}
	}

	cancelLeaveEdit() {
		this.editingLeaveType = null;
		this.editForm = {};
	}

	resetToDefaults() {
		this.config = { ...DEFAULT_LEAVE_CONFIG };
		this.#resetTrackingState();
		this.hasChanges = true;
	}

	async loadSettings(): Promise<void> {
		this.isLoading = true;
		this.error = null;
		
		try {
			const policies = await leaveSettingsService.listPolicies();
			if (!policies?.length) return;
			
			const cdPolicy = policies.find(p => p.country_code === DEFAULT_COUNTRY_CODE) || policies[0];
			if (!cdPolicy) return;
			
			this.currentPolicy = cdPolicy;
			this.policyId = cdPolicy.id || null;
			this.config.annualLeaveDays = cdPolicy.standard_annual_days;
			this.#originalAnnualDays = cdPolicy.standard_annual_days;
			
			// Load carry over settings
			this.config.allowsCarryOver = cdPolicy.allows_carry_over ?? false;
			this.config.maxCarryOverDays = cdPolicy.max_carry_over_days ?? 10;
			this.config.carryOverExpirationMonth = cdPolicy.carry_over_expiration_month ?? 3;
			this.#originalAllowsCarryOver = this.config.allowsCarryOver;
			this.#originalMaxCarryOverDays = this.config.maxCarryOverDays;
			this.#originalCarryOverExpirationMonth = this.config.carryOverExpirationMonth;

			// Load request limits
			this.config.maxConsecutiveDays = cdPolicy.max_consecutive_days ?? 30;
			this.config.noticePeriodDays = cdPolicy.notice_period_days ?? 15;
			this.#originalMaxConsecutiveDays = this.config.maxConsecutiveDays;
			this.#originalNoticePeriodDays = this.config.noticePeriodDays;
			
			if (this.policyId) {
				await this.#loadCircumstanceRules();
				await this.#loadSeniorityRules();
			}
			
			this.hasChanges = false;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement';
		} finally {
			this.isLoading = false;
		}
	}

	/**
	 * Load settings from pre-fetched data (TanStack Query integration)
	 * This method is called by $effect() in the page component when TanStack Query data is available
	 */
	loadFromData(
		policy: LeavePolicy,
		circumstanceRules: CircumstanceLeaveRule[],
		seniorityRules: Array<{ id?: string; years_of_service: number; bonus_days: number }>
	): void {
		// Reset all tracking state first to prevent stale references
		this.#resetTrackingState();
		
		this.currentPolicy = policy;
		this.policyId = policy.id || null;
		this.config.annualLeaveDays = policy.standard_annual_days;
		this.#originalAnnualDays = policy.standard_annual_days;

		// Load carry over settings
		this.config.allowsCarryOver = policy.allows_carry_over ?? false;
		this.config.maxCarryOverDays = policy.max_carry_over_days ?? 10;
		this.config.carryOverExpirationMonth = policy.carry_over_expiration_month ?? 3;
		this.#originalAllowsCarryOver = this.config.allowsCarryOver;
		this.#originalMaxCarryOverDays = this.config.maxCarryOverDays;
		this.#originalCarryOverExpirationMonth = this.config.carryOverExpirationMonth;

		// Load request limits
		this.config.maxConsecutiveDays = policy.max_consecutive_days ?? 30;
		this.config.noticePeriodDays = policy.notice_period_days ?? 15;
		this.#originalMaxConsecutiveDays = this.config.maxConsecutiveDays;
		this.#originalNoticePeriodDays = this.config.noticePeriodDays;

		// Process circumstance rules
		this.#processCircumstanceRules(circumstanceRules);

		// Process seniority rules
		this.#processSeniorityRules(seniorityRules);

		this.hasChanges = false;
		this.validationErrors = {};
	}

	validateConfig(): boolean {
		const result = LeaveConfigValidationSchema.safeParse({
			annualLeaveDays: this.config.annualLeaveDays,
			allowsCarryOver: this.config.allowsCarryOver,
			maxCarryOverDays: this.config.maxCarryOverDays,
			carryOverExpirationMonth: this.config.carryOverExpirationMonth,
			seniorityBonus: this.config.seniorityBonus,
		});

		if (!result.success) {
			const errors: Record<string, string> = {};
			for (const issue of result.error.issues) {
				const path = issue.path.join('.');
				errors[path] = issue.message;
			}
			this.validationErrors = errors;
			return false;
		}

		this.validationErrors = {};
		return true;
	}

	/**
	 * Get all pending changes that need to be saved
	 * Returns null if no changes or validation fails
	 */
	getPendingChanges(): {
		policyId: string;
		policyUpdates: Parameters<typeof leaveSettingsService.updatePolicy>[1] | null;
		circumstanceRules: Array<{
			ruleId: string;
			data: Parameters<typeof leaveSettingsService.updateCircumstanceRule>[1];
		}>;
		seniorityRule: 
			| { type: 'update'; ruleId: string; data: Parameters<typeof leaveSettingsService.updateSeniorityRule>[1] }
			| { type: 'create'; policyId: string; data: Parameters<typeof leaveSettingsService.createSeniorityRule>[1] }
			| { type: 'delete'; ruleId: string }
			| null;
	} | null {
		// Validation Zod avant envoi
		if (!this.validateConfig()) {
			return null;
		}

		if (!this.policyId) return null;

		const policyUpdates = this.#getPolicyUpdates();
		const circumstanceRules = this.#getCircumstanceRuleChanges();
		const seniorityRule = this.#getSeniorityRuleChange();

		// Return null if no changes at all
		if (!policyUpdates && circumstanceRules.length === 0 && !seniorityRule) {
			return null;
		}

		return {
			policyId: this.policyId,
			policyUpdates,
			circumstanceRules,
			seniorityRule
		};
	}

	/**
	 * Commit changes to tracking state after successful save
	 */
	commitChanges(): void {
		// Commit policy changes
		if (this.#originalAnnualDays !== null) {
			this.#originalAnnualDays = this.config.annualLeaveDays;
		}
		if (this.#originalAllowsCarryOver !== null) {
			this.#originalAllowsCarryOver = this.config.allowsCarryOver;
		}
		if (this.#originalMaxCarryOverDays !== null) {
			this.#originalMaxCarryOverDays = this.config.maxCarryOverDays;
		}
		if (this.#originalCarryOverExpirationMonth !== null) {
			this.#originalCarryOverExpirationMonth = this.config.carryOverExpirationMonth;
		}
		if (this.#originalMaxConsecutiveDays !== null) {
			this.#originalMaxConsecutiveDays = this.config.maxConsecutiveDays;
		}
		if (this.#originalNoticePeriodDays !== null) {
			this.#originalNoticePeriodDays = this.config.noticePeriodDays;
		}

		// Commit circumstance rules changes
		for (const leave of this.config.specialLeaves) {
			this.#updateLeaveTracking(leave);
		}

		// Commit seniority rule changes (handled in #getSeniorityRuleChange)
		const { enabled, yearsPerBonus, bonusDays } = this.config.seniorityBonus;
		if (enabled && this.#seniorityRuleId) {
			this.#originalSeniorityYears = yearsPerBonus;
			this.#originalSeniorityBonusDays = bonusDays;
		}

		this.hasChanges = false;
	}

	/**
	 * Legacy save method - now delegates to prepare + external mutation
	 * Kept for backwards compatibility
	 */
	async saveSettings(): Promise<boolean> {
		const changes = this.getPendingChanges();
		if (!changes) {
			notification.toast.error('Veuillez corriger les erreurs de validation');
			return false;
		}

		this.isSaving = true;
		this.error = null;
		
		try {
			// Call service directly (legacy behavior)
			if (changes.policyUpdates) {
				await leaveSettingsService.updatePolicy(changes.policyId, changes.policyUpdates, true);
			}
			for (const rule of changes.circumstanceRules) {
				await leaveSettingsService.updateCircumstanceRule(rule.ruleId, rule.data, true);
			}
			if (changes.seniorityRule) {
				if (changes.seniorityRule.type === 'update') {
					await leaveSettingsService.updateSeniorityRule(changes.seniorityRule.ruleId, changes.seniorityRule.data, true);
				} else if (changes.seniorityRule.type === 'create') {
					const newRule = await leaveSettingsService.createSeniorityRule(changes.seniorityRule.policyId, changes.seniorityRule.data);
					this.#seniorityRuleId = newRule.id || null;
				} else if (changes.seniorityRule.type === 'delete') {
					await leaveSettingsService.deleteSeniorityRule(changes.seniorityRule.ruleId);
					this.#seniorityRuleId = null;
				}
			}
			
			this.commitChanges();
			notification.toast.success('Configuration enregistrée');
			return true;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors de la sauvegarde';
			return false;
		} finally {
			this.isSaving = false;
		}
	}

	// PRIVATE METHODS - Backend Sync
	async #loadCircumstanceRules(): Promise<void> {
		if (!this.policyId) return;
		
		const rules = await leaveSettingsService.listCircumstanceRules(this.policyId);
		const newRuleIdMap = new Map<string, string>();
		const newSpecialLeaves: SpecialLeave[] = [];
		
		for (const rule of rules) {
			if (rule.id) newRuleIdMap.set(rule.type, rule.id);
			
			const frontendType = BACKEND_TO_FRONTEND_TYPE[rule.type];
			if (!frontendType) continue;
			
			const { label, icon } = LEAVE_PRESENTATION[frontendType];
			newSpecialLeaves.push({
				type: frontendType,
				label,
				daysAllowed: rule.duration_days,
				description: rule.description || '',
				icon,
				isPaid: rule.is_paid
			});
		}
		
		this.config.specialLeaves = newSpecialLeaves;
		this.ruleIdMap = newRuleIdMap;
		
		// Track original values
		for (const leave of this.config.specialLeaves) {
			this.#originalLeaveDays.set(leave.type, leave.daysAllowed);
			this.#originalIsPaid.set(leave.type, leave.isPaid ?? true);
		}
	}

	async #loadSeniorityRules(): Promise<void> {
		if (!this.policyId) return;
		
		const seniorityRules = await leaveSettingsService.listSeniorityRules(this.policyId);
		
		if (seniorityRules?.length > 0) {
			const firstRule = seniorityRules[0];
			this.#seniorityRuleId = firstRule.id || null;
			this.config.seniorityBonus.enabled = true;
			this.config.seniorityBonus.yearsPerBonus = firstRule.years_of_service;
			this.config.seniorityBonus.bonusDays = firstRule.bonus_days;
			this.#originalSeniorityYears = firstRule.years_of_service;
			this.#originalSeniorityBonusDays = firstRule.bonus_days;
		} else {
			this.#seniorityRuleId = null;
			this.config.seniorityBonus.enabled = false;
			this.#originalSeniorityYears = null;
			this.#originalSeniorityBonusDays = null;
		}
	}

	// PRIVATE METHODS - Change Detection
	#getPolicyUpdates(): Parameters<typeof leaveSettingsService.updatePolicy>[1] | null {
		if (!this.policyId || this.#originalAnnualDays === null) return null;
		
		const updates: Parameters<typeof leaveSettingsService.updatePolicy>[1] = {};
		let hasUpdates = false;
		
		if (this.config.annualLeaveDays !== this.#originalAnnualDays) {
			updates.standard_annual_days = this.config.annualLeaveDays;
			hasUpdates = true;
		}
		if (this.config.allowsCarryOver !== this.#originalAllowsCarryOver) {
			updates.allows_carry_over = this.config.allowsCarryOver;
			hasUpdates = true;
		}
		if (this.config.maxCarryOverDays !== this.#originalMaxCarryOverDays) {
			updates.max_carry_over_days = this.config.maxCarryOverDays;
			hasUpdates = true;
		}
		if (this.config.carryOverExpirationMonth !== this.#originalCarryOverExpirationMonth) {
			updates.carry_over_expiration_month = this.config.carryOverExpirationMonth;
			hasUpdates = true;
		}
		if (this.config.maxConsecutiveDays !== this.#originalMaxConsecutiveDays) {
			updates.max_consecutive_days = this.config.maxConsecutiveDays;
			hasUpdates = true;
		}
		if (this.config.noticePeriodDays !== this.#originalNoticePeriodDays) {
			updates.notice_period_days = this.config.noticePeriodDays;
			hasUpdates = true;
		}
		
		return hasUpdates ? updates : null;
	}

	#getCircumstanceRuleChanges(): Array<{
		ruleId: string;
		data: Parameters<typeof leaveSettingsService.updateCircumstanceRule>[1];
	}> {
		const changes: Array<{
			ruleId: string;
			data: Parameters<typeof leaveSettingsService.updateCircumstanceRule>[1];
		}> = [];

		for (const leave of this.config.specialLeaves) {
			const backendType = FRONTEND_TO_BACKEND_TYPE[leave.type];
			const ruleId = this.ruleIdMap.get(backendType);
			if (!ruleId) continue;
			
			const hasChanges = this.#hasLeaveChanges(leave);
			if (!hasChanges) continue;
			
			changes.push({
				ruleId,
				data: {
					type: backendType,
					duration_days: leave.daysAllowed,
					is_paid: leave.isPaid ?? true,
					description: leave.description || ''
				}
			});
		}

		return changes;
	}

	#hasLeaveChanges(leave: SpecialLeave): boolean {
		const originalDays = this.#originalLeaveDays.get(leave.type);
		const originalIsPaid = this.#originalIsPaid.get(leave.type);
		const originalDesc = this.#originalDescription.get(leave.type);
		
		return (
			(originalDays !== undefined && leave.daysAllowed !== originalDays) ||
			(originalIsPaid !== undefined && (leave.isPaid ?? true) !== originalIsPaid) ||
			(originalDesc !== undefined && (leave.description || '') !== originalDesc)
		);
	}

	#updateLeaveTracking(leave: SpecialLeave): void {
		this.#originalLeaveDays.set(leave.type, leave.daysAllowed);
		this.#originalIsPaid.set(leave.type, leave.isPaid ?? true);
		this.#originalDescription.set(leave.type, leave.description || '');
	}

	#getSeniorityRuleChange():
		| { type: 'update'; ruleId: string; data: Parameters<typeof leaveSettingsService.updateSeniorityRule>[1] }
		| { type: 'create'; policyId: string; data: Parameters<typeof leaveSettingsService.createSeniorityRule>[1] }
		| { type: 'delete'; ruleId: string }
		| null {
		if (!this.policyId) return null;
		
		const { enabled, yearsPerBonus, bonusDays } = this.config.seniorityBonus;
		
		if (enabled) {
			const yearsChanged = this.#originalSeniorityYears !== yearsPerBonus;
			const bonusChanged = this.#originalSeniorityBonusDays !== bonusDays;
			
			if (this.#seniorityRuleId && (yearsChanged || bonusChanged)) {
				// Check for conflicts with other rules
				if (yearsChanged && this.#hasSeniorityConflict(yearsPerBonus, this.#seniorityRuleId)) {
					console.warn(`Seniority rule conflict: years_of_service=${yearsPerBonus} already exists`);
					// Don't return a change that would cause a conflict
					// Reset the config value to prevent further attempts
					this.config.seniorityBonus.yearsPerBonus = this.#originalSeniorityYears ?? yearsPerBonus;
					return null;
				}
				
				// Check if the rule ID still exists in the current data
				const ruleExists = this.#seniorityRules.some(r => r.id === this.#seniorityRuleId);
				if (!ruleExists) {
					console.warn(`Seniority rule ${this.#seniorityRuleId} no longer exists, creating new rule instead`);
					// Fall through to create a new rule
				} else {
					// Update existing
					return {
						type: 'update',
						ruleId: this.#seniorityRuleId,
						data: {
							years_of_service: yearsPerBonus,
							bonus_days: bonusDays
						}
					};
				}
			} else if (!this.#seniorityRuleId) {
				// Create with defaults
				const defaults = { years: 5, days: 1 };
				// Note: We modify config here which is a side effect, 
				// but this maintains backward compatibility with original logic
				this.config.seniorityBonus.yearsPerBonus = defaults.years;
				this.config.seniorityBonus.bonusDays = defaults.days;
				
				return {
					type: 'create',
					policyId: this.policyId,
					data: {
						years_of_service: defaults.years,
						bonus_days: defaults.days
					}
				};
			}
		} else if (this.#seniorityRuleId) {
			// Delete disabled rule
			return {
				type: 'delete',
				ruleId: this.#seniorityRuleId
			};
		}
		
		return null;
	}

	// PRIVATE METHODS - Data Processing
	#processCircumstanceRules(rules: CircumstanceLeaveRule[]): void {
		const newRuleIdMap = new Map<string, string>();
		const newSpecialLeaves: SpecialLeave[] = [];
		
		for (const rule of rules) {
			if (rule.id) newRuleIdMap.set(rule.type, rule.id);
			
			const frontendType = BACKEND_TO_FRONTEND_TYPE[rule.type];
			if (!frontendType) continue;
			
			const { label, icon } = LEAVE_PRESENTATION[frontendType];
			newSpecialLeaves.push({
				type: frontendType,
				label,
				daysAllowed: rule.duration_days,
				description: rule.description || '',
				icon,
				isPaid: rule.is_paid
			});
		}
		
		this.config.specialLeaves = newSpecialLeaves;
		this.ruleIdMap = newRuleIdMap;
		
		for (const leave of this.config.specialLeaves) {
			this.#originalLeaveDays.set(leave.type, leave.daysAllowed);
			this.#originalIsPaid.set(leave.type, leave.isPaid ?? true);
		}
	}
	
	#processSeniorityRules(rules: Array<{ id?: string; years_of_service: number; bonus_days: number }>): void {
		// Store all rules for conflict detection
		this.#seniorityRules = rules || [];
		
		if (rules?.length > 0) {
			const firstRule = rules[0];
			this.#seniorityRuleId = firstRule.id || null;
			this.config.seniorityBonus.enabled = true;
			this.config.seniorityBonus.yearsPerBonus = firstRule.years_of_service;
			this.config.seniorityBonus.bonusDays = firstRule.bonus_days;
			this.#originalSeniorityYears = firstRule.years_of_service;
			this.#originalSeniorityBonusDays = firstRule.bonus_days;
		} else {
			this.#seniorityRuleId = null;
			this.config.seniorityBonus.enabled = false;
			this.#originalSeniorityYears = null;
			this.#originalSeniorityBonusDays = null;
		}
	}

	/**
	 * Check if a years_of_service value would conflict with another existing rule
	 */
	#hasSeniorityConflict(yearsOfService: number, excludeRuleId?: string): boolean {
		return this.#seniorityRules.some(rule => 
			rule.years_of_service === yearsOfService && 
			rule.id !== excludeRuleId
		);
	}

	/**
	 * Get all seniority rule IDs except the one we're currently managing
	 * Used to delete extra rules before creating/updating
	 */
	getExtraSeniorityRuleIds(currentRuleId?: string | null): string[] {
		return this.#seniorityRules
			.filter(rule => rule.id && rule.id !== currentRuleId)
			.map(rule => rule.id!);
	}

	#resetTrackingState(): void {
		this.#originalAnnualDays = null;
		this.#originalAllowsCarryOver = null;
		this.#originalMaxCarryOverDays = null;
		this.#originalCarryOverExpirationMonth = null;
		this.#originalMaxConsecutiveDays = null;
		this.#originalNoticePeriodDays = null;
		this.#originalLeaveDays.clear();
		this.#originalIsPaid.clear();
		this.#originalDescription.clear();
		this.#seniorityRuleId = null;
		this.#originalSeniorityYears = null;
		this.#originalSeniorityBonusDays = null;
		this.#seniorityRules = [];
	}

	// PUBLIC UTILITY
	calculateLeaveBalance(
		employeeId: string,
		year: number,
		yearsOfService: number,
		usedDays: number,
		specialLeavesUsed: Record<SpecialLeaveType, number>
	): LeaveBalance {
		let totalDays = this.config.annualLeaveDays;
		let seniorityBonusDays = 0;

		if (this.config.seniorityBonus.enabled) {
			const bonusCount = Math.floor(yearsOfService / this.config.seniorityBonus.yearsPerBonus);
			seniorityBonusDays = bonusCount * this.config.seniorityBonus.bonusDays;
			if (this.config.seniorityBonus.maxBonus) {
				seniorityBonusDays = Math.min(seniorityBonusDays, this.config.seniorityBonus.maxBonus);
			}
			totalDays += seniorityBonusDays;
		}

		return {
			employeeId,
			year,
			totalDays,
			usedDays,
			remainingDays: totalDays - usedDays,
			seniorityBonusDays,
			specialLeavesUsed
		};
	}
}


export const leaveSettingsStore = new LeaveSettingsStore();

/**
 * UI-specific state for leave settings
 * Lives in memory only (resets on page reload)
 */
export const leaveUiStore = $state({
	bannerSeen: false
});
