import type {
	PayrollConfiguration, PayrollConfigurationUpdate, SMIGConfiguration,
	TaxBracketConfig, PayrollAdjustmentConfig, OvertimeRule,
	LegalAllowanceConfig, SocialContributionRate
} from '../../types/types';
import type { ExchangeRateResponse } from '@/hr/payroll/queries/payroll';
import { payrollConfigApiStore } from './payrollConfig.client.svelte';
import { notification } from '@/stores/notification.svelte';


export class PayrollConfigStore {
	exchangeRateInfo = $state<ExchangeRateResponse | null>(null);

	/** Taux USD → CDF : provient de /configuration/exchange-rate/ (BCC en priorité) */
	exchangeRate = $derived.by(() => {
		const rate = Number(this.exchangeRateInfo?.rate);
		return Number.isFinite(rate) && rate > 0 ? rate : 0;
	});

	configuration = $state<PayrollConfiguration | null>(null);
	smigRates = $state<SMIGConfiguration[]>([]);
	taxBrackets = $state<TaxBracketConfig[]>([]);
	adjustments = $state<PayrollAdjustmentConfig[]>([]);
	overtimeRules = $state<OvertimeRule[]>([]);
	legalAllowances = $state<LegalAllowanceConfig[]>([]);
	socialContributions = $state<SocialContributionRate[]>([]);
	isSavingConfiguration = $state(false);

	activeSMIG = $derived(
		this.smigRates.find((s) => s.is_active) ?? this.smigRates[0] ?? null
	);

	/** Charge la configuration globale + SMIG + barème fiscal + catalogue + taux de change. */
	async syncConfiguration() {
		const [cfg, smig, brackets, adj, overtime, allowances, exchangeRate, contributions] = await Promise.allSettled([
			payrollConfigApiStore.fetchConfiguration(),
			payrollConfigApiStore.fetchSMIG(),
			payrollConfigApiStore.fetchTaxBrackets(),
			payrollConfigApiStore.fetchAdjustmentTypes(),
			payrollConfigApiStore.fetchOvertimeRules(),
			payrollConfigApiStore.fetchLegalAllowances(),
			payrollConfigApiStore.fetchExchangeRate(),
			payrollConfigApiStore.fetchSocialContributions(),
		]);

		if (cfg.status === 'fulfilled' && cfg.value) this.configuration = cfg.value;
		if (smig.status === 'fulfilled' && smig.value) this.smigRates = smig.value;
		if (brackets.status === 'fulfilled' && brackets.value) this.taxBrackets = brackets.value;
		if (adj.status === 'fulfilled' && adj.value) this.adjustments = adj.value;
		if (overtime.status === 'fulfilled' && overtime.value) this.overtimeRules = overtime.value;
		if (allowances.status === 'fulfilled' && allowances.value) this.legalAllowances = allowances.value;
		if (exchangeRate.status === 'fulfilled' && exchangeRate.value) this.exchangeRateInfo = exchangeRate.value;
		if (contributions.status === 'fulfilled' && contributions.value) this.socialContributions = contributions.value;

		const allFailed = [cfg, smig, brackets, adj, overtime, allowances, exchangeRate, contributions].every(r => r.status === 'rejected');
		if (allFailed) throw new Error('Configuration indisponible');
	}

	/** Sauvegarde la configuration globale */
	async saveConfiguration(data: PayrollConfigurationUpdate) {
		this.isSavingConfiguration = true;
		try {
			const updated = await payrollConfigApiStore.updateConfiguration(data);
			if (updated) {
				this.configuration = updated;
			}
			return updated;
		} finally {
			this.isSavingConfiguration = false;
		}
	}

	/** Recharge le taux de change USD → CDF (force une synchro BCC au bouton « Recharger ») */
	async refreshExchangeRate(forceSync = false) {
		try {
			const rate = await payrollConfigApiStore.fetchExchangeRate(forceSync);
			if (rate) {
				this.exchangeRateInfo = rate;
				notification.toast.success(
					`Taux de change actualisé : 1 USD = ${Number(rate.rate).toLocaleString('fr-FR')} CDF`
				);
			} else {
				notification.toast.warning("Aucun taux de change n'a pu être récupéré.");
			}
			return rate;
		} catch (e: any) {
			notification.toast.error(e?.message ?? "Échec de l'actualisation du taux de change.");
			return null;
		}
	}

	/** Met à jour une règle d'heures supplémentaires */
	async saveOvertimeRule(ruleId: string, data: Partial<OvertimeRule>) {
		const updated = await payrollConfigApiStore.updateOvertimeRule(ruleId, data);
		if (updated) {
			this.overtimeRules = this.overtimeRules.map(r => (r.id === updated.id ? updated : r));
		}
		return updated;
	}

	/** Met à jour une allocation légale */
	async saveLegalAllowance(allowanceId: string, data: Partial<LegalAllowanceConfig>) {
		const updated = await payrollConfigApiStore.updateLegalAllowance(allowanceId, data);
		if (updated) {
			this.legalAllowances = this.legalAllowances.map(a => (a.id === updated.id ? updated : a));
		}
		return updated;
	}

	async resetLegalAllowances() {
		await payrollConfigApiStore.resetLegalAllowances();
		await this.syncConfiguration();
	}

	async resetAdjustments() {
		await payrollConfigApiStore.resetAdjustments();
		await this.syncConfiguration();
	}

	async toggleAdjustmentActive(adjustmentId: string, isActive: boolean) {
		const updated = await payrollConfigApiStore.toggleAdjustmentActive(adjustmentId, isActive);
		if (updated) {
			this.adjustments = this.adjustments.map(a => (a.id === updated.id ? updated : a));
		}
		return updated;
	}

	async createAdjustment(data: Partial<PayrollAdjustmentConfig>) {
		const created = await payrollConfigApiStore.createAdjustment(data);
		if (created) {
			this.adjustments = [...this.adjustments, created];
		}
		return created;
	}

	async updateAdjustment(adjustmentId: string, data: Partial<PayrollAdjustmentConfig>) {
		const updated = await payrollConfigApiStore.updateAdjustment(adjustmentId, data);
		if (updated) {
			this.adjustments = this.adjustments.map(a => (a.id === updated.id ? updated : a));
		}
		return updated;
	}

	async deleteAdjustment(adjustmentId: string) {
		await payrollConfigApiStore.deleteAdjustment(adjustmentId);
		this.adjustments = this.adjustments.filter(a => a.id !== adjustmentId);
	}
}


export const payrollConfigStore = new PayrollConfigStore();

