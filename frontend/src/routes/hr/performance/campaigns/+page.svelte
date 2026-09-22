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
	import { useCampaignsQuery, useActivateCampaignMutation, 
           useCloseCampaignMutation, syncCampaignsStore 
  } from '@/hr/performance/queries/performanceQueries';
	import { campaignStore } from '@/hr/performance/stores/campaigns.svelte';
	import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_TYPE_LABELS } from '@/hr/performance/constants';
	import type { Campaign } from '@/hr/performance/types/types';
	import CampaignSheet from '@/hr/performance/components/campaigns/sheets/CampaignSheet.svelte';
	import CampaignList from '@/hr/performance/components/campaigns/views/CampaignList.svelte';
	import CampaignsActions from '@/hr/performance/components/campaigns/actions/CampaignsActions.svelte';
	import { ui } from '@/stores/ui.svelte';
	import { get } from 'svelte/store';
	import { ERROR_MESSAGES, getFriendlyErrorMessage } from "@/constants/errors";


	// TanStack Query — les données restent dans le cache TanStack
	const campaignsQuery = useCampaignsQuery(
		() => campaignStore.currentPage,
		() => ({
			status: campaignStore.statusFilter || undefined,
			campaign_type: campaignStore.typeFilter || undefined,
			search: campaignStore.searchQuery || undefined,
		})
	);

	// Synchroniser le store avec les données de la query
	$effect(() => {
		syncCampaignsStore($campaignsQuery);
	});

	// Re-fetch quand les filtres changent
	$effect(() => {
		campaignStore.searchQuery;
		campaignStore.statusFilter;
		campaignStore.typeFilter;
		campaignStore.currentPage;
		campaignStore.perPage;
		get(campaignsQuery).refetch();
	});

	// Enregistrer les actions dans le store UI
	$effect(() => {
		ui.addActions('campaigns', CampaignsActionsSnippet);
		return () => {
			ui.removeActions('campaigns');
		};
	});

	const campaigns = $derived<Campaign[]>($campaignsQuery.data?.results ?? []);
	const count = $derived($campaignsQuery.data?.count ?? 0);

	// Labels pour FilterChips
	function getFilterDisplayLabel(key: string, value: string): string {
		if (key === 'status') return CAMPAIGN_STATUS_LABELS[value as keyof typeof CAMPAIGN_STATUS_LABELS] || value;
		if (key === 'campaign_type') return CAMPAIGN_TYPE_LABELS[value as keyof typeof CAMPAIGN_TYPE_LABELS] || value;
		if (key === 'search') return `Recherche: "${value}"`;
		return value;
	}

	// Sheet state
	let sheetOpen = $state(false);
	let editingCampaign = $state<Campaign | null>(null);

	function openCreateSheet() {
		editingCampaign = null;
		sheetOpen = true;
	}

	function openEditSheet(campaign: Campaign) {
		editingCampaign = campaign;
		sheetOpen = true;
	}

	function handleSheetClose() {
		sheetOpen = false;
		editingCampaign = null;
	}

	// Mutations
	const activateMutation = useActivateCampaignMutation();
	const closeMutation = useCloseCampaignMutation();

	const activateState = $derived($activateMutation);
	const closeState = $derived($closeMutation);

	async function handleActivate(campaignId: string) {
		$activateMutation.mutate(campaignId);
	}

	async function handleClose(campaignId: string) {
		$closeMutation.mutate(campaignId);
	}
</script>


<svelte:head>
	<title>Oxiliere RH - Campagnes</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
	{@render Header()}

	<div class="flex flex-1 flex-col overflow-hidden min-h-0">
		<FilterChips
			filters={campaignStore.filtersWithSearch}
			activeFiltersCount={campaignStore.activeFiltersCount}
			getDisplayLabel={getFilterDisplayLabel}
			onRemove={(key, value) => {
				if (key === 'search') {
					campaignStore.setSearchQuery('');
				} else if (key === 'status') {
					campaignStore.setStatusFilter('');
				} else if (key === 'campaign_type') {
					campaignStore.setTypeFilter('');
				}
			}}
			onReset={() => campaignStore.resetFilters()}
			class="py-1 pb-1.5 px-6 border-b border-slate-50"
		/>

		<!-- Overhead loading bar during refetch -->
		<LoadingBar loading={$campaignsQuery.isFetching} />

		<main class="flex flex-1 flex-col overflow-hidden min-h-0">
			<!-- Loading state -->
			{#if $campaignsQuery.isLoading && campaignStore.serverTotalCount === 0}
				<div class="flex justify-center items-center h-full">
					<AnimateSpin text="Chargement des campagnes" />
				</div>

			<!-- Error state -->
			{:else if $campaignsQuery.error && campaignStore.serverTotalCount === 0}
				<div class="flex justify-center items-center h-full">
					<Empty
						icon="alert-circle"
						title="Erreur de Connexion"
						description={getFriendlyErrorMessage($campaignsQuery.error) || ERROR_MESSAGES.NETWORK.UNKNOWN}
						iconClass="text-red-400"
						iconContainerClass="bg-red-50/30"
						iconSize={28}
						iconStrokeWidth={1.3}
					>
						<Button
							onclick={() => get(campaignsQuery).refetch()}
							variant="outline"
							class="h-7 mt-2 rounded-lg transition-colors"
						>
							<AppIcon name="refresh-cw" size={16} />
							Réessayer
						</Button>
					</Empty>
				</div>

			<!-- Content state -->
			{:else}
				<div class="flex-1 overflow-y-auto min-h-0" transition:fade={{ duration: 200 }}>
					{#if campaigns.length === 0}
						<Empty
							icon="flag"
							title="Aucune campagne"
							description={campaignStore.activeFiltersCount
								? "Aucune campagne ne correspond à vos critères."
								: "Créez votre première campagne d'évaluation pour commencer."}
						>
							{#if campaignStore.activeFiltersCount}
								<Button variant="ghost" onclick={() => campaignStore.resetFilters()} class="h-7 bg-slate-50">
									<AppIcon name="x" size={16} class="text-slate-400" />
									Réinitialiser les filtres
								</Button>
							{:else}
								<Button onclick={openCreateSheet} class="h-7">
									<AppIcon name="plus" size={16} />
									Nouvelle campagne
								</Button>
							{/if}
						</Empty>
					{:else}
						<CampaignList
							{campaigns}
							onEdit={openEditSheet}
							onActivate={handleActivate}
							onClose={handleClose}
							isActivating={activateState.isPending}
							isClosing={closeState.isPending}
						/>
					{/if}
				</div>
			{/if}

			<!-- Pagination -->
			{#if campaignStore.serverTotalCount > 0}
				<div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
					<DataPagination
						currentCount={campaigns.length}
						totalCount={campaignStore.serverTotalCount}
						currentPage={campaignStore.currentPage}
						totalPages={campaignStore.serverTotalPages}
						perPage={campaignStore.perPage}
						onPageChange={(p) => campaignStore.setPage(p)}
						onPerPageChange={(s) => campaignStore.setPerPage(s)}
						onNext={() => campaignStore.nextPage()}
						onPrev={() => campaignStore.prevPage()}
						unitLabel="campagnes"
					/>
				</div>
			{/if}
		</main>
	</div>
</div>


{#snippet Header()}
	<div class="flex items-center px-5 py-1.5 border-b border-slate-50">
		<SearchBar
			bind:value={campaignStore.searchQuery}
			placeholder="Rechercher une campagne..."
			class="w-125"
			inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
			iconSize={22}
			onClear={() => campaignStore.setSearchQuery('')}
		/>
	</div>
{/snippet}


<!-- WRAPPER FOR ui.addActions -->
{#snippet CampaignsActionsSnippet()}
	<CampaignsActions onCreate={openCreateSheet} />
{/snippet}


<CampaignSheet
	bind:open={sheetOpen}
	campaign={editingCampaign}
	onclose={handleSheetClose}
/>

