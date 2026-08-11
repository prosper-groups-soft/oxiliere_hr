<script lang="ts">
	import { fade } from 'svelte/transition';
	import { Button } from '@/components/ui/button';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
	import Empty from '@/components/shared/containers/empty/Empty.svelte';
	import ReviewStatusBadge from '../../shared/ReviewStatusBadge.svelte';
	import { getInitials } from '@/utilities/common/string';
	import { getAvatarPalette } from '@/utilities/common/func';
	import { getMediaUrl } from '@/utilities/common/media';
	import { cn } from '@/utilities/common/css';
	import { useReviewDetailQuery } from '@/features/performance/queries/performanceQueries';
	import { GOAL_TYPE_LABELS, SKILL_CATEGORY_LABELS } from '@/features/performance/constants';
	import type { PerformanceReview } from '@/features/performance/types/types';


	let {
		reviewId = $bindable(null),
	}: {
		reviewId: string | null;
	} = $props();


	// ── Detail query ──
	const detailQuery = useReviewDetailQuery(() => reviewId ?? '');
	const review = $derived<PerformanceReview | null>($detailQuery.data ?? null);

	// Force refetch when reviewId changes (bridges reactivity gap with TanStack)
	$effect(() => {
		if (reviewId) {
			$detailQuery.refetch();
		}
	});

	function close() {
		reviewId = null;
	}

	const palette = $derived(review ? getAvatarPalette(review.employeeName) : null);
	const initials = $derived(review
		? getInitials(
			review.employeeLastName || review.employeeName.split(' ').slice(-1)[0] || '',
			review.employeeMiddleName || '',
			review.employeeFirstName || review.employeeName.split(' ')[0] || ''
		)
		: ''
	);

	const managerFullName = $derived(
		review ? [review.managerLastName, review.managerMiddleName, review.managerFirstName]
			.filter(Boolean)
			.join(' ') || review.managerName : ''
	);

	function formatDate(iso: string | undefined): string {
		if (!iso) return '—';
		return new Date(iso).toLocaleDateString('fr-FR', {
			day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
		});
	}

	// ── Slide transition ──
	function slideFromRight(node: Element, { duration = 250 }) {
		return {
			duration,
			css: (t: number) => `transform: translateX(${(1 - t) * 100}%); opacity: ${t};`
		};
	}
</script>


{#if reviewId !== null}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-40 bg-black/40"
		role="none"
		onclick={close}
		onkeydown={(e) => { if (e.key === 'Escape') close(); }}
		transition:fade={{ duration: 200 }}
	></div>

	<!-- Panel -->
	<div
		class="fixed top-0 right-0 z-50 h-full w-full max-w-xl bg-white shadow-2xl border-l border-slate-200 flex flex-col"
		transition:slideFromRight={{ duration: 250 }}
	>
		<!-- Header -->
		<div class="px-5 py-2 border-b border-slate-100 flex items-center justify-between shrink-0 bg-white">
			<div class="flex items-center gap-3 min-w-0">
				<span class="text-sm font-medium text-slate-700 truncate">
					{review?.employeeName ?? 'Détail'}
				</span>
			</div>

			<Button variant="ghost" size="sm" onclick={close} class="h-8 w-8 p-0 rounded-lg">
				<AppIcon name="x" size={18} class="text-slate-400" />
			</Button>
		</div>

		<!-- Scrollable content -->
		<div class="flex-1 overflow-y-auto px-5 py-4">
			{#if $detailQuery.isPending}
				<div class="flex justify-center items-center h-full">
					<AnimateSpin text="Chargement de l'évaluation" />
				</div>
			{:else if $detailQuery.error}
				<div class="flex justify-center items-center h-full">
					<Empty
						icon="alert-circle"
						title="Erreur"
						description={$detailQuery.error?.message || "Impossible de charger l'évaluation"}
						iconClass="text-red-400"
						iconContainerClass="bg-red-50/30"
						iconSize={28}
						iconStrokeWidth={1.3}
					>
						<Button onclick={() => $detailQuery.refetch()} variant="outline" class="h-7 mt-2">
							<AppIcon name="refresh-cw" />
							Réessayer
						</Button>
					</Empty>
				</div>
			{:else if review}
				<div transition:fade={{ duration: 200 }} class="space-y-5">

					<!-- Employé -->
					<section>
						<h3 class="text-[0.78rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Employé</h3>
						<div class="flex items-center gap-3">
							<Avatar class="size-10 rounded-full ring-1 ring-slate-100 shrink-0">
								<AvatarImage src={getMediaUrl(review.employeeAvatar || '')} alt={review.employeeName} class="object-cover" />
								<AvatarFallback class={cn("text-[0.9rem] font-bold", palette?.bg, palette?.text)}>
									{initials}
								</AvatarFallback>
							</Avatar>
							<div class="flex flex-col">
								<span class="text-[0.95rem] font-semibold text-slate-800">{review.employeeName}</span>
								{#if review.employeeJobTitle}
									<span class="text-[0.84rem] text-slate-500">{review.employeeJobTitle}</span>
								{/if}
							</div>
						</div>
					</section>

					<!-- Evaluateur -->
					<section>
						<h3 class="text-[0.78rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Evaluateur</h3>
						{#if review.managerName}
							<div class="flex items-center gap-3">
								<Avatar class="size-9 rounded-full ring-1 ring-slate-100 shrink-0">
									<AvatarImage src={getMediaUrl(review.managerAvatar || '')} alt={managerFullName} class="object-cover" />
									<AvatarFallback class="text-[0.84rem] font-bold bg-slate-100 text-slate-500">
										{getInitials(
											review.managerLastName || managerFullName.split(' ').slice(-1)[0] || '',
											review.managerMiddleName || '',
											review.managerFirstName || managerFullName.split(' ')[0] || ''
										)}
									</AvatarFallback>
								</Avatar>
								<span class="text-[0.9rem] font-medium text-slate-700">{managerFullName}</span>
							</div>
						{:else}
							<span class="text-slate-400 flex items-center gap-1.5">
								<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
								<span class="text-[0.84rem] text-slate-400">Aucun évaluateur assigné</span>
							</span>
						{/if}
					</section>

					<hr class="border-slate-100" />

					<!-- Statut & Campagne -->
					<section>
						<h3 class="text-[0.78rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Statut & Campagne</h3>
						<div class="space-y-2">
							<div class="flex items-center gap-2">
								<span class="text-[0.82rem] font-medium text-slate-500 w-28 shrink-0">Statut</span>
								<ReviewStatusBadge status={review.status} employeeSubmittedAt={review.employeeSubmittedAt} managerSubmittedAt={review.managerSubmittedAt} />
							</div>
							<div class="flex items-center gap-2">
								<span class="text-[0.82rem] font-medium text-slate-500 w-28 shrink-0">Campagne</span>
								<span class="text-[0.84rem] text-slate-700">{review.campaignName}</span>
							</div>
						</div>
					</section>

					<hr class="border-slate-100" />

					<!-- Scores comparés -->
					<section>
						<h3 class="text-[0.78rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Scores</h3>
						<div class="grid grid-cols-2 gap-3">
							<!-- Auto-évaluation -->
							<div class="rounded-xl border border-emerald-100 bg-emerald-50/30 p-3.5">
								<span class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[0.7rem] font-semibold text-emerald-700 mb-2">Auto-évaluation</span>
								{#if review.employeeScore}
									<div class="flex items-center gap-1.5 mt-1">
										<div class="flex">
											{#each Array(5) as _, i}
												<svg class="size-5 {i < Math.round(review.employeeScore) ? 'text-emerald-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
													<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
												</svg>
											{/each}
										</div>
										<span class="text-[0.95rem] font-bold text-emerald-700 tabular-nums">{review.employeeScore.toFixed(1)}</span>
									</div>
									{#if review.employeeSubmittedAt}
										<p class="text-[0.82rem] text-emerald-500/70 mt-1">Soumise le {formatDate(review.employeeSubmittedAt)}</p>
									{/if}
								{:else}
									<p class="text-[0.84rem] text-slate-400 mt-1">En attente</p>
								{/if}
							</div>

							<!-- Évaluation évaluateur -->
							<div class="rounded-xl border border-purple-100 bg-purple-50/30 p-3.5">
								<span class="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2 py-0.5 text-[0.7rem] font-semibold text-purple-700 mb-2">Note évaluateur</span>
								{#if review.evaluatorScore}
									<div class="flex items-center gap-1.5 mt-1">
										<div class="flex">
											{#each Array(5) as _, i}
												<svg class="size-5 {i < Math.round(review.evaluatorScore) ? 'text-purple-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
													<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
												</svg>
											{/each}
										</div>
										<span class="text-[0.95rem] font-bold text-purple-700 tabular-nums">{review.evaluatorScore.toFixed(1)}</span>
									</div>
									{#if review.managerSubmittedAt}
										<p class="text-[0.82rem] text-purple-500/70 mt-1">Soumise le {formatDate(review.managerSubmittedAt)}</p>
									{/if}
								{:else}
									<p class="text-[0.84rem] text-slate-400 mt-1">En attente</p>
								{/if}
							</div>
						</div>

						{#if review.disputed}
							<div class="mt-3 flex flex-col gap-2 rounded-xl bg-rose-50/60 border border-rose-100 px-4 py-2.5">
								<span class="inline-flex items-center gap-1.5 text-[0.84rem] font-semibold text-rose-600">
									<AppIcon name="alert-circle" size={18} class="text-rose-500 shrink-0" />
									Contesté
								</span>
								{#if review.disputeReason}
									<p class="text-[0.84rem] text-rose-700/80 ml-1">{review.disputeReason}</p>
								{/if}
							</div>
						{/if}
					</section>

					<hr class="border-slate-100" />

					<!-- Objectifs comparés -->
					<section>
						<h3 class="text-[0.8rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Objectifs</h3>
						{#if (review.goals?.length ?? 0) > 0 || (review.goalsManager?.length ?? 0) > 0}
							<div class="space-y-2">
								{#each review.goalsManager ?? review.goals ?? [] as goal, i}
									{@const empGoal = review.goals?.[i]}
									{@const mgrGoal = review.goalsManager?.[i]}
									<div class="rounded-lg border border-slate-100 bg-white overflow-hidden">
										<div class="flex items-center justify-between px-3 py-2 border-b border-slate-50">
											<div class="flex items-center gap-2 min-w-0">
												<span class="size-5 rounded-full bg-blue-50 text-[0.82rem] font-bold text-blue-600 flex items-center justify-center shrink-0">{i + 1}</span>
												<span class="text-[0.84rem] text-slate-700 truncate">{goal.description}</span>
											</div>
                      <div class="flex gap-1 items-center">
                        {#if goal.type}
                          <span class="shrink-0 inline-flex items-center rounded-full px-1.5 py-0.5 text-[0.75rem] font-medium {goal.type === 'KPI' ? 'bg-amber-50 text-amber-600' : 'bg-sky-50 text-sky-600'}">
                            {GOAL_TYPE_LABELS[goal.type]}
                          </span>
                        {/if}
                        {#if goal.weight != null}
                          <span class="text-[0.82rem] font-semibold text-blue-500 shrink-0">{Math.round(goal.weight * 100)}%</span>
                        {/if}
                      </div>
										</div>
										<div class="grid grid-cols-2 divide-x divide-slate-100">
											<!-- Colonne employé -->
											<div class="px-3 py-1.5 flex items-center gap-2 {!empGoal?.employee_rating ? 'opacity-40' : ''}">
												<span class="text-[0.82rem] font-semibold text-emerald-600">Employé</span>
												{#if empGoal?.employee_rating}
													<div class="flex items-center gap-0.5 ml-auto">
														{#each Array(5) as _, j}
															<svg class="size-4 {j < (empGoal?.employee_rating ?? 0) ? 'text-emerald-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
																<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
															</svg>
														{/each}
													</div>
												{:else}
													<span class="text-[0.8rem] text-slate-300 ml-auto">Non évalué</span>
												{/if}
											</div>
											<!-- Colonne évaluateur -->
											<div class="px-3 py-1.5 flex items-center gap-2 {!mgrGoal?.manager_rating ? 'opacity-40' : ''}">
												<span class="text-[0.82rem] font-semibold text-purple-600">Évaluateur</span>
												{#if mgrGoal?.manager_rating}
													<div class="flex items-center gap-0.5 ml-auto">
														{#each Array(5) as _, j}
															<svg class="size-4 {j < (mgrGoal?.manager_rating ?? 0) ? 'text-purple-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
																<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
															</svg>
														{/each}
													</div>
												{:else}
													<span class="text-[0.82rem] text-slate-300 ml-auto">Non évalué</span>
												{/if}
											</div>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<span class="text-slate-400 flex items-center gap-1.5">
								<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
								<span class="text-[0.84rem] text-slate-400">Aucun objectif</span>
							</span>
						{/if}
					</section>

					<hr class="border-slate-100" />

					<!-- Compétences comparées -->
					<section>
						<h3 class="text-[0.82rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Compétences</h3>
						{#if (review.skills?.length ?? 0) > 0 || (review.skillsManager?.length ?? 0) > 0}
							<div class="space-y-2">
								{#each review.skillsManager ?? review.skills ?? [] as skill, i}
									{@const empSkill = review.skills?.[i]}
									{@const mgrSkill = review.skillsManager?.[i]}
									<div class="rounded-lg border border-slate-100 bg-white overflow-hidden">
										<div class="flex items-center justify-between px-3 py-2 border-b border-slate-50">
											<div class="flex items-center gap-2 min-w-0">
												<span class="size-5 rounded-full bg-indigo-50 text-[0.82rem] font-bold text-indigo-600 flex items-center justify-center shrink-0">{i + 1}</span>
												<span class="text-[0.84rem] text-slate-700 truncate">{skill.name}</span>
											</div>
                      <div class="flex gap-1 items-center">
                        {#if skill.category}
                          <span class="shrink-0 inline-flex items-center rounded-full bg-indigo-50 px-1.5 py-0.5 text-[0.8rem] font-medium text-indigo-600">
                            {SKILL_CATEGORY_LABELS[skill.category]}
                          </span>
                        {/if}
                        {#if (skill.weight ?? empSkill?.weight) != null}
                          <span class="text-[0.82rem] font-semibold text-blue-500 shrink-0">{Math.round((skill.weight ?? empSkill?.weight ?? 0) * 100)}%</span>
                        {/if}
                      </div>
										</div>
										<div class="grid grid-cols-2 divide-x divide-slate-100">
											<!-- Colonne employé -->
											<div class="px-3 py-1.5 flex items-center gap-2 {!empSkill?.employee_level ? 'opacity-40' : ''}">
												<span class="text-[0.82rem] font-semibold text-emerald-600">Employé</span>
												{#if empSkill?.employee_level}
													<div class="flex items-center gap-0.5 ml-auto">
														{#each Array(5) as _, j}
															<svg class="size-4 {j < (empSkill?.employee_level ?? 0) ? 'text-emerald-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
																<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
															</svg>
														{/each}
													</div>
												{:else}
													<span class="text-[0.82rem] text-slate-300 ml-auto">Non évalué</span>
												{/if}
											</div>
											<!-- Colonne évaluateur -->
											<div class="px-3 py-1.5 flex items-center gap-2 {!mgrSkill?.manager_level ? 'opacity-40' : ''}">
												<span class="text-[0.82rem] font-semibold text-purple-600">Évaluateur</span>
												{#if mgrSkill?.manager_level}
													<div class="flex items-center gap-0.5 ml-auto">
														{#each Array(5) as _, j}
															<svg class="size-4 {j < (mgrSkill?.manager_level ?? 0) ? 'text-purple-400' : 'text-slate-200'}" fill="currentColor" viewBox="0 0 20 20">
																<path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
															</svg>
														{/each}
													</div>
												{:else}
													<span class="text-[0.82rem] text-slate-300 ml-auto">Non évalué</span>
												{/if}
											</div>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<span class="text-slate-400 flex items-center gap-1.5">
								<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
								<span class="text-[0.84rem] text-slate-400">Aucune compétence</span>
							</span>
						{/if}
					</section>

					<hr class="border-slate-100" />

					<!-- Commentaires -->
					<section>
						<h3 class="text-[0.78rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Commentaires</h3>
						<div class="space-y-3">
							{#if review.employeeComment}
								<div class="rounded-lg border border-emerald-100 bg-white overflow-hidden">
									<div class="flex items-center gap-2 px-3 py-2 bg-emerald-50/50 border-b border-emerald-100">
										<div class="size-6 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
											<svg class="size-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
										</div>
										<span class="text-[0.82rem] font-semibold text-emerald-700">Commentaire employé</span>
									</div>
									<p class="text-[0.84rem] text-slate-700 p-3">{review.employeeComment}</p>
								</div>
							{/if}
							{#if review.managerComment}
								<div class="rounded-lg border border-purple-100 bg-white overflow-hidden">
									<div class="flex items-center gap-2 px-3 py-2 bg-purple-50/50 border-b border-purple-100">
										<div class="size-6 rounded-full bg-purple-100 flex items-center justify-center shrink-0">
											<svg class="size-3.5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
										</div>
										<span class="text-[0.82rem] font-semibold text-purple-700">Commentaire évaluateur</span>
									</div>
									<p class="text-[0.84rem] text-slate-700 p-3">{review.managerComment}</p>
								</div>
							{:else if !review.employeeComment}
							<span class="text-slate-400 flex items-center gap-1.5">
								<AppIcon name="circle-x" size={16} class="text-slate-400 shrink-0" />
								<span class="text-[0.84rem] text-slate-400">Aucun commentaire</span>
							</span>
							{/if}
						</div>
					</section>
          
					<hr class="border-slate-100" />

					<!-- Dates -->
					<section>
						<h3 class="text-[0.78rem] font-bold uppercase tracking-widest text-[#737783] mb-3">Dates</h3>
						<div class="space-y-1.5">
							<div class="flex items-center gap-2">
								<span class="text-[0.82rem] font-medium text-slate-500 w-32 shrink-0">Création</span>
								<span class="text-[0.84rem] text-slate-700">{formatDate(review.createdAt)}</span>
							</div>
							<div class="flex items-center gap-2">
								<span class="text-[0.82rem] font-medium text-slate-500 w-32 shrink-0">Dernière activité</span>
								<span class="text-[0.84rem] text-slate-700">{formatDate(review.updatedAt)}</span>
							</div>
							{#if review.employeeSubmittedAt}
								<div class="flex items-center gap-2">
									<span class="text-[0.82rem] font-medium text-slate-500 w-32 shrink-0">Soumis employé</span>
									<span class="text-[0.84rem] text-slate-700">{formatDate(review.employeeSubmittedAt)}</span>
								</div>
							{/if}
							{#if review.managerSubmittedAt}
								<div class="flex items-center gap-2">
									<span class="text-[0.82rem] font-medium text-slate-500 w-32 shrink-0">Soumis évaluateur</span>
									<span class="text-[0.84rem] text-slate-700">{formatDate(review.managerSubmittedAt)}</span>
								</div>
							{/if}
							{#if review.acknowledgedAt}
								<div class="flex items-center gap-2">
									<span class="text-[0.82rem] font-medium text-slate-500 w-32 shrink-0">Approuvé</span>
									<span class="text-[0.84rem] text-slate-700">{formatDate(review.acknowledgedAt)}</span>
								</div>
							{/if}
						</div>
					</section>

				</div>
			{/if}
		</div>
	</div>
{/if}

