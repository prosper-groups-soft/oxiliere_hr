<script lang="ts">
  import { fade } from 'svelte/transition';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import SearchBar from '@/components/shared/elements/SearchBar.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import GroupCard from './views/GroupCard.svelte';
  import type { Group } from '$lib/features/admin/access/types/access.types';

  interface Props {
    groups: Group[];
    onEdit: (group: Group) => void;
    onSync: (slug: string) => void;
    onDelete: (slug: string) => void;
    onCreate: () => void;
  }

  const { groups, onEdit, onSync, onDelete, onCreate }: Props = $props();

  let searchQuery = $state('');

  const filteredGroups = $derived.by(() => {
    if (!searchQuery.trim()) return groups;
    const query = searchQuery.toLowerCase();
    return groups.filter(group => 
      group.name.toLowerCase().includes(query) || 
      group.slug.toLowerCase().includes(query)
    );
  });
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
      onclick={onCreate}
    >
      <AppIcon name="plus" size={17} />
      Créer un groupe
    </Button>
  </div>

  <!-- Grid -->
  <div class="flex-1 overflow-y-auto">
    <div in:fade={{ duration: 200 }} class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {#each filteredGroups as group}
        <GroupCard {group} {onEdit} {onSync} {onDelete} />
      {/each}
      
      {#if filteredGroups.length === 0 && groups.length > 0}
        <div class="col-span-full">
          <Empty 
            icon="search" 
            title="Aucun résultat" 
            description="Aucun groupe ne correspond à votre recherche." 
          />
        </div>
      {:else if groups.length === 0}
        <div class="col-span-full">
          <Empty 
            icon="shield-off" 
            title="Aucun groupe" 
            description="Commencez par créer votre premier groupe de sécurité." 
          />
        </div>
      {/if}
    </div>
  </div>
</div>

