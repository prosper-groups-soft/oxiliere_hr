<script lang="ts">
	import accessStore from '../../stores/accessStore.svelte';
	import { Checkbox } from '@/components/ui/checkbox';
	import { 
		Table, 
		TableBody, 
		TableCell, 
		TableHead, 
		TableHeader, 
		TableRow 
	} from '@/components/ui/table';
	import { onMount } from 'svelte';
	import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
	import type { User } from '../../../settings/types/user.types';

	interface Props {
		user: User;
	}

	let { user }: Props = $props();

	// Actions column definition
	const actions = [
		{ id: 'r', label: 'Lire', color: 'text-blue-600' },
		{ id: 'w', label: 'Écrire', color: 'text-green-600' },
		{ id: 'u', label: 'Modifier', color: 'text-amber-600' },
		{ id: 'd', label: 'Supprimer', color: 'text-red-600' },
		{ id: 'a', label: 'Admin', color: 'text-purple-600' }
	];

	// Local state for user grants (to avoid too many API calls while clicking)
	let userGrants = $state<any[]>([]);
	let isLoading = $state(false);

	onMount(async () => {
		isLoading = true;
		await accessStore.fetchScopes();
		await fetchUserGrants();
		isLoading = false;
	});

	// Refetch when user changes
	$effect(() => {
		if (user.id) {
			fetchUserGrants();
		}
	});

	async function fetchUserGrants() {
		// Use the grants endpoint filtered by user_id
		const response = await fetch(`/api/access/grants?user_id=${user.id}`).then(r => r.json());
		userGrants = response.results || [];
	}

	// Reactive permissions map - recalculates when userGrants changes
	const permissionsMap = $derived.by(() => {
		const map = new Map<string, string[]>();
		userGrants.forEach(g => {
			map.set(g.scope, [...g.actions]);
		});
		return map;
	});

	async function togglePermission(scope: string, action: string) {
		const grant = userGrants.find(g => g.scope === scope);
		let updatedActions = grant ? [...grant.actions] : [];

		if (updatedActions.includes(action)) {
			updatedActions = updatedActions.filter(a => a !== action);
		} else {
			updatedActions.push(action);
		}

		try {
			if (grant) {
				if (updatedActions.length === 0) {
					// Delete grant if no actions left
					await fetch(`/api/access/grants/${grant.id}`, { method: 'DELETE' });
				} else {
					// Update existing grant
					await fetch(`/api/access/grants/${grant.id}`, {
						method: 'PUT',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ actions: updatedActions })
					});
				}
			} else if (updatedActions.length > 0) {
				// Create new grant
				await fetch(`/api/access/grants`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						user_id: user.id,
						scope: scope,
						actions: updatedActions
					})
				});
			}
			await fetchUserGrants();
		} catch (e) {
			console.error("Failed to toggle permission", e);
		}
	}
</script>


<div class="rounded-xl border border-slate-20 bg-white overflow-hidden shadow-sm">
	<Table>
		<TableHeader class="bg-slate-50/50">
			<TableRow>
				<TableHead class="w-[180px] text-[0.75rem] font-bold uppercase tracking-wider text-slate-500">Module / Scope</TableHead>
				{#each actions as action}
					<TableHead class="text-center text-[0.7rem] font-bold uppercase tracking-wider text-slate-500">
						{action.label}
					</TableHead>
				{/each}
			</TableRow>
		</TableHeader>
		<TableBody>
			{#each accessStore.scopes as scope}
				<TableRow class="hover:bg-slate-50/50 transition-colors">
					<TableCell class="font-medium text-slate-700 py-3">
						<div class="flex items-center gap-2">
							<div class="w-1.5 h-1.5 rounded-full bg-indigo-400"></div>
							{scope}
						</div>
					</TableCell>
					{#each actions as action}
						{@const isChecked = permissionsMap.get(scope)?.includes(action.id) ?? false}
						<TableCell class="text-center py-3">
							<div class="flex justify-center">
								<Checkbox 
									checked={isChecked}
									onCheckedChange={() => togglePermission(scope, action.id)}
									class="border-slate-300 data-[state=checked]:bg-indigo-600 data-[state=checked]:border-indigo-600"
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
				iconStrokeWidth={1.3}
			/>
		</div>
	{/if}
</div>

