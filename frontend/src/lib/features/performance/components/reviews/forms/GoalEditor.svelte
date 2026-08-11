<script lang="ts">
	import { fade } from 'svelte/transition';
	import { Button } from '@/components/ui/button';
	import { Input } from '@/components/ui/input';
	import { Label } from '@/components/ui/label';
	import * as Select from '@/components/ui/select';
	import { Switch } from '@/components/ui/switch';
	import { GOAL_TYPE_LABELS } from '../../../constants';
	import type { Goal, PerformanceGoalType } from '../../../types/types';

  
	let {
		goals = $bindable([] as Goal[]),
		mode = 'employee', // 'employee' | 'manager' | 'template'
		totalBudget = 1, // poids alloué à cette catégorie (ex: 0.6 pour objectifs)
		editable = true, // false = mode sélection simplifié (ReviewSheet)
		selectionOnly = false,
	}: {
		goals?: Goal[];
		mode?: 'employee' | 'manager' | 'template';
		totalBudget?: number;
		editable?: boolean;
		selectionOnly?: boolean;
	} = $props();

	const isTemplate = $derived(mode === 'template');

	// --- Mode sélection (non-éditable) ---
	const selectedGoals = $derived(goals.filter(g => g.selected));
	const selectedCount = $derived(selectedGoals.length);
	const hasSelection = $derived(selectedCount > 0);

	// Redistribue les poids quand la sélection change
	$effect(() => {
		if (!editable) {
			const count = goals.filter(g => g.selected).length;
			if (count === 0) {
				if (goals.length === 0) return;
				goals = goals.map(g => ({ ...g, weight: 0 }));
				return;
			}
			const equalWeight = totalBudget / count;
			let needsUpdate = false;
			const newGoals = goals.map(g => {
				const w = g.selected ? equalWeight : 0;
				if (Math.abs((g.weight ?? 0) - w) > 0.001) needsUpdate = true;
				return { ...g, weight: w };
			});
			if (needsUpdate) goals = newGoals;
		}
	});

	// --- Mode éditable ---
	const goalCount = $derived(goals.length);
	const hasGoals = $derived(goalCount > 0);
	const allocatedSum = $derived(editable
		? goals.reduce((sum, g) => sum + (g.weight ?? 0), 0)
		: selectedGoals.reduce((sum, g) => sum + (g.weight ?? 0), 0)
	);
	const budgetTotal = $derived(totalBudget);
	const remainingBudget = $derived(parseFloat((budgetTotal - allocatedSum).toFixed(4)));
	const budgetPercentage = $derived(Math.round(budgetTotal * 100));
	const allocatedPercentage = $derived(Math.round(allocatedSum * 100));
	const remainingPercentage = $derived(Math.round(remainingBudget * 100));
	const isOverBudget = $derived(remainingBudget < -0.001);

	/** Auto-distribue les poids équitablement selon le budget total */
	function redistributeWeights() {
		if (!editable) {
			const selected = goals.filter(g => g.selected);
			const count = selected.length;
			if (count === 0) return;
			const equalWeight = totalBudget / count;
			goals = goals.map(g => g.selected ? { ...g, weight: equalWeight } : { ...g, weight: 0 });
			return;
		}
		const count = goals.length;
		if (count === 0) return;
		const equalWeight = parseFloat((totalBudget / count).toFixed(4));
		goals = goals.map((g) => ({ ...g, weight: equalWeight }));
	}

	function addGoal() {
		const newIndex = goals.length;
		goals = [...goals, {
			description: '',
			type: 'OBJECTIVE' as PerformanceGoalType,
			weight: 0,
			employee_rating: undefined,
			manager_rating: undefined,
			manager_comment: undefined,
		}];
		redistributeWeights();
		// Déplier le nouveau bloc
		const next = new Set(collapsedGoals);
		next.delete(newIndex);
		collapsedGoals = next;
	}


	function removeGoal(index: number) {
		// Blur l'élément actif pour empêcher le saut de focus
		(document.activeElement as HTMLElement)?.blur();
		goals = goals.filter((_, i) => i !== index);
		redistributeWeights();
	}

	function updateField(index: number, field: keyof Goal, value: unknown) {
		const newGoals = goals.map((g) => ({ ...g }));
		newGoals[index] = { ...newGoals[index], [field]: value };

		// Auto-ajustement des autres poids quand on modifie le weight
		if (field === 'weight' && newGoals.length > 1) {
			const newWeight = (value as number) ?? 0;
			const otherSum = newGoals.reduce((sum, g, i) => (i !== index ? sum + (g.weight ?? 0) : sum), 0);

			if (otherSum > 0.001) {
				const newOtherSum = totalBudget - newWeight;
				if (newOtherSum >= -0.001) {
					newGoals.forEach((g, i) => {
						if (i !== index && otherSum > 0) {
							const proportion = (g.weight ?? 0) / otherSum;
							g.weight = parseFloat((newOtherSum * proportion).toFixed(4));
						}
					});
				}
			} else {
				const equalOther = parseFloat(((totalBudget - newWeight) / (newGoals.length - 1)).toFixed(4));
				newGoals.forEach((g, i) => {
					if (i !== index) g.weight = equalOther;
				});
			}
		}

		goals = newGoals;
	}

	// Collapse state for each goal - tous pliés par défaut
	let collapsedGoals = $state<Set<number>>(new Set());

	// Flag non-réactif pour n'initialiser qu'une seule fois
	let _goalsInitialized = false;

	// Quand les goals sont chargés (asynchrone), tout plier immédiatement
	$effect(() => {
		if (goals.length > 0 && !_goalsInitialized) {
			collapsedGoals = new Set(goals.map((_, i) => i));
			_goalsInitialized = true;
		}
	});

	function toggleCollapse(i: number) {
		const next = new Set(collapsedGoals);
		if (next.has(i)) {
			next.delete(i);
		} else {
			next.add(i);
		}
		collapsedGoals = next;
	}

	function isCollapsed(i: number): boolean {
		return collapsedGoals.has(i);
	}

	const ratingField = $derived(mode === 'employee' ? 'employee_rating' as const : 'manager_rating' as const);

	function toggleRating(index: number, n: number) {
		const current = goals[index][ratingField];
		// Cliquer une étoile déjà remplie → remet à zéro
		if (current != null && n <= current) {
			updateField(index, ratingField, undefined);
		} else {
			updateField(index, ratingField, current === n ? undefined : n);
		}
	}

	function getRating(goal: Goal): number | undefined {
		return mode === 'employee' ? goal.employee_rating : goal.manager_rating;
	}
</script>


<div class="space-y-3">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<div class="flex size-7 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
				<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
				</svg>
			</div>
			<Label class="text-[0.875rem] font-medium text-slate-700 cursor-default">
				{isTemplate ? 'Objectifs par défaut' : editable
					? (mode === 'employee' ? 'Objectifs (auto-évaluation)' : "Objectifs (évaluation évaluateur)")
					: (mode === 'employee' ? 'Objectifs (auto-évaluation)' : "Objectifs (évaluation évaluateur)")
				}
			</Label>
			{#if editable && hasGoals}
				<span class="inline-flex items-center justify-center h-5 min-w-5 rounded-full bg-blue-100 px-1.5 text-[0.82rem] font-semibold text-blue-700 tabular-nums">
					{goalCount}
				</span>
			{/if}
			{#if !editable && hasSelection}
				<span class="inline-flex items-center justify-center h-5 min-w-5 rounded-full bg-emerald-100 px-1.5 text-[0.82rem] font-semibold text-emerald-700 tabular-nums">
					{selectedCount} sélectionné{selectedCount > 1 ? 's' : ''}
				</span>
			{/if}
		</div>
		{#if editable}
			<Button
				type="button"
				variant="outline"
				size="sm"
				onmousedown={(e) => e.preventDefault()}
				onclick={addGoal}
				class="h-7 px-2.5 text-[0.82rem] font-medium gap-1 shadow-fine"
			>
				<svg class="size-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
				</svg>
				Ajouter
			</Button>
		{/if}
	</div>

	<!-- Budget bar -->
	{#if editable && hasGoals}
		<div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
			<div class="flex-1 flex items-center gap-2">
				<div class="flex-1 h-2 rounded-full bg-slate-200 overflow-hidden">
					<div
						class="h-full rounded-full transition-all duration-300 {isOverBudget ? 'bg-rose-400' : 'bg-blue-500'}"
						style="width: {Math.min(allocatedSum / totalBudget, 1) * 100}%"
					></div>
				</div>
				<span class="text-[0.82rem] font-semibold text-slate-700 tabular-nums shrink-0">
					{allocatedPercentage}% / {budgetPercentage}%
				</span>
			</div>
			{#if remainingPercentage > 0}
				<span class="text-[0.75rem] text-slate-400 shrink-0">
					<i class="text-blue-500 not-italic">{remainingPercentage}%</i> restant
				</span>
			{:else if isOverBudget}
				<span class="text-[0.75rem] text-rose-500 font-medium shrink-0">
					Dépassement de {Math.abs(remainingPercentage)}%
				</span>
			{:else}
				<span class="text-[0.75rem] text-emerald-600 font-medium shrink-0">
					Budget atteint
				</span>
			{/if}
		</div>
	{/if}

	<!-- Empty state -->
	{#if !hasGoals}
		<div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50 py-8 px-4 transition-colors hover:border-slate-300">
			<div class="flex size-8 items-center justify-center rounded-full bg-blue-50 mb-3">
				<svg class="size-4.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
				</svg>
			</div>
			<p class="text-sm font-medium text-slate-600">Aucun objectif</p>
			<p class="mt-1 text-xs text-slate-400 text-center max-w-48">
				{editable ? "Ajoutez des objectifs à atteindre pour cette période d'évaluation." : "Aucun objectif défini pour cette campagne."}
			</p>
		</div>
	{/if}

	<!-- Mode non-éditable : sélection compacte avec Switch -->
	{#if !editable}
		<div class="space-y-2">
			{#each goals as goal, i (i)}
				{@const isSelected = goal.selected ?? false}
				{@const rating = getRating(goal)}
				<div
					class="flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all {isSelected ? 'border-blue-200 bg-blue-50/40' : 'border-slate-200 bg-white hover:border-slate-300'}"
				>
					{#if selectionOnly}
						<Switch bind:checked={goals[i].selected} />
					{:else}
						<div class="size-10 flex items-center justify-center shrink-0">
							{#if isSelected}
								<svg class="size-4.5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
								</svg>
							{:else}
								<svg class="size-4.5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
								</svg>
							{/if}
						</div>
					{/if}

					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2 flex-wrap">
							<span class="text-[0.875rem] font-medium text-slate-900 truncate">
								{goal.description || 'Objectif sans description'}
							</span>
							<span class="shrink-0 inline-flex items-center rounded-full px-1.5 py-0.5 text-[0.8rem] font-medium {goal.type === 'KPI' ? 'bg-amber-50 text-amber-600' : 'bg-sky-50 text-sky-600'}">
								{GOAL_TYPE_LABELS[goal.type]}
							</span>
							{#if isSelected && goal.weight != null}
								<span class="shrink-0 text-[0.82rem] font-semibold text-blue-500 tabular-nums">
									{Math.round(goal.weight * 100)}%
								</span>
							{/if}
						</div>
					</div>

					<!-- Notes (étoiles) : visibles seulement si sélectionné et pas en mode selectionOnly -->
					{#if isSelected && !selectionOnly}
						<div class="flex items-center gap-0.5 shrink-0">
							{#each [1, 2, 3, 4, 5] as n}
								<button
									type="button"
									onmousedown={(e) => e.preventDefault()}
									onclick={() => toggleRating(i, n)}
									class="size-7 flex items-center justify-center transition-all duration-150 cursor-pointer rounded-md
										{n <= (rating ?? 0)
											? 'text-amber-400 scale-110'
											: 'text-slate-300 bg-slate-100/60 hover:text-amber-300 hover:scale-110'}"
									title="{n}/5"
								>
									<svg class="size-4.5" viewBox="0 0 24 24" fill="currentColor">
										<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
									</svg>
								</button>
							{/each}
						</div>
					{/if}
				</div>
			{/each}
		</div>

	<!-- Mode éditable : design existant avec collapse -->
	{:else}
		{#each goals as goal, i (i)}
			<div
				class="group relative rounded-xl border border-slate-200 bg-white shadow-fine transition-all hover:border-slate-300 overflow-hidden {isCollapsed(i) ? 'cursor-pointer' : ''}"
				class:expanded={!isCollapsed(i)}
				class:collapsed={isCollapsed(i)}
			>
				<!-- Header unique : change d'apparence selon collapsed/expanded -->
				<button
					type="button"
					onclick={() => toggleCollapse(i)}
					class="w-full text-left cursor-pointer group/header focus:outline-none"
					title={isCollapsed(i) ? 'Déplier pour voir les détails' : 'Plier pour réduire'}
				>
					<div
						class="flex items-center gap-2 px-4 py-3"
						class:border-b={!isCollapsed(i)}
						class:border-slate-100={!isCollapsed(i)}
					>
						<div class="flex size-7 items-center justify-center rounded-full bg-blue-600 text-[0.7rem] font-bold text-white shadow-fine shrink-0">
							{i + 1}
						</div>

						<!-- Vue pliée : description + note + poids -->
						<div class="flex-1 flex items-center gap-3 min-w-0" class:hidden={!isCollapsed(i)}>
							<span class="text-[0.875rem] font-medium text-slate-900 truncate">
								{goal.description || 'Nouvel objectif'}
							</span>
							{#if goal.weight != null}
								<span class="text-[0.82rem] font-bold text-blue-500 shrink-0">{Math.round(goal.weight * 100)}%</span>
							{/if}
							{#if goal.employee_rating}
								<span class="flex items-center gap-1 text-[0.75rem] font-medium text-amber-600 shrink-0">
									<svg class="size-3.5" fill="currentColor" viewBox="0 0 20 20">
										<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
									</svg>
									{goal.employee_rating}/5
								</span>
							{/if}
						</div>

						<!-- Vue dépliée : titre court -->
						<span class="flex-1 text-[0.82rem] font-medium text-slate-700" class:hidden={isCollapsed(i)}>Objectif {i + 1}</span>

						<!-- Bouton supprimer -->
						<span
							onmousedown={(e) => { e.preventDefault(); e.stopPropagation(); }}
							onclick={(e) => { e.preventDefault(); e.stopPropagation(); removeGoal(i); }}
							class="flex size-7 items-center justify-center rounded-lg bg-white text-red-400 border border-red-200 hover:bg-red-100 hover:text-red-600 hover:border-red-300 transition-all cursor-pointer shrink-0"
							role="none"
						>
							<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
							</svg>
						</span>

						<!-- Indicateur plier/déplier -->
						<span class="flex items-center gap-1.5 text-slate-400">
							<span class="text-[0.65rem] font-medium uppercase tracking-wider opacity-0 group-hover/header:opacity-100 transition-opacity shrink-0">{isCollapsed(i) ? 'Déplier' : 'Plier'}</span>
							<svg class="size-4 transition-transform {isCollapsed(i) ? '' : 'rotate-180'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</span>
					</div>
				</button>

				<!-- Contenu déplié : toujours dans le DOM, caché par CSS -->
				<div class="p-4 pt-3 space-y-4" class:hidden={isCollapsed(i)} transition:fade={{ duration: 120 }}>
					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">Description</Label>
						<Input
							type="text"
							placeholder="Description de l'objectif"
							value={goal.description}
							oninput={(e) => updateField(i, 'description', (e.currentTarget as HTMLInputElement).value)}
							class="h-9 border-slate-200 bg-white text-[0.875rem] placeholder:text-slate-400 focus:bg-white transition-colors shadow-fine"
						/>
					</div>

					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">Type d'objectif</Label>
						<Select.Root
							type="single"
							value={goal.type}
							onValueChange={(v) => updateField(i, 'type', v as PerformanceGoalType)}
						>
							<Select.Trigger class="h-9 border-slate-200 bg-white text-[0.82rem] font-normal w-full shadow-fine">
								{GOAL_TYPE_LABELS[goal.type]}
							</Select.Trigger>
							<Select.Content class="bg-white border-slate-100 shadow-fine z-100 min-w-32">
								{#each Object.entries(GOAL_TYPE_LABELS) as [value, label]}
									<Select.Item {value} label={label} class="text-[0.82rem]">{label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>

					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">
							Pondération
						</Label>
						<div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
							<input
								type="range"
								min="0"
								max={Math.round(totalBudget * 100)}
								step="5"
								value={Math.round((goal.weight ?? 0) * 100)}
								oninput={(e) => updateField(i, 'weight', parseInt((e.currentTarget as HTMLInputElement).value) / 100)}
								class="flex-1 h-1.5 accent-indigo-500 cursor-pointer"
							/>
							<span class="text-[0.82rem] font-semibold text-indigo-700 tabular-nums min-w-10 text-right">
								{Math.round((goal.weight ?? 0) * 100)}%
							</span>
						</div>
					</div>

					{#if !isTemplate}
					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">
							{mode === 'employee' ? "Note employé (auto-évaluation)" : 'Note manager'}
						</Label>
						<div class="flex items-center gap-1 h-9">
							{#each [1, 2, 3, 4, 5] as n}
								<button
									type="button"
									onmousedown={(e) => e.preventDefault()}
									onclick={() => {
										const field = mode === 'employee' ? 'employee_rating' : 'manager_rating';
										updateField(i, field, (goal[field] === n) ? undefined : n);
									}}
									class="size-8 flex items-center justify-center transition-all duration-150 cursor-pointer rounded-md
										{n <= (mode === 'employee' ? (goal.employee_rating ?? 0) : (goal.manager_rating ?? 0))
											? 'text-amber-400 scale-110'
											: 'text-slate-300 bg-slate-100/60 hover:text-amber-300 hover:scale-110'}"
									title="{n}/5"
								>
									<svg class="size-5" viewBox="0 0 24 24" fill="currentColor">
										<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
									</svg>
								</button>
							{/each}
						</div>
					</div>
					{/if}

					{#if !isTemplate && mode === 'manager'}
						<div class="space-y-1.5">
							<Label for="comment-{i}" class="text-[0.82rem] font-medium text-slate-600">Commentaire</Label>
							<textarea
								id="comment-{i}"
							  placeholder="Commentaire de l'évaluateur sur cet objectif..."
								value={goal.manager_comment ?? ''}
								oninput={(e) => updateField(i, 'manager_comment', (e.currentTarget as HTMLTextAreaElement).value)}
								class="w-full h-16 rounded-lg border border-slate-200 bg-white p-2.5 text-[0.82rem] placeholder:text-slate-400 focus:bg-white focus:border-slate-300 transition-all resize-none shadow-fine"
							></textarea>
						</div>
					{/if}
				</div>
			</div>
		{/each}
	{/if}
</div>
