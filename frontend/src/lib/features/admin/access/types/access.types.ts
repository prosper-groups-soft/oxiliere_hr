export interface Role {
	slug: string;
	name: string;
	created_at: string;
	updated_at: string;
}

export interface Group {
	slug: string;
	name: string;
	roles: Role[];
	created_at: string;
	updated_at: string;
}

export interface RoleGrant {
	id: number;
	role: Role;
	scope: string;
	actions: string[];
	context: Record<string, any>;
}

export interface Grant {
	id: number;
	user_id: string; // Backend uses int/uuid, frontend will treat as string
	role?: Role;
	scope: string;
	actions: string[];
	context: Record<string, any>;
	created_at: string;
	updated_at: string;
}

export interface RoleCreate {
	slug: string;
	name: string;
}

export interface GroupCreate {
	slug: string;
	name: string;
	roles: string[]; // List of role slugs
}

export interface RoleGrantCreate {
	role: string;
	scope: string;
	actions: string[];
	context?: Record<string, any>;
}

export interface UserGroupAssignment {
	user_id: string;
	group: string;
}

export interface UserRoleAssignment {
	user_id: string;
	role: string;
}
