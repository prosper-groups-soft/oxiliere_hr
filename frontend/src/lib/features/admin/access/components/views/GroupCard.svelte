<script lang="ts">
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import type { Group } from '$lib/features/admin/access/types/access.types';

  interface Props {
    group: Group;
    onEdit: (group: Group) => void;
    onSync: (slug: string) => void;
    onDelete: (slug: string) => void;
  }

  const { group, onEdit, onSync, onDelete }: Props = $props();
</script>


<div class="group relative bg-white rounded-xl border border-indigo-100 p-5 transition-all duration-300 hover:shadow-fine hover:border-indigo-600/20 flex flex-col min-h-[180px]">
  <!-- Header -->
  <div class="flex items-start justify-between mb-4">
    <div class="flex items-center gap-3">
      <div class="h-10 w-10 rounded-lg bg-indigo-50 flex items-center justify-center border border-indigo-100 group-hover:bg-indigo-600 transition-colors">
        <AppIcon name="shield" size={20} class="text-indigo-600 group-hover:text-white transition-colors" />
      </div>
      <div>
        <h4 class="text-[0.94rem] font-bold text-slate-900 leading-tight border-b-0">
          {group.name}
        </h4>
        <div class="text-[0.838rem] text-slate-500 mt-0.5">
          {group.slug}
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
      <DropdownMenu.Content align="end" class="w-48 p-1 bg-white shadow-fine border-slate-100 rounded-lg">
        <DropdownMenu.Item 
          onclick={() => onEdit(group)}
          class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-slate-800 cursor-pointer rounded-md hover:bg-slate-50 transition-colors"
        >
          <AppIcon name="edit" size={15} class="text-slate-500" />
          <span>Modifier le groupe</span>
        </DropdownMenu.Item>
        <DropdownMenu.Item 
          onclick={() => onSync(group.slug)}
          class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-slate-800 cursor-pointer rounded-md hover:bg-slate-50 transition-colors"
        >
          <AppIcon name="refresh-cw" size={15} class="text-slate-500" />
          <span>Sync. des membres</span>
        </DropdownMenu.Item>
        <DropdownMenu.Separator class="bg-slate-50 my-1" />
        <DropdownMenu.Item 
          onclick={() => onDelete(group.slug)}
          class="flex items-center gap-2 px-2 py-1.5 text-[0.82rem] text-red-600 cursor-pointer rounded-md hover:bg-red-50/50! hover:text-red-700! transition-colors"
        >
          <AppIcon name="trash" size={15} class="text-red-600" />
          <span>Supprimer</span>
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>

  <!-- Roles Body -->
  <div class="flex-1 mt-2">
    <span class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-tight block mb-2">Rôles assignés ({group.roles.length})</span>
    <div class="flex flex-wrap gap-1.5">
      {#each group.roles as role}
        <Badge class="bg-slate-100 text-slate-700 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-700 text-[0.74rem] font-medium transition-colors rounded-full">
          {role.name}
        </Badge>
      {/each}
      {#if group.roles.length === 0}
        <span class="text-[0.8rem] text-slate-500">Aucun rôle</span>
      {/if}
    </div>
  </div>
</div>

