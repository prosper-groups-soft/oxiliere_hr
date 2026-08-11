<script lang="ts">
	import { fade } from 'svelte/transition';
	import { Button } from '@/components/ui/button';
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import DataPagination from '@/components/layout/elements/DataPagination.svelte';
	import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
	import LoadingBar from '@/components/layout/elements/LoadingBar.svelte';
	import Empty from '@/components/shared/containers/empty/Empty.svelte';
	import SearchBar from '@/components/shared/elements/SearchBar.svelte';
	import FilterChips from '@/components/shared/elements/FilterChips.svelte';
	import {
		useAllReviewsQuery, useCampaignsQuery,
		syncReviewsStore, useDeleteReviewMutation,
		useSubmitEmployeeReviewMutation, useSubmitManagerReviewMutation,
		useAcknowledgeReviewMutation, useDisputeReviewMutation,
	} from '@/features/performance/queries/performanceQueries';
	import { notification } from '@/stores/notification.svelte';
	import { reviewsStore } from '@/features/performance/stores/reviews.svelte';
	import { REVIEW_STATUS_LABELS } from '@/features/performance/constants';
	import type { ReviewStatus, PerformanceReview } from '@/features/performance/types/types';
	import ReviewList from '@/features/performance/components/reviews/views/ReviewList.svelte';
	import ReviewSheet from '@/features/performance/components/reviews/sheets/ReviewSheet.svelte';
	import ReviewDetailPanel from '@/features/performance/components/reviews/views/ReviewDetailPanel.svelte';
	import ReviewsActions from '@/features/performance/components/reviews/actions/ReviewsActions.svelte';
	import { ui } from '@/stores/ui.svelte';
	import { get } from 'svelte/store';
	import { ERROR_MESSAGES, getFriendlyErrorMessage } from "@/constants/errors";


	// Campaigns for filter label resolution
	const campaignsQuery = useCampaignsQuery(() => 1);
	const campaigns = $derived($campaignsQuery.data?.results ?? []);

	// TanStack Query — toutes les évaluations
	const reviewsQuery = useAllReviewsQuery(
		() => reviewsStore.currentPage,
		() => ({
			status: reviewsStore.statusFilter || undefined,
			campaign_id: reviewsStore.campaignFilter || undefined,
			search: reviewsStore.searchQuery || undefined,
		})
	);

	// Mutations
	const deleteReview = useDeleteReviewMutation();
	const submitEmployee = useSubmitEmployeeReviewMutation();
	const submitManager = useSubmitManagerReviewMutation();
	const acknowledge = useAcknowledgeReviewMutation();
	const dispute = useDisputeReviewMutation();

	// Synchroniser le store avec les données de la query
	$effect(() => {
		syncReviewsStore($reviewsQuery);
	});

	// Re-fetch quand les filtres changent
	$effect(() => {
		reviewsStore.searchQuery;
		reviewsStore.statusFilter;
		reviewsStore.campaignFilter;
		reviewsStore.currentPage;
		reviewsStore.perPage;
		get(reviewsQuery).refetch();
	});

	const reviews = $derived<PerformanceReview[]>($reviewsQuery.data?.results ?? []);

	// TODO: Remplacer par l'utilisateur connecté quand l'auth sera branchée
	// 'employee' = employé évalué, 'manager' = évaluateur, 'all' = tout le monde
	const currentMode = $state<'employee' | 'manager' | 'all'>('employee');

	// Labels pour FilterChips
	function getFilterDisplayLabel(key: string, value: string): string {
		if (key === 'status') return REVIEW_STATUS_LABELS[value as ReviewStatus] || value;
		if (key === 'campaign') {
			const c = campaigns.find(c => c.id === value);
			return c?.name ?? value;
		}
		if (key === 'search') return `Recherche: "${value}"`;
		return value;
	}

	// ===== CREATE SHEET =====
	let createSheetOpen = $state(false);
	function openCreateSheet() {
		createSheetOpen = true;
	}

	// ===== EDIT SHEET (depuis le dropdown d'une ligne) =====
	let editReview = $state<PerformanceReview | null>(null);
	let editMode = $state<'employee' | 'manager'>('employee');
	let editSheetOpen = $state(false);

	function openEditSheet(review: PerformanceReview, mode: 'employee' | 'manager') {
		editReview = review;
		editMode = mode;
		editSheetOpen = true;
	}

	// ===== DETAIL SLIDE-OVER =====
	let selectedReviewId = $state<string | null>(null);

	function selectReview(review: PerformanceReview) {
		selectedReviewId = review.id;
	}

	function handleDelete(review: PerformanceReview) {
		const mutation = $deleteReview;
		notification.confirm({
			title: 'Supprimer cette évaluation ?',
			message: "Cette action est irréversible.",
			type: 'danger',
			yesText: 'Supprimer',
			onYes: async () => {
				await mutation.mutateAsync(review.id);
			},
		});
	}

	// ===== UI ACTIONS =====
	$effect(() => {
		ui.addActions('reviews', ReviewsActionsSnippet);
		return () => {
			ui.removeActions('reviews');
		};
	});
</script>


<svelte:head>
	<title>Oxiliere RH - Évaluations</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
	{@render Header()}

	<div class="flex flex-1 flex-col overflow-hidden min-h-0">
		<FilterChips
			filters={reviewsStore.filtersWithSearch}
			activeFiltersCount={reviewsStore.activeFiltersCount}
			getDisplayLabel={getFilterDisplayLabel}
			onRemove={(key, value) => {
				if (key === 'search') {
					reviewsStore.setSearchQuery('');
				} else if (key === 'status') {
					reviewsStore.setStatusFilter('');
				} else if (key === 'campaign') {
					reviewsStore.setCampaignFilter('');
				}
			}}
			onReset={() => reviewsStore.resetFilters()}
			class="py-1 pb-1.5 px-6 border-b border-slate-50"
		/>

		<!-- Overhead loading bar during refetch -->
		<LoadingBar loading={$reviewsQuery.isFetching} />

		<main class="flex flex-1 flex-col overflow-hidden min-h-0">
			{#if $reviewsQuery.isLoading && reviewsStore.serverTotalCount === 0}
				<div class="flex justify-center items-center h-full">
					<AnimateSpin text="Chargement des évaluations" />
				</div>
			{:else if $reviewsQuery.error && reviewsStore.serverTotalCount === 0}
				<div class="flex justify-center items-center h-full">
					<Empty
						icon="alert-circle"
						title="Erreur de Connexion"
						description={getFriendlyErrorMessage($reviewsQuery.error) || ERROR_MESSAGES.NETWORK.UNKNOWN}
						iconClass="text-red-400"
						iconContainerClass="bg-red-50/30"
						iconSize={28}
						iconStrokeWidth={1.3}
					>
						<Button
							onclick={() => get(reviewsQuery).refetch()}
							variant="outline"
							class="h-7 mt-2 rounded-lg transition-colors"
						>
							<AppIcon name="refresh-cw" size={16} />
							Réessayer
						</Button>
					</Empty>
				</div>
			{:else}
				<div class="flex-1 overflow-y-auto min-h-0" transition:fade={{ duration: 200 }}>
					{#if reviews.length === 0}
						<Empty
							icon="file-x"
							title="Aucune évaluation"
							description={reviewsStore.activeFiltersCount
								? "Aucune évaluation ne correspond à vos critères."
								: "Aucune évaluation n'a encore été créée."}
						>
							{#if reviewsStore.activeFiltersCount}
								<Button variant="ghost" onclick={() => reviewsStore.resetFilters()} class="h-7 bg-slate-50">
									<AppIcon name="x" size={16} class="text-slate-400" />
									Réinitialiser les filtres
								</Button>
							{:else}
								<Button onclick={openCreateSheet} class="h-7">
									<AppIcon name="plus" size={17} />
									Nouvelle évaluation
								</Button>
							{/if}
						</Empty>
					{:else}
						<ReviewList
							reviews={reviews}
							mode={currentMode}
							onSelect={selectReview}
							selectedId={selectedReviewId}
							onView={selectReview}
							onSelfAssess={(r) => openEditSheet(r, 'employee')}
							onEvaluate={(r) => openEditSheet(r, 'manager')}
							onSubmitEmployee={(r) => {
								notification.confirm({
									title: 'Soumettre à l\'évaluateur ?',
									message: 'Une fois soumise, vous ne pourrez plus modifier votre auto-évaluation.',
									type: 'info',
									yesText: 'Soumettre',
									onYes: async () => { await $submitEmployee.mutateAsync(r.id); },
								});
							}}
							onSubmitManager={(r) => {
								notification.confirm({
									title: 'Soumettre la notation ?',
									message: 'Une fois soumise, vous ne pourrez plus modifier votre évaluation.',
									type: 'info',
									yesText: 'Soumettre',
									onYes: async () => { await $submitManager.mutateAsync(r.id); },
								});
							}}
							onAcknowledge={(r) => {
								notification.confirm({
									title: 'Valider les résultats ?',
									message: 'En confirmant, vous reconnaissez avoir pris connaissance des résultats de votre évaluation.',
									type: 'success',
									yesText: 'Valider',
									onYes: async () => { await $acknowledge.mutateAsync(r.id); },
								});
							}}
							onDispute={(r) => {
								notification.confirm({
									title: 'Contester l\'évaluation ?',
									message: 'Vous êtes sur le point de contester les résultats. Expliquez les raisons ci-dessous.',
									type: 'warning',
									yesText: 'Contester',
									inputLabel: 'Motif de la contestation',
									inputValue: '',
									onYes: (reason?: string) => { if (reason) $dispute.mutateAsync({ reviewId: r.id, reason }); },
								});
							}}
							onDelete={handleDelete}
						/>
					{/if}
				</div>
			{/if}

			{#if reviewsStore.serverTotalCount > 0}
				<div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
					<DataPagination
						currentCount={reviews.length}
						totalCount={reviewsStore.serverTotalCount}
						currentPage={reviewsStore.currentPage}
						totalPages={reviewsStore.serverTotalPages}
						perPage={reviewsStore.perPage}
						onPageChange={(p) => reviewsStore.setPage(p)}
						onPerPageChange={(s) => reviewsStore.setPerPage(s)}
						onNext={() => reviewsStore.nextPage()}
						onPrev={() => reviewsStore.prevPage()}
						unitLabel="évaluations"
					/>
				</div>
			{/if}
		</main>
	</div>
</div>


<!-- ===== DETAIL SLIDE-OVER ===== -->
<ReviewDetailPanel bind:reviewId={selectedReviewId} />

<!-- ===== CREATE SHEET ===== -->
<ReviewSheet bind:open={createSheetOpen} />

<!-- ===== EDIT SHEET (depuis la ligne) ===== -->
{#if editReview}
	<ReviewSheet bind:open={editSheetOpen} review={editReview} mode={editMode} />
{/if}


<!-- ===== SNIPPETS ===== -->

{#snippet Header()}
	<div class="flex items-center px-5 py-1.5 border-b border-slate-50">
		<SearchBar
			bind:value={reviewsStore.searchQuery}
			placeholder="Rechercher une évaluation..."
			class="w-125"
			inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
			iconSize={22}
			onClear={() => reviewsStore.setSearchQuery('')}
		/>
	</div>
{/snippet}


{#snippet ReviewsActionsSnippet()}
	<ReviewsActions onCreate={openCreateSheet} campaigns={campaigns} />
{/snippet}


