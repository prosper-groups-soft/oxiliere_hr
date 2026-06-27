<script lang="ts">
  import { slide, fade } from "svelte/transition";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { getFriendlyErrorMessage } from "@/constants/errors";
  import { notification } from "@/stores/notification.svelte";
  import { accessService } from "../../../services/access.service";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { auth } from "@/features/auth/stores/auth.svelte";
  import { 
    guardSelfGroupRevoke, 
    guardLastMemberRemoval 
  } from "../../../utils/access-guards";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import UserListItem from "@/components/shared/items/UserListItem.svelte";
  import ConfirmAction from "@/components/shared/actions/ConfirmAction.svelte";
  import type { 
    Group, 
    SystemUser,
    GroupMember,
  } from "../../../types/access.types";
  import { 
    useGroupMembersQuery, 
    useAddGroupMemberMutation, 
    useRemoveGroupMemberMutation 
  } from "../../../queries/accessQueries.svelte";


  interface Props {
    group: Group;
  }


  let { group }: Props = $props();

  // Reactive query - recreated when group.slug changes
  // Initialize with empty values to avoid capturing group reference
  let membersQuery = $state(useGroupMembersQuery(''));
  let lastGroupSlug = $state<string>('');
  
  // Recreate query when group.slug changes (runs immediately on mount)
  $effect(() => {
    const slug = group.slug;
    if (slug && slug !== lastGroupSlug) {
      membersQuery = useGroupMembersQuery(slug);
      lastGroupSlug = slug;
    }
  });

  // Mutations
  const addMemberMutation = useAddGroupMemberMutation();
  const removeMemberMutation = useRemoveGroupMemberMutation();

  // Local State
  let isLoadingSystemUsers = $state(false);
  let showAddMember = $state(false);
  let memberToRemove = $state<string | null>(null);
  let systemUsers = $state<SystemUser[]>([]);
  let selectedUserId = $state<string | null>(null);
  let userSearchQuery = $state("");

  // Derived from query
  const members = $derived(($membersQuery.data ?? []) as GroupMember[]);
  const isLoadingMembers = $derived($membersQuery.isLoading);
  const isAddingMember = $derived($addMemberMutation.isPending);

  // Derived
  const filteredUsers = $derived(
    userSearchQuery.trim() 
      ? systemUsers.filter(u => {
          const query = userSearchQuery.toLowerCase();
          return u.user.first_name?.toLowerCase().includes(query) ||
            u.user.last_name?.toLowerCase().includes(query) ||
            u.user.email?.toLowerCase().includes(query);
        })
      : systemUsers
  );

  async function loadSystemUsers() {
    if (systemUsers.length > 0) return;
    isLoadingSystemUsers = true;
    try {
      const response = await accessService.listUsers({ page: 1, page_size: 100 });
      systemUsers = response?.results || [];
    } catch (e) {
      console.error('Failed to load system users:', e);
      notification.toast.error(getFriendlyErrorMessage(e));
    } finally {
      isLoadingSystemUsers = false;
    }
  }

  async function addMember() {
    if (!selectedUserId) return;
    try {
      await $addMemberMutation.mutateAsync({ slug: group.slug, userId: selectedUserId });
      notification.toast.success("Membre ajouté au groupe.");
      selectedUserId = null;
      userSearchQuery = "";
      showAddMember = false;
    } catch (e: any) {
      console.error('Error adding member:', e);
      notification.toast.error(getFriendlyErrorMessage(e));
    }
  }

  async function confirmRemoveMember() {
    if (!memberToRemove) return;
    
    // Guard 1: Prevent self-revoke from system groups
    const guardCheck = guardSelfGroupRevoke(
      auth.currentUser?.id || '', 
      memberToRemove, 
      group.slug
    );
    if (!guardCheck.canProceed) {
      notification.toast.error(guardCheck.message!);
      memberToRemove = null;
      return;
    }
    
    // Guard 2: Prevent removing last member from critical groups
    const lastMemberCheck = guardLastMemberRemoval(group.slug, members.length);
    if (!lastMemberCheck.canProceed) {
      notification.toast.error(lastMemberCheck.message!);
      memberToRemove = null;
      return;
    }
    
    try {
      await $removeMemberMutation.mutateAsync({ slug: group.slug, userId: memberToRemove });
      notification.toast.success("Membre retiré du groupe.");
    } catch (e: any) {
      console.error('Error removing member:', e);
      notification.toast.error(getFriendlyErrorMessage(e) || "Erreur lors du retrait du membre.");
    } finally {
      memberToRemove = null;
    }
  }

  function cancelAdd() {
    showAddMember = false;
    selectedUserId = null;
    userSearchQuery = "";
  }
</script>


<div class="space-y-4">
  <div class="flex items-center justify-between">
    <Label class="flex items-center gap-2">
      Membres du groupe ({members.length})
    </Label>
    <Button 
      variant="default" 
      size="sm"
      onclick={() => { showAddMember = !showAddMember; if (showAddMember) loadSystemUsers(); }}
      class="h-7.5 text-[0.85rem] gap-1.5 transition-all"
    >
      <AppIcon name={showAddMember ? "x" :"plus"} size={17} />
      {showAddMember ? 'Annuler' : 'Ajouter'}
    </Button>
  </div>
  
  <!-- Add Member Form -->
  {#if showAddMember}
    <div class="p-3 rounded-lg border border-slate-100 bg-slate-100/30 space-y-3" transition:slide={{ duration: 200 }}>
      <Label>Sélectionnez un utilisateur à ajouter :</Label>
      
      <!-- Search Input -->
      <div class="relative">
        <AppIcon name="search" size={19} class="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <Input 
          type="text"
          bind:value={userSearchQuery} 
          placeholder="Rechercher un utilisateur..." 
          class="h-10 text-[0.9rem] pl-9 flex-1 rounded-lg"
        />
      </div>
      
      <!-- Users List -->
      <div class="max-h-48 overflow-y-auto custom-scrollbar bg-white rounded-lg border border-slate-200">
        {#if isLoadingSystemUsers}
          <div class="flex items-center justify-center max-h-48" transition:fade={{ duration: 150 }}>
            <AnimateSpin text="Chargement des utilisateurs" class="text-slate-400 size-3" />
          </div>
        {:else if filteredUsers.length === 0}
          <div class="text-center py-4 text-[0.8rem] text-slate-500 max-h-48" transition:fade={{ duration: 200 }}>
            {userSearchQuery ? 'Aucun utilisateur trouvé' : 'Commencez à taper pour rechercher'}
          </div>
        {:else}
          <div transition:slide={{ duration: 200 }}>
          {#each filteredUsers as user (user.user.id)}
            {@const isAlreadyMember = members.some(m => m.user.id === user.user.id)}
            <UserListItem
              user={user.user}
              selected={selectedUserId === user.user.id}
              disabled={isAlreadyMember}
              disabledReason={isAlreadyMember ? "déjà membre" : ""}
              onSelect={() => selectedUserId = user.user.id}
              icon={{ name: "check", class: "text-emerald-500 shrink-0" }}
            />
          {/each}
          </div>
        {/if}
      </div>
      
      <!-- Action Buttons -->
      <div class="flex gap-2">
        <Button 
          variant="outline"
          onclick={cancelAdd}
          class="h-8.5 flex-1 rounded-lg"
        >
          Annuler
        </Button>
        <Button 
          onclick={addMember}
          variant="outline"
          disabled={isAddingMember || !selectedUserId}
          class="h-8.5 text-indigo-600 hover:text-indigo-700 flex-1 cursor-pointer rounded-lg"
        >
          {#if isAddingMember}
            <AnimateSpin text="" class="size-3 text-indigo-600" />
          {:else}
            <AppIcon name="check" size={17} />
          {/if}
          Ajouter
        </Button>
      </div>
    </div>
  {/if}
  
  <!-- Members List -->
  <div class="rounded-xl border border-slate-200 bg-slate-50/50 overflow-hidden">
    {#if isLoadingMembers}
      <div class="text-center flex justify-center items-center h-45" transition:fade={{ duration: 150 }}>
        <AnimateSpin text="Chargement des membres" class="size-3" />
      </div>
    {:else if members.length === 0}
      <div class="text-center flex flex-col items-center justify-center max-h-64 h-45" transition:fade={{ duration: 200 }}>
        <AppIcon name="users" size={26} strokeWidth={1.4} class="text-slate-500 mx-auto mb-2" />
        <p class="text-[0.88rem] text-slate-700">
          Aucun membre dans ce groupe
        </p>
        <p class="text-[0.875rem] text-slate-500">
          Cliquez sur <span class="font-medium text-[0.8rem]">Ajouter</span> pour inviter des membres
        </p>
      </div>
    {:else}
      <div class="max-h-64 overflow-y-auto custom-scrollbar" transition:slide={{ duration: 200 }}>
        {#each members as member}
          {@const palette = getAvatarPalette(member.user.first_name + ' ' + member.user.last_name)}
          <div class="flex items-center gap-2 p-3 border-b border-slate-100 last:border-b-0 bg-white hover:bg-indigo-50/5! transition-colors">
            <div class="h-9.5 w-9.5 rounded-full flex items-center justify-center text-[0.8rem] font-medium shrink-0 border {palette.bg} {palette.text} {palette.borderColor}">
              {getInitials(member.user.first_name, member.user.last_name)}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[0.88rem] font-medium text-slate-800 truncate">
                {member.user.first_name} {member.user.last_name}
              </p>
              <p class="text-[0.88rem] text-slate-500 truncate">
                {member.user.email}
              </p>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              {#if member.user.is_active}
                <span class="inline-flex h-2 w-2 rounded-full bg-emerald-400" title="Actif"></span>
              {:else}
                <span class="inline-flex h-2 w-2 rounded-full bg-slate-300" title="Inactif"></span>
              {/if}      
              <ConfirmAction
                isConfirming={memberToRemove === member.user.id}
                onRequest={() => memberToRemove = member.user.id}
                onConfirm={confirmRemoveMember}
                onCancel={() => memberToRemove = null}
                labels={{ action: "Retirer", confirm: "Retirer" }}
                icons={{ action: "x", confirm: "check", cancel: "x" }}
                variant="danger"
              />
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

