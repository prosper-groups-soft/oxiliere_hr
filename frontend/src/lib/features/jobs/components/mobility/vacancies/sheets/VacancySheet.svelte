<script lang="ts">
	import * as Sheet from "@/components/ui/sheet";
	import { Button } from "@/components/ui/button";
	import { Input } from "@/components/ui/input";
	import { Label } from "@/components/ui/label";
	import {
		Select,
		SelectContent,
		SelectItem,
		SelectTrigger
	} from "@/components/ui/select";
	import AppIcon from "@/components/layout/elements/AppIcon.svelte";
	import { notification } from "@/stores/notification.svelte";
	import type { Vacancy, VacancyPriority, VacancyStatus } from "../../../../types/types";
	import { cn } from "@/utilities/common/css";
	import { fade, slide } from "svelte/transition";
	import {
		useCreateVacancyMutation,
		useUpdateVacancyMutation
	} from "../../../../queries/vacancyQueries";
	import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
	import { usePositionsQuery } from "../../../../queries/jobQueries";
	import { z } from 'zod';
	import { vacancySchema } from "../../../../schemas/vacancy.schema";
	import ValidationError from "@/components/ui/validation-error/ValidationError.svelte";
	import { PRIORITY_CONFIG, STATUS_CONFIG } from "../../../../constants/vacancy.constants";

	let {
		open = $bindable(false),
		vacancy = $bindable(null)
	} = $props<{
		open: boolean,
		vacancy?: Vacancy | null
	}>();

	// --- Form state ---
	let formPositionId = $state('');
	let formPriority = $state<VacancyPriority>('MEDIUM');
	let formStatus = $state<VacancyStatus>('OPEN');
	let formOpenedDate = $state('');
	let formTargetDate = $state<string | null>(null);
	let formReason = $state('');

	$effect(() => {
		if (open) {
			if (vacancy) {
				formPositionId = vacancy.positionId;
				formPriority = vacancy.priority;
				formStatus = vacancy.status;
				formOpenedDate = vacancy.openedDate;
				formTargetDate = vacancy.targetDate || null;
				formReason = vacancy.reason || '';
			} else {
				formPositionId = '';
				formPriority = 'MEDIUM';
				formStatus = 'OPEN';
				formOpenedDate = new Date().toISOString().split('T')[0];
				formTargetDate = null;
				formReason = '';
			}
		}
	});

	// Mutations
	const createMutation = useCreateVacancyMutation();
	const updateMutation = useUpdateVacancyMutation();

	// Derived states
	const isSaving = $derived($createMutation.isPending || $updateMutation.isPending);

	// --- Validation state ---
	let validationErrors = $state<Record<string, string>>({});

	function clearValidationError(field: string) {
		validationErrors = { ...validationErrors, [field]: '' };
	}

	function validateForm(): boolean {
		validationErrors = {};

		const result = vacancySchema.safeParse({
			position_id: formPositionId,
			priority: formPriority,
			status: formStatus,
			opened_date: formOpenedDate,
			target_date: formTargetDate,
			reason: formReason || undefined
		});

		if (!result.success) {
			result.error.issues.forEach((err: z.core.$ZodIssue) => {
				const field = err.path.join('.');
				validationErrors = { ...validationErrors, [field]: err.message };
			});
			return false;
		}

		return true;
	}

	// Reset validation errors when modal opens
	$effect(() => {
		if (open) {
			validationErrors = {};
		}
	});

	async function handleSave() {
		// Validation Zod
		if (!validateForm()) {
			notification.toast.error('Veuillez corriger les erreurs du formulaire');
			return;
		}

		const data = {
			position_id: formPositionId,
			priority: formPriority,
			status: formStatus,
			opened_date: formOpenedDate,
			target_date: formTargetDate,
			reason: formReason || undefined
		};

		try {
			if (vacancy) {
				await $updateMutation.mutateAsync({ id: vacancy.id, data });
			} else {
				await $createMutation.mutateAsync(data);
			}
			open = false;
		} catch (error) {
			// Error already handled by mutation
		}
	}

	// Queries for select options
	const allPositionsQuery = usePositionsQuery();

	const selectedPos = $derived(
		$allPositionsQuery.data?.find(p => p.id === formPositionId) || 
		(vacancy?.position?.id === formPositionId ? vacancy.position : null)
	);
	
</script>


<Sheet.Root bind:open>
	<Sheet.Content side="right" class="sm:max-w-lg bg-white p-0 flex flex-col h-full overflow-hidden">
		
    <!-- Header aligned with PositionSheet -->
		<Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
			<div class="flex items-center gap-3">
				<div class="space-y-0.5 min-w-0">
					<Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
						{vacancy ? 'Modifier le besoin' : 'Nouveau besoin'}
					</Sheet.Title>
				</div>
			</div>
		</Sheet.Header>

		<div class="flex-1 overflow-y-auto custom-scrollbar">
			<div class="p-4 space-y-7" in:fade={{ duration: 200 }}>

				<!-- Poste à pourvoir (Select Pattern) -->
				<div class="space-y-2.5">
					<Label class="text-slate-900">Poste à pourvoir <span class="text-red-500">*</span></Label>
					{#key formPositionId}
					<Select type="single" value={formPositionId} onValueChange={(v) => { formPositionId = v; clearValidationError('position_id'); }}>
						<SelectTrigger class={cn(
							"h-11 w-full bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors",
							validationErrors.position_id && "border-red-500"
						)}>
							<div class="flex items-center gap-0.5">
								{#if selectedPos}
								<div class="h-2 w-2 rounded-full bg-emerald-500 shrink-0"></div>
								<div class="flex gap-1.5 items-start">
									<span class="text-[0.87rem] font-semibold text-slate-800">{selectedPos.name}</span>
										{#if selectedPos.job_family?.name || selectedPos.org_unit?.name}
											<span class="text-[0.85rem] text-slate-400 pl-1.5 border-l border-slate-300">
												{selectedPos.job_family?.name}{selectedPos.job_family?.name && selectedPos.org_unit?.name ? ' · ' : ''}{selectedPos.org_unit?.name}
											</span>
										{/if}
									</div>
								{:else}
								<span class="text-[0.87rem] font-medium text-slate-400">Sélectionner un poste...</span>
							{/if}
							</div>
						</SelectTrigger>
						<SelectContent class="z-9999 max-h-72">
							{#if $allPositionsQuery.isLoading}
								<AnimateSpin class="size-3" text="Chargement des postes" textPosition="right" />
							{:else if $allPositionsQuery.data}
								{#each $allPositionsQuery.data as pos}
									<SelectItem value={pos.id} class="text-[0.85rem] py-2.5">
										<div class="flex flex-col items-start gap-0.5">
											<span class="font-medium text-[0.87rem]">{pos.name}</span>
											{#if pos.job_family?.name || pos.org_unit?.name}
												<span class="text-[0.85rem] text-slate-400">
													{pos.job_family?.name}{pos.job_family?.name && pos.org_unit?.name ? ' · ' : ''}{pos.org_unit?.name}
												</span>
											{/if}
										</div>
									</SelectItem>
								{/each}
							{/if}
						</SelectContent>
					</Select>
					{/key}
					<ValidationError errors={validationErrors} field="position_id" />
				</div>

				<!-- Type de besoin -->
				<div class="space-y-3">
					<Label class="text-slate-900">Priorité</Label>
					<div class="grid grid-cols-3 gap-3">
						{#each ['HIGH', 'MEDIUM', 'LOW'] as priority}
						{@const typedPriority = priority as VacancyPriority}
						{@const priorityCfg = PRIORITY_CONFIG[typedPriority]}
						<button
							type="button"
							onclick={() => formPriority = typedPriority}
							class={cn(
								"flex flex-col items-center gap-2 p-3 rounded-xl border text-center transition-all group cursor-pointer",
								formPriority === typedPriority
									? "bg-primary/5 border-primary text-primary shadow-md"
									: "bg-white border-slate-200 text-slate-700 hover:border-indigo-300 hover:bg-indigo-50/50 hover:shadow-xs"
							)}
						>
							<AppIcon name={priorityCfg.icon} size={18} class={priorityCfg.color} />
							<span class="text-[0.8rem] font-medium">{priorityCfg.label}</span>
						</button>
						{/each}
					</div>
				</div>

				<!-- Grid for Date -->
				<div class="grid grid-cols-2 gap-4">
					<div class="space-y-2.5">
						<Label for="vac-opened-date" class="text-slate-900">Date d'ouverture <span class="text-red-500">*</span></Label>
						<Input
							id="vac-opened-date"
							type="date"
							bind:value={formOpenedDate}
							oninput={() => clearValidationError('opened_date')}
							class={cn(
								"h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
								validationErrors.opened_date && "border-red-500 focus:ring-red-500"
							)}
						/>
						<ValidationError errors={validationErrors} field="opened_date" />
					</div>

					<div class="space-y-2.5">
						<Label for="vac-target-date" class="text-slate-900">Date cible</Label>
						<Input
							id="vac-target-date"
							type="date"
							bind:value={formTargetDate}
							class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
						/>
					</div>
				</div>

				<!-- Statut -->
				<div class="space-y-3">
					<Label class="text-slate-900">Statut</Label>
					<div class="grid grid-cols-2 gap-3">
						{#each ['OPEN', 'IN_PROGRESS', 'RECRUITMENT', 'CANCELLED'] as status}
						{@const typedStatus = status as VacancyStatus}
						{@const statusCfg = STATUS_CONFIG[typedStatus]}
              <button
                type="button"
                onclick={() => formStatus = typedStatus}
                class={cn(
                  "flex items-center gap-2 p-3 rounded-xl border text-left transition-all group cursor-pointer",
                  formStatus === typedStatus
                    ? "bg-primary/5 border-primary text-primary shadow-md"
                    : "bg-white border-slate-200 text-slate-700 hover:border-indigo-300 hover:bg-indigo-50/50 hover:shadow-xs"
                )}
              >
                <AppIcon name={statusCfg.icon} size={16} class={statusCfg.color} />
                <span class="text-[0.8rem]">{statusCfg.label}</span>
              </button>
						{/each}
					</div>
				</div>

				<!-- Visual Feedback Box : grid -->
				<div class="p-5 rounded-2xl bg-slate-50 border border-slate-100 grid-cols-2 gap-4 hidden" in:slide={{ duration: 300 }}>
					<div class="flex items-center gap-3">
						<div class="h-9 w-9 rounded-xl bg-white flex items-center justify-center shadow-sm {PRIORITY_CONFIG[formPriority].color} border border-slate-100">
							<AppIcon name={PRIORITY_CONFIG[formPriority].icon} size={18} />
						</div>
						<div class="flex flex-col">
							<span class="text-[0.6rem] font-black text-slate-400 uppercase tracking-widest">Priorité</span>
							<span class="text-[0.8rem] font-bold text-slate-700">{PRIORITY_CONFIG[formPriority].label}</span>
						</div>
					</div>
					<div class="flex items-center gap-3">
						<div class="h-9 w-9 rounded-xl bg-white flex items-center justify-center shadow-sm {STATUS_CONFIG[formStatus].color} border border-slate-100">
							<AppIcon name={STATUS_CONFIG[formStatus].icon} size={18} />
						</div>
						<div class="flex flex-col">
							<span class="text-[0.6rem] font-black text-slate-400 uppercase tracking-widest">Statut</span>
							<span class="text-[0.8rem] font-bold text-slate-700">{STATUS_CONFIG[formStatus].label}</span>
						</div>
					</div>
				</div>

				<!-- Raison -->
				<div class="space-y-2.5">
					<Label for="vac-reason" class="text-slate-900">Motif ou Commentaire</Label>
					<textarea
						id="vac-reason"
						bind:value={formReason}
						oninput={() => clearValidationError('reason')}
						class={cn(
							"w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400",
							validationErrors.reason && "border-red-500 focus:ring-red-500"
						)}
						placeholder="Précisez les raisons du besoin (ex: Départ, Augmentation d'activité...)"
					></textarea>
					<ValidationError errors={validationErrors} field="reason" />
				</div>
			</div>
		</div>

		<!-- Footer aligned with PositionSheet -->
		<Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
			<div class="flex gap-3 w-full">
				<Sheet.Close class="flex-1">
					<Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
						<AppIcon name="x" size={18} class="text-slate-300" />
						Annuler
					</Button>
				</Sheet.Close>
				<Button
					onclick={handleSave}
					disabled={isSaving}
					class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-70"
				>
					{#if isSaving}
						<AnimateSpin text="" class="size-3 border-white" />
					{:else}
						<AppIcon name="check" size={18} />
					{/if}
					Enregistrer
				</Button>
			</div>
		</Sheet.Footer>
    
	</Sheet.Content>
</Sheet.Root>


<style>
	.custom-scrollbar::-webkit-scrollbar { width: 4px; }
	.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
	.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>

