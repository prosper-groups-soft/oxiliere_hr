import {
	DEFAULT_LEAVE_CONFIG
} from '../types/leave.types';

import type {
	LeaveConfig,
	SpecialLeave,
	SpecialLeaveType,
	LeaveBalance
} from '../types/leave.types';

export class LeaveSettingsStore {
	// --- Reactive State ---
	config = $state<LeaveConfig>({ ...DEFAULT_LEAVE_CONFIG });
	isLoading = $state(false);
	isSaving = $state(false);
	error = $state<string | null>(null);
	hasChanges = $state(false);

	// Editing state for special leaves
	editingLeaveType = $state<SpecialLeaveType | null>(null);
	editForm = $state<Partial<SpecialLeave>>({});

	// --- Derived State ---
	annualLeaveDays = $derived(this.config.annualLeaveDays);
	specialLeaves = $derived(this.config.specialLeaves);
	seniorityBonus = $derived(this.config.seniorityBonus);
	totalSpecialLeaveDays = $derived(
		this.config.specialLeaves.reduce((sum, sl) => sum + sl.daysAllowed, 0)
	);

	// Total days including seniority bonus (example: after 10 years)
	maxAnnualDays = $derived(() => {
		if (!this.config.seniorityBonus.enabled) return this.config.annualLeaveDays;
		const maxYears = this.config.seniorityBonus.maxBonus
			? this.config.seniorityBonus.maxBonus * this.config.seniorityBonus.yearsPerBonus
			: 30;
		const maxBonus = Math.floor(maxYears / this.config.seniorityBonus.yearsPerBonus) *
			this.config.seniorityBonus.bonusDays;
		return this.config.annualLeaveDays + maxBonus;
	});

	// --- Actions ---
	setAnnualLeaveDays(days: number) {
		if (days >= 12 && days <= 40) {
			this.config.annualLeaveDays = days;
			this.hasChanges = true;
		}
	}

	updateSpecialLeave(type: SpecialLeaveType, updates: Partial<SpecialLeave>) {
		const index = this.config.specialLeaves.findIndex(sl => sl.type === type);
		if (index !== -1) {
			this.config.specialLeaves[index] = {
				...this.config.specialLeaves[index],
				...updates
			};
			this.hasChanges = true;
		}
	}

	updateSeniorityBonus(updates: Partial<typeof this.config.seniorityBonus>) {
		this.config.seniorityBonus = {
			...this.config.seniorityBonus,
			...updates
		};
		this.hasChanges = true;
	}

	toggleSeniorityBonus() {
		this.config.seniorityBonus.enabled = !this.config.seniorityBonus.enabled;
		this.hasChanges = true;
	}

	setAllowHalfDays(allow: boolean) {
		this.config.allowHalfDays = allow;
		this.hasChanges = true;
	}

	setRequireApproval(require: boolean) {
		this.config.requireApproval = require;
		this.hasChanges = true;
	}

	setMaxConsecutiveDays(days: number) {
		this.config.maxConsecutiveDays = days;
		this.hasChanges = true;
	}

	setNoticePeriodDays(days: number) {
		this.config.noticePeriodDays = days;
		this.hasChanges = true;
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
		this.hasChanges = true;
	}

	async saveSettings() {
		this.isSaving = true;
		this.error = null;
		try {
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 800));
			this.hasChanges = false;
			return true;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors de la sauvegarde';
			return false;
		} finally {
			this.isSaving = false;
		}
	}

	async loadSettings() {
		this.isLoading = true;
		this.error = null;
		try {
			// Simulate API call
			await new Promise(resolve => setTimeout(resolve, 500));
			// Keep default config for now
			this.hasChanges = false;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement';
		} finally {
			this.isLoading = false;
		}
	}

	// Calculate leave balance for an employee
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

