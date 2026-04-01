<script lang="ts">
  import { Button } from '@/components/ui/button';
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { Role, RoleGrant } from '$lib/features/admin/access/types/access.types';

  interface Props {
    role: Role;
    grants: RoleGrant[];
    onExplore: (role: Role) => void;
  }

  const { role, grants, onExplore }: Props = $props();
</script>


<div class="group/row flex items-center min-h-16 py-2 px-6 bg-white border-b border-slate-100 hover:bg-slate-50/80 transition-colors last:border-0">
  <!-- Role Name -->
  <div class="w-[20%] pr-4 flex items-center gap-3">
    <div class="h-8 w-8 rounded-full bg-amber-50 flex items-center justify-center border border-amber-100">
      <AppIcon name="award" size={14} class="text-amber-600" />
    </div>
    <span class="text-[0.88rem] text-slate-900 font-semibold truncate leading-tight group-hover/row:text-amber-700 transition-colors border-b-0">
      {role.name}
    </span>
  </div>
  
  <!-- Slug -->
  <div class="w-[20%] pr-4">
    <code class="text-[0.75rem] font-mono bg-slate-100 text-slate-500 px-2 py-1 rounded border border-slate-200">
      {role.slug}
    </code>
  </div>
  
  <!-- Scopes Array -->
  <div class="w-[45%] pr-4">
    <div class="flex flex-wrap gap-1.5 py-1">
      {#each grants as rg}
        <Badge variant="outline" class="text-[0.65rem] bg-indigo-50/50 text-indigo-700 border-indigo-100/60 uppercase tracking-tighter shadow-none">
          {rg.scope} <span class="text-indigo-400 ml-1">[{rg.actions.join('')}]</span>
        </Badge>
      {/each}
      {#if grants.length === 0}
        <span class="text-slate-400 text-[0.75rem] italic flex items-center gap-1.5"><AppIcon name="alert-circle" size={12}/> Limité (Aucun accès)</span>
      {/if}
    </div>
  </div>
  
  <!-- Actions -->
  <div class="w-[15%] flex justify-end">
     <Button 
      variant="outline" 
      size="sm" 
      class="h-8 px-3 text-[0.75rem] font-medium border-slate-200 text-slate-500 shadow-none cursor-pointer hover:text-indigo-600 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all opacity-0 group-hover/row:opacity-100"
      onclick={() => onExplore(role)}
    >
      <AppIcon name="settings-2" size={14} class="mr-1.5" />
      Explorer
    </Button>
  </div>
</div>

