import { bankingEndpoint } from '../api/banking.endpoints';
import { CURRENCIES } from '@/hr/constants/finance';
import { buildFullName } from '@/hr/utilities/common/employee.utils';
import type { PaginatedResponse } from '@/hr/types/pagination';
import type { 
  BankInstitution, 
  BankInstitutionBackendResponse,
  BankAccount,
  BankAccountBackendResponse,
  Currency,
  AccountType,
  VerificationStatus,
} from '../types/types';


/**
 * Maps a backend BankInstitutionBackendResponse (snake_case) to frontend BankInstitution (camelCase).
 */
function mapBankInstitution(raw: BankInstitutionBackendResponse): BankInstitution {
  return {
    id: raw.id,
    name: raw.name,
    shortName: raw.code,
    country: raw.country_code,
    type: raw.is_mobile_money ? 'mobile_money' : 'bank',
    swiftCode: raw.swift_code || undefined,
    isActive: raw.is_active,
    logoUrl: raw.logo || undefined,
  };
}

/**
 * Maps a backend BankAccountBackendResponse (snake_case) to frontend BankAccount (camelCase).
 */
function mapBankAccount(raw: BankAccountBackendResponse): BankAccount {
  let status: VerificationStatus = 'pending';
  if (raw.status === 'VERIFIED') {
    status = 'verified';
  } else if (raw.status === 'REJECTED') {
    status = 'rejected';
  } else if (raw.status === 'BLOCKED') {
    status = 'blocked';
  }

  // Map account_type (backend uses uppercase like 'CHECKING', 'SAVINGS') to frontend type
  const typeLower = (raw.account_type || '').toLowerCase();
  let type: AccountType = 'checking';
  if (typeLower.includes('saving') || typeLower === 'savings') {
    type = 'savings';
  } else if (typeLower.includes('mobile') || typeLower === 'mobile_money') {
    type = 'mobile_money';
  }

  // Normalize currencies
  const rawCurrencies: string[] = Array.isArray(raw.currencies) ? raw.currencies : ['USD'];
  const validCurrencies: Currency[] = Object.values(CURRENCIES);
  const currencies: Currency[] = rawCurrencies
    .map(c => c.toUpperCase() as Currency)
    .filter((c): c is Currency => validCurrencies.includes(c));
  const safeCurrencies: Currency[] = currencies.length > 0 ? currencies : ['USD' as Currency];
  const rawDefault = raw.default_currency?.toUpperCase() as Currency;
  const defaultCurrency: Currency = validCurrencies.includes(rawDefault) ? rawDefault : safeCurrencies[0];

  // Extract employee name from nested employee object
  const employeeRaw: any = raw.employee || {};
  const employeeName = buildFullName(employeeRaw) || employeeRaw.name || employeeRaw.email || '';
  const employeePhoto = employeeRaw.avatar_url || undefined;

  return {
    id: raw.id,
    employeeId: employeeRaw.id || '',
    employeeName,
    employeePhoto,
    institutionId: raw.bank?.id || '',
    accountName: raw.account_name,
    accountNumber: raw.account_number,
    branchCode: raw.branch_code || undefined,
    iban: raw.iban || undefined,
    swift: raw.bank?.swift_code || undefined,
    currencies: safeCurrencies,
    defaultCurrency,
    type,
    isPrimary: raw.is_primary,
    status,
    verifiedAt: raw.verified_at || undefined,
    notes: raw.notes || undefined,
    createdAt: raw.created_at,
  };
}


/**
 * Service for banking operations.
 * Handles API communication and data mapping.
 */
class BankingService {
  /**
   * GET /api/banking/banks
   * Fetches all financial institutions and maps them to frontend format.
   */
  async listInstitutions(): Promise<BankInstitution[]> {
    const response = await bankingEndpoint.listBanks();
    const items = Array.isArray(response) ? response : (response as any)?.results ?? [];
    return items.map(mapBankInstitution);
  }

  /**
   * POST /api/banking/banks
   */
  async createInstitution(data: {
    name: string;
    code: string;
    swift_code?: string;
    is_mobile_money?: boolean;
    country_code?: string;
    is_active?: boolean;
  }): Promise<BankInstitution> {
    const response = await bankingEndpoint.createBank(data);
    return mapBankInstitution(response);
  }

  /**
   * PUT /api/banking/banks/{bank_id}
   */
  async updateInstitution(
    bankId: string,
    data: {
      name?: string;
      code?: string;
      swift_code?: string;
      is_mobile_money?: boolean;
      country_code?: string;
      is_active?: boolean;
    }
  ): Promise<BankInstitution> {
    const response = await bankingEndpoint.updateBank(bankId, data);
    return mapBankInstitution(response);
  }

  /**
   * DELETE /api/banking/banks/{bank_id}
   */
  async deleteInstitution(bankId: string): Promise<void> {
    await bankingEndpoint.deleteBank(bankId);
  }

  // --- Accounts ---

  /**
   * GET /api/banking/accounts
   * Fetches all bank accounts and maps them to frontend format.
   */
  async listAccounts(params?: {
    page?: number;
    limit?: number;
    search?: string;
    ordering?: string;
    currency?: string;
    is_primary?: boolean;
    status?: string;
    bank_id?: string;
  }): Promise<PaginatedResponse<BankAccount>> {
    const response = await bankingEndpoint.listAccounts(params);
    return {
      count: response.count,
      next: response.next,
      previous: response.previous,
      results: response.results.map(mapBankAccount),
    };
  }

  /**
   * POST /api/banking/accounts
   */
  async createAccount(data: {
    employee_id: string;
    bank_id: string;
    account_number: string;
    account_name: string;
    account_type?: string;
    currencies?: string[];
    default_currency?: string;
    branch_code?: string;
    iban?: string;
    is_primary?: boolean;
  }): Promise<BankAccount> {
    const response = await bankingEndpoint.createAccount(data);
    return mapBankAccount(response);
  }

  /**
   * PUT /api/banking/accounts/{account_id}
   */
  async updateAccount(
    accountId: string,
    data: {
      employee_id?: string;
      bank_id?: string;
      account_number?: string;
      account_name?: string;
      account_type?: string;
      currencies?: string[];
      default_currency?: string;
      branch_code?: string;
      iban?: string;
      is_primary?: boolean;
      status?: string;
      notes?: string;
    }
  ): Promise<BankAccount> {
    const response = await bankingEndpoint.updateAccount(accountId, data);
    return mapBankAccount(response);
  }

  /**
   * DELETE /api/banking/accounts/{account_id}
   */
  async deleteAccount(accountId: string): Promise<void> {
    await bankingEndpoint.deleteAccount(accountId);
  }

  /**
   * POST /api/banking/accounts/{account_id}/verify
   */
  async verifyAccount(accountId: string): Promise<BankAccount> {
    const response = await bankingEndpoint.verifyAccount(accountId);
    return mapBankAccount(response);
  }

  /**
   * POST /api/banking/accounts/{account_id}/unverify
   */
  async unverifyAccount(accountId: string): Promise<BankAccount> {
    const response = await bankingEndpoint.unverifyAccount(accountId);
    return mapBankAccount(response);
  }

  /**
   * POST /api/banking/accounts/{account_id}/primary
   */
  async setPrimaryAccount(accountId: string): Promise<BankAccount> {
    const response = await bankingEndpoint.setPrimaryAccount(accountId);
    return mapBankAccount(response);
  }

  /**
   * POST /api/banking/accounts/{account_id}/activate
   */
  async activateAccount(accountId: string): Promise<BankAccount> {
    const response = await bankingEndpoint.activateAccount(accountId);
    return mapBankAccount(response);
  }

  /**
   * POST /api/banking/accounts/{account_id}/deactivate
   */
  async deactivateAccount(accountId: string): Promise<BankAccount> {
    const response = await bankingEndpoint.deactivateAccount(accountId);
    return mapBankAccount(response);
  }
}


export const bankingService = new BankingService();
