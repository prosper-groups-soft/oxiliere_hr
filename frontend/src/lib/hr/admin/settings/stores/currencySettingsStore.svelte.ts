import type {
	CurrencyConfig,
	ExchangeRate,
	ExchangeRateFilters,
	RegionalConfig,
	CurrencyCode
} from '../types/currency.types';
import { 
  CURRENCIES, 
  DEFAULT_REGIONAL_CONFIG 
} from '../types/currency.types';


// Mock exchange rates
const MOCK_EXCHANGE_RATES: ExchangeRate[] = [
	{
		id: 'rate-1',
		from: 'USD',
		to: 'CDF',
		rate: 2800,
		inverseRate: 1 / 2800,
		date: new Date('2024-03-25'),
		source: 'MANUAL',
		isActive: true,
		createdBy: 'admin',
		notes: 'Taux standard'
	},
	{
		id: 'rate-2',
		from: 'USD',
		to: 'CDF',
		rate: 2785,
		inverseRate: 1 / 2785,
		date: new Date('2024-03-24'),
		source: 'MANUAL',
		isActive: false,
		createdBy: 'admin'
	},
	{
		id: 'rate-3',
		from: 'USD',
		to: 'CDF',
		rate: 2820,
		inverseRate: 1 / 2820,
		date: new Date('2024-03-23'),
		source: 'MANUAL',
		isActive: false,
		createdBy: 'rh'
	}
];


export class CurrencySettingsStore {
	// --- Reactive State ---
	config = $state<RegionalConfig>({ ...DEFAULT_REGIONAL_CONFIG });
	exchangeRates = $state<ExchangeRate[]>(MOCK_EXCHANGE_RATES);
	isLoading = $state(false);
	isSaving = $state(false);
	error = $state<string | null>(null);
	hasChanges = $state(false);

	// Form state for new exchange rate
	newRate = $state({
		from: 'USD' as CurrencyCode,
		to: 'CDF' as CurrencyCode,
		rate: 2800,
		notes: ''
	});
	showAddRateForm = $state(false);

	// History filters
	historyFilters = $state<ExchangeRateFilters>({});
	historyPage = $state(1);
	historyPerPage = $state(10);

	// --- Derived State ---
	currentRate = $derived(
		this.exchangeRates.find(r => r.isActive) || null
	);

	primaryCurrency = $derived(this.config.currency.primaryCurrency);
	secondaryCurrency = $derived(this.config.currency.secondaryCurrency);
	displayBoth = $derived(this.config.currency.displayBoth);

	// Filtered history
	filteredHistory = $derived.by(() => {
		let result = [...this.exchangeRates];

		if (this.historyFilters.fromDate) {
			result = result.filter(r => r.date >= this.historyFilters.fromDate!);
		}
		if (this.historyFilters.toDate) {
			result = result.filter(r => r.date <= this.historyFilters.toDate!);
		}
		if (this.historyFilters.currencyPair) {
			result = result.filter(r =>
				`${r.from}-${r.to}` === this.historyFilters.currencyPair
			);
		}

		return result.sort((a, b) => b.date.getTime() - a.date.getTime());
	});

	paginatedHistory = $derived.by(() => {
		return this.filteredHistory.slice(
			(this.historyPage - 1) * this.historyPerPage,
			this.historyPage * this.historyPerPage
		);
	});

	historyTotalPages = $derived(
		Math.ceil(this.filteredHistory.length / this.historyPerPage) || 1
	);

	// Statistics
	rateStats = $derived(() => {
		if (this.exchangeRates.length === 0) return null;
		const rates = this.exchangeRates.map(r => r.rate);
		return {
			min: Math.min(...rates),
			max: Math.max(...rates),
			average: rates.reduce((a, b) => a + b, 0) / rates.length,
			latest: rates[0],
			variation: rates.length > 1 ? rates[0] - rates[1] : 0
		};
	});

	// --- Actions ---
	setPrimaryCurrency(currencyCode: CurrencyCode) {
		const currency = CURRENCIES.find(c => c.code === currencyCode);
		if (currency) {
			this.config.currency.primaryCurrency = currency;
			this.hasChanges = true;
		}
	}

	setSecondaryCurrency(currencyCode: CurrencyCode | null) {
		if (currencyCode === null) {
			this.config.currency.secondaryCurrency = undefined;
		} else {
			const currency = CURRENCIES.find(c => c.code === currencyCode);
			if (currency) {
				this.config.currency.secondaryCurrency = currency;
			}
		}
		this.hasChanges = true;
	}

	toggleDisplayBoth() {
		this.config.currency.displayBoth = !this.config.currency.displayBoth;
		this.hasChanges = true;
	}

	setAutoUpdate(enabled: boolean) {
		this.config.currency.autoUpdate = enabled;
		this.hasChanges = true;
	}

	updateCompanyInfo(updates: Partial<typeof this.config.companyInfo>) {
		this.config.companyInfo = { ...this.config.companyInfo, ...updates };
		this.hasChanges = true;
	}

	addExchangeRate(data: Omit<ExchangeRate, 'id' | 'date' | 'inverseRate' | 'isActive'>) {
		const newRate: ExchangeRate = {
			...data,
			id: `rate-${Date.now()}`,
			date: new Date(),
			inverseRate: 1 / data.rate,
			isActive: true
		};

		// Deactivate previous rates for this pair
		this.exchangeRates = this.exchangeRates.map(r =>
			r.from === data.from && r.to === data.to && r.isActive
				? { ...r, isActive: false }
				: r
		);

		this.exchangeRates = [newRate, ...this.exchangeRates];
		this.showAddRateForm = false;
		this.newRate = { from: 'USD', to: 'CDF', rate: 2800, notes: '' };
		this.hasChanges = true;
	}

	setActiveRate(id: string) {
		const rate = this.exchangeRates.find(r => r.id === id);
		if (rate) {
			// Deactivate others for same pair
			this.exchangeRates = this.exchangeRates.map(r =>
				r.from === rate.from && r.to === rate.to
					? { ...r, isActive: r.id === id }
					: r
			);
		}
	}

	deleteRate(id: string) {
		this.exchangeRates = this.exchangeRates.filter(r => r.id !== id);
	}

	// Conversion helpers
	convert(amount: number, from: CurrencyCode, to: CurrencyCode): number {
		if (from === to) return amount;

		const rate = this.currentRate;
		if (!rate) return amount;

		if (from === rate.from && to === rate.to) {
			return amount * rate.rate;
		}
		if (from === rate.to && to === rate.from) {
			return amount * rate.inverseRate;
		}

		return amount;
	}

	formatAmount(amount: number, currency: CurrencyCode): string {
		const currencyInfo = CURRENCIES.find(c => c.code === currency);
		if (!currencyInfo) return `${amount}`;

		const { decimalSeparator, thousandSeparator } = this.config.numberFormat;
		const parts = amount.toFixed(currencyInfo.decimals).split('.');
		const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousandSeparator);
		const decimalPart = parts[1];

		if (decimalPart) {
			return `${currencyInfo.symbol} ${integerPart}${decimalSeparator}${decimalPart}`;
		}
		return `${currencyInfo.symbol} ${integerPart}`;
	}

	// Form actions
	toggleAddRateForm() {
		this.showAddRateForm = !this.showAddRateForm;
	}

	setNewRateField<K extends keyof typeof this.newRate>(
		field: K,
		value: typeof this.newRate[K]
	) {
		this.newRate[field] = value;
	}

	// History pagination
	setHistoryPage(page: number) {
		if (page >= 1 && page <= this.historyTotalPages) {
			this.historyPage = page;
		}
	}

	setHistoryPerPage(size: number) {
		this.historyPerPage = size;
		this.historyPage = 1;
	}

	// Filter actions
	setHistoryDateRange(from?: Date, to?: Date) {
		this.historyFilters.fromDate = from;
		this.historyFilters.toDate = to;
		this.historyPage = 1;
	}

	resetHistoryFilters() {
		this.historyFilters = {};
		this.historyPage = 1;
	}

	// Persistence
	async saveSettings() {
		this.isSaving = true;
		this.error = null;
		try {
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
			await new Promise(resolve => setTimeout(resolve, 500));
			this.hasChanges = false;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement';
		} finally {
			this.isLoading = false;
		}
	}

	resetToDefaults() {
		this.config = { ...DEFAULT_REGIONAL_CONFIG };
		this.hasChanges = true;
	}
}


export const currencySettingsStore = new CurrencySettingsStore();

