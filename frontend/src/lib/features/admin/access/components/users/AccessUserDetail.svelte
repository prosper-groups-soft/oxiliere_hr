<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Switch } from "@/components/ui/switch";
  import { Label } from "@/components/ui/label";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { cn } from "@/utilities/common/css";
  import type { SystemUser, Grant, Group, Role } from "../../types/access.types";
  import { accessStore } from "../../stores/accessStore.svelte";
  import { accessUserStore } from "../../stores/accessUserStore.svelte";
  import { accessService } from "../../services/access.service";
  import { 
    accessQueryKeys, 
    useUserGroupsQuery, 
    useUserGrantsQuery 
  } from "../../queries/accessQueries.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { useQueryClient } from "@tanstack/svelte-query";
  import { guardLastMemberRemoval } from "../../utils/access-guards";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";


  interface Props {
    user: SystemUser;
    onClose: () => void;
    onSave: (id: string, data: any) => Promise<void>;
    onToggleActive?: (id: string) => Promise<void>;
  }

  
  let { user, onClose, onSave, onToggleActive }: Props = $props();

  // TanStack Query client for cache invalidation
  const queryClient = useQueryClient();

  // Form state - use $state for mutable values
  // Note: initialized with empty values, $effect will sync with props
  let firstName = $state('');
  let lastName = $state('');
  let email = $state('');
  let isActive = $state(false);
  let isAdmin = $state(false);
  let isOwner = $state(false);
  let selectedGroupSlugs = $state<string[]>([]);
  let isSaving = $state(false);

  // Reactive user ID
  const userId = $derived(user.user.id);

  // TanStack queries for user-specific data (pass getter functions for reactivity)
  const userGroupsQuery = useUserGroupsQuery(() => userId);
  const userGrantsQuery = useUserGrantsQuery(() => userId);

  // Invalidate queries when user changes
  $effect(() => {
    const currentUserId = userId;
    queryClient.invalidateQueries({ queryKey: ['access', 'users', 'groups'] });
    queryClient.invalidateQueries({ queryKey: ['access', 'users', 'grants'] });
  });

  // Sync queries with store
  $effect(() => {
    accessUserStore.setUserGroups($userGroupsQuery.data);
    accessUserStore.setUserGrants($userGrantsQuery.data);
  });

  // Reset form when user changes or store data loads
  $effect(() => {
    firstName = user.user.first_name;
    lastName = user.user.last_name;
    email = user.user.email;
    isActive = user.user.is_active;
    isAdmin = user.is_admin;
    isOwner = user.is_owner;
    // Also trigger on selectedUserGroups change to ensure fresh slugs
    selectedGroupSlugs = accessUserStore.selectedUserGroups.map((g: Group) => g.slug);
  });

  const initials = $derived(
    getInitials(firstName, lastName)
  );

  const avatarPalette = $derived(
    getAvatarPalette(firstName + ' ' + lastName)
  );

  const hasChanges = $derived(
    firstName !== user.user.first_name ||
    lastName !== user.user.last_name ||
    email !== user.user.email ||
    isActive !== user.user.is_active ||
    isAdmin !== user.is_admin ||
    isOwner !== user.is_owner ||
    JSON.stringify([...selectedGroupSlugs].sort()) !== JSON.stringify(accessUserStore.selectedUserGroups.map((g: Group) => g.slug).sort())
  );

  // Derived roles from grants
  const userRoles = $derived(() => {
    const grants = accessUserStore.selectedUserGrants;
    const roles = grants
      .filter((g: Grant) => g.role)
      .map((g: Grant) => g.role!)
      .filter((role: Role, index: number, self: Role[]) => 
        index === self.findIndex((r: Role) => r.slug === role.slug)
      );
    return roles;
  });

  // Get assigned role slugs for quick lookup
  const assignedRoleSlugs = $derived(() => 
    userRoles().map((r: Role) => r.slug)
  );

  function resetForm() {
    firstName = user.user.first_name;
    lastName = user.user.last_name;
    email = user.user.email;
    isActive = user.user.is_active;
    isAdmin = user.is_admin;
    isOwner = user.is_owner;
    selectedGroupSlugs = accessUserStore.selectedUserGroups.map((g: Group) => g.slug);
  }

  async function handleSave() {
    // Guard: ensure we have a valid TenantUser ID
    if (!user.id) {
      console.error('Cannot save user: missing TenantUser ID (user.id is undefined)', user);
      // Try to reload the page to get fresh data with proper IDs
      notification.toast.error('Erreur: ID utilisateur manquant. Rafraîchissement des données...');
      return;
    }

    // Build payload with ONLY changed fields to avoid corrupting other data
    const changedData: any = {};
    if (firstName !== user.user.first_name) changedData.first_name = firstName;
    if (lastName !== user.user.last_name) changedData.last_name = lastName;
    if (email !== user.user.email) changedData.email = email;
    if (isActive !== user.user.is_active) changedData.is_active = isActive;
    if (isAdmin !== user.is_admin) changedData.is_admin = isAdmin;
    if (isOwner !== user.is_owner) changedData.is_owner = isOwner;

    // Only include groups if they actually changed
    const originalGroups = accessUserStore.selectedUserGroups.map((g: Group) => g.slug).sort();
    const currentGroups = [...selectedGroupSlugs].sort();
    if (JSON.stringify(originalGroups) !== JSON.stringify(currentGroups)) {
      changedData.groups = selectedGroupSlugs;
    }

    // Skip if nothing changed
    if (Object.keys(changedData).length === 0) {
      notification.toast.info('Aucune modification à sauvegarder');
      return;
    }

    try {
      isSaving = true;
      await onSave(user.id, changedData);
      // Update local state to reflect saved changes immediately
      // (in case parent hasn't updated the user prop yet)
      if (changedData.first_name !== undefined) user.user.first_name = changedData.first_name;
      if (changedData.last_name !== undefined) user.user.last_name = changedData.last_name;
      if (changedData.email !== undefined) user.user.email = changedData.email;
      if (changedData.is_active !== undefined) user.user.is_active = changedData.is_active;
      if (changedData.is_admin !== undefined) user.is_admin = changedData.is_admin;
      if (changedData.is_owner !== undefined) user.is_owner = changedData.is_owner;
      // Invalidate all access queries (users, groups, groupMembers) so every tab shows fresh data
      await queryClient.invalidateQueries({ queryKey: accessQueryKeys.all });
    } catch (e) {
      // Reset form to original values on error
      resetForm();
    } finally {
      isSaving = false;
    }
  }

  // Frontend guards - check if we can toggle and show error if not
  function checkCanToggleAdmin(): boolean {
    // Trying to toggle off (isAdmin is currently true, will become false)
    if (isAdmin && accessUserStore.adminCount <= 1) {
      notification.toast.error('Impossible de retirer les droits administrateur au dernier administrateur');
      return false;
    }
    return true;
  }

  function checkCanToggleOwner(): boolean {
    // Trying to toggle off (isOwner is currently true, will become false)
    if (isOwner && accessUserStore.ownerCount <= 1) {
      notification.toast.error('Impossible de retirer les droits propriétaire au dernier propriétaire');
      return false;
    }
    return true;
  }

  function checkCanToggleActive(): boolean {
    // Trying to disable (isActive is currently true, will become false)
    if (isActive) {
      if (isAdmin && accessUserStore.adminCount <= 1) {
        notification.toast.error('Impossible de désactiver le dernier administrateur');
        return false;
      }
      if (isOwner && accessUserStore.ownerCount <= 1) {
        notification.toast.error('Impossible de désactiver le dernier propriétaire');
        return false;
      }
    }
    return true;
  }

  async function toggleRole(roleSlug: string) {
    const isAssigned = assignedRoleSlugs().includes(roleSlug);
    try {
      if (isAssigned) {
        await accessUserStore.revokeRole(user.user.id, roleSlug);
      } else {
        await accessUserStore.assignRole(user.user.id, roleSlug);
      }
      // Clear cache to force list refresh
      accessUserStore.clearUserGroupsCache();
    } catch (e) {
      // Error handled by store, state already reset
    }
  }

  async function toggleGroup(groupSlug: string) {
    const currentSlugs = [...selectedGroupSlugs];
    const isAssigned = currentSlugs.includes(groupSlug);
    
    if (isAssigned) {
      // GUARD: Check if trying to remove last member from system group
      const group = accessStore.groups.find(g => g.slug === groupSlug);
      if (group) {
        const guard = guardLastMemberRemoval(groupSlug, group.member_count);
        if (!guard.canProceed) {
          notification.toast.error(guard.message || 'Action bloquée');
          return;
        }
      }
      
      try {
        await accessService.revokeGroupFromUser({ user_id: user.user.id, group: groupSlug });
        // Update local state after successful API call
        accessUserStore.selectedUserGroups = accessUserStore.selectedUserGroups.filter((g: Group) => g.slug !== groupSlug);
        selectedGroupSlugs = accessUserStore.selectedUserGroups.map((g: Group) => g.slug);
        notification.toast.success('Groupe retiré avec succès');
        
        // Clear cache and invalidate queries
        accessUserStore.clearUserGroupsCache();
        await accessStore.fetchGroups();
        await queryClient.invalidateQueries({ queryKey: accessQueryKeys.all });
      } catch (e: any) {
        // Error handled by service
      }
    } else {
      try {
        await accessService.assignGroupToUser({ user_id: user.user.id, group: groupSlug });
        // Update local state after successful API call
        const group = accessStore.groups.find((g: Group) => g.slug === groupSlug);
        if (group) {
          accessUserStore.selectedUserGroups = [...accessUserStore.selectedUserGroups, group];
          selectedGroupSlugs = accessUserStore.selectedUserGroups.map((g: Group) => g.slug);
        }
        notification.toast.success('Groupe assigné avec succès');
        
        // Clear cache and invalidate queries
        accessUserStore.clearUserGroupsCache();
        await accessStore.fetchGroups();
        await queryClient.invalidateQueries({ queryKey: accessQueryKeys.all });
      } catch (e: any) {
        // Error handled by service
      }
    }
  }
</script>


<div class="h-full flex flex-col bg-white">
  <!-- Header -->
  <div class="flex items-center justify-between px-5 py-3 border-b border-slate-100 bg-slate-50/50 shrink-0">
    <div class="flex items-center gap-3">
      <div class="w-11 h-11 rounded-full flex items-center justify-center font-semibold text-sm border {avatarPalette.bg} {avatarPalette.text} {avatarPalette.borderColor}">
        {initials}
      </div>
      <div>
        <h3 class="text-sm font-semibold text-slate-900">{firstName} {lastName}</h3>
        <span class="text-[0.85rem] text-slate-500">{email}</span>
      </div>
    </div>
    <button 
      class="p-2 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
      onclick={onClose}
    >
      <AppIcon name="x" size={18} />
    </button>
  </div>

  <!-- Content -->
  <div class="flex-1 overflow-y-auto p-5 space-y-5">
    <!-- Status -->
    <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
      <div class="flex items-center gap-3">
        <div class={cn(
          "w-2 h-2 rounded-full",
          isActive ? "bg-emerald-500" : "bg-slate-400"
        )}></div>
        <span class="text-sm font-medium text-slate-700">
          Compte {isActive ? 'actif' : 'inactif'}
        </span>
      </div>
      <div 
        class={cn("relative", isActive && (isAdmin && accessUserStore.adminCount <= 1 || isOwner && accessUserStore.ownerCount <= 1) && "cursor-not-allowed opacity-50")}
        onclick={(e) => {
          if (isActive && (isAdmin && accessUserStore.adminCount <= 1 || isOwner && accessUserStore.ownerCount <= 1)) {
            e.preventDefault();
            e.stopPropagation();
            checkCanToggleActive();
            return false;
          }
        }}
        role="none"
      >
        <Switch 
          checked={isActive} 
          onCheckedChange={(v) => {
            if (checkCanToggleActive()) {
              isActive = v;
            }
          }}
          disabled={isActive && (isAdmin && accessUserStore.adminCount <= 1 || isOwner && accessUserStore.ownerCount <= 1)}
          class="cursor-pointer"
        />
      </div>
    </div>

    <!-- Permissions -->
    <div class="space-y-3">
      <h4 class="text-[0.75rem] font-bold text-slate-400 uppercase tracking-wider">Permissions</h4>
      
      <div class="grid gap-3">
        <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
          <div class="flex items-center gap-3">
            <AppIcon name="shield" size={20} class="text-indigo-500" />
            <div>
              <span class="text-sm font-medium text-slate-800">Administrateur</span>
              <p class="text-[0.85rem] text-slate-500">Accès complet à l'administration</p>
            </div>
          </div>
          <div 
            class={cn("relative", isAdmin && accessUserStore.adminCount <= 1 && "cursor-not-allowed opacity-50")}
            onclick={(e) => {
              if (isAdmin && accessUserStore.adminCount <= 1) {
                e.preventDefault();
                e.stopPropagation();
                checkCanToggleAdmin();
                return false;
              }
            }}
            role="none"
          >
            <Switch 
              checked={isAdmin} 
              onCheckedChange={(v) => {
                if (checkCanToggleAdmin()) {
                  isAdmin = v;
                }
              }}
              disabled={isAdmin && accessUserStore.adminCount <= 1}
              class="cursor-pointer"
            />
          </div>
        </div>
        
        <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
          <div class="flex items-center gap-3">
            <AppIcon name="crown" size={20} class="text-amber-500" />
            <div>
              <span class="text-sm font-medium text-slate-800">Propriétaire</span>
              <p class="text-[0.85rem] text-slate-500">Contrôle total du système</p>
            </div>
          </div>
          <div 
            class={cn("relative", isOwner && accessUserStore.ownerCount <= 1 && "cursor-not-allowed opacity-50")}
            onclick={(e) => {
              if (isOwner && accessUserStore.ownerCount <= 1) {
                e.preventDefault();
                e.stopPropagation();
                checkCanToggleOwner();
                return false;
              }
            }}
            role="none"
          >
            <Switch 
              checked={isOwner} 
              onCheckedChange={(v) => {
                if (checkCanToggleOwner()) {
                  isOwner = v;
                }
              }}
              disabled={isOwner && accessUserStore.ownerCount <= 1}
              class="cursor-pointer"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Basic Info -->
    <div class="space-y-3">
      <h4 class="text-[0.75rem] font-bold text-slate-400 uppercase tracking-wider">Informations</h4>
      
      <div class="grid gap-3">
        <div class="space-y-1.5">
          <Label for="firstName" class="text-sm">Prénom</Label>
          <Input
            id="firstName"
            type="text"
            bind:value={firstName}
            class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
          />
        </div>
        
        <div class="space-y-1.5">
          <Label for="lastName" class="text-sm">Nom</Label>
          <Input
            id="lastName"
            type="text"
            bind:value={lastName}
            class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
          />
        </div>
        
        <div class="space-y-1.5">
          <Label for="email" class="text-sm">Email</Label>
          <Input
            id="email"
            type="email"
            bind:value={email}
            class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
          />
        </div>
      </div>
    </div>

    <!-- Roles -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-[0.75rem] font-bold text-slate-400 uppercase tracking-wider">
          Rôles ({userRoles().length})
        </h4>
        <span class="text-[0.84rem] text-slate-400">Cliquez pour assigner/retirer</span>
      </div>
      
      <div class="flex flex-wrap gap-2">
        {#each accessStore.roles as role}
          <button
            type="button"
            onclick={() => toggleRole(role.slug)}
            class={cn(
              "px-3 py-1.5 text-[0.84rem] rounded-full border transition-all cursor-pointer shadow-fine active:scale-95 active:shadow-none",
              assignedRoleSlugs().includes(role.slug)
                ? "bg-indigo-50 text-indigo-700 border-indigo-200"
                : "bg-white text-slate-700 border-slate-200 hover:bg-slate-50"
            )}
          >
            {role.name}
          </button>
        {/each}
        
        {#if accessStore.roles.length === 0}
          <span class="text-[0.85rem] text-slate-400">Aucun rôle disponible</span>
        {/if}
      </div>
      
      <!-- Current Roles Display -->
      <div class="pt-2 border-t border-slate-100">
        <Label class="text-sm mb-2">Rôles actuels :</Label>
        <div class="flex flex-wrap gap-2">
          {#if userRoles().length === 0}
            <span class="text-[0.84rem] text-slate-400">Aucun rôle assigné</span>
          {:else}
            {#each userRoles() as role}
              <Badge
                class="text-[0.85rem] px-2 py-1.5 font-medium border rounded-full bg-indigo-50 text-indigo-700 border-indigo-200"
              >
                {role.name}
              </Badge>
            {/each}
          {/if}
        </div>
      </div>
    </div>

    <!-- Groups -->
    <div class="space-y-3">
      <h4 class="text-[0.75rem] font-bold text-slate-400 uppercase tracking-wider">Groupes ({accessUserStore.selectedUserGroups.length})</h4>
      
      <div class="flex flex-wrap gap-2">
        {#each accessStore.groups as group}
          <button
            onclick={() => toggleGroup(group.slug)}
            class={cn(
              "px-3 py-1.5 text-[0.85rem] rounded-full border transition-all cursor-pointer active:scale-95 active:shadow-none",
              selectedGroupSlugs.includes(group.slug)
                ? "bg-indigo-50 text-indigo-700 border-indigo-200"
                : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
            )}
          >
            {group.name}
          </button>
        {/each}
      </div>
    </div>

    <!-- User ID -->
    <div class="pt-4 border-t hidden">
      <span class="text-[0.85rem] text-slate-400">
        Utilisateur tenant ID: {user.id} | Utilisateur ID: {user.user.id}
      </span>
    </div>
  </div>

  <!-- Footer -->
  <div class="px-5 py-2.5 border-t border-slate-100 flex gap-3 bg-slate-50/30 shrink-0">
    <Button 
      variant="outline" 
      class="flex-1 h-9"
      onclick={onClose}
    >
      <AppIcon name="x" class="text-slate-300" size={16} />
      Annuler
    </Button>
    <Button 
      class="flex-1 h-9 bg-indigo-600 hover:bg-indigo-700"
      disabled={!hasChanges || isSaving}
      onclick={handleSave}
    >
      {#if isSaving}
        <AnimateSpin text="" class="border-white size-3" />
      {:else}
        <AppIcon name="check" size={16} />
      {/if}
      Enregistrer
    </Button>
  </div>
</div>

