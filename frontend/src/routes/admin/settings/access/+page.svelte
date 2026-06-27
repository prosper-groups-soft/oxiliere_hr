<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { replaceState } from '$app/navigation';
  import { page } from '$app/state';
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { accessStore } from '@/features/admin/access/stores/accessStore.svelte';
  import { 
    ERROR_MESSAGES, 
    getFriendlyErrorMessage 
  } from '@/constants/errors';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';

  import AccessTabs from '@/features/admin/access/components/nav/AccessTabs.svelte';
  import UsersManagement from '@/features/admin/access/components/mgmt/UsersManagement.svelte';
  import GroupsManagement from '@/features/admin/access/components/mgmt/GroupsManagement.svelte';
  import RolesManagement from '@/features/admin/access/components/mgmt/RolesManagement.svelte';

  onMount(() => {
    accessStore.init();
  });

  // --- Tabs Logic ---
  const TABS = [
    { id: 'users', label: 'Utilisateurs', icon: 'user' },
    { id: 'groups', label: 'Groupes', icon: 'users' },
    { id: 'roles', label: 'Rôles', icon: 'key' }
  ];
  // Read tab from URL once on mount (not in $effect to avoid reactivity loop)
  onMount(() => {
    if (browser) {
      const params = new URLSearchParams(window.location.search);
      const tabFromUrl = params.get('tab');
      const validTabs = TABS.map(t => t.id);
      if (tabFromUrl && validTabs.includes(tabFromUrl)) {
        accessStore.activeTabId = tabFromUrl;
      }
    }
  });

  function handleTabChange(tabId: string) {
    accessStore.activeTabId = tabId;
    // Defer URL update using requestIdleCallback or setTimeout fallback
    const scheduleUpdate = typeof requestIdleCallback !== 'undefined' 
      ? (cb: () => void) => requestIdleCallback(cb, { timeout: 100 })
      : (cb: () => void) => setTimeout(cb, 0);
    
    scheduleUpdate(() => {
      const url = new URL(page.url);
      url.searchParams.set('tab', tabId);
      replaceState(url, {});
    });
  }
</script>


<svelte:head>
  <title>Paramètres - Sécurité & Accès | Oxiliere HR</title>
</svelte:head>


<div class="h-full flex flex-col animate-in fade-in duration-500">

  <!-- Tabs Navigation Header -->
  <div class="border-b border-slate-100 pr-8 pl-1 pt-1.5 flex items-center justify-between bg-white sticky top-0 z-10">
    <AccessTabs 
      tabs={TABS} 
      activeTabId={accessStore.activeTabId} 
      onTabChange={handleTabChange} 
    />
  </div>

  <!-- Content Area -->
  <div class="flex-1 overflow-hidden">
  
    {#if accessStore.isLoading && accessStore.groups.length === 0}
      <div class="flex justify-center items-center h-full">
        <AnimateSpin text="Chargement" />
      </div>
    {:else if accessStore.error && accessStore.groups.length === 0}
      <div class="flex justify-center items-center h-full">
        <Empty 
          icon="alert-circle" 
          title="Erreur de Connexion" 
          description={getFriendlyErrorMessage(accessStore.error) || ERROR_MESSAGES.NETWORK.UNKNOWN} 
          iconClass="text-red-400" 
          iconContainerClass="bg-red-50/30"
          iconSize={28}
          iconStrokeWidth={1.3} 
        >
          <Button 
            onclick={() => accessStore.init()}
            variant="outline" 
            class="h-7 mt-2 rounded-lg transition-colors"
          >
            <AppIcon name="refresh-cw" />
            Réessayer
          </Button> 
        </Empty>
      </div>
    {:else}
      <!-- All tabs mounted but hidden with opacity transition to prevent flash -->
      <div class="relative h-full">
        <div class="absolute inset-0 transition-opacity duration-200 {accessStore.activeTabId === 'users' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}">
          <UsersManagement />
        </div>
        <div class="absolute inset-0 transition-opacity duration-200 {accessStore.activeTabId === 'groups' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}">
          <GroupsManagement />
        </div>
        <div class="absolute inset-0 transition-opacity duration-200 {accessStore.activeTabId === 'roles' ? 'opacity-100 z-10' : 'opacity-0 z-0 pointer-events-none'}">
          <RolesManagement />
        </div>
      </div>
    {/if}

  </div>
</div>

