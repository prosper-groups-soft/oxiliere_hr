<script lang="ts">
  import { slide } from "svelte/transition";
  import { Checkbox } from "@/components/ui/checkbox";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { accessStore } from "../../../stores/accessStore.svelte";
  import { 
    getScopeLabel, 
    getActionById 
  } from "../../../constants/access.constants";
  import type { Role, RoleGrant } from "../../../types/access.types";

  interface Props {
    role: Role;
    isSelected: boolean;
    isExpanded: boolean;
    expandedScopes: Set<string>;
    onToggle: () => void;
    onToggleExpand: (e: Event) => void;
  }

  let { 
    role, 
    isSelected, 
    isExpanded, 
    expandedScopes,
    onToggle, 
    onToggleExpand 
  }: Props = $props();

  function getRoleGrants(roleSlug: string): RoleGrant[] {
    return accessStore.roleGrants.filter(rg => rg.role.slug === roleSlug);
  }

  function toggleScope(scopeKey: string, e: Event) {
    e.stopPropagation();
    const newSet = new Set(expandedScopes);
    if (newSet.has(scopeKey)) {
      newSet.delete(scopeKey);
    } else {
      newSet.add(scopeKey);
    }
    // Update parent state through two-way binding or callback
    expandedScopes = newSet;
  }
</script>


<div class="rounded-lg border border-slate-200 bg-white hover:bg-indigo-50/50 transition-all overflow-hidden shadow-fine">
  <!-- Role Header Row -->
  <div class="flex items-center gap-3 p-3 cursor-pointer" onclick={onToggleExpand} role="none">
    <div onclick={(e) => { e.stopPropagation(); }} role="none">
      <Checkbox 
        id="role-{role.slug}" 
        checked={isSelected} 
        onCheckedChange={onToggle}
        class="bg-white data-[state=checked]:bg-indigo-600 data-[state=checked]:border-indigo-600 h-4.5 w-4.5 rounded-sm shrink-0 cursor-pointer"
      />
    </div>
    <div class="flex-1 flex flex-row min-w-0 items-center">
      <p class="text-[0.875rem] font-medium truncate flex-2 pr-3 border-r border-slate-200">
        {role.name}
      </p>
      <p class="text-[0.875rem] text-muted-foreground truncate flex-1 pl-3">
        {role.slug}
      </p>
    </div>
    <!-- Expand Button -->
    <button
      class="p-1.5 rounded-md hover:bg-slate-100 transition-colors shrink-0"
      class:text-indigo-600={isExpanded}
      class:text-slate-400={!isExpanded}
      onclick={onToggleExpand}
      title="Voir les permissions"
    >
      <AppIcon 
        name="chevron-down" 
        size={17} 
        class="transition-transform duration-200 {isExpanded ? 'rotate-180' : ''}" 
      />
    </button>
  </div>
  
  <!-- Permissions Details (Expandable) -->
  {#if isExpanded}
    {@const grants = getRoleGrants(role.slug)}
    <div class="p-3" transition:slide={{ duration: 200 }}>
      {#if grants.length > 0}
        <div class="space-y-1 bg-white hover:bg-white! rounded-md p-2 border border-slate-100">
          <p class="text-[0.87rem] font-medium text-slate-700 uppercase tracking-tight mb-2">Permissions</p>
          {#each grants as grant}
            {@const scopeKey = `${role.slug}-${grant.scope}`}
            {@const scopeLabel = getScopeLabel(grant.scope)}
            {@const isScopeExpanded = expandedScopes.has(scopeKey)}
            {@const filteredCount = grant.actions.filter(id => !id.toLowerCase().includes('a')).length}
            <div class="rounded-md overflow-hidden">
              <!-- Scope Header (Accordion) -->
              <button
                class="w-full flex items-center justify-between px-2 py-1.5 text-left hover:bg-slate-100/50 rounded-md transition-colors cursor-pointer"
                onclick={(e) => toggleScope(scopeKey, e)}
              >
                <div class="flex items-center gap-2">
                  <AppIcon 
                    name="chevron-down" 
                    size={16} 
                    class="text-slate-400 transition-transform duration-200 {isScopeExpanded ? 'rotate-180' : ''}" 
                  />
                  <span class="text-[0.87rem] font-medium text-slate-800">{scopeLabel}</span>
                </div>
                <span class="text-[0.78rem] font-medium bg-slate-100 px-3 py-0.5 rounded-full">
                  {filteredCount} permission{filteredCount > 1 ? 's' : ''}
                </span>
              </button>
              
              <!-- Actions (Expandable) -->
              {#if isScopeExpanded}
                {@const displayActions = grant.actions.filter(id => !id.toLowerCase().includes('a'))}
                <div class="mt-2 ml-7 px-2 py-0 space-y-1.5" transition:slide={{ duration: 150 }}>
                  {#each displayActions as actionId}
                    {@const actionDef = getActionById(actionId)}
                    <div class="flex items-center gap-2 text-[0.85rem] text-slate-600">
                      <span class="w-1 h-1 rounded-full bg-slate-300"></span>
                      <span class="text-[0.88rem]">{actionDef?.label ?? actionId}</span>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <p class="text-[0.875rem] text-slate-500">Aucune permission définie pour ce rôle</p>
      {/if}
    </div>
  {/if}
</div>

