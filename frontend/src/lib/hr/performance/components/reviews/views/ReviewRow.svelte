<script lang="ts">
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import { Badge } from '@/components/ui/badge';
	import { Button } from '@/components/ui/button';
	import { cn } from '@/utilities/common/css';
	import * as DropdownMenu from '@/components/ui/dropdown-menu';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import { getInitials } from '@/utilities/common/string';
	import { getAvatarPalette } from '@/utilities/common/func';
	import { getMediaUrl } from '@/utilities/common/media';
	import { fade } from 'svelte/transition';
	import ReviewStatusBadge from '../../shared/ReviewStatusBadge.svelte';
	import type { PerformanceReview } from '../../../types/types';


	let {
		review,
		mode = 'all',
		onClick,
		selected = false,
		onView,
		onSelfAssess,
		onEvaluate,
		onSubmitEmployee,
		onSubmitManager,
		onAcknowledge,
		onDispute,
		onDelete,
	}: {
		review: PerformanceReview;
		mode?: 'employee' | 'manager' | 'all';
		onClick?: () => void;
		selected?: boolean;
		onView?: () => void;
		onSelfAssess?: () => void;
		onEvaluate?: () => void;
		onSubmitEmployee?: () => void;
		onSubmitManager?: () => void;
		onCalibrate?: () => void;
		onAcknowledge?: () => void;
		onDispute?: () => void;
		onDelete?: () => void;
	} = $props();

	const palette = $derived(getAvatarPalette(review.employeeName));

	// Visibilité des actions selon le statut, la soumission et le mode
	const isEmployee = $derived(mode === 'employee' || mode === 'all');
	const isManager = $derived(mode === 'manager' || mode === 'all');

	// Visibilité conditionnelle des scores croisés :
	// - Un employé ne voit PAS le score évaluateur tant qu'il n'a pas soumis
	// - Un évaluateur ne voit PAS le score employé tant qu'il n'a pas soumis
	const showEmployeeScore = $derived(
		mode === 'all'
		|| mode === 'employee'
		|| (mode === 'manager' && !!review.managerSubmittedAt)
	);
	const showEvaluatorScore = $derived(
		mode === 'all'
		|| mode === 'manager'
		|| (mode === 'employee' && !!review.employeeSubmittedAt)
	);

	const canSelfAssess = $derived(review.status === 'EMPLOYEE_DRAFT' && !review.employeeSubmittedAt && !!onSelfAssess && isEmployee);
	const canEvaluate = $derived(review.status === 'EMPLOYEE_DRAFT' && !review.managerSubmittedAt && !!onEvaluate && isManager);
	const canSubmitEmployee = $derived(review.status === 'EMPLOYEE_DRAFT' && !review.employeeSubmittedAt && !!onSubmitEmployee && !!review.employeeScore && isEmployee);
	const canSubmitManager = $derived(review.status === 'EMPLOYEE_DRAFT' && !review.managerSubmittedAt && !!onSubmitManager && !!review.evaluatorScore && isManager);
	const canAcknowledge = $derived(review.status === 'SUBMITTED' && !review.disputed && !!onAcknowledge && isEmployee);
	const canDispute = $derived(review.status === 'SUBMITTED' && !review.acknowledgedAt && !!onDispute && isEmployee);
	const canDelete = $derived(review.status === 'EMPLOYEE_DRAFT' && !review.employeeSubmittedAt && !review.managerSubmittedAt && !!onDelete);
	const canView = $derived(!!onView);
	const initials = $derived(
		getInitials(
			review.employeeLastName || review.employeeName.split(' ').slice(-1)[0] || '',
			review.employeeMiddleName || '',
			review.employeeFirstName || review.employeeName.split(' ')[0] || ''
		)
	);
  
	function formatFullDate(iso: string | undefined): string {
		if (!iso) return '';
		try {
			return new Date(iso).toLocaleDateString('fr-FR', {
				day: 'numeric',
				month: 'short',
				year: 'numeric',
				hour: '2-digit',
				minute: '2-digit',
			});
		} catch {
			return '';
		}
	}

	function getScoreLabel(): string {
		if (review.displayScore) return '';
		if (review.employeeSubmittedAt && review.managerSubmittedAt) return "En attente de validation";
		if (review.employeeSubmittedAt) return "En attente évaluateur";
		if (review.managerSubmittedAt) return "En attente employé";
		return "Pas encore évalué";
	}
	const scoreLabel = $derived(getScoreLabel());



	const lastDate = $derived(review.updatedAt || review.createdAt || '');

	const managerFullName = $derived(
		[review.managerLastName, review.managerMiddleName, review.managerFirstName]
			.filter(Boolean)
			.join(' ') || review.managerName
	);

	const employeeFullName = $derived(
		[review.employeeLastName, review.employeeMiddleName, review.employeeFirstName]
			.filter(Boolean)
			.join(' ') || review.employeeName
	);
</script>


<div
	in:fade={{ duration: 200 }}
	class={cn(
		"group flex items-center py-3 pl-6 pr-2 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors",
		selected && "bg-indigo-50/50 border-l-2 border-l-indigo-500 hover:bg-indigo-50/50"
	)}
	tabindex="0"
	role="button"
	onclick={onClick}
	onkeydown={(e) => e.key === 'Enter' && onClick?.()}
>
	<!-- Employee -->
	<div class="w-[22%] flex items-center gap-2.5">
		<Avatar class="size-8 rounded-full ring-1 ring-slate-100 shrink-0">
			<AvatarImage src={getMediaUrl(review.employeeAvatar || '')} alt={review.employeeName} class="object-cover" />
			<AvatarFallback class={cn("text-[0.84rem] font-bold", palette.bg, palette.text)}>
				{initials}
			</AvatarFallback>
		</Avatar>
		<div class="flex flex-col min-w-0">
			<span class="text-[0.85rem] font-medium text-slate-800 truncate group-hover:text-indigo-600 transition-colors">
				{employeeFullName}
			</span>
			{#if review.employeeJobTitle}
				<span class="text-[0.84rem] text-slate-500 truncate">{review.employeeJobTitle}</span>
			{/if}
		</div>
	</div>

	<!-- Evaluator -->
	<div class="w-[18%] flex items-center gap-2">
		{#if review.managerName}
			<Avatar class="size-7 rounded-full ring-1 ring-slate-100 shrink-0">
				<AvatarImage src={getMediaUrl(review.managerAvatar || '')} alt={managerFullName} class="object-cover" />
				<AvatarFallback class="text-[0.75rem] font-bold bg-slate-100 text-slate-500">
					{getInitials(
						review.managerLastName || managerFullName.split(' ').slice(-1)[0] || '',
						review.managerMiddleName || '',
						review.managerFirstName || managerFullName.split(' ')[0] || ''
					)}
				</AvatarFallback>
			</Avatar>
			<span class="text-[0.84rem] text-slate-600 truncate">{managerFullName}</span>
		{:else}
			<span class="text-slate-400 text-[0.84rem]">Non assigné</span>
		{/if}
	</div>

	<!-- Status -->
	<div class="w-[12%] flex items-center">
		<ReviewStatusBadge status={review.status} employeeSubmittedAt={review.employeeSubmittedAt} managerSubmittedAt={review.managerSubmittedAt} />
	</div>

	<!-- Campaign -->
	<div class="w-[16%] flex flex-col justify-center gap-0.5">
		<div class="flex items-center gap-1.5">
			<AppIcon name="layout" size={16} class="text-slate-400 shrink-0" />
			<span class="text-[0.84rem] text-slate-700 truncate">{review.campaignName}</span>
		</div>
	</div>

	<!-- Score -->
	<div class="w-[18%] flex flex-col items-start gap-0.5 min-w-0">
		{#if showEmployeeScore && showEvaluatorScore && review.employeeScore && review.evaluatorScore}
			<div class="flex items-center gap-3">
				<!-- Auto-évaluation -->
				<div class="flex flex-col items-start gap-0.5">
					<span class="inline-flex items-center gap-1 rounded-full bg-emerald-50/60 px-2 py-0.5 text-[0.68rem] font-semibold text-emerald-600 tracking-tight">Auto</span>
					<div class="flex items-center gap-1">
						<div class="flex items-center gap-0.5">
							{#each Array(5) as _, i}
								<svg class="size-2.5 {i < Math.round(review.employeeScore) ? 'text-emerald-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
								</svg>
							{/each}
						</div>
						<span class="text-[0.78rem] font-bold text-emerald-600 tabular-nums">{review.employeeScore.toFixed(1)}</span>
					</div>
				</div>
				<!-- Séparateur -->
				<div class="h-8 w-px bg-slate-200 shrink-0"></div>
				<!-- Évaluateur -->
				<div class="flex flex-col items-start gap-0.5">
					<span class="inline-flex items-center gap-1 rounded-full bg-purple-50/60 px-2 py-0.5 text-[0.68rem] font-semibold text-purple-600 tracking-tight">Éval</span>
					<div class="flex items-center gap-1">
						<div class="flex items-center gap-0.5">
							{#each Array(5) as _, i}
								<svg class="size-2.5 {i < Math.round(review.evaluatorScore) ? 'text-purple-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
									<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
								</svg>
							{/each}
						</div>
						<span class="text-[0.78rem] font-bold text-purple-600 tabular-nums">{review.evaluatorScore.toFixed(1)}</span>
					</div>
				</div>
			</div>
			{#if review.displayScore}
				<span class="inline-flex items-center gap-1 rounded-full bg-indigo-50/60 px-2 py-0.5 text-[0.7rem] font-semibold text-indigo-500/80 tracking-tight">Final {review.displayScore.toFixed(1)}</span>
			{/if}
		{:else if showEvaluatorScore && review.evaluatorScore}
			<div class="flex items-center gap-0.5">
				{#each Array(5) as _, i}
					<svg
						class="size-3 {i < Math.round(review.evaluatorScore) ? 'text-purple-400' : 'text-slate-200'}"
						fill="currentColor"
						viewBox="0 0 20 20"
					>
						<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
					</svg>
				{/each}
			</div>
			<span class="text-[0.84rem] font-bold text-purple-600 tabular-nums">{review.evaluatorScore.toFixed(1)}</span>
			<span class="inline-flex items-center gap-1 rounded-full bg-purple-50/60 px-2 py-0.5 text-[0.72rem] font-semibold text-purple-500/80 tracking-tight">Note évaluateur</span>
		{:else if showEmployeeScore && review.employeeScore}
			<div class="flex items-center gap-0.5">
				{#each Array(5) as _, i}
					<svg
						class="size-3 {i < Math.round(review.employeeScore) ? 'text-emerald-400' : 'text-slate-200'}"
						fill="currentColor"
						viewBox="0 0 20 20"
					>
						<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
					</svg>
				{/each}
			</div>
			<span class="text-[0.84rem] font-bold text-emerald-600 tabular-nums">{review.employeeScore.toFixed(1)}</span>
			<span class="inline-flex items-center gap-1 rounded-full bg-emerald-50/60 px-2 py-0.5 text-[0.72rem] font-semibold text-emerald-500/80 tracking-tight">Auto-évaluation</span>
		{:else}
			<span class="text-slate-500 flex gap-1.5 items-center">
				<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
				<span class="text-[0.84rem]">{scoreLabel}</span>
			</span>
		{/if}
	</div>

	<!-- Resultat (contestation) -->
	<div class="w-[12%] flex items-center gap-1 flex-wrap">
		{#if review.disputed}
			<Badge variant="outline" class="bg-rose-50 text-rose-600 border-rose-200 text-[0.84rem] font-bold px-1.5 py-0.5 rounded-full">
				Contestée
			</Badge>
			{#if review.disputeReason}
				<span class="text-[0.72rem] text-rose-500/70 italic truncate max-w-full leading-tight mt-0.5" title={review.disputeReason}>
					{review.disputeReason}
				</span>
			{/if}
		{:else if review.status === 'SUBMITTED' || review.status === 'ACKNOWLEDGED'}
			<span class="inline-flex items-center gap-0.5 text-[0.84rem] font-semibold text-indigo-600">
				<AppIcon name="circle-check" size={16} />
				{review.status === 'ACKNOWLEDGED' ? 'Validée' : 'Soumise'}
			</span>
		{:else}
			<span class="text-[0.84rem] text-slate-500 flex gap-1.5 items-center">
				<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
				<span class="text-[0.84rem]">Pas de résultat</span>
			</span>
		{/if}
	</div>

	<!-- Date -->
	<div class="w-[8%] text-right pr-2">
		{#if lastDate}
			<span class="text-[0.84rem] font-medium text-slate-500 tabular-nums leading-snug">
				{formatFullDate(lastDate)}
			</span>
		{:else}
			<span class="text-[0.84rem] text-slate-400 flex gap-1.5 items-center justify-end">
				<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
				<span class="text-[0.84rem]">Date inconnue</span>
			</span>
		{/if}
	</div>

	<!-- Actions dropdown -->
	<div class="w-[6%] flex justify-end shrink-0" onclick={(e) => e.stopPropagation()} onkeydown={() => {}} role="none">
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				<Button variant="ghost" size="sm" class="h-7 w-7 p-0 rounded-lg mr-2">
					<AppIcon name="more-vertical" size={17} class="text-slate-500" />
				</Button>
			</DropdownMenu.Trigger>

			<DropdownMenu.Content align="end" class="w-56 p-1 z-100">
				{#if canView}
					<DropdownMenu.Item onclick={onView} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="eye" size={16} class="text-slate-500 mr-2" />
						Voir les détails
					</DropdownMenu.Item>
				{/if}

				{#if canSelfAssess}
					<DropdownMenu.Item onclick={onSelfAssess} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="edit" size={16} class="text-blue-500 mr-2" />
						Noter mes objectifs
					</DropdownMenu.Item>
				{/if}

				{#if canEvaluate}
					<DropdownMenu.Item onclick={onEvaluate} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="check-circle" size={16} class="text-purple-500 mr-2" />
						Évaluer l'employé
					</DropdownMenu.Item>
				{/if}

				{#if canSubmitEmployee}
					<DropdownMenu.Item onclick={onSubmitEmployee} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="send" size={16} class="text-blue-600 mr-2" />
						Soumettre à l'évaluateur
					</DropdownMenu.Item>
				{/if}

				{#if canSubmitManager}
					<DropdownMenu.Item onclick={onSubmitManager} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="send" size={16} class="text-purple-600 mr-2" />
						Soumettre la notation
					</DropdownMenu.Item>
				{/if}

				{#if canAcknowledge}
					<DropdownMenu.Item onclick={onAcknowledge} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="eye" size={16} class="text-emerald-500 mr-2" />
						Valider les résultats
					</DropdownMenu.Item>
				{/if}

				{#if canDispute}
					<DropdownMenu.Item onclick={onDispute} class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer">
						<AppIcon name="alert-circle" size={16} class="text-red-500 mr-2" />
						Contester
					</DropdownMenu.Item>
				{/if}

				{#if canDelete}
					<DropdownMenu.Separator />
					<DropdownMenu.Item
						onclick={onDelete}
						class="rounded-lg px-2 py-1.5 text-[0.86rem]! cursor-pointer text-red-500! hover:bg-red-50! hover:text-red-600!"
					>
						<AppIcon name="trash-2" size={16} class="text-red-500 mr-2" />
						Supprimer
					</DropdownMenu.Item>
				{/if}
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</div>
</div>

