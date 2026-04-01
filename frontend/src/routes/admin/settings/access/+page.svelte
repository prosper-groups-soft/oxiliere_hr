<script lang="ts">
  import { onMount } from 'svelte';
  import { accessStore } from '@/features/admin/access/stores/accessStore.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';

  import GroupSheet from '@/features/admin/access/components/sheets/GroupSheet.svelte';
  import RolePermissionSheet from '@/features/admin/access/components/sheets/RolePermissionSheet.svelte';
  import AccessTabs from '@/features/admin/access/components/nav/AccessTabs.svelte';
  import GroupsGrid from '@/features/admin/access/components/GroupsGrid.svelte';
  import RolesTable from '@/features/admin/access/components/RolesTable.svelte';
  import type { Group, Role } from '@/features/admin/access/types/access.types';
  import { notification } from '@/stores/notification.svelte';

  onMount(() => {
    accessStore.init();
  });

  // --- Tabs Logic ---
  const TABS = [
    { id: 'groups', label: 'Groupes de sécurité', icon: 'users' },
    { id: 'roles', label: 'Rôles & Scopes', icon: 'key' }
  ];
  let activeTabId = $state('groups');

  function handleTabChange(tabId: string) {
    activeTabId = tabId;
  }

  // --- Sheet State ---
  let isGroupSheetOpen = $state(false);
  let selectedGroup = $state<Group | null>(null);

  let isRoleSheetOpen = $state(false);
  let selectedRole = $state<Role | null>(null);

  function openGroupSheet(group: Group | null = null) {
    selectedGroup = group;
    isGroupSheetOpen = true;
  }

  function openRoleSheet(role: Role) {
    selectedRole = role;
    isRoleSheetOpen = true;
  }

  async function handleDeleteGroup(slug: string) {
    notification.confirm({
      title: 'Supprimer le groupe',
      message: 'Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action est irréversible.',
      type: 'danger',
      yesText: 'Supprimer',
      onYes: async () => {
        try {
          await accessStore.deleteGroup(slug);
          notification.toast.success("Groupe supprimé.");
        } catch (e: any) {
          notification.toast.error("Erreur lors de la suppression.");
        }
      }
    });
  }

  async function handleSyncGroup(slug: string) {
    try {
      await accessStore.syncGroup(slug);
      notification.toast.success("Synchronisation terminée.");
    } catch (e: any) {
      notification.toast.error("Échec de la synchronisation.");
    }
  }
</script>


<div class="h-full flex flex-col animate-in fade-in duration-500">
  <!-- Tabs Navigation Header -->
  <div class="border-b border-slate-100 pr-8 pl-1 pt-1.5 flex items-center justify-between bg-white sticky top-0 z-10">
    <AccessTabs 
      tabs={TABS} 
      activeTabId={activeTabId} 
      onTabChange={handleTabChange} 
    />
  </div>

  <!-- Content Area -->
  <div class="flex-1 overflow-hidden">
    {#if accessStore.isLoading && accessStore.groups.length === 0}
      <div class="flex justify-center items-center h-full">
        <AnimateSpin text="Chargement des configurations de sécurité..." />
      </div>
    {:else if accessStore.error && accessStore.groups.length === 0}
      <div class="py-12 bg-white rounded-xl border border-red-200 shadow-none max-w-2xl mx-auto mt-10">
        <Empty 
          icon="alert-octagon" 
          title="Erreur de Connexion" 
          description={accessStore.error || "Impossible de communiquer avec le serveur d'authentification."} 
          iconClass="text-red-400" 
          iconSize={32} 
        />
      </div>
    {:else}
      
      <!-- TAB CONTENT: GROUPS -->
      {#if activeTabId === 'groups'}
        <GroupsGrid 
          groups={accessStore.groups} 
          onEdit={openGroupSheet}
          onSync={handleSyncGroup}
          onDelete={handleDeleteGroup}
          onCreate={() => openGroupSheet()}
        />
      {/if}

      <!-- TAB CONTENT: ROLES -->
      {#if activeTabId === 'roles'}
        <RolesTable 
          roles={accessStore.roles}
          getGrantsForRole={accessStore.getGrantsForRole}
          onExplore={openRoleSheet}
        />
      {/if}

    {/if}
  </div>
</div>


<!-- Modals / Sheets via Portals -->
<GroupSheet 
  bind:open={isGroupSheetOpen} 
  group={selectedGroup} 
/>

<RolePermissionSheet 
  bind:open={isRoleSheetOpen} 
  role={selectedRole} 
/>
