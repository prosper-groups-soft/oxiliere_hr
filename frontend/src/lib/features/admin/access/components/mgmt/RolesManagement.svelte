<script lang="ts">
  import { fade } from 'svelte/transition';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import accessStore from '../../stores/accessStore.svelte';
  import RolePermissionMatrix from '../permissions/RolePermissionMatrix.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import type { Role } from '@/features/admin/access/types/access.types';
  import { useQueryClient } from '@tanstack/svelte-query';
  import { 
    useRolesQuery, 
    useRoleGrantsQuery, 
    useScopesQuery 
  } from "../../queries/accessQueries.svelte";

  const queryClient = useQueryClient();
  
  // TanStack Query hooks
  const rolesQuery = useRolesQuery();
  const roleGrantsQuery = useRoleGrantsQuery();
  const scopesQuery = useScopesQuery();

  // Initialize store with queryClient for invalidation
  $effect(() => {
    accessStore.setQueryClient(queryClient);
  });

  // Sync query results to store
  $effect(() => {
    if ($rolesQuery.data) accessStore.roles = $rolesQuery.data;
  });
  $effect(() => {
    if ($roleGrantsQuery.data) accessStore.roleGrants = $roleGrantsQuery.data;
  });
  $effect(() => {
    if ($scopesQuery.data) accessStore.scopes = $scopesQuery.data;
  });

  // View state for UI logic
  const viewState = $derived.by(() => {
    if ($rolesQuery.isLoading) return 'initial-loading';
    if (($rolesQuery.data ?? []).length > 0) return 'content';
    return 'empty';
  });

  function selectRole(role: Role) {
    accessStore.selectedRole = role;
  }
  

  function clearSelection() {
    accessStore.selectedRole = null;
  }
</script>


{#snippet RoleList()}
  <div class="lg:col-span-5 flex flex-col overflow-hidden border-b border-slate-100 bg-white">
    <!-- Header -->
    <div class="sticky top-0 z-10 flex items-center h-10 px-6 bg-white border-b border-slate-100">
      <span class="w-[60%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Nom du rôle</span>
      <span class="w-[40%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Identifiant</span>
    </div>

    <!-- Role List -->
    <div class="flex-1 overflow-y-auto relative">
      {#if viewState === 'initial-loading'}
        <div class="absolute inset-0 flex items-center justify-center bg-white/50" in:fade={{ duration: 150 }}>
          <AnimateSpin text="Chargement..." />
        </div>
      {:else if viewState === 'empty'}
        <div class="h-full flex items-center justify-center" in:fade={{ duration: 150 }}>
          <Empty 
            icon="shield-off" 
            title="Aucun rôle" 
            description="Aucun rôle n'est configuré dans le système." 
            iconClass="text-slate-300" 
            iconSize={28}
            iconStrokeWidth={1.3}
          />
        </div>
      {:else}
        <div class="divide-y divide-slate-100" in:fade={{ duration: 200 }}>
          {#each accessStore.roles as role (role.slug)}
            {@const isSelected = accessStore.selectedRole?.slug === role.slug}
            <div 
              class="group/row flex items-center min-h-16 py-2 px-5 bg-white border-b border-slate-100 hover:bg-slate-50/80 transition-colors last:border-0 cursor-pointer {isSelected ? 'bg-indigo-50/30! hover:bg-indigo-50!' : ''}"
              onclick={() => selectRole(role)}
              role="none"
            >
              <!-- Role Name -->
              <div class="w-[60%] text-[0.88rem] text-slate-900 font-semibold truncate leading-tight group-hover/row:text-indigo-700 transition-colors border-b-0 {isSelected ? 'text-indigo-700' : ''}">
                {role.name}
              </div>
              
              <!-- Slug -->
              <div class="w-[40%]">
                <span class="text-[0.83rem] bg-slate-50/30 px-2 py-0.5 border border-slate-200 rounded-full shadow-fine">
                  {role.slug}
                </span>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/snippet}


{#snippet RoleDetails()}
  <div class="lg:col-span-7 flex flex-col overflow-hidden border border-r-0 border-b-0 border-slate-100 bg-slate-50/30">
    {#if accessStore.selectedRole}
      <div class="flex flex-col h-full bg-white">
        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-2 border-b bg-slate-50/50 shrink-0">
          <div class="flex items-center gap-3">
            <div class="h-11 w-11 rounded-full bg-amber-50 flex items-center justify-center border border-amber-100">
              <AppIcon name="award" size={18} class="text-amber-600" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-900">{accessStore.selectedRole.name}</h3>
              <span class="text-[0.75rem] bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                {accessStore.selectedRole.slug}
              </span>
            </div>
          </div>
          <button 
            class="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
            onclick={clearSelection}
          >
            <AppIcon name="x" size={18} />
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-hidden min-h-0">
          <RolePermissionMatrix role={accessStore.selectedRole} />
        </div>

        <!-- Footer -->
        <div class="px-5 py-4 border-t flex flex-row gap-3 bg-slate-50/30 shrink-0">
          <Button variant="outline" class="flex-1 h-10" onclick={clearSelection}>
            <AppIcon name="x" size={17} class="text-slate-300" />
            Fermer
          </Button>
        </div>
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center h-full p-8">
        <Empty 
          icon="award" 
          title="" 
          description="Sélectionnez un rôle pour voir et modifier ses permissions" 
          iconClass="text-amber-400" 
          iconSize={28}
          iconStrokeWidth={1.3}
        />
      </div>
    {/if}
  </div>
{/snippet}


<div class="h-full flex flex-col">
  <div class="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-12 gap-0 min-h-0">
    {@render RoleList()}
    {@render RoleDetails()}
  </div>
</div>

