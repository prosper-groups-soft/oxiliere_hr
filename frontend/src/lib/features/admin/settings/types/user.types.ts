// Types Utilisateurs et RBAC

export type UserRole = 'RH_ADMIN' | 'MANAGER' | 'EMPLOYEE';

export interface UserRoleConfig {
	role: UserRole;
	label: string;
	description: string;
	level: number;
	color: string;
}

export const USER_ROLES: UserRoleConfig[] = [
	{
		role: 'RH_ADMIN',
		label: 'RH Admin',
		description: 'Gestion complète des ressources humaines, paie et employés',
		level: 1,
		color: 'bg-blue-100 text-blue-700 border-blue-200'
	},
	{
		role: 'MANAGER',
		label: 'Manager',
		description: 'Validation des congés d\'équipe et accès limité aux rapports',
		level: 2,
		color: 'bg-green-100 text-green-700 border-green-200'
	},
	{
		role: 'EMPLOYEE',
		label: 'Employé',
		description: 'Accès à l\'espace personnel uniquement',
		level: 3,
		color: 'bg-slate-100 text-slate-700 border-slate-200'
	}
];

export type PermissionAction = 'create' | 'read' | 'update' | 'delete' | 'approve' | 'export' | 'config';

export type PermissionModule = 'employees' | 'leaves' | 'payroll' | 'settings' | 'recruitment' | 'attendance' | 'reports';

export interface Permission {
	module: PermissionModule;
	action: PermissionAction;
	allowed: boolean;
}

export interface User {
	id: number | string;
	email: string;
	username: string;
	firstName: string;
	lastName: string;
	isActive: boolean;
	groups: string[]; // Slugs des groupes assignés
	department?: string;
	phone?: string;
	role: UserRole;
	avatarUrl?: string;
	createdAt?: Date | string;
	lastLogin?: Date | string;
}

export interface CreateUserInput {
	email: string;
	firstName: string;
	lastName: string;
	role: UserRole;
	department?: string;
	phone?: string;
}

export interface UpdateUserInput {
	firstName?: string;
	lastName?: string;
	role?: UserRole;
	isActive?: boolean;
	department?: string;
	phone?: string;
}

export interface UserFilters {
	search: string;
	role: UserRole[];
	department: string[];
	isActive: boolean | null;
}

// Permissions par défaut pour chaque rôle
export const DEFAULT_ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
	RH_ADMIN: [
		{ module: 'employees', action: 'create', allowed: true },
		{ module: 'employees', action: 'read', allowed: true },
		{ module: 'employees', action: 'update', allowed: true },
		{ module: 'employees', action: 'delete', allowed: false },
		{ module: 'employees', action: 'export', allowed: true },
		{ module: 'leaves', action: 'create', allowed: true },
		{ module: 'leaves', action: 'read', allowed: true },
		{ module: 'leaves', action: 'update', allowed: true },
		{ module: 'leaves', action: 'approve', allowed: true },
		{ module: 'leaves', action: 'config', allowed: true },
		{ module: 'payroll', action: 'read', allowed: true },
		{ module: 'payroll', action: 'update', allowed: true },
		{ module: 'payroll', action: 'export', allowed: true },
		{ module: 'payroll', action: 'config', allowed: true },
		{ module: 'settings', action: 'read', allowed: true },
		{ module: 'settings', action: 'update', allowed: false },
		{ module: 'recruitment', action: 'create', allowed: true },
		{ module: 'recruitment', action: 'read', allowed: true },
		{ module: 'recruitment', action: 'update', allowed: true },
		{ module: 'attendance', action: 'read', allowed: true },
		{ module: 'attendance', action: 'update', allowed: true },
		{ module: 'attendance', action: 'config', allowed: true },
		{ module: 'reports', action: 'read', allowed: true },
		{ module: 'reports', action: 'export', allowed: true }
	],
	MANAGER: [
		{ module: 'employees', action: 'read', allowed: true },
		{ module: 'employees', action: 'export', allowed: false },
		{ module: 'leaves', action: 'read', allowed: true },
		{ module: 'leaves', action: 'approve', allowed: true },
		{ module: 'payroll', action: 'read', allowed: false },
		{ module: 'settings', action: 'read', allowed: false },
		{ module: 'recruitment', action: 'read', allowed: true },
		{ module: 'attendance', action: 'read', allowed: true },
		{ module: 'reports', action: 'read', allowed: true }
	],
	EMPLOYEE: [
		{ module: 'employees', action: 'read', allowed: false },
		{ module: 'leaves', action: 'create', allowed: true },
		{ module: 'leaves', action: 'read', allowed: true },
		{ module: 'payroll', action: 'read', allowed: true },
		{ module: 'settings', action: 'read', allowed: false },
		{ module: 'attendance', action: 'read', allowed: true }
	]
};
