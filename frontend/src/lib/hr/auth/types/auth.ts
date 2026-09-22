import type { UserSimple } from '@/types/users';


export interface LoginCredentials {
	email: string;
	password?: string;
	remember_me?: boolean;
}


export interface AuthResponse {
	access: string;
	refresh: string;
	user: UserSimple;
}

