<script lang="ts">
  import { fade } from 'svelte/transition';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import SearchBar from '@/components/shared/elements/SearchBar.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import GroupCard from '../groups/GroupCard.svelte';
  import GroupSheet from '../sheets/group-sheet/GroupSheet.svelte';
  import type { Group } from '../../types/access.types';
  import { notification } from "@/stores/notification.svelte";
  import { getFriendlyErrorMessage } from "@/constants/errors";
  import { 
    guardSystemGroupDelete, 
    guardSystemGroupDeleteWarning 
  } from '../../utils/access-guards';
  import { 
    useGroupsQuery, 
    useDeleteGroupMutation 
  } from '../../queries/accessQueries.svelte';

  
  // TanStack Query
  const groupsQuery = useGroupsQuery();
  const deleteGroupMutation = useDeleteGroupMutation();

  // Local state
  let searchQuery = $state('');
  let isGroupSheetOpen = $state(false);
  let selectedGroup = $state<Group | null>(null);


  // Derived: Filtered groups based on search
  const filteredGroups = $derived.by(() => {
    const groups = $groupsQuery.data ?? [];
    if (!searchQuery.trim()) return groups;
    const query = searchQuery.toLowerCase();
    return groups.filter((group: Group) => 
      group.name.toLowerCase().includes(query) || 
      group.slug.toLowerCase().includes(query)
    );
  });


  // View state for UI
  const viewState = $derived.by(() => {
    if ($groupsQuery.isLoading) return 'initial-loading';
    if (filteredGroups.length > 0) return 'content';
    return 'empty';
  });

  
  function openGroupSheet(group: Group | null = null) {
    selectedGroup = group;
    isGroupSheetOpen = true;
  }


  async function handleDeleteGroup(group: Group) {
    // Guard 3: Empêcher la suppression d'un groupe système avec membres
    const guardCheck = guardSystemGroupDelete(group.slug, group.member_count || 0);
    
    if (!guardCheck.canProceed) {
      notification.toast.error(guardCheck.message!);
      return;
    }

    // Guard 3b: Avertissement pour les groupes système (même sans membres)
    const warningCheck = guardSystemGroupDeleteWarning(group.slug);
    const confirmMessage = warningCheck.warning 
      ? `${warningCheck.warning}\n\nÊtes-vous sûr de vouloir supprimer ce groupe ? Cette action est irréversible.`
      : 'Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action est irréversible.';

    notification.confirm({
      title: 'Supprimer le groupe',
      message: confirmMessage,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: async () => {
        try {
          await $deleteGroupMutation.mutateAsync(group.slug);
          notification.toast.success("Groupe supprimé.");
        } catch (e: any) {
          notification.toast.error(getFriendlyErrorMessage(e));
        }
      }
    });
  }
</script>


<div class="flex flex-col h-full px-2 py-3">

  <!-- Header with search and create button -->
  <div class="flex items-center gap-3 pb-5 pr-8">
    <div class="flex-1">
      <SearchBar 
        bind:value={searchQuery} 
        placeholder="Rechercher un groupe..." 
        class="w-125"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
        iconSize={22}
        onClear={() => searchQuery = ""}
      />
    </div>
    
    <Button 
      size="sm" 
      class="h-7.5 px-3 text-[0.86rem] bg-indigo-600 hover:bg-indigo-700 text-white shadow-fine transition-all cursor-pointer"
      onclick={() => openGroupSheet()}
    >
      <AppIcon name="plus" size={17} />
      Créer un groupe
    </Button>
  </div>

  <!-- Grid -->
  <div class="flex-1 overflow-y-auto">
    <div class="min-h-full flex flex-col items-center justify-start gap-4">
      {#if viewState === 'initial-loading'}
        <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
          <AnimateSpin text="Chargement des groupes" />
        </div>
      {:else if viewState === 'content'}
        <div in:fade={{ duration: 200 }} class="w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-7 pr-8">
          {#each filteredGroups as group (group.slug)}
            <GroupCard
              {group}
              onEdit={() => openGroupSheet(group)}
              onDelete={() => handleDeleteGroup(group)}
            />
          {/each}
        </div>
      {:else}
        {@const hasAnyGroups = ($groupsQuery.data ?? []).length > 0}
        <div class="flex-1 flex items-center" in:fade={{ duration: 200, delay: 50 }}>
          <Empty 
            icon={hasAnyGroups ? "search-x" : "shield-off"}
            title={hasAnyGroups ? "Aucun résultat" : "Aucun groupe"}
            description={hasAnyGroups 
              ? "Aucun groupe ne correspond à votre recherche." 
              : "Commencez par créer votre premier groupe de sécurité."}
            iconSize={28}
            iconStrokeWidth={1.3}
          />
        </div>
      {/if}
    </div>
  </div>
</div>


<!-- Sheet -->
<GroupSheet 
  bind:open={isGroupSheetOpen} 
  group={selectedGroup} 
/>

