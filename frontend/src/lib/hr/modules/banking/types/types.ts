export type VerificationStatus = 'verified' | 'pending' | 'rejected' | 'blocked';
export type AccountType = 'savings' | 'checking' | 'mobile_money' | 'salary';
export type Currency = 'USD' | 'CDF' | 'EUR';

export interface BankInstitution {
	id: string;
	name: string;
	shortName: string;
	country: string;
	logoUrl?: string;
	type: 'bank' | 'mobile_money';
	swiftCode?: string;
	isActive: boolean;
}

/** Raw response from GET /api/banking/banks (backend snake_case) */
export interface BankInstitutionBackendResponse {
	id: string;
	name: string;
	code: string;
	swift_code?: string;
	is_mobile_money: boolean;
	country_code: string;
	is_active: boolean;
	logo?: string | null;
	created_at: string;
	updated_at: string;
}

/** Backend BankOut nested inside BankAccountOut */
export interface BankOutBackendResponse {
	id: string;
	name: string;
	code: string;
	swift_code?: string;
	is_mobile_money: boolean;
	country_code: string;
	is_active: boolean;
	logo?: string | null;
	created_at: string;
	updated_at: string;
}

/** Raw response from GET /api/banking/accounts (backend snake_case) */
export interface BankAccountBackendResponse {
	id: string;
	account_number: string;
	account_name: string;
	account_type: string;
	currencies: string[];
	default_currency: string;
	branch_code?: string | null;
	iban?: string | null;
	is_primary: boolean;
	status: string;
	verified_at?: string | null;
	notes?: string | null;
	created_at: string;
	updated_at: string;
	bank: BankOutBackendResponse;
	employee: {
		id: string;
		[name: string]: any;
	};
	employee_id: {
		id: string;
		[name: string]: any;
	};
}

export interface BankAccount {
	id: string;
	employeeId: string;
	employeeName: string;
	employeePhoto?: string;
	institutionId: string;
	accountName: string;
	accountNumber: string;
	branchCode?: string;
	iban?: string;
	swift?: string;
	currencies: Currency[];
	defaultCurrency: Currency;
	type: AccountType;
	isPrimary: boolean;
	status: VerificationStatus;
	verifiedAt?: string;
	notes?: string;
	createdAt: string;
}

export interface BankingFilters {
	search: string;
	status: VerificationStatus[];
	currency: Currency[];
	institutionId: string[];
}

/** Filters for server-side bank account queries */
export type BankAccountFilters = {
  currency?: string[];
  status?: VerificationStatus[];
  institutionId?: string[];
};

