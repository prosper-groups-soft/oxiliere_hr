/**
 * TanStack Query hooks for Access Management (Groups)
 * 
 * Following the pattern from leaveQueries.ts:
 * - Queries for data fetching
 * - Mutations for CRUD operations
 * - Automatic cache invalidation on mutations
 */

import { 
  createQuery, 
  createMutation, 
  useQueryClient
} from '@tanstack/svelte-query';
import { accessService } from '../services/access.service';
import type { GroupCreate } from '../types/access.types';
import { accessUserService } from "../services/accessUser.service";


// Query keys for cache management
export const accessQueryKeys = {
  all: ['access'] as const,
  groups: () => [...accessQueryKeys.all, 'groups'] as const,
  group: (slug: string) => [...accessQueryKeys.groups(), slug] as const,
  groupMembers: (slug: string) => [...accessQueryKeys.group(slug), 'members'] as const,
  roles: () => [...accessQueryKeys.all, 'roles'] as const,
  roleGrants: () => [...accessQueryKeys.all, 'roleGrants'] as const,
  scopes: () => [...accessQueryKeys.all, 'scopes'] as const,
};

// QUERIES

/**
 * Query: List all groups
 * GET /api/access/groups
 */
export function useGroupsQuery() {
  return createQuery({
    queryKey: accessQueryKeys.groups(),
    queryFn: () => accessService.listGroups(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}


/**
 * Query: List all roles
 * GET /api/access/roles
 */
export function useRolesQuery() {
  return createQuery({
    queryKey: accessQueryKeys.roles(),
    queryFn: () => accessService.listRoles(),
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Query: Get members of a specific group
 * GET /api/access/groups/{slug}/members
 */
export function useGroupMembersQuery(slug: string) {
  return createQuery({
    
    get queryKey() { return accessQueryKeys.groupMembers(slug); },
    queryFn: () => accessService.getGroupMembers(slug),
    staleTime: 1000 * 60 * 2,
    enabled: !!slug,
  });
}


/**
 * Query: List all role grants (permission templates)
 * GET /api/access/role-grants
 */
export function useRoleGrantsQuery() {
  return createQuery({
    queryKey: accessQueryKeys.roleGrants(),
    queryFn: () => accessService.listRoleGrants(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}


/**
 * Query: List all available scopes
 * GET /api/access/scopes
 */
export function useScopesQuery() {
  return createQuery({
    queryKey: accessQueryKeys.scopes(),
    queryFn: () => accessService.listScopes(),
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

// MUTATIONS

/**
 * Mutation: Create a new group
 * POST /api/access/groups
 */
export function useCreateGroupMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (data: GroupCreate) => accessService.createGroup(data),
    onSuccess: () => {
      // Invalidate groups list to trigger refetch
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
    },
  });
}


/**
 * Mutation: Update an existing group
 * PUT /api/access/groups/{group_slug}
 */
export function useUpdateGroupMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ slug, data }: { slug: string; data: Partial<GroupCreate> }) => 
      accessService.updateGroup(slug, data),
    onSuccess: (_, variables) => {
      // Invalidate both the list and the specific group
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.group(variables.slug) });
    },
  });
}


/**
 * Mutation: Delete a group
 * DELETE /api/access/groups/{group_slug}
 */
export function useDeleteGroupMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (slug: string) => accessService.deleteGroup(slug),
    onSuccess: () => {
      // Invalidate groups list to trigger refetch
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
    },
  });
}


/**
 * Mutation: Add a member to a group
 * POST /api/access/groups/{slug}/members
 */
export function useAddGroupMemberMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ slug, userId }: { slug: string; userId: string }) => 
      accessService.assignGroupToUser({ user_id: userId, group: slug }),
    onSuccess: (_, variables) => {
      // Invalidate both members list and groups list (for member_count update)
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groupMembers(variables.slug) });
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
    },
  });
}


/**
 * Mutation: Remove a member from a group
 * DELETE /api/access/groups/{slug}/members/{user_id}
 */
export function useRemoveGroupMemberMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ slug, userId }: { slug: string; userId: string }) => 
      accessService.revokeGroupFromUser({ user_id: userId, group: slug }),
    onSuccess: (_, variables) => {
      // Invalidate both members list and groups list (for member_count update)
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groupMembers(variables.slug) });
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
    },
  });
}

// USERS QUERIES

// Query keys for users
const usersQueryKeys = {
  all: () => ['access', 'users'] as const,
  list: (filters: {
    search?: string;
    page?: number;
    page_size?: number;
    groups?: string[];
    roles?: string[];
    is_active?: boolean;
  }) => [...usersQueryKeys.all(), 'list', filters] as const,
  detail: (id: string) => [...usersQueryKeys.all(), 'detail', id] as const,
  groups: (userId: string) => [...usersQueryKeys.all(), 'groups', userId] as const,
  grants: (userId: string) => [...usersQueryKeys.all(), 'grants', userId] as const,
};


// Query: List users with filters (Reactive version for Svelte 5)
type UserFilters = {
  search?: string;
  page?: number;
  page_size?: number;
  groups?: string[];
  roles?: string[];
  is_active?: boolean;
};

export function useUsersQuery(filtersGetter: () => UserFilters) {
  return createQuery({
    get queryKey() {
      const filters = filtersGetter();
      return ['access', 'users', 'list', filters];
    },
    queryFn: () => {
      const filters = filtersGetter();
      return accessUserService.listUsers(filters);
    },
  });
}


// Query: Get single user detail
export function useUserDetailQuery(userId: string | null) {
  return createQuery({
    get queryKey() { return ['access', 'users', 'detail', userId || '']; },
    queryFn: () => accessUserService.getUser(userId!),
    enabled: !!userId,
  });
}


// Query: Get user groups
export function useUserGroupsQuery(userIdGetter: () => string | null) {
  return createQuery({
    get queryKey() { return ['access', 'users', 'groups', userIdGetter() || '']; },
    queryFn: () => accessUserService.getUserGroups(userIdGetter()!),
    get enabled() { return !!userIdGetter(); },
  });
}


// Query: Get user grants
export function useUserGrantsQuery(userIdGetter: () => string | null) {
  return createQuery({
    get queryKey() { return ['access', 'users', 'grants', userIdGetter() || '']; },
    queryFn: () => accessUserService.getUserGrants(userIdGetter()!),
    get enabled() { return !!userIdGetter(); },
  });
}


// Mutation: Create user
export function useCreateUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (data: Parameters<typeof accessUserService.createUser>[0]) =>
      accessUserService.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.all() });
    },
  });
}


// Mutation: Update user
export function useUpdateUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ tenantUserId, userId, data }: {
      tenantUserId: string;
      userId: string;
      data: Parameters<typeof accessUserService.updateUser>[2];
    }) => accessUserService.updateUser(tenantUserId, userId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.all() });
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.detail(variables.userId) });
      // Invalidate groups and groupMembers to refresh member data across all components
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
      // Invalidate all groupMembers queries (cascades from groups key)
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.all });
    },
  });
}


// Mutation: Toggle user active status
export function useToggleUserActiveMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ tenantUserId, userId, isActive }: {
      tenantUserId: string;
      userId: string;
      isActive: boolean;
    }) => accessUserService.toggleUserActive(tenantUserId, userId, isActive),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.all() });
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.detail(variables.userId) });
      // Invalidate groups to refresh member status indicators in GroupCard
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.groups() });
    },
  });
}


// Mutation: Delete user
export function useDeleteUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (userId: string) => accessUserService.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.all() });
    },
  });
}


// Mutation: Assign group to user
export function useAssignGroupToUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ userId, group }: { userId: string; group: string }) =>
      accessService.assignGroupToUser({ user_id: userId, group }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.groups(variables.userId) });
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.all() });
    },
  });
}


// Mutation: Revoke group from user
export function useRevokeGroupFromUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ userId, group }: { userId: string; group: string }) =>
      accessService.revokeGroupFromUser({ user_id: userId, group }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.groups(variables.userId) });
      queryClient.invalidateQueries({ queryKey: usersQueryKeys.all() });
    },
  });
}


/**
 * Mutation: Create a role grant
 */
export function useCreateRoleGrantMutation() {
  const queryClient = useQueryClient();
  return createMutation({
    mutationFn: (data: Parameters<typeof accessService.createRoleGrant>[0]) =>
      accessService.createRoleGrant(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
    },
  });
}


/**
 * Mutation: Update a role grant
 */
export function useUpdateRoleGrantMutation() {
  const queryClient = useQueryClient();
  return createMutation({
    mutationFn: ({ id, actions }: { id: number; actions: string[] }) =>
      accessService.updateRoleGrant(id, actions),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
    },
  });
}


/**
 * Mutation: Delete a role grant
 */
export function useDeleteRoleGrantMutation() {
  const queryClient = useQueryClient();
  return createMutation({
    mutationFn: (id: number) => accessService.deleteRoleGrant(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
    },
  });
}


/**
 * Mutation: Restore role defaults
 */
export function useRestoreRoleDefaultsMutation() {
  const queryClient = useQueryClient();
  return createMutation({
    mutationFn: (roleSlug: string) => accessService.restoreRoleDefaults(roleSlug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
    },
  });
}

