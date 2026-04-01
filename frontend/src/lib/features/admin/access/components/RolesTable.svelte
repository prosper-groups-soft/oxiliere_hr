<script lang="ts">
  import RoleRow from './views/RoleRow.svelte';
  import type { 
    Role, 
    RoleGrant 
  } from '$lib/features/admin/access/types/access.types';

  interface Props {
    roles: Role[];
    getGrantsForRole: (roleSlug: string) => RoleGrant[];
    onExplore: (role: Role) => void;
  }

  const { roles, getGrantsForRole, onExplore }: Props = $props();
</script>


<div class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col">
  <div class="flex items-center h-10 px-6 bg-slate-50/80 border-b border-slate-200">
    <div class="w-[20%] text-[0.75rem] font-bold text-slate-500 uppercase tracking-wider">Rôle système</div>
    <div class="w-[20%] text-[0.75rem] font-bold text-slate-500 uppercase tracking-wider">Référence interne</div>
    <div class="w-[45%] text-[0.75rem] font-bold text-slate-500 uppercase tracking-wider">Autorisations (Scopes)</div>
    <div class="w-[15%] text-right text-[0.75rem] font-bold text-slate-500 uppercase tracking-wider">Configuration</div>
  </div>
  
  <div class="flex flex-col">
    {#each roles as role}
      {@const grants = getGrantsForRole(role.slug)}
      <RoleRow {role} {grants} {onExplore} />
    {/each}
  </div>
</div>

