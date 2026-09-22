<script lang="ts">
	import { fade } from 'svelte/transition';
	import { Button } from '@/components/ui/button';
	import { Input } from '@/components/ui/input';
	import { Label } from '@/components/ui/label';
	import * as Select from '@/components/ui/select';
	import { Switch } from '@/components/ui/switch';
	import { SKILL_CATEGORY_LABELS } from '../../../constants';
	import type { Skill, SkillCategory } from '../../../types/types';

  
	let {
		skills = $bindable([] as Skill[]),
		mode = 'employee', // 'employee' | 'manager' | 'template'
		totalBudget = 1,    // poids alloué à cette catégorie (ex: 0.4 pour compétences)
		editable = true,    // false = mode sélection simplifié (ReviewSheet)
		selectionOnly = false,
	}: {
		skills?: Skill[];
		mode?: 'employee' | 'manager' | 'template';
		totalBudget?: number;
		editable?: boolean;
		selectionOnly?: boolean;
	} = $props();

	const isTemplate = $derived(mode === 'template');

	// --- Mode sélection (non-éditable) ---
	const selectedSkills = $derived(skills.filter(s => s.selected));
	const selectedCount = $derived(selectedSkills.length);
	const hasSelection = $derived(selectedCount > 0);

	// Redistribue les poids quand la sélection change
	$effect(() => {
		if (!editable) {
			const count = skills.filter(s => s.selected).length;
			if (count === 0) {
				if (skills.length === 0) return;
				skills = skills.map(s => ({ ...s, weight: 0 }));
				return;
			}
			const equalWeight = totalBudget / count;
			let needsUpdate = false;
			const newSkills = skills.map(s => {
				const w = s.selected ? equalWeight : 0;
				if (Math.abs((s.weight ?? 0) - w) > 0.001) needsUpdate = true;
				return { ...s, weight: w };
			});
			if (needsUpdate) skills = newSkills;
		}
	});

	// --- Mode éditable ---
	const skillCount = $derived(skills.length);
	const hasSkills = $derived(skillCount > 0);
	const allocatedSum = $derived(editable
		? skills.reduce((sum, s) => sum + (s.weight ?? 0), 0)
		: selectedSkills.reduce((sum, s) => sum + (s.weight ?? 0), 0)
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
			const selected = skills.filter(s => s.selected);
			const count = selected.length;
			if (count === 0) return;
			const equalWeight = totalBudget / count;
			skills = skills.map(s => s.selected ? { ...s, weight: equalWeight } : { ...s, weight: 0 });
			return;
		}
		const count = skills.length;
		if (count === 0) return;
		const equalWeight = parseFloat((totalBudget / count).toFixed(4));
		skills = skills.map((s) => ({ ...s, weight: equalWeight }));
	}

	function addSkill() {
		const newIndex = skills.length;
		skills = [...skills, {
			name: '',
			category: 'BEHAVIORAL' as SkillCategory,
			weight: 0,
			employee_level: undefined,
			manager_level: undefined,
		}];
		redistributeWeights();
		// Déplier le nouveau bloc
		const next = new Set(collapsedSkills);
		next.delete(newIndex);
		collapsedSkills = next;
	}

	function removeSkill(index: number) {
		// Blur l'élément actif pour empêcher le saut de focus
		(document.activeElement as HTMLElement)?.blur();
		skills = skills.filter((_, i) => i !== index);
		redistributeWeights();
	}

	function updateField(index: number, field: string, value: unknown) {
		const newSkills = skills.map((s) => ({ ...s }));
		newSkills[index] = { ...newSkills[index], [field]: value };

		// Auto-ajustement des autres poids quand on modifie le weight
		if (field === 'weight' && newSkills.length > 1) {
			const newWeight = (value as number) ?? 0;
			const otherSum = newSkills.reduce((sum, s, i) => (i !== index ? sum + (s.weight ?? 0) : sum), 0);

			if (otherSum > 0.001) {
				const newOtherSum = totalBudget - newWeight;
				if (newOtherSum >= -0.001) {
					newSkills.forEach((s, i) => {
						if (i !== index && otherSum > 0) {
							const proportion = (s.weight ?? 0) / otherSum;
							s.weight = parseFloat((newOtherSum * proportion).toFixed(4));
						}
					});
				}
			} else {
				const equalOther = parseFloat(((totalBudget - newWeight) / (newSkills.length - 1)).toFixed(4));
				newSkills.forEach((s, i) => {
					if (i !== index) s.weight = equalOther;
				});
			}
		}

		skills = newSkills;
	}

	const levelLabel = (level: number): string => {
		const labels = ['Débutant', 'Débutant+', 'Intermédiaire', 'Avancé', 'Expert'];
		return labels[level - 1] || '';
	};

	const currentLevel = (skill: Skill): number | undefined => {
		return mode === 'employee' ? skill.employee_level : skill.manager_level;
	};

	// Collapse state for each skill - tous pliés par défaut
	let collapsedSkills = $state<Set<number>>(new Set());

	// Flag non-réactif pour n'initialiser qu'une seule fois
	let _skillsInitialized = false;

	// Quand les skills sont chargés (asynchrone), tout plier immédiatement
	$effect(() => {
		if (skills.length > 0 && !_skillsInitialized) {
			collapsedSkills = new Set(skills.map((_, i) => i));
			_skillsInitialized = true;
		}
	});

	function toggleCollapse(i: number) {
		const next = new Set(collapsedSkills);
		if (next.has(i)) {
			next.delete(i);
		} else {
			next.add(i);
		}
		collapsedSkills = next;
	}

	function isCollapsed(i: number): boolean {
		return collapsedSkills.has(i);
	}

	const levelField = $derived(mode === 'employee' ? 'employee_level' as const : 'manager_level' as const);

	function toggleLevel(index: number, n: number) {
		const current = skills[index][levelField];
		// Cliquer une étoile déjà remplie → remet à zéro
		if (current != null && n <= current) {
			updateField(index, levelField, undefined);
		} else {
			updateField(index, levelField, current === n ? undefined : n);
		}
	}
</script>


<div class="space-y-3">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<div class="flex size-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
				<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
				</svg>
			</div>
			<Label class="text-[0.875rem] font-medium text-slate-700 cursor-default">
				{isTemplate ? 'Compétences par défaut' : editable
					? (mode === 'employee' ? 'Compétences (auto-évaluation)' : "Compétences (évaluation évaluateur)")
					: (mode === 'employee' ? 'Compétences (auto-évaluation)' : "Compétences (évaluation évaluateur)")
				}
			</Label>
			{#if editable && hasSkills}
				<span class="inline-flex items-center justify-center h-5 min-w-5 rounded-full bg-indigo-100 px-1.5 text-[0.82rem] font-semibold text-indigo-700 tabular-nums">
					{skillCount}
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
				onclick={addSkill}
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
	{#if editable && hasSkills}
		<div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
			<div class="flex-1 flex items-center gap-2">
				<div class="flex-1 h-2 rounded-full bg-slate-200 overflow-hidden">
					<div
						class="h-full rounded-full transition-all duration-300 {isOverBudget ? 'bg-rose-400' : 'bg-indigo-500'}"
						style="width: {Math.min(allocatedSum / totalBudget, 1) * 100}%"
					></div>
				</div>
				<span class="text-[0.82rem] font-semibold text-slate-700 tabular-nums shrink-0">
					{allocatedPercentage}% / {budgetPercentage}%
				</span>
			</div>
			{#if remainingPercentage > 0}
				<span class="text-[0.82rem] text-slate-400 shrink-0">
					<i class="text-indigo-500 not-italic text-[0.82rem]">{remainingPercentage}%</i> restant
				</span>
			{:else if isOverBudget}
				<span class="text-[0.82rem] text-rose-500 font-medium shrink-0">
					Dépassement de {Math.abs(remainingPercentage)}%
				</span>
			{:else}
				<span class="text-[0.82rem] text-emerald-600 font-medium shrink-0">
					Budget atteint
				</span>
			{/if}
		</div>
	{/if}

	<!-- Empty state -->
	{#if !hasSkills}
		<div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50 py-8 px-4 transition-colors hover:border-slate-300">
			<div class="flex size-8 items-center justify-center rounded-full bg-indigo-50 mb-3">
				<svg class="size-4.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
				</svg>
			</div>
			<p class="text-sm font-medium text-slate-600">Aucune compétence</p>
			<p class="mt-1 text-xs text-slate-400 text-center max-w-48">
				{editable ? "Évaluez les compétences de l'employé pour cette période." : "Aucune compétence définie pour cette campagne."}
			</p>
		</div>
	{/if}

	<!-- Mode non-éditable : sélection compacte avec Switch -->
	{#if !editable}
		<div class="space-y-2">
			{#each skills as skill, i (i)}
				{@const isSelected = skill.selected ?? false}
				{@const level = currentLevel(skill)}
				<div
					class="flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all {isSelected ? 'border-indigo-200 bg-indigo-50/40' : 'border-slate-200 bg-white hover:border-slate-300'}"
				>
					{#if selectionOnly}
						<Switch bind:checked={skills[i].selected} />
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
								{skill.name || 'Compétence sans nom'}
							</span>
							{#if skill.category}
								<span class="shrink-0 inline-flex items-center rounded-full bg-indigo-50 px-1.5 py-0.5 text-[0.8rem] font-medium text-indigo-600">
									{SKILL_CATEGORY_LABELS[skill.category]}
								</span>
							{/if}
							{#if isSelected && skill.weight != null}
								<span class="shrink-0 text-[0.82rem] font-semibold text-indigo-500 tabular-nums">
									{Math.round(skill.weight * 100)}%
								</span>
							{/if}
						</div>
					</div>

					<!-- Niveaux : visibles seulement si sélectionné et pas en mode selectionOnly -->
					{#if isSelected && !selectionOnly}
						<div class="flex items-center gap-0.5 shrink-0">
							{#each [1, 2, 3, 4, 5] as n}
								<button
									type="button"
									onmousedown={(e) => e.preventDefault()}
									onclick={() => toggleLevel(i, n)}
									class="size-7 flex items-center justify-center transition-all duration-150 cursor-pointer rounded-md
										{n <= (level ?? 0)
											? 'text-indigo-500 scale-110'
											: 'text-slate-300 bg-slate-100/60 hover:text-indigo-400 hover:scale-110'}"
									title={levelLabel(n)}
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
		{#each skills as skill, i (i)}
			<div
				class="group relative rounded-xl border border-slate-200 bg-white shadow-fine transition-all hover:border-slate-300 overflow-hidden {isCollapsed(i) ? 'cursor-pointer' : ''}"
				class:expanded={!isCollapsed(i)}
				class:collapsed={isCollapsed(i)}
			>
				<!-- Header unique -->
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
						<div class="flex size-7 items-center justify-center rounded-full bg-indigo-600 text-[0.82rem] font-bold text-white shadow-fine shrink-0">
							{i + 1}
						</div>

						<!-- Vue pliée : nom + catégorie + niveau + poids -->
						<div class="flex-1 flex items-center gap-3 min-w-0" class:hidden={!isCollapsed(i)}>
							<span class="text-[0.875rem] font-medium text-slate-900 truncate">
								{skill.name || 'Nouvelle compétence'}
							</span>
							{#if skill.category}
								<span class="inline-flex items-center rounded-full bg-indigo-50 px-1.5 py-0.5 text-[0.82rem] font-semibold text-indigo-600 shrink-0">
									{SKILL_CATEGORY_LABELS[skill.category]}
								</span>
							{/if}
							{#if skill.weight != null}
								<span class="text-[0.82rem] font-bold text-indigo-500 shrink-0">
									{Math.round(skill.weight * 100)}%
								</span>
							{/if}
							{#if currentLevel(skill)}
								<span class="flex items-center gap-1 text-[0.82rem] font-medium text-indigo-600 shrink-0">
									{currentLevel(skill)}/5
								</span>
							{/if}
						</div>

						<!-- Vue dépliée : titre court -->
						<span class="flex-1 text-[0.82rem] font-medium text-slate-700" class:hidden={isCollapsed(i)}>Compétence {i + 1}</span>

						<!-- Bouton supprimer -->
						<span
							onmousedown={(e) => { e.preventDefault(); e.stopPropagation(); }}
							onclick={(e) => { e.preventDefault(); e.stopPropagation(); removeSkill(i); }}
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

				<!-- Contenu déplié : toujours dans le DOM -->
				<div class="p-4 pt-3 space-y-3" class:hidden={isCollapsed(i)} transition:fade={{ duration: 120 }}>
					<!-- Nom -->
					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">Nom de la compétence</Label>
						<Input
							type="text"
							placeholder="Nom de la compétence"
							value={skill.name}
							oninput={(e) => updateField(i, 'name', (e.currentTarget as HTMLInputElement).value)}
							class="h-9 border-slate-200 bg-white text-[0.875rem] placeholder:text-slate-400 focus:bg-white transition-colors shadow-fine"
						/>
					</div>

					<!-- Catégorie -->
					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">Catégorie</Label>
						<Select.Root
							type="single"
							value={skill.category ?? 'BEHAVIORAL'}
							onValueChange={(v) => updateField(i, 'category', v)}
						>
							<Select.Trigger class="h-9 border-slate-200 bg-white text-[0.82rem] font-normal w-full shadow-fine">
								{SKILL_CATEGORY_LABELS[skill.category ?? 'BEHAVIORAL']}
							</Select.Trigger>
							<Select.Content class="bg-white border-slate-100 shadow-fine z-100 min-w-36">
								{#each Object.entries(SKILL_CATEGORY_LABELS) as [value, label]}
									<Select.Item {value} label={label} class="text-[0.82rem]">{label}</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</div>

					<!-- Poids -->
					<div class="space-y-1.5">
						<Label class="text-[0.82rem] font-medium text-slate-600">Poids (sur {budgetPercentage}%)</Label>
						<div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200">
							<input
								type="range"
								min="0"
								max={totalBudget}
								step="0.01"
								value={skill.weight ?? 0}
								oninput={(e) => updateField(i, 'weight', parseFloat((e.currentTarget as HTMLInputElement).value))}
								class="flex-1 h-1.5 accent-indigo-500 cursor-pointer"
							/>
							<span class="text-[0.82rem] font-semibold text-indigo-700 tabular-nums min-w-10 text-right">
								{Math.round((skill.weight ?? 0) * 100)}%
							</span>
						</div>
					</div>

					{#if !isTemplate}
					<div class="space-y-1.5">
						<div class="flex items-center justify-between">
							<Label class="text-[0.82rem] font-medium text-slate-600">
								{mode === 'employee' ? "Niveau employé (auto-évaluation)" : 'Niveau manager'}
							</Label>
							<span class="text-[0.82rem] font-semibold text-indigo-600 tabular-nums">{currentLevel(skill) ?? '-'}/5</span>
						</div>
						<div class="flex items-center gap-1 h-9">
							{#each [1, 2, 3, 4, 5] as n}
								<button
									type="button"
									onmousedown={(e) => e.preventDefault()}
									onclick={() => {
										const field = mode === 'employee' ? 'employee_level' : 'manager_level';
										updateField(i, field, (currentLevel(skill) === n) ? undefined : n);
									}}
									class="size-8 flex items-center justify-center transition-all duration-150 cursor-pointer rounded-md
										{n <= (currentLevel(skill) ?? 0)
											? 'text-indigo-500 scale-110'
											: 'text-slate-300 bg-slate-100/60 hover:text-indigo-400 hover:scale-110'}"
									title={levelLabel(n)}
								>
									<svg class="size-5" viewBox="0 0 24 24" fill="currentColor">
										<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
									</svg>
								</button>
							{/each}
						</div>
						<div class="flex items-center justify-between">
							<span class="text-[0.82rem] text-slate-400">Débutant</span>
							<span class="text-[0.82rem] text-slate-400">Expert</span>
						</div>
					</div>
					{/if}
				</div>
			</div>
		{/each}
	{/if}
</div>
