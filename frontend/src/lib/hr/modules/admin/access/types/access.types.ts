export interface Role {
	slug: string;
	name: string;
	created_at: string;
	updated_at: string;
}


export interface Group {
	slug: string;
	name: string;
	app: string | null;
	roles: Role[];
	member_count: number;
	role_count: number;
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
	scope: string; // Added scope to UserRoleAssignment type
}


export interface UserGrantOverride {
	user_id: string;
	scope: string;
	actions: string[];
	context?: Record<string, any>;
}


export interface GroupMember {
	user: {
		id: string;
		oxi_id: string;
		first_name: string;
		last_name: string;
		email: string;
		is_active: boolean;
		photo: string | null;
	};
	group_id: string;
	created_at: string;
}


export interface SystemUser {
	id: string; // TenantUser ID (for PUT/DELETE operations)
	user: {
		id: string; // User ID
		oxi_id: string;
		first_name: string;
		last_name: string;
		email: string;
		is_active: boolean;
		photo: string | null;
	};
	is_owner: boolean;
	is_admin: boolean;
	status: string;
	is_active: boolean;
	groups?: string[]; // group slugs
}


// API User types (from /api/users endpoints)
export interface ApiUser {
	id: string;
	email: string;
	username: string;
	first_name: string;
	last_name: string;
	is_active: boolean;
	groups: string[]; // group slugs
}


export interface PaginatedSystemUsersResponse {
	count: number;
	next: string | null;
	previous: string | null;
	results: SystemUser[];
}


export interface ApiUserCreate {
	email: string;
	first_name: string;
	last_name: string;
	password: string;
	is_active?: boolean;
	groups?: string[];
}


export interface ApiUserUpdate {
	email?: string;
	first_name?: string;
	last_name?: string;
	is_active?: boolean;
	groups?: string[];
	is_admin?: boolean;
	is_owner?: boolean;
	status?: string;
}


export interface ApiUserAdminUpdate {
	is_admin?: boolean;
	is_owner?: boolean;
	status?: string;
}

