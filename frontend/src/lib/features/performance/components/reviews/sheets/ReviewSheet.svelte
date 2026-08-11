<script lang="ts">
	import * as Sheet from '@/components/ui/sheet';
	import * as Select from '@/components/ui/select';
	import { Label } from '@/components/ui/label';
	import { Textarea } from '@/components/ui/textarea';
	import { Button } from '@/components/ui/button';
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import { cn } from '@/utilities/common/css';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import { getInitials } from '@/utilities/common/string';
	import { getAvatarPalette } from '@/utilities/common/func';
	import { buildFullName } from '@/utilities/common/employee.utils';
	import { getMediaUrl } from '@/utilities/common/media';
	import ValidationError from '@/components/ui/validation-error';
	import {
		useCampaignsQuery, useCampaignParticipantsQuery,
		useCampaignEvaluatorsQuery, useCreateReviewMutation,
		useUpdateEmployeeReviewMutation, useUpdateManagerReviewMutation
	} from '../../../queries/performanceQueries';
	import { CAMPAIGN_TYPE_LABELS } from '../../../constants';
	import GoalEditor from '../forms/GoalEditor.svelte';
	import SkillEditor from '../forms/SkillEditor.svelte';
	import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
	import { formatDate } from '@/utilities/common/date';
	import type { PerformanceReview, Goal, Skill } from '../../../types/types';


	let {
		open = $bindable(false),
		review = null,
		mode = 'employee',
	}: {
		open: boolean;
		review?: PerformanceReview | null;
		mode?: 'employee' | 'manager';
	} = $props();

	const isEditMode = $derived(!!review);

	const createReviewMutation = useCreateReviewMutation();
	const updateEmployeeMutation = useUpdateEmployeeReviewMutation();
	const updateManagerMutation = useUpdateManagerReviewMutation();

	// Campaigns query (for campaign selector)
	const campaignsQuery = useCampaignsQuery(
		() => 1,
		() => ({ status: 'ACTIVE' })
	);
	let campaigns = $derived($campaignsQuery.data?.results ?? []);

	// Form state
	let selectedEmployeeStr = $state('');
	let selectedCampaignStr = $state('');
	let selectedManagerStr = $state('');
	let goals = $state<Goal[]>([]);
	let skills = $state<Skill[]>([]);
	let employeeComment = $state('');
	let isSaving = $state(false);
	let submitError = $state<string | null>(null);
	let validationErrors = $state<Record<string, string>>({});

	// Participants de la campagne sélectionnée — déclarés AVANT les $derived qui les utilisent
	const campaignParticipantsQuery = useCampaignParticipantsQuery(() => selectedCampaignStr);
	let campaignEmployees = $derived($campaignParticipantsQuery.data ?? []);

	// Évaluateurs (managers) de la campagne sélectionnée
	const campaignEvaluatorsQuery = useCampaignEvaluatorsQuery(() => selectedCampaignStr);
	let campaignEvaluators = $derived($campaignEvaluatorsQuery.data ?? []);

	const selectedEmployeeObj = $derived(
		selectedEmployeeStr
			? campaignEmployees.find((e) => String(e.id) === selectedEmployeeStr)
			: undefined
	);

	const selectedManagerObj = $derived(
		selectedManagerStr
			? campaignEvaluators.find((e) => String(e.id) === selectedManagerStr)
			: undefined
	);

	const selectedCampaignObj = $derived(
		selectedCampaignStr
			? campaigns.find((c) => c.id === selectedCampaignStr)
			: undefined
	);

	// Force refetch quand la campagne change (gap TanStack Query / Svelte 5)
	$effect(() => {
		if (selectedCampaignStr) {
			$campaignParticipantsQuery.refetch();
			$campaignEvaluatorsQuery.refetch();
		}
	});

	// Initialize form values
	function initializeForm() {
		if (review) {
			selectedCampaignStr = review.campaignId;
			if (mode === 'manager') {
				const mgrGoals = review.goalsManager?.length ? review.goalsManager : review.goals;
				const mgrSkills = review.skillsManager?.length ? review.skillsManager : review.skills;
				goals = mgrGoals.map(g => ({
					description: g.description,
					type: g.type,
					weight: g.weight,
					employee_rating: undefined,
					manager_rating: g.manager_rating,
					manager_comment: g.manager_comment,
					selected: true,
				}));
				skills = mgrSkills.map(s => ({
					name: s.name,
					category: s.category,
					weight: s.weight,
					employee_level: undefined,
					manager_level: s.manager_level,
					selected: true,
				}));
				employeeComment = review.managerComment;
			} else {
				goals = review.goals.map(g => ({ ...g, selected: true }));
				skills = review.skills.map(s => ({ ...s, selected: true }));
				employeeComment = review.employeeComment;
			}
		} else {
			selectedEmployeeStr = '';
			selectedCampaignStr = '';
			selectedManagerStr = '';
			goals = [];
			skills = [];
			employeeComment = '';
		}
		validationErrors = {};
		submitError = null;
	}

	// Reset when opening
	$effect(() => {
		if (open) {
			initializeForm();
		}
	});

	// Quand on change de campagne en mode création, pré-remplir les défauts
	let lastCampaignId = $state('');
	$effect(() => {
		if (!isEditMode && selectedCampaignStr && selectedCampaignStr !== lastCampaignId) {
			lastCampaignId = selectedCampaignStr;
			if (selectedCampaignObj?.default_goals?.length) {
				goals = selectedCampaignObj.default_goals.map(g => ({ ...g, selected: true }));
			} else {
				goals = [];
			}
			if (selectedCampaignObj?.default_skills?.length) {
				skills = selectedCampaignObj.default_skills.map(s => ({ ...s, selected: true }));
			} else {
				skills = [];
			}
		}
	});

	function clearValidationError(field: string) {
		validationErrors = { ...validationErrors, [field]: '' };
	}

	function validateForm(): boolean {
		const errors: Record<string, string> = {};
		if (!isEditMode) {
			if (!selectedEmployeeStr) errors.employee = "Veuillez choisir un employé";
			if (!selectedCampaignStr) errors.campaign = "Veuillez choisir une campagne";
		}
		validationErrors = errors;
		return Object.keys(errors).length === 0;
	}

	function isValidUUID(str: string): boolean {
		return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
	}

	async function handleSubmit() {
		if (!validateForm()) return;

		if (!isEditMode && !isValidUUID(selectedEmployeeStr)) return;

		isSaving = true;
		submitError = null;

		try {
			if (isEditMode && review) {
				if (mode === 'manager') {
					await $updateManagerMutation.mutateAsync({
						reviewId: review.id,
						data: {
							goals_manager: goals
								.filter(g => g.selected && g.description.trim())
								.map(g => ({
									description: g.description,
									type: g.type,
									weight: g.weight,
									manager_rating: g.manager_rating,
									manager_comment: g.manager_comment,
								})),
							skills_manager: skills
								.filter(s => s.selected && s.name.trim())
								.map(s => ({
									name: s.name,
									category: s.category,
									weight: s.weight,
									manager_level: s.manager_level,
								})),
							manager_comment: employeeComment,
						},
					});
				} else {
					await $updateEmployeeMutation.mutateAsync({
						reviewId: review.id,
						data: {
							goals: goals.filter(g => g.selected && g.description.trim()),
							skills: skills.filter(s => s.selected && s.name.trim()),
							employee_comment: employeeComment,
						},
					});
				}
			} else {
				await $createReviewMutation.mutateAsync({
					campaign_id: selectedCampaignStr,
					employee_id: selectedEmployeeStr,
					manager_id: selectedManagerStr || undefined,
					goals: goals.filter(g => g.selected && g.description.trim()),
					skills: skills.filter(s => s.selected && s.name.trim()),
					employee_comment: employeeComment,
				});
			}
			open = false;
		} catch (err: unknown) {
			const axiosErr = err as { response?: { data?: { detail?: string } } };
			submitError = axiosErr?.response?.data?.detail
				|| (err instanceof Error ? err.message : String(err));
		} finally {
			isSaving = false;
		}
	}
</script>


<Sheet.Root bind:open>
	<Sheet.Content side="right" class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white h-full">
		<Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
			<Sheet.Title class="text-[0.95rem] font-bold text-slate-900 text-left">
				{#if isEditMode}
					{mode === 'manager' ? "Évaluation de l'évaluateur" : "Modifier l'auto-évaluation"}
				{:else}
					Créer une évaluation
				{/if}
			</Sheet.Title>
			{#if isEditMode && review}
				<p class="text-[0.84rem] text-slate-500 mt-0.5">
					{review.employeeName} · {review.campaignName}
					{#if mode === 'manager'}
						<span class="inline-flex items-center gap-1 ml-2 px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 text-[0.84rem] font-medium">
							Mode évaluateur
						</span>
					{/if}
				</p>
			{/if}
		</Sheet.Header>

		<div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
			{#if !isEditMode}
				<!-- Campaign selector -->
				<div class="space-y-2">
					<Label for="campaign-select" class="text-[0.875rem] font-medium text-slate-700">
						Campagne (en cours)<span class="text-rose-500">*</span>
					</Label>
					<Select.Root type="single" bind:value={selectedCampaignStr} onValueChange={() => clearValidationError('campaign')}>
						<Select.Trigger id="campaign-select" class={cn(
							"h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem] cursor-pointer",
							validationErrors.campaign && "border-red-500"
						)}>
							{#if selectedCampaignStr}
								{@const campaign = campaigns.find(c => c.id === selectedCampaignStr)}
								<div class="flex items-center gap-2 truncate">
									<span class="text-[0.87rem] font-medium truncate">{campaign?.name ?? 'Campagne inconnue'}</span>
									{#if campaign}
										<span class="text-[0.84rem] text-slate-400 shrink-0 px-2 border-l border-slate-200">
											{CAMPAIGN_TYPE_LABELS[campaign.campaign_type] || campaign.campaign_type}
										</span>
										<span class="flex items-center gap-1.5 shrink-0 ml-1">
											<span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-blue-50 text-blue-600 text-[0.75rem] font-semibold" title="Participants">
												<svg class="size-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
												{campaignEmployees.length}
											</span>
											<span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600 text-[0.75rem] font-semibold" title="Évaluateurs">
												<svg class="size-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
												{campaignEvaluators.length}
											</span>
										</span>
									{/if}
								</div>
							{:else}
								<span class="text-slate-400 text-[0.87rem]">Choisir une campagne...</span>
							{/if}
						</Select.Trigger>
						<Select.Content class="max-h-60 z-100">
							{#if $campaignsQuery.isLoading}
								<div class="flex items-center justify-center py-4 text-slate-400 text-[0.84rem]">
									<AnimateSpin textPosition="right" text="Chargement des campagnes" class="size-3" />
								</div>
							{:else if campaigns.length === 0}
								<div class="flex items-center justify-center gap-1.5 py-4 text-slate-400 text-[0.84rem]">
									<AppIcon name="calendar" size={17} class="text-slate-300 shrink-0" />
									Aucune campagne active n'est disponible
								</div>
							{:else}
								{#each campaigns as campaign}
									<Select.Item value={campaign.id} class="py-2.5 cursor-pointer">
										<div class="flex flex-col min-w-0">
											<span class="text-[0.87rem] font-medium truncate">{campaign.name}</span>
											<span class="text-[0.84rem] text-slate-500">
												{CAMPAIGN_TYPE_LABELS[campaign.campaign_type] || campaign.campaign_type}
												· {formatDate(campaign.start_date, false, true)} → {formatDate(campaign.end_date, false, true)}
											</span>
										</div>
									</Select.Item>
								{/each}
							{/if}
						</Select.Content>
					</Select.Root>
					<ValidationError errors={validationErrors} field="campaign" />
				</div>

				<!-- Employee selector -->
				<div class="space-y-2">
					<Label for="employee-select" class="text-[0.875rem] font-medium text-slate-700">
						Participant évalué<span class="text-rose-500">*</span>
					</Label>
					<Select.Root type="single" bind:value={selectedEmployeeStr}>
						<Select.Trigger id="employee-select" class={cn(
							"h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem] cursor-pointer",
							validationErrors.employee && "border-red-500"
						)}>
							{#if !selectedCampaignStr}
								<span class="text-slate-300 text-[0.87rem]">Sélectionnez d'abord une campagne</span>
							{:else if selectedEmployeeObj}
								{@const empPalette = getAvatarPalette(buildFullName(selectedEmployeeObj) || '')}
								<div class="flex items-center gap-2 truncate">
									<Avatar class="h-7 w-7 rounded-full border border-slate-200 shrink-0">
										<AvatarImage src={getMediaUrl(selectedEmployeeObj.profile_photo || selectedEmployeeObj.avatarUrl || '')} alt={buildFullName(selectedEmployeeObj) || ''} class="object-cover" />
										<AvatarFallback class={cn("text-[0.84rem] font-bold", empPalette.bg, empPalette.text)}>
											{getInitials(selectedEmployeeObj.last_name || selectedEmployeeObj.lastName || '', selectedEmployeeObj.middle_name || selectedEmployeeObj.middleName || '', selectedEmployeeObj.first_name || selectedEmployeeObj.firstName || '')}
										</AvatarFallback>
									</Avatar>
									<span class="text-[0.87rem] font-medium truncate">{buildFullName(selectedEmployeeObj)}</span>
								</div>
							{:else}
								<span class="text-slate-400 text-[0.87rem]">Choisir un employé...</span>
							{/if}
						</Select.Trigger>
						<Select.Content class="max-h-60 z-100">
							{#if $campaignParticipantsQuery.isLoading}
								<div class="flex items-center justify-center py-4 text-slate-400 text-[0.84rem]">
									<AnimateSpin textPosition="right" text="Chargement des employés" class="size-3" />
								</div>
							{:else if campaignEmployees.length === 0}
								<div class="flex items-center justify-center gap-1.5 py-4 text-slate-400 text-[0.84rem]">
									<AppIcon name="users" size={17} class="text-slate-300 shrink-0" />
									Aucun employé dans cette campagne
								</div>
							{:else}
								{#each campaignEmployees as employee}
									{@const empFullName = buildFullName(employee) || ''}
									{@const empPalette = getAvatarPalette(empFullName)}
									{@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
									<Select.Item value={employee.id.toString()} class="py-2.5 cursor-pointer">
										<div class="flex items-center gap-3">
											<Avatar class="h-8.5 w-8.5 rounded-full border border-slate-200 shrink-0">
												<AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
												<AvatarFallback class={cn("text-[0.84rem] font-bold", empPalette.bg, empPalette.text)}>
													{getInitials(employee.last_name || employee.lastName || '', employee.middle_name || employee.middleName || '', employee.first_name || employee.firstName || '')}
												</AvatarFallback>
											</Avatar>
											<div class="flex flex-col min-w-0">
												<span class="text-[0.87rem] font-medium truncate">{empFullName}</span>
												{#if employee.job_title || employee.jobTitle || employee.org_unit || employee.orgUnit}
													<span class="text-[0.84rem] text-slate-500 truncate">
														{employee.job_title || employee.jobTitle}{employee.job_title || employee.jobTitle ? ' · ' : ''}{employee.org_unit || employee.orgUnit}
													</span>
												{/if}
											</div>
										</div>
									</Select.Item>
								{/each}
							{/if}
						</Select.Content>
					</Select.Root>
					<ValidationError errors={validationErrors} field="employee" />
				</div>

				<!-- Manager selector -->
				<div class="space-y-2">
					<Label for="manager-select" class="text-[0.875rem] font-medium text-slate-700">
						Evaluateur
					</Label>
					<Select.Root type="single" bind:value={selectedManagerStr}>
						<Select.Trigger id="manager-select" class={cn(
							"h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem] cursor-pointer",
						)}>
							{#if !selectedCampaignStr}
								<span class="text-slate-300 text-[0.87rem]">Sélectionnez d'abord une campagne</span>
							{:else if selectedManagerObj}
								{@const mngPalette = getAvatarPalette(buildFullName(selectedManagerObj) || '')}
								<div class="flex items-center gap-2 truncate">
									<Avatar class="h-7 w-7 rounded-full border border-slate-200 shrink-0">
										<AvatarImage src={getMediaUrl(selectedManagerObj.profile_photo || selectedManagerObj.avatarUrl || '')} alt={buildFullName(selectedManagerObj) || ''} class="object-cover" />
										<AvatarFallback class={cn("text-[0.84rem] font-bold", mngPalette.bg, mngPalette.text)}>
											{getInitials(selectedManagerObj.last_name || selectedManagerObj.lastName || '', selectedManagerObj.middle_name || selectedManagerObj.middleName || '', selectedManagerObj.first_name || selectedManagerObj.firstName || '')}
										</AvatarFallback>
									</Avatar>
									<span class="text-[0.87rem] font-medium truncate">{buildFullName(selectedManagerObj)}</span>
								</div>
							{:else}
								<span class="text-slate-400 text-[0.87rem]">Choisir un manager...</span>
							{/if}
						</Select.Trigger>
						<Select.Content class="max-h-60 z-100">
							{#if $campaignEvaluatorsQuery.isLoading}
								<div class="flex items-center justify-center py-4 text-slate-400 text-[0.84rem]">
									<AnimateSpin textPosition="right" text="Chargement d'évaluateurs" class="size-3" />
								</div>
							{:else if campaignEvaluators.length === 0}
								<div class="py-4 text-center text-[0.82rem] text-slate-400 flex gap-2 items-center justify-center">
									<AppIcon name="users" size={15} class="text-slate-400" />
									Aucun évaluateur dans cette campagne
								</div>
							{:else}
								<Select.Item value="" class="py-2 cursor-pointer text-slate-400 text-[0.84rem]">
									<div class="flex items-center gap-2 text-[0.86rem]">
										<AppIcon name="circle-x" size={17} />
										Pas d'évaluateur
									</div>
								</Select.Item>
								{#each campaignEvaluators as employee}
									{@const empFullName = buildFullName(employee) || ''}
									{@const empPalette = getAvatarPalette(empFullName)}
									{@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
									<Select.Item value={employee.id.toString()} class="py-2.5 cursor-pointer">
										<div class="flex items-center gap-3">
											<Avatar class="h-8.5 w-8.5 rounded-full border border-slate-200 shrink-0">
												<AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
												<AvatarFallback class={cn("text-[0.84rem] font-bold", empPalette.bg, empPalette.text)}>
													{getInitials(employee.last_name || employee.lastName || '', employee.middle_name || employee.middleName || '', employee.first_name || employee.firstName || '')}
												</AvatarFallback>
											</Avatar>
											<div class="flex flex-col min-w-0">
												<span class="text-[0.87rem] font-medium truncate">{empFullName}</span>
												{#if employee.job_title || employee.jobTitle || employee.org_unit || employee.orgUnit}
													<span class="text-[0.84rem] text-slate-500 truncate">
														{employee.job_title || employee.jobTitle}{employee.job_title || employee.jobTitle ? ' · ' : ''}{employee.org_unit || employee.orgUnit}
													</span>
												{/if}
											</div>
										</div>
									</Select.Item>
								{/each}
							{/if}
						</Select.Content>
					</Select.Root>
				</div>
			{/if}

			<!-- Goals & Skills : visible uniquement si une campagne est sélectionnée -->
			{#if selectedCampaignObj}
				<!-- Goals -->
				{@const gw = review?.campaignGoalWeight ?? selectedCampaignObj?.goal_weight ?? 0.6}
				{#if (gw) != null}
					<div class="flex items-center gap-2">
						<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[0.84rem] font-semibold">
							Poids objectifs : {Math.round(gw * 100)}%
						</span>
					</div>
				{/if}
				<GoalEditor bind:goals {mode} totalBudget={gw} editable={false} selectionOnly={!isEditMode} />

				<!-- Skills -->
				{@const sw = review?.campaignSkillWeight ?? selectedCampaignObj?.skill_weight ?? 0.4}
				{#if (sw) != null}
					<div class="flex items-center gap-2">
						<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[0.84rem] font-semibold">
							Poids compétences : {Math.round(sw * 100)}%
						</span>
					</div>
				{/if}
				<SkillEditor bind:skills {mode} totalBudget={sw} editable={false} selectionOnly={!isEditMode} />
        
			{:else}
				<div class="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50 py-10 px-6 mt-2">
					<svg class="size-8 text-slate-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
					</svg>
					<p class="text-sm font-medium text-slate-500">Sélectionnez une campagne</p>
					<p class="mt-1 text-[0.82rem] text-slate-400 text-center max-w-64">
						Choisissez une campagne dans la liste ci-dessus pour définir les objectifs et compétences de cette évaluation.
					</p>
				</div>
			{/if}

			<!-- Comment (uniquement en mode édition) -->
			{#if isEditMode}
			<div class="space-y-1.5">
				<Label for="employee-comment" class="text-[0.875rem] font-medium text-slate-700">{mode === 'manager' ? "Commentaire de l'évaluateur" : 'Votre commentaire'}</Label>
				<Textarea
					id="employee-comment"
					bind:value={employeeComment}
					placeholder="Commentaire sur l'évaluation..."
					class="min-h-20 shadow-fine text-[0.84rem]"
				/>
			</div>
			{/if}
		</div>

		<Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
			<Sheet.Close class="flex-1">
				<Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer" onclick={() => {}}>
					<AppIcon name="x" size={18} class="text-slate-300" />
					Annuler
				</Button>
			</Sheet.Close>
			<Button
				onclick={handleSubmit}
				disabled={isSaving}
				class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer disabled:opacity-50"
			>
				{#if isSaving}
					<AnimateSpin class="border-white size-3" text="" />
				{:else}
					<AppIcon name={mode === 'manager' ? 'check-circle' : 'check'} size={18} />
				{/if}
				{isEditMode ? (mode === 'manager' ? "Enregistrer l'évaluation" : 'Enregistrer') : "Créer l'évaluation"}
			</Button>
		</Sheet.Footer>
	</Sheet.Content>
</Sheet.Root>




