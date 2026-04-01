import type { 
  BankAccount, 
  BankInstitution, 
  BankingFilters 
} from '../types/types';


export class BankingStore {
	// --- Data ---
	institutions = $state<BankInstitution[]>([
		{ id: 'ecobank', name: 'Ecobank RDC', shortName: 'Ecobank', country: 'RDC', type: 'bank', swiftCode: 'ECOBCDKI' },
		{ id: 'rawbank', name: 'Rawbank SARL', shortName: 'Rawbank', country: 'RDC', type: 'bank', swiftCode: 'RAWBCOKI' },
		{ id: 'equity', name: 'Equity BCDC', shortName: 'Equity', country: 'RDC', type: 'bank', swiftCode: 'EQUIBCKI' },
		{ id: 'mpesa', name: 'Vodacom M-Pesa', shortName: 'M-Pesa', country: 'RDC', type: 'mobile_money' },
		{ id: 'orange', name: 'Orange Money', shortName: 'Orange', country: 'RDC', type: 'mobile_money' }
	]);

	accounts = $state<BankAccount[]>([
		{
			id: 'acc-1',
			employeeId: 1,
			employeeName: 'Jean-Paul Mabuso',
			institutionId: 'rawbank',
			accountName: 'Compte Courant',
			accountNumber: '1234567890123456',
			currency: 'USD',
			type: 'checking',
			isPrimary: true,
			status: 'verified',
			verifiedAt: '2024-03-01T10:00:00Z',
			createdAt: '2024-02-15T09:00:00Z'
		},
		{
			id: 'acc-2',
			employeeId: 2,
			employeeName: 'Merveille Kabamba',
			institutionId: 'ecobank',
			accountName: 'Épargne Personnel',
			accountNumber: '9876543210987654',
			currency: 'CDF',
			type: 'savings',
			isPrimary: true,
			status: 'pending',
			createdAt: '2024-03-10T14:30:00Z'
		},
		{
			id: 'acc-3',
			employeeId: 3,
			employeeName: 'Christian Luvambo',
			institutionId: 'mpesa',
			accountName: 'M-Pesa Pro',
			accountNumber: '+243810000000',
			currency: 'USD',
			type: 'mobile_money',
			isPrimary: true,
			status: 'verified',
			verifiedAt: '2024-01-20T11:00:00Z',
			createdAt: '2024-01-15T08:00:00Z'
		}
	]);

	// --- Filters ---
	filters = $state<BankingFilters>({
		search: '',
		status: [],
		currency: [],
		institutionId: []
	});

	institutionFilters = $state({
		search: '',
		type: [] as ('bank' | 'mobile_money')[]
	});

	// --- Derived ---
	filteredAccounts = $derived.by(() => {
		return this.accounts.filter(acc => {
			const matchesSearch = acc.employeeName.toLowerCase().includes(this.filters.search.toLowerCase()) || 
								  acc.accountNumber.includes(this.filters.search);
			const matchesStatus = this.filters.status.length === 0 || this.filters.status.includes(acc.status);
			const matchesCurrency = this.filters.currency.length === 0 || this.filters.currency.includes(acc.currency);
			const matchesBank = this.filters.institutionId.length === 0 || this.filters.institutionId.includes(acc.institutionId);
			
			return matchesSearch && matchesStatus && matchesCurrency && matchesBank;
		});
	});

	filteredInstitutions = $derived.by(() => {
		return this.institutions.filter(inst => {
			const matchesSearch = inst.name.toLowerCase().includes(this.institutionFilters.search.toLowerCase()) || 
								  inst.shortName.toLowerCase().includes(this.institutionFilters.search.toLowerCase());
			const matchesType = this.institutionFilters.type.length === 0 || this.institutionFilters.type.includes(inst.type);
			
			return matchesSearch && matchesType;
		});
	});

	activeFiltersCount = $derived(
		this.filters.status.length + this.filters.currency.length + this.filters.institutionId.length
	);

	activeInstitutionFiltersCount = $derived(this.institutionFilters.type.length);

	// --- Actions ---
	getInstitutionById(id: string) {
		return this.institutions.find(i => i.id === id);
	}

	toggleFilter(category: keyof BankingFilters, value: string) {
		const current = this.filters[category] as string[];
		if (current.includes(value)) {
			this.filters[category] = current.filter((v) => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
	}

	toggleInstitutionType(type: 'bank' | 'mobile_money') {
		if (this.institutionFilters.type.includes(type)) {
			this.institutionFilters.type = this.institutionFilters.type.filter(t => t !== type);
		} else {
			this.institutionFilters.type = [...this.institutionFilters.type, type];
		}
	}

	resetFilters() {
		this.filters = {
			search: '',
			status: [],
			currency: [],
			institutionId: []
		};
	}

	resetInstitutionFilters() {
		this.institutionFilters = {
			search: '',
			type: []
		};
	}

	addAccount(data: Omit<BankAccount, 'id' | 'createdAt' | 'status'>) {
		const newAccount: BankAccount = {
			...data,
			id: `acc-${Date.now()}`,
			createdAt: new Date().toISOString(),
			status: 'pending'
		};
		// Reassign to trigger reactivity
		this.accounts = [...this.accounts, newAccount];
	}

	updateAccount(id: string, data: Partial<Omit<BankAccount, 'id'>>) {
		const index = this.accounts.findIndex(a => a.id === id);
		if (index !== -1) {
			this.accounts[index] = { ...this.accounts[index], ...data };
			this.accounts = [...this.accounts];
		}
	}

	deleteAccount(id: string) {
		this.accounts = this.accounts.filter(a => a.id !== id);
	}

	verifyAccount(id: string) {
		const acc = this.accounts.find(a => a.id === id);
		if (acc) {
			acc.status = 'verified';
			acc.verifiedAt = new Date().toISOString();
		}
	}

	blockAccount(id: string) {
		const acc = this.accounts.find(a => a.id === id);
		if (acc) acc.status = 'blocked';
	}

	// --- Institution Actions ---
	addInstitution(data: Omit<BankInstitution, 'id'>) {
		const newInstitution: BankInstitution = {
			...data,
			id: data.name.toLowerCase().replace(/\s+/g, '-') + '-' + Date.now()
		};
		this.institutions = [...this.institutions, newInstitution];
	}

	updateInstitution(id: string, data: Partial<Omit<BankInstitution, 'id'>>) {
		const index = this.institutions.findIndex(i => i.id === id);
		if (index !== -1) {
			this.institutions[index] = { ...this.institutions[index], ...data };
			this.institutions = [...this.institutions];
		}
	}

	deleteInstitution(id: string) {
		this.institutions = this.institutions.filter(i => i.id !== id);
		// Optionally: clean up accounts that were linked to this institution
		// For now, we'll keep it simple as it's a mock.
	}
}


export const bankingStore = new BankingStore();

