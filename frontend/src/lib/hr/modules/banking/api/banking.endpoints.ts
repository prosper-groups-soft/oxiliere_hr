import APIEndPoint from '@/hr/utilities/http/rest';
import type { PaginatedResponse } from '@/hr/types/pagination';
import type { BankInstitutionBackendResponse, BankAccountBackendResponse } from '../types/types';


/**
 * API Endpoints for Banking (institutions + accounts)
 * Base path: /api/banking
 */
export const bankingEndpoint = {
  /**
   * GET /api/banking/banks
   * Lists all registered banks and mobile money providers.
   */
  listBanks: async (): Promise<BankInstitutionBackendResponse[]> => {
    const endpoint = new APIEndPoint('/api/banking/banks', '/api/banking/banks');
    return await endpoint.list();
  },

  /**
   * POST /api/banking/banks
   * Creates a new financial institution.
   */
  createBank: async (data: {
    name: string;
    code: string;
    swift_code?: string;
    is_mobile_money?: boolean;
    country_code?: string;
  }): Promise<BankInstitutionBackendResponse> => {
    const endpoint = new APIEndPoint('/api/banking/banks', '/api/banking/banks');
    const response = await endpoint.create(data);
    return response[1] || response;
  },

  /**
   * PUT /api/banking/banks/{bank_id}
   * Updates a financial institution.
   */
  updateBank: async (
    bankId: string,
    data: {
      name?: string;
      code?: string;
      swift_code?: string;
      is_mobile_money?: boolean;
      country_code?: string;
    }
  ): Promise<BankInstitutionBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/banks/${bankId}`,
      `/api/banking/banks/${bankId}`
    );
    const response = await endpoint.update(data);
    return response[1] || response;
  },

  /**
   * DELETE /api/banking/banks/{bank_id}
   * Deletes a financial institution.
   */
  deleteBank: async (bankId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/banking/banks/${bankId}`,
      `/api/banking/banks/${bankId}`
    );
    await endpoint.destroy();
  },

  /**
   * POST /api/banking/banks/{bank_id}/upload-logo
   * Uploads a logo image for a financial institution.
   */
  uploadBankLogo: async (bankId: string, file: File): Promise<BankInstitutionBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/banks/${bankId}/upload-logo`,
      `/api/banking/banks/${bankId}/upload-logo`
    );
    const formData = new FormData();
    formData.append('logo', file);
    return await endpoint.create(formData);
  },

  /**
   * POST /api/banking/banks/seed
   * Bulk-creates default DRC financial institutions (deduplicated by code).
   */
  seedBanks: async (codes?: string[]): Promise<{
    created: string[];
    created_count: number;
    skipped: string[];
    skipped_count: number;
  }> => {
    const endpoint = new APIEndPoint('/api/banking/banks/seed', '/api/banking/banks/seed');
    const body = codes ? { codes } : {};
    const response = await endpoint.create(body);
    return response[1] || response;
  },

  /**
   * GET /api/banking/banks/seed/list
   * Returns the list of institutions available for seeding from the fixture.
   */
  listSeedableBanks: async (): Promise<{
    code: string;
    name: string;
    is_mobile_money: boolean;
    exists: boolean;
  }[]> => {
    const endpoint = new APIEndPoint('/api/banking/banks/seed/list', '/api/banking/banks/seed/list');
    return await endpoint.list();
  },

  // --- Accounts ---

  /**
   * GET /api/banking/accounts
   * Lists all employee bank accounts.
   */
  listAccounts: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    ordering?: string;
    currency?: string;
    is_primary?: boolean;
    status?: string;
    bank_id?: string;
  }): Promise<PaginatedResponse<BankAccountBackendResponse>> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.search) queryParams.set('search', params.search);
    if (params?.ordering) queryParams.set('ordering', params.ordering);
    if (params?.currency) queryParams.set('currency', params.currency);
    if (params?.is_primary !== undefined) queryParams.set('is_primary', params.is_primary.toString());
    if (params?.status) queryParams.set('status', params.status);
    if (params?.bank_id) queryParams.set('bank_id', params.bank_id);
    const queryString = queryParams.toString();
    const url = queryString ? `/api/banking/accounts?${queryString}` : '/api/banking/accounts';
    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list();
  },

  /**
   * POST /api/banking/accounts
   * Creates a new bank account for an employee.
   */
  createAccount: async (data: {
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
    notes?: string;
  }): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint('/api/banking/accounts', '/api/banking/accounts');
    const response = await endpoint.create(data);
    return response[1] || response;
  },

  /**
   * PUT /api/banking/accounts/{account_id}
   * Updates an existing bank account.
   */
  updateAccount: async (
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
  ): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}`,
      `/api/banking/accounts/${accountId}`
    );
    const response = await endpoint.partial_update(data);
    return response[1] || response;
  },

  /**
   * DELETE /api/banking/accounts/{account_id}
   * Deletes a bank account.
   */
  deleteAccount: async (accountId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}`,
      `/api/banking/accounts/${accountId}`
    );
    await endpoint.destroy();
  },

  /**
   * POST /api/banking/accounts/{account_id}/verify
   * Verifies a bank account.
   */
  verifyAccount: async (accountId: string): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}/verify`,
      `/api/banking/accounts/${accountId}/verify`
    );
    return await endpoint.create({});
  },

  /**
   * POST /api/banking/accounts/{account_id}/unverify
   * Unverifies a bank account.
   */
  unverifyAccount: async (accountId: string): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}/unverify`,
      `/api/banking/accounts/${accountId}/unverify`
    );
    return await endpoint.create({});
  },

  /**
   * POST /api/banking/accounts/{account_id}/primary
   * Sets an account as primary.
   */
  setPrimaryAccount: async (accountId: string): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}/primary`,
      `/api/banking/accounts/${accountId}/primary`
    );
    return await endpoint.create({});
  },

  /**
   * POST /api/banking/accounts/{account_id}/activate
   * Activates a bank account.
   */
  activateAccount: async (accountId: string): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}/activate`,
      `/api/banking/accounts/${accountId}/activate`
    );
    return await endpoint.create({});
  },

  /**
   * POST /api/banking/accounts/{account_id}/deactivate
   * Deactivates a bank account.
   */
  deactivateAccount: async (accountId: string): Promise<BankAccountBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/banking/accounts/${accountId}/deactivate`,
      `/api/banking/accounts/${accountId}/deactivate`
    );
    return await endpoint.create({});
  },
};
