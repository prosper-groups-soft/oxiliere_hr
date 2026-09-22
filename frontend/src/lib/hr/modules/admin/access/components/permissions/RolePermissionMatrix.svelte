<script lang="ts">
    import accessStore from '../../stores/accessStore.svelte';
    import type { Role } from '../../types/access.types';
    import { 
        getScopeLabel,
        ACTION_HIERARCHY,
        PERMISSION_ACTIONS
    } from '../../constants/access.constants';
    import { isLockedRole } from '../../utils/access-guards';
    import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
    import { notification } from '@/hr/stores/notification.svelte';
    import { getFriendlyErrorMessage } from '@/hr/constants/errors';
    import { Button } from '@/components/ui/button';
    import PermissionMatrixTable from './PermissionMatrixTable.svelte';

    interface Props {
        role: Role;
    }

    let { role }: Props = $props();

    // Rôle verrouillé si c'est un rôle système critique (ex: admin)
    const isLocked = $derived(isLockedRole(role.slug));

    // Configuration des colonnes d'actions
    const actions = PERMISSION_ACTIONS;

    /**
     * Recherche réactive des permissions.
     * Utilisation de $derived.by pour forcer la réévaluation par Svelte 5
     * à chaque modification du tableau accessStore.roleGrants.
     */
    const permissionsMap = $derived.by(() => {
      const map = new Map<string, string[]>();
      accessStore.roleGrants
      .filter((rg: any) => rg.role.slug === role.slug)
      .forEach((rg: any) => {
        map.set(rg.scope, [...rg.actions]);
      });
      return map;
    });

    // Toggle entire row (all actions for a scope)
    async function toggleRow(scope: string, shouldSelect: boolean) {
        if (isLocked) return;
        const rg = accessStore.roleGrants.find(
            (item: any) => item.role.slug === role.slug && item.scope === scope
        );

        try {
            if (shouldSelect) {
                const allActionIds = actions.map(a => a.id);
                if (rg) {
                    await accessStore.updateRoleGrant(rg.id, allActionIds);
                } else {
                    await accessStore.createRoleGrant({
                        role: role.slug,
                        scope: scope,
                        actions: allActionIds
                    });
                }
                notification.toast.success(`Toutes les permissions accordées pour le module "${getScopeLabel(scope)}"`);
            } else {
                if (rg) {
                    await accessStore.deleteRoleGrant(rg.id);
                    notification.toast.success(`Toutes les permissions retirées pour le module "${getScopeLabel(scope)}"`);
                }
            }
        } catch (e) {
            notification.toast.error(getFriendlyErrorMessage(e));
            console.error(e);
        }
    }

    // Toggle entire column (one action for all scopes)
    async function toggleColumn(actionId: string, shouldSelect: boolean) {
        if (isLocked) return;
        const actionLabel = actions.find(a => a.id === actionId)?.label || actionId;
        let affectedCount = 0;
        
        // Calculer toutes les actions à ajouter ou retirer selon la hiérarchie
        const actionsToProcess = shouldSelect 
            ? [actionId, ...getAllDependencies(actionId)]  // Ajouter l'action + dépendances
            : [actionId, ...getAllDependents(actionId)];   // Retirer l'action + dépendants
        const actionsSet = new Set(actionsToProcess);
        
        try {
            for (const scope of accessStore.scopes) {
                const currentActions = permissionsMap.get(scope) || [];
                const rg = accessStore.roleGrants.find(
                    (item: any) => item.role.slug === role.slug && item.scope === scope
                );

                if (shouldSelect) {
                    // Ajouter toutes les actions manquantes
                    const actionsToAdd = actionsToProcess.filter(a => !currentActions.includes(a));
                    if (actionsToAdd.length > 0) {
                        const updatedActions = [...currentActions, ...actionsToAdd];
                        if (rg) {
                            await accessStore.updateRoleGrant(rg.id, updatedActions);
                        } else {
                            await accessStore.createRoleGrant({
                                role: role.slug,
                                scope: scope,
                                actions: updatedActions
                            });
                        }
                        affectedCount++;
                    }
                } else {
                    // Retirer toutes les actions concernées
                    const actionsToRemove = actionsToProcess.filter(a => currentActions.includes(a));
                    if (actionsToRemove.length > 0) {
                        const updatedActions = currentActions.filter(a => !actionsSet.has(a));
                        if (rg) {
                            if (updatedActions.length === 0) {
                                await accessStore.deleteRoleGrant(rg.id);
                            } else {
                                await accessStore.updateRoleGrant(rg.id, updatedActions);
                            }
                        }
                        affectedCount++;
                    }
                }
            }
            
            if (affectedCount > 0) {
                const affectedActions = Array.from(actionsSet).map(a => actions.find(act => act.id === a)?.label || a).join(', ');
                if (shouldSelect) {
                    notification.toast.success(`Permission(s) ${affectedActions} accordée(s) pour ${affectedCount} module${affectedCount > 1 ? 's' : ''}`);
                } else {
                    notification.toast.success(`Permission(s) ${affectedActions} retirée(s) pour ${affectedCount} module${affectedCount > 1 ? 's' : ''}`);
                }
            }
        } catch (e) {
            notification.toast.error(getFriendlyErrorMessage(e));
            console.error(e);
        }
    }

    // Hiérarchie des actions : quand on donne une action, on doit aussi donner ses dépendances
    // Quand on retire une action, on doit retirer tout ce qui dépend d'elle
    function getAllDependencies(actionId: string): string[] {
        const deps = ACTION_HIERARCHY[actionId as keyof typeof ACTION_HIERARCHY];
        if (!deps) return [];
        
        // Récursivement récupérer toutes les dépendances
        const allDeps = new Set<string>(deps);
        deps.forEach(dep => {
            getAllDependencies(dep).forEach(d => allDeps.add(d));
        });
        return Array.from(allDeps);
    }

    // Récupérer toutes les actions qui dépendent de l'action donnée
    function getAllDependents(actionId: string): string[] {
        const dependents: string[] = [];
        for (const [action, deps] of Object.entries(ACTION_HIERARCHY)) {
            if (deps.has(actionId)) {
                dependents.push(action);
                // Récursivement ajouter les dépendants
                dependents.push(...getAllDependents(action));
            }
        }
        return dependents;
    }

    async function togglePermission(scope: string, actionId: string, checked: boolean) {
        if (isLocked) return;
        // Récupération des actions actuelles via la Map réactive
        const currentActions = permissionsMap.get(scope) || [];
        let updatedActions = [...currentActions];

        if (checked) {
            // Ajouter l'action et toutes ses dépendances
            const actionsToAdd = [actionId, ...getAllDependencies(actionId)];
            actionsToAdd.forEach(a => {
                if (!updatedActions.includes(a)) {
                    updatedActions.push(a);
                }
            });
        } else {
            // Retirer l'action et tout ce qui en dépend
            const actionsToRemove = new Set([actionId, ...getAllDependents(actionId)]);
            updatedActions = updatedActions.filter(a => !actionsToRemove.has(a));
        }

        const rg = accessStore.roleGrants.find(
            item => item.role.slug === role.slug && item.scope === scope
        );

        try {
            const actionLabel = actions.find(a => a.id === actionId)?.label || actionId;
            
            // Calculer quelles actions ont réellement changé
            const added = updatedActions.filter(a => !currentActions.includes(a));
            const removed = currentActions.filter(a => !updatedActions.includes(a));
            
            if (rg) {
                if (updatedActions.length === 0) {
                    await accessStore.deleteRoleGrant(rg.id);
                    notification.toast.success(`Permission "${actionLabel}" et dépendances retirées pour le module "${getScopeLabel(scope)}"`);
                } else {
                    await accessStore.updateRoleGrant(rg.id, updatedActions);
                    
                    // Message spécifique selon les changements
                    if (added.length > 0 && removed.length === 0) {
                        const addedLabels = added.map(a => actions.find(act => act.id === a)?.label || a).join(', ');
                        notification.toast.success(`Permission(s) accordée(s) : ${addedLabels}`);
                    } else if (removed.length > 0 && added.length === 0) {
                        const removedLabels = removed.map(a => actions.find(act => act.id === a)?.label || a).join(', ');
                        notification.toast.success(`Permission(s) retirée(s) : ${removedLabels}`);
                    } else {
                        notification.toast.success(`Permissions mises à jour pour "${getScopeLabel(scope)}"`);
                    }
                }
            } else if (updatedActions.length > 0) {
                await accessStore.createRoleGrant({
                    role: role.slug,
                    scope: scope,
                    actions: updatedActions
                });
                const addedLabels = added.map(a => actions.find(act => act.id === a)?.label || a).join(', ');
                notification.toast.success(`Permission(s) accordée(s) : ${addedLabels}`);
            }
        } catch (e) {
            notification.toast.error(getFriendlyErrorMessage(e));
            console.error(e);
        }
    }

    async function handleRestore() {
        if (isLocked) return;
        
        notification.confirm({
            title: "Restaurer les permissions par défaut ?",
            message: `Toutes les permissions personnalisées du rôle "${role.name}" seront supprimées et remplacées par les configurations d'origine. Cette action est irréversible.`,
            type: "danger",
            yesText: "Restaurer",
            noText: "Annuler",
            onYes: async () => {
                try {
                    await accessStore.restoreRoleDefaults(role.slug);
                    notification.toast.success("Permissions restaurées avec succès.");
                } catch (e: any) {
                    notification.toast.error(getFriendlyErrorMessage(e));
                }
            }
        });
    }
</script>


<div class="h-full flex flex-col border border-slate-200 border-t-0 border-l-0 border-r-0 border-b-0 overflow-hidden">
  
  {#if isLocked}
    <div class="h-12 px-2 bg-indigo-50/50 border-b border-indigo-100 flex items-center gap-3">
      <div class="h-8 w-8 rounded-full bg-white flex items-center justify-center shadow-fine border border-indigo-100">
        <AppIcon name="lock" size={15} class="text-indigo-600" />
      </div>
      <div>
        <h4 class="text-[0.82rem] font-semibold text-indigo-900 leading-none">Rôle Système Verrouillé</h4>
        <p class="text-[0.8rem] text-indigo-700/80 mt-0.5">
          Ce rôle est essentiel et ne peut pas être modifié depuis l'interface.
        </p>
      </div>
    </div>
  {/if}

  {#if !isLocked}
    <div class="h-12 px-2 pr-8 bg-slate-50/50 border-b border-slate-200 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="h-8 w-8 rounded-full bg-white flex items-center justify-center shadow-fine border border-slate-200">
          <AppIcon name="shield" size={15} class="text-slate-500" />
        </div>
        <span class="text-[0.8rem] font-bold text-slate-700 uppercase tracking-tight">Configuration des accès</span>
      </div>
      <Button 
        variant="default" 
        size="sm" 
        class="h-7 px-3"
        onclick={handleRestore}
      >
        <AppIcon name="rotate-ccw" size={14} />
        Rétablir les défauts
      </Button>
    </div>
  {/if}

  <PermissionMatrixTable
      {role}
      scopes={accessStore.scopes}
      {permissionsMap}
      {isLocked}
      isLoading={false}
      onToggleRow={toggleRow}
      onToggleColumn={toggleColumn}
      onTogglePermission={togglePermission}
  />

</div>

