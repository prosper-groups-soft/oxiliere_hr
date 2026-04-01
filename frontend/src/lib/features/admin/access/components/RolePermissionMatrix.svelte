<script lang="ts">
	import { accessStore } from '../stores/accessStore.svelte';
	import { Checkbox } from '@/components/ui/checkbox';
	import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
	import type { Role, RoleGrant } from '../types/access.types';
	import { onMount } from 'svelte';
	import { notification } from '@/stores/notification.svelte';
	import Empty from '@/components/shared/containers/empty/Empty.svelte';

	interface Props {
		role: Role;
	}

	let { role }: Props = $props();

	// Actions column definition
	const actions = [
		{ id: 'r', label: 'Lire' },
		{ id: 'w', label: 'Écrire' },
		{ id: 'u', label: 'Modifier' },
		{ id: 'd', label: 'Supprimer' },
		{ id: 'a', label: 'Admin' }
	];

	let isLoading = $state(false);

	onMount(async () => {
		isLoading = true;
		if (accessStore.scopes.length === 0) await accessStore.fetchScopes();
		if (accessStore.roleGrants.length === 0) await accessStore.fetchRoleGrants();
		isLoading = false;
	});

	function getRoleGrant(scope: string): RoleGrant | undefined {
		return accessStore.roleGrants.find(rg => rg.role.slug === role.slug && rg.scope === scope);
	}

	function hasPermission(scope: string, action: string): boolean {
		const rg = getRoleGrant(scope);
		return rg ? rg.actions.includes(action) : false;
	}

	async function togglePermission(scope: string, action: string) {
		const rg = getRoleGrant(scope);
		let updatedActions = rg ? [...rg.actions] : [];

		if (updatedActions.includes(action)) {
			updatedActions = updatedActions.filter(a => a !== action);
		} else {
			updatedActions.push(action);
		}

		try {
			if (rg) {
				if (updatedActions.length === 0) {
					// Delete role grant if no actions left
					await accessStore.deleteRoleGrant(rg.id);
				} else {
					// Update existing role grant
					await accessStore.updateRoleGrant(rg.id, updatedActions);
				}
			} else if (updatedActions.length > 0) {
				// Create new role grant
				await accessStore.createRoleGrant({
					role: role.slug,
					scope: scope,
					actions: updatedActions
				});
			}
		} catch (e: any) {
			notification.toast.error("Échec de la mise à jour des permissions du rôle.");
		}
	}
</script>


<div class="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm max-h-[60vh] overflow-y-auto">
	<Table>
		<TableHeader class="bg-slate-50/50 sticky top-0 z-10 shadow-sm">
			<TableRow>
				<TableHead class="w-[180px] text-[0.7rem] font-bold uppercase tracking-wider text-slate-500">Scope</TableHead>
				{#each actions as action}
					<TableHead class="text-center text-[0.7rem] font-bold uppercase tracking-wider text-slate-500">
						{action.label}
					</TableHead>
				{/each}
			</TableRow>
		</TableHeader>
		<TableBody>
			{#each accessStore.scopes as scope}
				<TableRow class="hover:bg-slate-50/30 transition-colors">
					<TableCell class="font-medium text-slate-700 py-2.5 text-[0.8rem]">
						<div class="flex items-center gap-1.5">
							<div class="w-1.5 h-1.5 rounded-full bg-amber-400"></div>
							{scope}
						</div>
					</TableCell>
					{#each actions as action}
						<TableCell class="text-center py-2.5">
							<div class="flex justify-center">
								<Checkbox 
									checked={hasPermission(scope, action.id)} 
									onCheckedChange={() => togglePermission(scope, action.id)}
									class="border-slate-300 data-[state=checked]:bg-amber-600 data-[state=checked]:border-amber-600"
								/>
							</div>
						</TableCell>
					{/each}
				</TableRow>
			{/each}
		</TableBody>
	</Table>
	
	{#if accessStore.scopes.length === 0 && !isLoading}
		<div class="p-12 flex justify-center items-center">
			<Empty 
				title="Aucun scope"
				description="Aucun scope de permission n'est configuré dans le système."
				icon="key"
				iconSize={28}
			/>
		</div>
	{/if}
</div>

