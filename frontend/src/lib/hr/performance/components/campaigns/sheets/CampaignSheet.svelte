<script lang="ts">
	import * as Sheet from '@/components/ui/sheet';
	import { Label } from '@/components/ui/label';
	import { Input } from '@/components/ui/input';
	import { Textarea } from '@/components/ui/textarea';
	import { Button } from '@/components/ui/button';
	import * as Select from '@/components/ui/select';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import ValidationError from '@/components/ui/validation-error';
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
	import { useAllEmployees } from '@/hr/employees/queries/employeeQueries';
	import { getInitials } from '@/utilities/common/string';
	import { getAvatarPalette } from '@/utilities/common/func';
	import { buildFullName } from '@/utilities/common/employee.utils';
	import { getMediaUrl } from '@/utilities/common/media';
	import { cn } from '@/utilities/common/css';
	import { useCreateCampaignMutation, useUpdateCampaignMutation } from '@/hr/performance/queries/performanceQueries';
	import { performanceService } from '@/hr/performance/services/performance.service';
	import { CAMPAIGN_TYPE_LABELS } from '@/hr/performance/constants';
	import GoalEditor from '@/hr/performance/components/reviews/forms/GoalEditor.svelte';
  import SkillEditor from '@/hr/performance/components/reviews/forms/SkillEditor.svelte';
  import type { Campaign, Goal, Skill } from '@/hr/performance/types/types';


	let {
		open = $bindable(false),
		campaign = null,
		onclose,
	}: {
		open: boolean;
		campaign?: Campaign | null;
		onclose?: () => void;
	} = $props();

	const isEditMode = $derived(!!campaign);

	const createMutation = useCreateCampaignMutation();
	const updateMutation = useUpdateCampaignMutation();
	const employeesQuery = useAllEmployees();
	const allEmployees = $derived($employeesQuery.data || []);

	// Form state
	let name = $state('');
	let description = $state('');
	let campaign_type = $state('SEMESTRIAL');
	let start_date = $state('');
	let end_date = $state('');
	let submission_deadline = $state('');
	let goal_weight = $state(0.6);
	let skill_weight = $state(0.4);
	let participant_ids = $state<string[]>([]);
	let participantSearch = $state('');
	let evaluator_ids = $state<string[]>([]);
	let evaluatorSearch = $state('');
	let defaultGoals = $state<Goal[]>([]);
	let defaultSkills = $state<Skill[]>([]);
	let isSaving = $state(false);
	let submitError = $state<string | null>(null);
	let validationErrors = $state<Record<string, string>>({});

	const filteredParticipants = $derived(
		allEmployees.filter((e: any) => {
			const fullName = buildFullName(e);
			if (!fullName) return false;
			return (
				fullName.toLowerCase().includes(participantSearch.toLowerCase()) &&
				!participant_ids.includes(String(e.id))
			);
		})
	);

	const selectedParticipants = $derived(
		participant_ids
			.map(id => allEmployees.find((e: any) => String(e.id) === id))
			.filter((e): e is NonNullable<typeof e> => e != null)
	);

	const filteredEvaluators = $derived(
		allEmployees.filter((e: any) => {
			const fullName = buildFullName(e);
			if (!fullName) return false;
			return (
				fullName.toLowerCase().includes(evaluatorSearch.toLowerCase()) &&
				!evaluator_ids.includes(String(e.id))
			);
		})
	);

	const selectedEvaluators = $derived(
		evaluator_ids
			.map(id => allEmployees.find((e: any) => String(e.id) === id))
			.filter((e): e is NonNullable<typeof e> => e != null)
	);

	function toggleParticipant(id: string) {
		if (participant_ids.includes(id)) {
			participant_ids = participant_ids.filter(p => p !== id);
		} else {
			participant_ids = [...participant_ids, id];
		}
	}

	function toggleEvaluator(id: string) {
		if (evaluator_ids.includes(id)) {
			evaluator_ids = evaluator_ids.filter(p => p !== id);
		} else {
			evaluator_ids = [...evaluator_ids, id];
		}
	}

	function initializeForm() {
		if (campaign) {
			name = campaign.name;
			description = campaign.description || '';
			campaign_type = campaign.campaign_type;
			start_date = campaign.start_date;
			end_date = campaign.end_date;
			submission_deadline = campaign.submission_deadline;
			goal_weight = campaign.goal_weight ?? 0.6;
			skill_weight = campaign.skill_weight ?? 0.4;
			defaultGoals = campaign.default_goals.map(g => ({ ...g }));
			defaultSkills = campaign.default_skills.map(s => ({ ...s }));
			// Load existing participants for edit mode
			performanceService.listParticipants(campaign.id).then(list => {
				participant_ids = list.map(p => p.employee_id);
			}).catch(() => {
				participant_ids = [];
			});
			// Load existing evaluators for edit mode
			performanceService.listEvaluatorsDetail(campaign.id).then(list => {
				evaluator_ids = list.map(p => p.id);
			}).catch(() => {
				evaluator_ids = [];
			});
		} else {
			name = '';
			description = '';
			campaign_type = 'SEMESTRIAL';
			start_date = '';
			end_date = '';
			submission_deadline = '';
			goal_weight = 0.6;
			skill_weight = 0.4;
			participant_ids = [];
			evaluator_ids = [];
			defaultGoals = [];
			defaultSkills = [];
		}
		participantSearch = '';
		evaluatorSearch = '';
		validationErrors = {};
		submitError = null;
	}

	$effect(() => {
		if (open) initializeForm();
	});

	function clearError(field: string) {
		validationErrors = { ...validationErrors, [field]: '' };
	}

	function validateForm(): boolean {
		const errors: Record<string, string> = {};
		if (!name.trim()) errors.name = 'Le nom est requis';
		if (!start_date) errors.start_date = 'La date de début est requise';
		if (!end_date) errors.end_date = 'La date de fin est requise';
		if (!submission_deadline) errors.submission_deadline = 'La date limite est requise';
		if (start_date && end_date && end_date < start_date)
			errors.end_date = 'La date de fin doit être postérieure Ã  la date de début';
		if (start_date && submission_deadline && submission_deadline < end_date)
			errors.submission_deadline = 'La date limite doit être postérieure Ã  la date de fin';
		if (goal_weight + skill_weight < 0.99 || goal_weight + skill_weight > 1.01)
			errors.goal_weight = 'La somme des poids doit être égale Ã  1';
		if (!isEditMode && participant_ids.length === 0)
			errors.participants = 'Ajoutez au moins un participant';
		validationErrors = errors;
		return Object.keys(errors).length === 0;
	}

	async function handleSubmit() {
		if (!validateForm()) return;

		isSaving = true;
		submitError = null;

		try {
			const data = {
				name: name.trim(),
				description: description.trim(),
				campaign_type,
				start_date,
				end_date,
				submission_deadline,
				goal_weight,
				skill_weight,
				default_goals: defaultGoals.map(g => ({
					description: g.description?.trim() || 'Nouvel objectif',
					type: g.type,
					weight: g.weight,
					employee_rating: undefined,
				})),
				default_skills: defaultSkills.map(s => ({
					name: s.name?.trim() || 'Nouvelle competence',
					category: s.category,
					weight: s.weight,
					employee_level: undefined,
				})),
				participant_ids,
				evaluator_ids,
			};

			if (isEditMode && campaign) {
				await $updateMutation.mutateAsync({ campaignId: campaign.id, data });
			} else {
				await $createMutation.mutateAsync(data);
			}
			open = false;
		} catch (err: any) {
			submitError = err?.message || 'Une erreur est survenue';
		} finally {
			isSaving = false;
		}
	}
</script>


<Sheet.Root bind:open>
	<Sheet.Content side="right" class="sm:max-w-176 p-0 overflow-hidden flex flex-col bg-white h-full">
		<Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
			<Sheet.Title class="text-[0.95rem] font-bold text-slate-900 text-left">
				{isEditMode ? 'Modifier la campagne' : 'Nouvelle campagne'}
			</Sheet.Title>
		</Sheet.Header>

		<div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
			<!-- Name -->
			<div class="space-y-2">
				<Label for="campaign-name" class="text-[0.875rem] font-medium text-slate-700">
					Nom <span class="text-rose-500">*</span>
				</Label>
				<Input
					id="campaign-name"
					bind:value={name}
					placeholder="Ex: Campagne Annuelle 2026"
					oninput={() => clearError('name')}
					class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
				/>
				<ValidationError errors={validationErrors} field="name" />
			</div>

			<!-- Description -->
			<div class="space-y-2">
				<Label for="campaign-desc" class="text-[0.875rem] font-medium text-slate-700">Description</Label>
				<Textarea
					id="campaign-desc"
					bind:value={description}
					placeholder="Instructions générales..."
					class="min-h-20 border-slate-200 bg-white shadow-fine text-[0.875rem]"
				/>
			</div>

			<!-- Type -->
			<div class="space-y-2">
				<Label class="text-[0.875rem] font-medium text-slate-700">
          Type de campagne
        </Label>
				<Select.Root type="single" bind:value={campaign_type}>
					<Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine flex items-center gap-2 text-[0.875rem]">
						{CAMPAIGN_TYPE_LABELS[campaign_type] || "Sélectionner..."}
					</Select.Trigger>
					<Select.Content class="bg-white border-slate-100 shadow-fine z-100">
						{#each Object.entries(CAMPAIGN_TYPE_LABELS) as [value, label]}
							<Select.Item value={value}>{label}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>

			<!-- Dates -->
			<div class="grid grid-cols-3 gap-4">
				<div class="space-y-2">
					<Label for="campaign-start" class="text-[0.875rem] font-medium text-slate-700">
						Début <span class="text-rose-500">*</span>
					</Label>
					<Input
						id="campaign-start"
						type="date"
						bind:value={start_date}
						oninput={() => clearError('start_date')}
						class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
					/>
					<ValidationError errors={validationErrors} field="start_date" />
				</div>
				<div class="space-y-2">
					<Label for="campaign-end" class="text-[0.875rem] font-medium text-slate-700">
						Fin <span class="text-rose-500">*</span>
					</Label>
					<Input
						id="campaign-end"
						type="date"
						bind:value={end_date}
						oninput={() => clearError('end_date')}
						class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
					/>
					<ValidationError errors={validationErrors} field="end_date" />
				</div>
				<div class="space-y-2">
					<Label for="campaign-deadline" class="text-[0.875rem] font-medium text-slate-700">
						Date limite de soumission <span class="text-rose-500">*</span>
					</Label>
					<Input
						id="campaign-deadline"
						type="date"
						bind:value={submission_deadline}
						oninput={() => clearError('submission_deadline')}
						class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
					/>
					<ValidationError errors={validationErrors} field="submission_deadline" />
				</div>
			</div>

			<!-- Participants -->
			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<Label class="text-[0.875rem] font-medium text-slate-700">
						Participants {#if !isEditMode}<span class="text-rose-500">*</span>{/if}
					</Label>
					{#if selectedParticipants.length > 0}
						<span class="text-[0.82rem] text-slate-400">
							{selectedParticipants.length} sélectionné{selectedParticipants.length > 1 ? 's' : ''}
						</span>
					{/if}
				</div>

				<!-- Selected participants tags -->
				{#if selectedParticipants.length > 0}
					<div class="flex flex-wrap gap-1.5">
						{#each selectedParticipants as emp (emp!.id)}
							{@const empName = buildFullName(emp) || ''}
							{@const palette = getAvatarPalette(empName)}
							<div class="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-100 text-[0.82rem] text-slate-700">
								<div class={cn("h-5 w-5 rounded-full flex items-center justify-center text-[0.55rem] font-bold shrink-0", palette.bg, palette.text)}>
									{getInitials(emp!.last_name || '', emp!.middle_name || '', emp!.first_name || '')}
								</div>
								<span class="text-[0.82rem] text-nowrap">{empName}</span>
								<button
                  onmousedown={(e) => e.preventDefault()}
									onclick={() => toggleParticipant(String(emp!.id))}
									class="ml-0.5 text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
								>
									<AppIcon name="x" size={15} />
								</button>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Employee search + list -->
				<div class="relative">
					<div class="relative">
						<AppIcon name="search" size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
						<Input
							bind:value={participantSearch}
							placeholder="Rechercher un employé..."
							class="h-9 pl-9 pr-3 border-slate-200 bg-white shadow-fine text-[0.85rem]"
						/>
					</div>

					<div class="mt-1.5 max-h-40 overflow-y-auto border border-slate-100 rounded-lg divide-y divide-slate-50 bg-white shadow-fine">
						{#if $employeesQuery.isLoading}
							<div class="flex items-center justify-center py-4 text-slate-400 text-[0.85rem]">
								<AnimateSpin text="" class="size-3" />
							</div>
						{:else if filteredParticipants.length === 0}
							<div class="py-4 text-center text-[0.82rem] text-slate-400 flex gap-2 items-center justify-center">
                <AppIcon name="circle-check" size={15} class="text-slate-400" />
								{participantSearch ? 'Aucun employé trouvé' : 'Tous les employés sont déjÃ  sélectionnés'}
							</div>
						{:else}
							{#each filteredParticipants as employee (employee.id)}
								{@const empFullName = buildFullName(employee) || ''}
								{@const empPalette = getAvatarPalette(empFullName)}
								{@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
								<button
                  onmousedown={(e) => e.preventDefault()}
									onclick={() => toggleParticipant(String(employee.id))}
									class="flex items-center gap-3 w-full px-3 py-2.5 text-left hover:bg-slate-50 transition-colors cursor-pointer"
								>
									<Avatar class="h-8 w-8 rounded-full border border-slate-200 shrink-0">
										<AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
										<AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
											{getInitials(employee.last_name || '', employee.middle_name || '', employee.first_name || '')}
										</AvatarFallback>
									</Avatar>
									<div class="flex flex-col min-w-0 flex-1">
										<span class="text-[0.85rem] font-medium truncate">{empFullName}</span>
										{#if employee.jobTitle || employee.orgUnit}
											<span class="text-[0.77rem] text-slate-500 truncate">
                        {employee.jobTitle || employee.orgUnit}
                      </span>
										{/if}
									</div>
									<AppIcon name="plus" size={15} class="text-slate-300 shrink-0" />
								</button>
							{/each}
						{/if}
					</div>
				</div>
				<ValidationError errors={validationErrors} field="participants" />
			</div>

			<!-- Évaluateurs -->
			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<Label class="text-[0.875rem] font-medium text-slate-700">
						Évaluateurs
					</Label>
					{#if selectedEvaluators.length > 0}
						<span class="text-[0.82rem] text-slate-400">
							{selectedEvaluators.length} sélectionné{selectedEvaluators.length > 1 ? 's' : ''}
						</span>
					{/if}
				</div>

				<!-- Selected evaluators tags -->
				{#if selectedEvaluators.length > 0}
					<div class="flex flex-wrap gap-1.5">
						{#each selectedEvaluators as emp (emp!.id)}
							{@const empName = buildFullName(emp) || ''}
							{@const palette = getAvatarPalette(empName)}
							<div class="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-100 text-[0.82rem] text-slate-700">
								<div class={cn("h-5 w-5 rounded-full flex items-center justify-center text-[0.55rem] font-bold shrink-0", palette.bg, palette.text)}>
									{getInitials(emp!.last_name || '', emp!.middle_name || '', emp!.first_name || '')}
								</div>
								<span class="text-[0.82rem] text-nowrap">{empName}</span>
								<button
									onmousedown={(e) => e.preventDefault()}
									onclick={() => toggleEvaluator(String(emp!.id))}
									class="ml-0.5 text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
								>
									<AppIcon name="x" size={15} />
								</button>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Employee search + list for evaluators -->
				<div class="relative">
					<div class="relative">
						<AppIcon name="search" size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
						<Input
							bind:value={evaluatorSearch}
							placeholder="Rechercher un évaluateur..."
							class="h-9 pl-9 pr-3 border-slate-200 bg-white shadow-fine text-[0.85rem]"
						/>
					</div>

					<div class="mt-1.5 max-h-40 overflow-y-auto border border-slate-100 rounded-lg divide-y divide-slate-50 bg-white shadow-fine">
						{#if $employeesQuery.isLoading}
							<div class="flex items-center justify-center py-4 text-slate-400 text-[0.85rem]">
								<AnimateSpin text="" class="size-3" />
							</div>
						{:else if filteredEvaluators.length === 0}
							<div class="py-4 text-center text-[0.82rem] text-slate-400 flex gap-2 items-center justify-center">
								<AppIcon name="circle-check" size={15} class="text-slate-400" />
								{evaluatorSearch ? 'Aucun employé trouvé' : 'Tous les employés sont déjÃ  sélectionnés'}
							</div>
						{:else}
							{#each filteredEvaluators as employee (employee.id)}
								{@const empFullName = buildFullName(employee) || ''}
								{@const empPalette = getAvatarPalette(empFullName)}
								{@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
								<button
									onmousedown={(e) => e.preventDefault()}
									onclick={() => toggleEvaluator(String(employee.id))}
									class="flex items-center gap-3 w-full px-3 py-2.5 text-left hover:bg-slate-50 transition-colors cursor-pointer"
								>
									<Avatar class="h-8 w-8 rounded-full border border-slate-200 shrink-0">
										<AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
										<AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
											{getInitials(employee.last_name || '', employee.middle_name || '', employee.first_name || '')}
										</AvatarFallback>
									</Avatar>
									<div class="flex flex-col min-w-0 flex-1">
										<span class="text-[0.85rem] font-medium truncate">{empFullName}</span>
										{#if employee.jobTitle || employee.orgUnit}
											<span class="text-[0.77rem] text-slate-500 truncate">
												{employee.jobTitle || employee.orgUnit}
											</span>
										{/if}
									</div>
									<AppIcon name="plus" size={15} class="text-slate-300 shrink-0" />
								</button>
							{/each}
						{/if}
					</div>
				</div>
			</div>

			<!-- Weights -->
			<div class="grid grid-cols-2 gap-4">
				<div class="space-y-2">
					<Label for="campaign-goal-w" class="text-[0.875rem] font-medium text-slate-700">
						Poids objectifs
					</Label>
					<Input
						id="campaign-goal-w"
						type="number"
						min="0"
						max="1"
						step="0.05"
						bind:value={goal_weight}
						oninput={() => clearError('goal_weight')}
						class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
					/>
					<ValidationError errors={validationErrors} field="goal_weight" />
				</div>
				<div class="space-y-2">
					<Label for="campaign-skill-w" class="text-[0.875rem] font-medium text-slate-700">
						Poids compétences
					</Label>
					<Input
						id="campaign-skill-w"
						type="number"
						min="0"
						max="1"
						step="0.05"
						bind:value={skill_weight}
						class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
					/>
				</div>
			</div>

			<!-- Objectifs par défaut (template) -->
			<div class="border-t border-slate-100 pt-6">
				<h3 class="text-sm font-semibold text-slate-700 mb-3">Objectifs par défaut</h3>
			  <p class="text-sm text-slate-400 mb-3">Ces objectifs seront copiés dans chaque évaluation. L'employé pourra les modifier ou en ajouter.</p>
			  <GoalEditor bind:goals={defaultGoals} mode="template" totalBudget={goal_weight} />
			</div>

			<!-- Compétences par défaut (template) -->
			<div class="border-t border-slate-100 pt-6">
			  <h3 class="text-sm font-semibold text-slate-700 mb-3">Compétences par défaut</h3>
			  <p class="text-sm text-slate-400 mb-3">Ces compétences seront copiées dans chaque évaluation. L'employé pourra les modifier ou en ajouter.</p>
			  <SkillEditor bind:skills={defaultSkills} mode="template" totalBudget={skill_weight} />
			</div>

		</div>

		<Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
			<Sheet.Close class="flex-1">
				<Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer" onclick={onclose || (() => {})}>
					<AppIcon name="x" size={17} class="text-slate-300" />
					Annuler
				</Button>
			</Sheet.Close>
			<Button
				onclick={handleSubmit}
				disabled={isSaving}
				class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer gap-2"
			>
				{#if isSaving}
					<AnimateSpin class="border-white size-3" text="" />
				{:else}
					<AppIcon name="check" size={17} />
				{/if}
				{isEditMode ? 'Enregistrer' : 'Créer la campagne'}
			</Button>
		</Sheet.Footer>
	</Sheet.Content>
</Sheet.Root>




