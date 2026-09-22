<script lang="ts">
  import { Checkbox } from '@/components/ui/checkbox';
  import type { Role } from '../../types/access.types';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import { 
    PERMISSION_ACTIONS, 
    getScopeLabel,
  } from '../../constants/access.constants';
  import SelectableItem from '@/hr/components/shared/items/SelectableItem.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';

  interface Props {
    role: Role;
    scopes: string[];
    permissionsMap: Map<string, string[]>;
    isLocked: boolean;
    isLoading: boolean;
    onToggleRow: (scope: string, shouldSelect: boolean) => void;
    onToggleColumn: (actionId: string, shouldSelect: boolean) => void;
    onTogglePermission: (scope: string, actionId: string, checked: boolean) => void;
  }

  let { 
    role, 
    scopes, 
    permissionsMap, 
    isLocked, 
    isLoading,
    onToggleRow,
    onToggleColumn,
    onTogglePermission
  }: Props = $props();

  const actions = PERMISSION_ACTIONS;

  function isRowFullySelected(scope: string): boolean {
    const currentActions = permissionsMap.get(scope) || [];
    return actions.every(action => currentActions.includes(action.id));
  }

  function isColumnFullySelected(actionId: string): boolean {
    if (scopes.length === 0) return false;
    return scopes.every(scope => {
      const currentActions = permissionsMap.get(scope) || [];
      return currentActions.includes(actionId);
    });
  }
</script>


<div class="flex-1 flex flex-col min-h-0 overflow-hidden">
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center bg-white/50">
      <AnimateSpin text="" />
    </div>
  {:else if scopes.length === 0}
    <div class="flex-1 flex justify-center items-center">
      <Empty 
        title="Aucun scope"
        description="Aucun scope de permission n'est configuré dans le système."
        icon="key"
        iconSize={28}
        iconStrokeWidth={1.3}
      />
    </div>
  {:else}
    <!-- Header -->
    <div class="flex-none flex bg-slate-50/80 border-b border-slate-200 sticky top-0 z-10 h-9">
      <div class="w-[280px] px-3 py-2 text-[0.75rem] text-slate-600 uppercase font-medium flex items-center border-r border-slate-200 shrink-0">
        Module
      </div>
      {#each actions as action}
        <div class="flex-1 min-w-[80px] px-3 py-2 flex items-center justify-center">
          <span 
            class="text-[0.75rem] text-slate-600 uppercase font-medium cursor-pointer hover:text-indigo-500 transition-colors select-none"
            onclick={() => onToggleColumn(action.id, !isColumnFullySelected(action.id))}
            role="none"
          >
            {action.label}
          </span>
        </div>
      {/each}
    </div>

    <!-- Body with rows filling available space -->
    <div class="flex-1 flex flex-col overflow-auto">
      {#each scopes as scope}
        <div class="flex flex-1 border-b border-slate-100 last:border-0 hover:bg-slate-50/30 transition-colors min-h-[40px]">
          <!-- Scope cell -->
          <div class="w-[280px] p-0 shrink-0 border-r border-slate-100">
            <SelectableItem
              id="scope-{scope}"
              title={getScopeLabel(scope)}
              checked={isRowFullySelected(scope)}
              onToggle={() => onToggleRow(scope, !isRowFullySelected(scope))}
              disabled={isLocked}
              class="h-full w-full rounded-none border-0"
            />
          </div>

          <!-- Action cells -->
          {#each actions as action}
            {@const isChecked = permissionsMap.get(scope)?.includes(action.id) ?? false}
            <div class="flex-1 min-w-[80px] flex items-center justify-center">
              <div class="flex items-center justify-center w-full h-full hover:bg-slate-50/50 transition-colors">
                <Checkbox 
                  checked={isChecked}
                  onCheckedChange={(checked) => onTogglePermission(scope, action.id, checked)}
                  disabled={isLocked}
                  class="border-slate-300 transition-all checked:bg-indigo-600 checked:border-indigo-600 cursor-pointer"
                />
              </div>
            </div>
          {/each}
        </div>
      {/each}
    </div>
  {/if}
</div>
