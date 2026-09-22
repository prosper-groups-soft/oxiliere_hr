// Types Paramètres Régionaux - Multi-devises (RDC)

export type CurrencyCode = 'CDF' | 'USD';

export interface Currency {
	code: CurrencyCode;
	name: string;
	symbol: string;
	isoCode: string; // ISO 4217
	decimals: number;
	isPrimary: boolean;
	flag?: string;
}

export const CURRENCIES: Currency[] = [
	{
		code: 'CDF',
		name: 'Franc Congolais',
		symbol: 'FC',
		isoCode: 'CDF',
		decimals: 2,
		isPrimary: true,
		flag: '🇨🇩'
	},
	{
		code: 'USD',
		name: 'Dollar Américain',
		symbol: '$',
		isoCode: 'USD',
		decimals: 2,
		isPrimary: false,
		flag: '🇺🇸'
	}
];

export interface ExchangeRate {
	id: string;
	from: CurrencyCode;
	to: CurrencyCode;
	rate: number; // 1 USD = 2800 CDF
	inverseRate: number; // 1 CDF = 0.000357 USD
	date: Date;
	source: 'MANUAL' | 'API_BCC' | 'API_ECB'; // Banque Centrale du Congo, European Central Bank
	isActive: boolean;
	createdBy?: string;
	notes?: string;
}

export interface CurrencyConfig {
	primaryCurrency: Currency;
	secondaryCurrency?: Currency;
	displayBoth: boolean;
	currentRate: ExchangeRate | null;
	autoUpdate: boolean;
	apiSource?: string;
}

export interface RegionalConfig {
	currency: CurrencyConfig;
	dateFormat: string; // 'DD/MM/YYYY' pour RDC
	timeFormat: '12h' | '24h';
	locale: string; // 'fr-CD' pour RDC
	timezone: string; // 'Africa/Kinshasa'
	numberFormat: {
		decimalSeparator: string; // ',' pour RDC
		thousandSeparator: string; // '.' ou ' '
	};
	companyInfo: {
		name: string;
		address: string;
		city: string;
		country: string;
		phone: string;
		email: string;
		rccm: string; // Registre du Commerce
		idNat: string; // Identification Nationale
		taxNumber: string; // Numéro impôt
	};
}

// Configuration régionale par défaut (RDC)
export const DEFAULT_REGIONAL_CONFIG: RegionalConfig = {
	currency: {
		primaryCurrency: CURRENCIES[0], // CDF
		secondaryCurrency: CURRENCIES[1], // USD
		displayBoth: true,
		currentRate: null,
		autoUpdate: false
	},
	dateFormat: 'DD/MM/YYYY',
	timeFormat: '24h',
	locale: 'fr-CD',
	timezone: 'Africa/Kinshasa',
	numberFormat: {
		decimalSeparator: ',',
		thousandSeparator: '.'
	},
	companyInfo: {
		name: '',
		address: '',
		city: '',
		country: 'Rép. Dém. du Congo',
		phone: '',
		email: '',
		rccm: '',
		idNat: '',
		taxNumber: ''
	}
};

export interface ExchangeRateFilters {
	fromDate?: Date;
	toDate?: Date;
	currencyPair?: string;
}
