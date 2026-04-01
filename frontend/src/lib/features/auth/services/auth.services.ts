import { 
  AuthEndpoint, 
  UserAccountEndpoints 
} from '../api/auth.endpoints';
import type { LoginCredentials } from '../types/auth';
import type { SessionUser } from '@/types/users';
import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';


export const authService = {
	/**
	 * Performs a login request
	 */
	login: async (credentials: LoginCredentials) => {
		return await AuthEndpoint.login.create(credentials);
	},

	/**
	 * Performs a logout request
	 */
	logout: async () => {
		return await AuthEndpoint.logout.create({});
	},

	/**
	 * Retrieves the current session user
	 */
	getSession: async (): Promise<SessionUser> => {
		return await UserAccountEndpoints.session.list();
	},

	/**
	 * Refreshes the authentication token
	 */
	refreshToken: async () => {
		return await AuthEndpoint.refresh_token.create({});
	}
};


/**
 * Hook for login mutation
 */
export function useLogin() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: authService.login,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ['session'] });
		}
	});
}


/**
 * Hook for logout mutation
 */
export function useLogout() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: authService.logout,
		onSuccess: () => {
			queryClient.setQueryData(['session'], null);
			queryClient.clear();
		}
	});
}


/**
 * Hook for fetching current session
 */
export function useSession() {
	return createQuery({
		queryKey: ['session'],
		queryFn: authService.getSession,
		retry: false,
		staleTime: 1000 * 60 * 5 // 5 minutes
	});
}

