<script lang="ts">
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import { Button } from '@/components/ui/button';
	import * as DropdownMenu from '@/components/ui/dropdown-menu';
	import { reviewsStore } from '../../../stores/reviews.svelte';
	import { REVIEW_STATUS_LABELS } from '../../../constants';
	import type { Campaign } from '../../../types/types';


	let {
		onCreate,
		campaigns = [] as Campaign[],
	}: {
		onCreate: () => void;
		campaigns?: Campaign[];
	} = $props();

	const activeFiltersCount = $derived(reviewsStore.activeFiltersCount);
</script>


<div class="flex items-center gap-2">
	<!-- Status Filter Dropdown -->
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			<Button
				variant="ghost"
				size="sm"
				class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
			>
				<AppIcon name="flag" size={15} class="mr-1.5" />
				Par statut
				{#if reviewsStore.statusFilter}
					<span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
						1
					</span>
				{/if}
			</Button>
		</DropdownMenu.Trigger>

		<DropdownMenu.Content align="end" class="w-52 p-1 z-100">
			<DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
				Statut évaluation
			</DropdownMenu.Label>

			<DropdownMenu.RadioGroup
				value={reviewsStore.statusFilter}
				onValueChange={(val: string) => reviewsStore.setStatusFilter(val as any)}
			>
				<DropdownMenu.RadioItem
					value=""
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					Tous les statuts
				</DropdownMenu.RadioItem>
				{#each Object.entries(REVIEW_STATUS_LABELS) as [key, label]}
					<DropdownMenu.RadioItem
						value={key}
						class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
					>
						{label}
					</DropdownMenu.RadioItem>
				{/each}
			</DropdownMenu.RadioGroup>

			{#if reviewsStore.statusFilter}
				<DropdownMenu.Separator />
				<DropdownMenu.Item
					onclick={() => reviewsStore.setStatusFilter('')}
					class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
				>
					<AppIcon name="x" size={16} class="text-inherit" />
					Réinitialiser
				</DropdownMenu.Item>
			{/if}
		</DropdownMenu.Content>
	</DropdownMenu.Root>

	<!-- Campaign Filter Dropdown -->
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			<Button
				variant="ghost"
				size="sm"
				class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
			>
				<AppIcon name="layers" size={15} class="mr-1.5" />
				Par campagne
				{#if reviewsStore.campaignFilter}
					<span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
						1
					</span>
				{/if}
			</Button>
		</DropdownMenu.Trigger>

		<DropdownMenu.Content align="end" class="w-64 p-1 z-100 max-h-72 overflow-y-auto">
			<DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
				Campagne d'évaluation
			</DropdownMenu.Label>

			<DropdownMenu.RadioGroup
				value={reviewsStore.campaignFilter}
				onValueChange={(val: string) => reviewsStore.setCampaignFilter(val)}
			>
				<DropdownMenu.RadioItem
					value=""
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					Toutes les campagnes
				</DropdownMenu.RadioItem>
				{#each campaigns as campaign}
					<DropdownMenu.RadioItem
						value={campaign.id}
						class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
					>
						{campaign.name}
					</DropdownMenu.RadioItem>
				{/each}
			</DropdownMenu.RadioGroup>

			{#if reviewsStore.campaignFilter}
				<DropdownMenu.Separator />
				<DropdownMenu.Item
					onclick={() => reviewsStore.setCampaignFilter('')}
					class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
				>
					<AppIcon name="x" size={16} class="text-inherit" />
					Réinitialiser
				</DropdownMenu.Item>
			{/if}
		</DropdownMenu.Content>
	</DropdownMenu.Root>

	<!-- Active Filters Badge -->
	{#if activeFiltersCount > 0}
		<button
			onclick={() => reviewsStore.resetFilters()}
			class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
		>
			<span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
			<AppIcon name="x" size={13} />
		</button>
	{/if}

	<div class="w-px h-5 bg-slate-200 mx-1"></div>

	<!-- Add Button -->
	<Button
		onclick={onCreate}
		variant="default"
		size="sm"
		class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg transition-all"
	>
		<AppIcon name="plus" size={17} />
		Nouvelle évaluation
	</Button>
</div>

