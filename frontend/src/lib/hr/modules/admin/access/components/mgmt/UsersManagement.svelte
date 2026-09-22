<script lang="ts">
  import { fade } from 'svelte/transition';
  import FilterChips from "@/hr/components/shared/elements/FilterChips.svelte";
  import { accessUserStore } from "../../stores/accessUserStore.svelte";
  import { accessStore } from "../../stores/accessStore.svelte";
  import AccessUserListItem from "../users/AccessUserListItem.svelte";
  import AccessUserDetail from "../users/AccessUserDetail.svelte";
  import AccessUserCreateSheet from "../sheets/users/AccessUserCreateSheet.svelte";
  import Empty from "@/hr/components/shared/containers/empty/Empty.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import DataPagination from "@/hr/components/layout/elements/DataPagination.svelte";
  import { useUsersQuery, useToggleUserActiveMutation, useDeleteUserMutation, useCreateUserMutation, useUpdateUserMutation } from "../../queries/accessQueries.svelte";
  import { useQueryClient } from '@tanstack/svelte-query';

  
  let isSheetOpen = $state(false);

  // TanStack Query hooks
  const queryClient = useQueryClient();
  const usersQuery = useUsersQuery(() => accessUserStore.queryFilters);
  const toggleActiveMutation = useToggleUserActiveMutation();
  const deleteMutation = useDeleteUserMutation();
  const createMutation = useCreateUserMutation();
  const updateMutation = useUpdateUserMutation();
  
  // Refetch when filters change
  $effect(() => {
    const filters = accessUserStore.queryFilters;
    queryClient.invalidateQueries({ queryKey: ['access', 'users', 'list'] });
  });

  // Sync query results to store
  $effect(() => {
    accessUserStore.setUsersData(
      $usersQuery.data,
      $usersQuery.isLoading,
      $usersQuery.isFetching,
      $usersQuery.error,
      $usersQuery.isSuccess
    );
  });

  // Provide mutations to store
  $effect(() => {
    accessUserStore.setMutations({
      toggleActive: $toggleActiveMutation,
      delete: $deleteMutation,
      create: $createMutation,
      update: $updateMutation
    });
  });

  function handleFilterRemove(key: string, value: string | boolean | number | null) {
    if (key === 'groups') {
      accessUserStore.toggleGroupFilter(String(value));
    }
    if (key === 'roles') {
      accessUserStore.toggleRoleFilter(String(value));
    }
    if (key === 'isActive') {
      accessUserStore.setActiveFilter(null);
    }
    // La query est invalidée via l'$effect ci-dessus
  }

  function getDisplayLabel(key: string, value: string | boolean | number | null): string {
    if (key === 'groups') {
      const group = accessStore.groups.find(g => g.slug === value);
      return group?.name || String(value);
    }
    if (key === 'roles') {
      const role = accessStore.roles.find(r => r.slug === value);
      return role?.name || String(value);
    }
    return String(value);
  }

</script>


{#snippet EmptyState()}
  {@const emptyIcon = accessUserStore.activeFiltersCount > 0 || accessUserStore.hasEverSeenUsers ? "search-x" : "users"}
  {@const emptyDescription = accessUserStore.activeFiltersCount > 0 || accessUserStore.hasEverSeenUsers 
    ? "Essayez d'ajuster vos filtres" 
    : "Aucun utilisateur dans le système"}
  <div class="absolute inset-0 flex items-center justify-center" in:fade={{ duration: 200, delay: 50 }}>
    <Empty 
     
      icon={emptyIcon}
      title="Aucun utilisateur trouvé"
      description={emptyDescription}
      iconStrokeWidth={1.1}
      iconSize={26}      
    />
  </div>
{/snippet}


{#snippet UserListItems()}
  {#each accessUserStore.users as user (user.user.id)}
    <AccessUserListItem
      {user}
      isSelected={accessUserStore.selectedUser?.user.id === user.user.id}
      onSelect={(u) => accessUserStore.selectUser(u)}
      onToggleActive={(id) => accessUserStore.toggleUserActive(id)}
    />
  {/each}
{/snippet}


{#snippet UserListSection()}
  <div class="lg:col-span-6 flex flex-col overflow-hidden border-t border-b border-slate-100">
    <FilterChips
      filters={{
        search: accessUserStore.searchQuery ? [accessUserStore.searchQuery] : [],
        groups: accessUserStore.selectedGroups,
        roles: accessUserStore.selectedRoles,
        isActive: accessUserStore.isActiveFilter !== null ? [accessUserStore.isActiveFilter ? 'Actif' : 'Inactif'] : []
      }}
      activeFiltersCount={accessUserStore.activeFiltersCount}
      getDisplayLabel={getDisplayLabel}
      onRemove={handleFilterRemove}
      onReset={() => accessUserStore.resetFilters()}
      class="px-6 py-2 border-b border-slate-50 bg-white/50"
    />
    <div class="flex-1 overflow-y-auto divide-y divide-slate-100 relative">
      {#if accessUserStore.viewState === 'initial-loading' || accessUserStore.isReloading}
        <div class="absolute inset-0 flex items-center justify-center bg-white z-20" in:fade={{ duration: 150 }} out:fade={{ duration: 150 }}>
          <AnimateSpin class="border-slate-400 size-4" text="" />
        </div>
      {/if}

      {#if accessUserStore.viewState === 'content'}
        <div class="h-full overflow-y-auto" in:fade={{ duration: 200 }}>
          {@render UserListItems()}
        </div>
      {:else if accessUserStore.viewState !== 'initial-loading' && !accessUserStore.isReloading}
        {@render EmptyState()}
      {/if}
    </div>

    {#if accessUserStore.users.length > 0}
      <div class="border-t border-slate-100 px-4 py-0 bg-white">
        <DataPagination
          currentCount={accessUserStore.users.length}
          totalCount={accessUserStore.totalCount}
          currentPage={accessUserStore.currentPage}
          totalPages={accessUserStore.totalPages}
          perPage={accessUserStore.perPage}
          onPageChange={(p) => accessUserStore.setPage(p)}
          onPerPageChange={(s) => accessUserStore.setPerPage(s)}
          onNext={() => accessUserStore.setPage(accessUserStore.currentPage + 1)}
          onPrev={() => accessUserStore.setPage(accessUserStore.currentPage - 1)}
          unitLabel="utilisateurs"
        />
      </div>
    {/if}
  </div>
{/snippet}


<div class="h-full flex flex-col">
  <div class="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-12 gap-0 min-h-0">
    {@render UserListSection()}
    {@render DetailSection()}
  </div>
</div>


{#snippet DetailSection()}
  <div class="lg:col-span-6 overflow-hidden border border-r-0 border-b-0 border-slate-100 bg-slate-50/30">
    {#if accessUserStore.selectedUser}
      <AccessUserDetail
        user={accessUserStore.selectedUser}
        onClose={() => accessUserStore.selectUser(null)}
        onSave={async (id, data) => { await accessUserStore.updateUser(id, data); }}
        onToggleActive={async (id) => { await accessUserStore.toggleUserActive(id); }}
      />
    {:else}
      <div class="flex flex-col items-center justify-center h-full p-8" in:fade={{ duration: 150, delay: 50 }}>
        <Empty 
          icon="user" 
          title="" 
          description="Sélectionnez un utilisateur pour voir et modifier ses informations" 
          iconClass="text-indigo-400" 
          iconSize={26}
          iconStrokeWidth={1.1}
        />
      </div>
    {/if}
  </div>
{/snippet}


<!-- Désactivé provisoirement (Architecture Microservices - Géré par le service Auth)
<AccessUserCreateSheet 
  open={isSheetOpen} 
  onOpenChange={(v) => isSheetOpen = v}
  onSubmit={(data) => accessUserStore.createUser(data)}
/>
-->

