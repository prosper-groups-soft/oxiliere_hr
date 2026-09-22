<script lang="ts">
	import { Button } from '@/components/ui/button';
	import { Badge } from '@/components/ui/badge';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import * as Tooltip from '@/components/ui/tooltip';
	import { cn } from '@/hr/utilities/common/css';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import { notification } from '@/hr/stores/notification.svelte';
	import { getAvatarPalette } from '@/hr/utilities/common/func';
	import { getInitials } from '@/hr/utilities/common/string';
	import { getMediaUrl } from '@/hr/utilities/common/media';

	import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_STATUS_COLORS, CAMPAIGN_TYPE_LABELS, CAMPAIGN_TYPE_COLORS, GOAL_TYPE_LABELS, SKILL_CATEGORY_LABELS } from '../../../constants';
	import type { Campaign } from '../../../types/types';


	interface Props {
		campaign: Campaign;
		onEdit: (campaign: Campaign) => void;
		onActivate: (campaignId: string) => void;
		onClose: (campaignId: string) => void;
		isActivating: boolean;
		isClosing: boolean;
	}

	let {
		campaign,
		onEdit,
		onActivate,
		onClose,
		isActivating,
		isClosing,
	}: Props = $props();

	const statusColors = $derived(CAMPAIGN_STATUS_COLORS[campaign.status]);
	const typeColors = $derived(CAMPAIGN_TYPE_COLORS[campaign.campaign_type] || {});

	const goals = $derived(campaign.default_goals ?? []);
	const skills = $derived(campaign.default_skills ?? []);
	const hasGoals = $derived(goals.length > 0);
	const hasSkills = $derived(skills.length > 0);

	const goalWeightLabel = $derived(campaign.goal_weight != null ? `${Math.round(campaign.goal_weight * 100)}%` : '');
	const skillWeightLabel = $derived(campaign.skill_weight != null ? `${Math.round(campaign.skill_weight * 100)}%` : '');

	const hasParticipants = $derived((campaign.participant_count ?? 0) > 0);
	const hasEvaluators = $derived((campaign.evaluator_count ?? 0) > 0);
	const showTooltip = $derived(hasParticipants || hasEvaluators);

	let tipOpen = $state(false);

	function formatDate(d: string): string {
		return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
	}
</script>


<Tooltip.Provider>
	<Tooltip.Root open={tipOpen}>
		<Tooltip.Trigger class="w-full">
			<div
				class="group flex items-center py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors max-h-30 overflow-y-auto row-scroll"
			  onmouseenter={() => { if (showTooltip) tipOpen = true; }}
			  onmouseleave={() => { tipOpen = false; }}
			  onclick={() => {
				  if (campaign.status === 'DRAFT') {
					  onEdit(campaign);
				  } else {
					  notification.toast.warning('Seules les campagnes en état brouillon peuvent être modifiées.');
				  }
			  }}
			  role="button"
			  tabindex="0"
			  onkeydown={(e) => e.key === 'Enter' && campaign.status === 'DRAFT' && onEdit(campaign)}
		 >
			<!-- Campagne (nom + type + statut + dates) -->
			<div class="w-[24%] flex flex-col gap-0.5 min-w-0">
				<div class="flex items-center gap-1.5 min-w-0">
					<div class={cn("h-2 w-2 rounded-full shrink-0", statusColors.dot)}></div>
					<span class="text-[0.9rem] font-semibold text-slate-800 truncate group-hover:text-primary transition-colors">{campaign.name}</span>
					<Badge variant="outline" class={cn("text-[0.84rem] rounded-full px-2 py-0 font-medium shrink-0", typeColors.bg, typeColors.text)}>
						{CAMPAIGN_TYPE_LABELS[campaign.campaign_type]}
					</Badge>
				</div>
				<div class="flex items-center gap-2 ml-[1.15rem]">
					<Badge variant="outline" class={cn("text-[0.84rem] rounded-full px-2 py-0 font-medium shrink-0", statusColors.bg, statusColors.text)}>
						{CAMPAIGN_STATUS_LABELS[campaign.status]}
					</Badge>
					<span class="text-[0.84rem] text-slate-400">
						{formatDate(campaign.start_date)} — {formatDate(campaign.end_date)}
					</span>
				</div>
			</div>

			<!-- Objectifs & Compétences -->
			<div class="w-[32%] flex flex-col gap-1.5 min-w-0 pr-2">
				{#if hasGoals || hasSkills}
					{#if hasGoals}
						<div class="flex flex-col gap-0.5">
							<div class="flex items-center gap-1.5">
								<span class="text-[0.84rem] font-semibold text-slate-500">Objectifs</span>
								{#if goalWeightLabel}
									<span class="text-[0.78rem] text-slate-400">(poids: {goalWeightLabel})</span>
								{/if}
							</div>
							<div class="flex flex-wrap gap-1">
								{#each goals.slice(0, 3) as goal}
									<span class="inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-full bg-blue-50 text-[0.84rem] text-blue-700">
										<span class="truncate text-[0.84rem]">{goal.description || 'Objectif'}</span>
										{#if goal.type}
											<span class="shrink-0 text-[0.7rem] font-semibold uppercase text-blue-400">{GOAL_TYPE_LABELS[goal.type] || goal.type}</span>
										{/if}
										{#if goal.weight != null}
											<span class="shrink-0 text-[0.7rem] font-bold text-blue-500">{Math.round(goal.weight * 100)}%</span>
										{/if}
									</span>
								{/each}
								{#if goals.length > 3}
									<span class="inline-flex items-center px-1.5 py-0.5 rounded-full bg-blue-50 text-[0.84rem] font-semibold text-blue-500">+{goals.length - 3}</span>
								{/if}
							</div>
						</div>
					{/if}
					{#if hasSkills}
						<div class="flex flex-col gap-0.5">
							<div class="flex items-center gap-1.5">
								<span class="text-[0.84rem] font-semibold text-slate-500">Compétences</span>
								{#if skillWeightLabel}
									<span class="text-[0.78rem] text-slate-400">(poids: {skillWeightLabel})</span>
								{/if}
							</div>
							<div class="flex flex-wrap gap-1">
								{#each skills.slice(0, 2) as skill}
									<span class="inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded-full bg-indigo-50 text-[0.84rem] text-indigo-700">
										<span class="truncate text-[0.84rem]">{skill.name || 'Compétence'}</span>
										{#if skill.category}
											<span class="shrink-0 text-[0.7rem] font-semibold uppercase text-indigo-400">{SKILL_CATEGORY_LABELS[skill.category] || skill.category}</span>
										{/if}
										{#if skill.weight != null}
											<span class="shrink-0 text-[0.7rem] font-bold text-indigo-500">{Math.round(skill.weight * 100)}%</span>
										{/if}
									</span>
								{/each}
								{#if skills.length > 2}
									<span class="inline-flex items-center px-1.5 py-0.5 rounded-full bg-indigo-50 text-[0.84rem] font-semibold text-indigo-500">+{skills.length - 2}</span>
								{/if}
							</div>
						</div>
					{/if}
				{:else}
					<div class="flex items-center gap-1 group-hover:opacity-80 transition-opacity">
						<svg class="size-4 text-slate-300 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
						</svg>
						<span class="text-[0.84rem] text-slate-400">Ajoutez des objectifs et compétences</span>
					</div>
				{/if}
			</div>

			<!-- Participants -->
			<div class="w-[16%] flex items-center gap-1.5">
				{#if hasParticipants}
					<div class="flex -space-x-1.5">
						{#each campaign.participants_preview?.slice(0, 4) ?? [] as p, i}
							{@const initials = getInitials(...p.name.split(' '))}
							{@const palette = getAvatarPalette(p.name)}
							{@const empPhoto = getMediaUrl(p.profile_photo)}
							<Avatar class={cn("h-9 w-9 rounded-full ring-2 ring-white shrink-0 cursor-default")}>
								<AvatarImage src={empPhoto} alt={p.name} class="object-cover" />
								<AvatarFallback class={cn("text-[0.82rem] font-bold", palette.bg, palette.text)}>{initials}</AvatarFallback>
							</Avatar>
						{/each}
						{#if campaign.participant_count > 4}
							<div class="h-9 w-9 rounded-full flex items-center justify-center text-[0.84rem] font-semibold bg-slate-100 text-slate-500 ring-2 ring-white shrink-0">
								+{campaign.participant_count - 4}
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center gap-1 group-hover:opacity-80 transition-opacity">
						<AppIcon name="users" size={16} class="text-slate-300 shrink-0" />
						<span class="text-[0.84rem] text-slate-400">Ajoutez des participants</span>
					</div>
				{/if}
			</div>

			<!-- Évaluateurs -->
			<div class="w-[16%] flex items-center gap-1.5">
				{#if hasEvaluators}
					<div class="flex -space-x-1.5">
						{#each campaign.evaluators_preview?.slice(0, 4) ?? [] as p, i}
							{@const initials = getInitials(...p.name.split(' '))}
							{@const palette = getAvatarPalette(p.name)}
							{@const empPhoto = getMediaUrl(p.profile_photo)}
							<Avatar class={cn("h-9 w-9 rounded-full ring-2 ring-white shrink-0 cursor-default")}>
								<AvatarImage src={empPhoto} alt={p.name} class="object-cover" />
								<AvatarFallback class={cn("text-[0.82rem] font-bold", palette.bg, palette.text)}>{initials}</AvatarFallback>
							</Avatar>
						{/each}
						{#if campaign.evaluator_count > 4}
							<div class="h-9 w-9 rounded-full flex items-center justify-center text-[0.84rem] font-semibold bg-slate-100 text-slate-500 ring-2 ring-white shrink-0">
								+{campaign.evaluator_count - 4}
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center gap-1 group-hover:opacity-80 transition-opacity">
						<AppIcon name="users" size={16} class="text-slate-300 shrink-0" />
						<span class="text-[0.84rem] text-slate-400">Ajoutez des évaluateurs</span>
					</div>
				{/if}
			</div>

			<!-- Actions -->
			<div class="w-[12%] flex items-center justify-end gap-1.5">
				{#if campaign.status === 'DRAFT'}
					<Button
						onclick={(ev) => {
							ev.stopPropagation();
							notification.confirm({
								title: 'Activer la campagne',
								message: `Êtes-vous sûr de vouloir activer la campagne « ${campaign.name} » ? Les évaluations seront créées automatiquement pour tous les participants.`,
								type: 'success',
								yesText: 'Activer',
								onYes: () => onActivate(campaign.id),
							});
						}}
						disabled={isActivating}
						class="h-7 px-2.5 rounded-md bg-emerald-50 text-emerald-700 hover:bg-emerald-100 text-[0.84rem] font-semibold transition-all cursor-pointer disabled:opacity-50"
					>
						<AppIcon name="play" size={13} class="mr-1" />
						Activer
					</Button>
				{/if}
				{#if campaign.status === 'ACTIVE'}
					<Button
						onclick={(ev) => {
							ev.stopPropagation();
							notification.confirm({
								title: 'Clôturer la campagne',
								message: `Êtes-vous sûr de vouloir clôturer la campagne « ${campaign.name} » ? Les évaluations seront verrouillées en lecture seule.`,
								type: 'danger',
								yesText: 'Clôturer',
								onYes: () => onClose(campaign.id),
							});
						}}
						disabled={isClosing}
						class="h-7 px-2.5 rounded-md bg-rose-50 text-rose-700 hover:bg-rose-100 text-[0.84rem] font-semibold transition-all cursor-pointer disabled:opacity-50"
					>
						<AppIcon name="lock" size={13} class="mr-1" />
						Clôturer
					</Button>
				{/if}
			</div>
		</div>
		</Tooltip.Trigger>

		{#if showTooltip}
			<Tooltip.Content side="top" align="center" class="z-50 p-0 overflow-hidden rounded-lg shadow-lg border bg-white min-w-[280px]">
				{#if hasParticipants}
					<div class="py-1.5 px-1">
						<div class="px-2.5 pb-1 text-[0.84rem] font-semibold text-slate-400">Participants</div>
						{#each campaign.participants_preview ?? [] as p}
							{@const empFullName = p.name}
							{@const empPalette = getAvatarPalette(empFullName)}
							{@const empPhoto = getMediaUrl(p.profile_photo)}
							{@const empInitials = getInitials(...p.name.split(' '))}
							<div class="flex items-center gap-2.5 px-2.5 py-1.5 rounded-md hover:bg-slate-50 transition-colors">
								<Avatar class="h-9 w-9 rounded-full border border-slate-200 shrink-0">
									<AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
									<AvatarFallback class={cn("text-[0.82rem] font-bold", empPalette.bg, empPalette.text)}>{empInitials}</AvatarFallback>
								</Avatar>
								<div class="flex flex-col min-w-0">
									<span class="text-[0.84rem] font-medium text-slate-800 truncate">{p.name}</span>
									{#if p.job_title || p.org_unit}
										<span class="text-[0.84rem] text-slate-500 truncate">{p.job_title || p.org_unit}</span>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				{/if}
				{#if hasParticipants && hasEvaluators}
					<div class="border-t border-slate-100"></div>
				{/if}
				{#if hasEvaluators}
					<div class="py-1.5 px-1">
						<div class="px-2.5 pb-1 text-[0.84rem] font-semibold text-slate-400">Évaluateurs</div>
						{#each campaign.evaluators_preview ?? [] as p}
							{@const empFullName = p.name}
							{@const empPalette = getAvatarPalette(empFullName)}
							{@const empPhoto = getMediaUrl(p.profile_photo)}
							{@const empInitials = getInitials(...p.name.split(' '))}
							<div class="flex items-center gap-2.5 px-2.5 py-1.5 rounded-md hover:bg-slate-50 transition-colors">
								<Avatar class="h-9 w-9 rounded-full border border-slate-200 shrink-0">
									<AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
									<AvatarFallback class={cn("text-[0.82rem] font-bold", empPalette.bg, empPalette.text)}>{empInitials}</AvatarFallback>
								</Avatar>
								<div class="flex flex-col min-w-0">
									<span class="text-[0.84rem] font-medium text-slate-800 truncate">{p.name}</span>
									{#if p.job_title || p.org_unit}
										<span class="text-[0.84rem] text-slate-500 truncate">{p.job_title || p.org_unit}</span>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				{/if}
				<div class="border-t px-3 py-1.5 text-slate-400 text-center bg-slate-25 flex items-center justify-center gap-3">
					<span class="text-[0.84rem]">{campaign.participant_count} participant{campaign.participant_count > 1 ? 's' : ''}</span>
					<span class="text-slate-200 text-[0.84rem]">|</span>
					<span class="text-[0.84rem]">{campaign.evaluator_count} évaluateur{campaign.evaluator_count > 1 ? 's' : ''}</span>
				</div>
			</Tooltip.Content>
		{/if}
	</Tooltip.Root>
</Tooltip.Provider>

