import type { 
	MemberDetail, 
	Organization 
} from '@/types/organization';
import type { PaginatedResponse } from '@/types/pagination';
import OrganizationEndpoints from '$lib/features/auth/api/organizations.endpoints';
import { getStaleTime } from './utils';


// Query Options Factory
export const organizationQueryOptions = {
	all: () => ['organizations'],

	lists: () => [...organizationQueryOptions.all(), 'list'],
	list: (filters: {
		pageIndex: number;
		pageSize: number;
		search?: string;
		is_active?: boolean | null;
	}) => ({
		queryKey: [...organizationQueryOptions.lists(), filters],
		queryFn: fetchOrganizations,
		staleTime: getStaleTime(5)
	}),

	detail: (id: string) => ({
		queryKey: ['current_organization', id],
		queryFn: fetchOrganization,
		staleTime: getStaleTime(5)
	}),

	members: (organizationId: string) => ['organisation_members', organizationId],
	membersList: (organizationId: string) => ({
		queryKey: ['organisation_members_list', organizationId],
		queryFn: fetchOrganizationUsers,
		staleTime: getStaleTime(5)
	}),

	memberDetail: (organizationId: string, userId: string) => ({
		queryKey: ['organisation_member_detail', organizationId, userId],
		queryFn: fetchOrganizationUserDetail,
		staleTime: getStaleTime(5)
	})
};


/**
 * Fetch paginated organizations list
 * QueryKey shape: [
 *   'organizations',
 *   { pageIndex: number, pageSize: number },
 *   search?: string,
 *   is_active?: boolean | null
 * ]
 */
export const fetchOrganizations = async ({ queryKey }: { queryKey: any[] }) => {
	const [_key, { pageIndex, pageSize }] = queryKey;

	const data: PaginatedResponse<Organization> = await OrganizationEndpoints.organizations.list({
		page: pageIndex + 1,
		page_size: pageSize
	});
	return data;
};


/**
 * Fetch a single organization by ID
 */
export const fetchOrganization = async ({ queryKey }: { queryKey: any[] }) => {
	const [_key, organizationId] = queryKey;

	const data: Organization = await OrganizationEndpoints.organizations.retrieve(organizationId);
	return data;
};


/**
 * Fetch organization users/members
 * QueryKey shape: [
 *   'organization_members',
 *   organizationId: string,
 *   { pageIndex: number, pageSize: number },
 *   search?: string,
 *   role?: string
 * ]
 */
export const fetchOrganizationUsers = async ({ queryKey }: { queryKey: any[] }) => {
	const [_key, organizationId, { pageIndex, pageSize }, filters, sorting] = queryKey;

	const data = await OrganizationEndpoints.organization_users.list(organizationId, {
		page: pageIndex + 1,
		page_size: pageSize,
		...filters
	});
	return data;
};


export const fetchOrganizationUserDetail = async ({ queryKey }: { queryKey: any[] }) => {
	const [_key, organizationId, userId] = queryKey;

	const data: MemberDetail = await OrganizationEndpoints.organization_users.retrieve(
		organizationId,
		userId
	);
	return data;
};

