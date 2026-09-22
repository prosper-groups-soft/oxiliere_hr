<script lang="ts">
  import { slide, fade } from 'svelte/transition';
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import type { Group, GroupMember, SystemUser } from '@/hr/admin/access/types/access.types';
  import { accessStore } from '../../stores/accessStore.svelte';
  import { accessUserStore } from '../../stores/accessUserStore.svelte';
  import { accessService } from '../../services/access.service';
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { useGroupMembersQuery } from '../../queries/accessQueries.svelte';
  import UserListItem from "@/components/shared/items/UserListItem.svelte";


  interface Props {
    group: Group;
    onEdit: (group: Group) => void;
    onDelete: (slug: string) => void;
  }

  const { group, onEdit, onDelete }: Props = $props();

  function navigateToRole(role: typeof group.roles[0]) {
    // Find the full role object from store
    const fullRole = accessStore.roles.find(r => r.slug === role.slug);
    if (fullRole) {
      accessStore.selectedRole = fullRole;
      accessStore.activeTabId = 'roles';
    }
  }

  async function navigateToUser(userId: string) {
    // Switch to users tab
    accessStore.activeTabId = 'users';
    
    // Find and select the user (users are loaded via TanStack Query)
    const user = accessUserStore.users.find((u: SystemUser) => u.user.id === userId);
    if (user) {
      accessUserStore.selectUser(user);
    } else {
      // User not in current page - reset filters and select from fresh data
      accessUserStore.resetFilters();
      // Wait for query to refresh with new filters
      setTimeout(() => {
        const fetchedUser = accessUserStore.users.find((u: SystemUser) => u.user.id === userId);
        if (fetchedUser) {
          accessUserStore.selectUser(fetchedUser);
        }
      }, 100);
    }
  }

  let isMembersExpanded = $state(false);
  let members = $state<GroupMember[]>([]);
  let isLoadingMembers = $state(false);

  // We explicitly fetch directly instead of relying on Svelte Query's reactive stores
  // because nested query invalidation in Svelte 5 + TanStack v5 can sometimes fail to
  // trigger UI updates inside conditionally rendered $effect blocks. By fetching on
  // tab switch & expand, we guarantee fresh data.
  $effect(() => {
    // Track activeTabId to trigger on tab switch back to 'groups'
    const tabId = accessStore.activeTabId;
    
    if (isMembersExpanded && tabId === 'groups') {
      // Clear array first to force UI unmount/remount
      members = [];
      loadMembers();
    }
  });

  async function loadMembers() {
    isLoadingMembers = true;
    try {
      // We rely on Svelte's direct re-render. If there's a backend cache issue,
      // it is handled at the network level. 
      members = await accessService.getGroupMembers(group.slug);
    } catch (e) {
      console.error(e);
    } finally {
      isLoadingMembers = false;
    }
  }
</script>


<div class="group relative bg-white rounded-xl border border-indigo-100 p-5 transition-all duration-300 hover:shadow-fine hover:border-indigo-600/20 flex flex-col min-h-[180px] cursor-pointer" onclick={() => onEdit(group)} role="none" in:fade={{ duration: 250 }}>
  <!-- Header -->
  <div class="flex items-start justify-between mb-4">
    <div class="flex items-center gap-3">
      <div>
        <h4 class="text-[0.94rem] font-bold text-slate-900 leading-tight border-b-0">
          {group.name}
        </h4>
        <div class="text-slate-500 mt-0.5 flex items-center gap-2">
          <span class="text-[0.85rem]">{group.slug}</span>
          <span class="text-slate-300">|</span>
          <span class="text-[0.85rem]">{group.member_count} membre{group.member_count > 1 ? 's' : ''}</span>
        </div>
      </div>
    </div>

    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({ props })}
          <button 
            {...props}
            class="h-7 w-7 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors flex items-center justify-center cursor-pointer -mr-2"
          >
            <AppIcon name="more-horizontal" size={17} />
          </button>
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="w-34 p-1 bg-white shadow-fine border-slate-100 rounded-lg">
        <DropdownMenu.Item 
          onclick={() => onEdit(group)}
          class="flex items-center gap-1.5 px-2 py-1.5 text-[0.82rem] text-slate-800 cursor-pointer rounded-md hover:bg-slate-50 transition-colors"
        >
          <AppIcon name="settings" size={16} class="text-slate-500" />
          <span>Gérer</span>
        </DropdownMenu.Item>
        <DropdownMenu.Item 
          onclick={() => onDelete(group.slug)}
          class="flex items-center gap-1.5 px-2 py-1.5 text-[0.82rem] text-red-600 cursor-pointer rounded-md hover:bg-red-50/50! hover:text-red-700! transition-colors"
        >
          <AppIcon name="trash" size={16} class="text-red-600" />
          <span>Supprimer</span>
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>

  <!-- Roles Body -->
  <div class="flex-1 mt-2">
    <span class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-tight block mb-2">Rôles assignés ({group.role_count})</span>
    <div class="flex flex-wrap gap-1.5">
      {#each group.roles as role}
        <Badge 
          class="bg-white shadow-fine text-slate-800 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-700 text-[0.78rem] font-medium transition-colors rounded-full cursor-pointer px-5 py-0.5"
          onclick={(ev) => { ev.stopPropagation(); navigateToRole(role); }}
        >
          {role.name}
        </Badge>
      {/each}
      {#if group.roles.length === 0}
        <span class="text-[0.85rem] text-slate-500">Aucun rôle</span>
      {/if}
    </div>
  </div>

  <!-- Members Body -->
  <div class="mt-3 p-1.5 border-t border-slate-100 bg-slate-50 rounded-xl"
    role="none"
    onclick={(e) => { e.stopPropagation(); isMembersExpanded = !isMembersExpanded; }}
  >
    <button 
      class="flex items-center justify-between w-full mb-1.5 cursor-pointer hover:bg-slate-50 rounded-lg p-1 -mx-1 transition-colors"
      onclick={(e) => { e.stopPropagation(); isMembersExpanded = !isMembersExpanded; }}
    >
      <span class="text-[0.78rem] font-semibold text-slate-500 uppercase tracking-tight">Membres ({group.member_count})</span>
      <div class="flex items-center gap-1 text-slate-400">
        {#if isLoadingMembers}
          <AnimateSpin text="" class="border-slate-400 size-3" />
        {/if}
        <AppIcon 
          name="chevron-down" 
          size={16} 
          class="transition-transform duration-200 {isMembersExpanded ? 'rotate-180' : ''}" 
        />
      </div>
    </button>
    
    {#if isMembersExpanded}
      <div class="space-y-2 max-h-40 overflow-y-auto custom-scrollbar bg-[#fefefe]! rounded-xl" style="--scrollbar-size: 3px" transition:slide={{ duration: 200 }}>
        {#if isLoadingMembers}
          <div class="flex items-center gap-2 p-2" in:fade={{ duration: 150 }}>
            <div class="h-8 w-8 rounded-full bg-slate-200 animate-pulse"></div>
            <div class="flex-1 space-y-1">
              <div class="h-3 w-24 bg-slate-200 rounded animate-pulse"></div>
              <div class="h-2 w-32 bg-slate-200 rounded animate-pulse"></div>
            </div>
          </div>
        {:else if members.length > 0}
          <div class="divide-y divide-slate-50" in:fade={{ duration: 200 }}>
            {#each members as member (member.user.id)}
              <div class="rounded-lg hover:bg-[#fefeff]! transition-colors">
                <UserListItem
                  user={member.user}
                  onSelect={() => navigateToUser(member.user.id)}
                  icon={member.user.is_active 
                    ? { name: "circle", class: "h-1 w-1 rounded-full bg-emerald-400 border-0  shrink-0" }
                    : { name: "circle", class: "h-1 w-1 rounded-full bg-slate-300 border-0 shrink-0" }
                  }
                />
              </div>
            {/each}
          </div>
        {:else if group.member_count > 0}
          <div class="text-center py-4" in:fade={{ duration: 150 }}>
            <p class="text-[0.85rem] text-slate-500">Aucun membre chargé</p>
          </div>
        {:else}
          <div class="text-center py-4" in:fade={{ duration: 150 }}>
            <p class="text-[0.85rem] text-slate-500">Aucun membre dans ce groupe</p>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

