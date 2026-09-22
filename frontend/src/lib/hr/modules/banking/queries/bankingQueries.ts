import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { bankingService } from '../services/banking.service';
import { bankingEndpoint } from '../api/banking.endpoints';
import { bankingStore } from '../stores/banking.svelte';
import type { BankAccount, BankAccountFilters } from '../types/types';
import { DEFAULT_PAGE_SIZE } from '@/hr/constants/ui/pagination';


// QUERY KEYS
export const bankingQueryKeys = {
  all: ['banking'] as const,
  institutions: () => [...bankingQueryKeys.all, 'institutions'] as const,
  accounts: (page?: number, limit?: number, search?: string, filters?: BankAccountFilters, sortBy?: string, sortOrder?: string) =>
    [...bankingQueryKeys.all, 'accounts', page ?? 1, limit ?? DEFAULT_PAGE_SIZE, search ?? '', filters ?? {}, sortBy ?? 'created_at', sortOrder ?? 'desc'] as const,
};


/**
 * Query to fetch all banking institutions.
 */
export function useBanksQuery() {
  return createQuery({
    queryKey: bankingQueryKeys.institutions(),
    queryFn: () => bankingService.listInstitutions(),
    staleTime: 1000 * 60 * 5,  // 5 min
    gcTime: 1000 * 60 * 10,     // 10 min
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Query to fetch bank accounts with pagination, search, filters and sorting (server-side).
 */
export function useAccountsQuery(
  page: () => number,
  limit: () => number = () => DEFAULT_PAGE_SIZE,
  search: () => string = () => '',
  filters: () => BankAccountFilters = () => ({}),
  sortBy: () => string = () => 'created_at',
  sortOrder: () => 'asc' | 'desc' = () => 'desc',
) {
  return createQuery({
    get queryKey() {
      return bankingQueryKeys.accounts(page(), limit(), search(), filters(), sortBy(), sortOrder());
    },
    queryFn: () => {
      const currentFilters = filters();
      return bankingService.listAccounts({
        page: page(),
        limit: limit(),
        search: search(),
        ordering: sortOrder() === 'desc' ? `-${sortBy()}` : sortBy(),
        currency: currentFilters.currency?.length === 1 ? currentFilters.currency[0] : undefined,
        status: currentFilters.status?.length === 1 ? currentFilters.status[0].toUpperCase() : undefined,
        bank_id: currentFilters.institutionId?.length === 1 ? currentFilters.institutionId[0] : undefined,
      });
    },
    staleTime: 1000 * 60 * 2,  // 2 min
    gcTime: 1000 * 60 * 5,     // 5 min
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Helper to sync account query data into the banking store.
 * Use inside a $effect in a .svelte component.
 */
export function syncAccountsStore(query: any) {
  const data = query.data as { results: BankAccount[]; count: number } | undefined;
  if (data) {
    const perPage = bankingStore.accountsPerPage;
    const totalPages = Math.ceil(data.count / perPage) || 1;
    bankingStore.setServerAccounts(data.results, data.count, totalPages);
  }
}


/**
 * Mutation to create a banking institution.
 */
export function useCreateBankMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: {
      name: string;
      code: string;
      swift_code?: string;
      is_mobile_money?: boolean;
      country_code?: string;
      is_active?: boolean;
    }) => bankingService.createInstitution(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.institutions() });
      notification.toast.success('Institution créée avec succès');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to update a banking institution.
 */
export function useUpdateBankMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      bankId,
      data,
    }: {
      bankId: string;
      data: {
        name?: string;
        code?: string;
        swift_code?: string;
        is_mobile_money?: boolean;
        country_code?: string;
        is_active?: boolean;
      };
    }) => bankingService.updateInstitution(bankId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.institutions() });
      notification.toast.success('Institution mise à jour');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to delete a banking institution.
 */
export function useDeleteBankMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (bankId: string) => bankingService.deleteInstitution(bankId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.institutions() });
      notification.toast.success('Institution supprimée');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error), { duration: 8000 });
    },
  });
}


/**
 * Mutation to upload a bank logo.
 */
export function useUploadBankLogoMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ bankId, file }: { bankId: string; file: File }) =>
      bankingEndpoint.uploadBankLogo(bankId, file),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.institutions() });
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to bulk-import default DRC financial institutions from fixture.
 */
export function useSeedBanksMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (codes?: string[]) => bankingEndpoint.seedBanks(codes),
    onSuccess: async (result) => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.institutions() });
      const msg = result.created_count > 0
        ? `${result.created_count} institution(s) ajoutée(s) avec succès`
        : 'Toutes les institutions sont déjà présentes';
      notification.toast.success(msg);
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


// --- Account Mutations ---

/**
 * Mutation to create a bank account.
 */
export function useCreateAccountMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: {
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
    }) => bankingService.createAccount(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.all });
      notification.toast.success('Compte bancaire créé avec succès');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to update a bank account.
 */
export function useUpdateAccountMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      accountId,
      data,
    }: {
      accountId: string;
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
      };
    }) => bankingService.updateAccount(accountId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.all });
      notification.toast.success('Compte bancaire mis à jour');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to delete a bank account.
 */
export function useDeleteAccountMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (accountId: string) => bankingService.deleteAccount(accountId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.all });
      notification.toast.success('Compte bancaire supprimé');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to verify a bank account.
 */
export function useVerifyAccountMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (accountId: string) => bankingService.verifyAccount(accountId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.all });
      notification.toast.success('Compte vérifié avec succès');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to set a bank account as primary.
 */
export function useSetPrimaryAccountMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (accountId: string) => bankingService.setPrimaryAccount(accountId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: bankingQueryKeys.all });
      notification.toast.success('Compte défini comme principal');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

