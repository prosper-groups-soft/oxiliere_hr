<script lang="ts">
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import { Button } from '@/components/ui/button';
	import * as DropdownMenu from '@/components/ui/dropdown-menu';
	import { campaignStore } from '../../../stores/campaigns.svelte';
	import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_TYPE_LABELS } from '../../../constants';


	let { onCreate }: { onCreate: () => void } = $props();

	const activeFiltersCount = $derived(campaignStore.activeFiltersCount);
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
				{#if campaignStore.statusFilter}
					<span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
						1
					</span>
				{/if}
			</Button>
		</DropdownMenu.Trigger>

		<DropdownMenu.Content align="end" class="w-48 p-1 z-100">
			<DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
				Statut campagne
			</DropdownMenu.Label>

			<DropdownMenu.RadioGroup
				value={campaignStore.statusFilter}
				onValueChange={(val: string) => campaignStore.setStatusFilter(val as any)}
			>
				<DropdownMenu.RadioItem
					value=""
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					Tous les statuts
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="DRAFT"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_STATUS_LABELS.DRAFT}
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="ACTIVE"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_STATUS_LABELS.ACTIVE}
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="CLOSED"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_STATUS_LABELS.CLOSED}
				</DropdownMenu.RadioItem>
			</DropdownMenu.RadioGroup>

			{#if campaignStore.statusFilter}
				<DropdownMenu.Separator />
				<DropdownMenu.Item
					onclick={() => campaignStore.setStatusFilter('')}
					class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
				>
					<AppIcon name="x" size={16} class="text-inherit" />
					Réinitialiser
				</DropdownMenu.Item>
			{/if}
		</DropdownMenu.Content>
	</DropdownMenu.Root>

	<!-- Type Filter Dropdown -->
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			<Button
				variant="ghost"
				size="sm"
				class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
			>
				<AppIcon name="folder-tree" size={15} class="mr-1.5" />
				Par type
				{#if campaignStore.typeFilter}
					<span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
						1
					</span>
				{/if}
			</Button>
		</DropdownMenu.Trigger>

		<DropdownMenu.Content align="end" class="w-48 p-1 z-100">
			<DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
				Type de campagne
			</DropdownMenu.Label>

			<DropdownMenu.RadioGroup
				value={campaignStore.typeFilter}
				onValueChange={(val: string) => campaignStore.setTypeFilter(val as any)}
			>
				<DropdownMenu.RadioItem
					value=""
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					Tous les types
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="ANNUAL"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_TYPE_LABELS.ANNUAL}
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="SEMESTRIAL"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_TYPE_LABELS.SEMESTRIAL}
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="TRIMESTRIAL"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_TYPE_LABELS.TRIMESTRIAL}
				</DropdownMenu.RadioItem>
				<DropdownMenu.RadioItem
					value="PROBATION"
					class="rounded-lg pl-6.5! py-1.5 px-2 text-[0.86rem]! cursor-pointer"
				>
					{CAMPAIGN_TYPE_LABELS.PROBATION}
				</DropdownMenu.RadioItem>
			</DropdownMenu.RadioGroup>

			{#if campaignStore.typeFilter}
				<DropdownMenu.Separator />
				<DropdownMenu.Item
					onclick={() => campaignStore.setTypeFilter('')}
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
			onclick={() => campaignStore.resetFilters()}
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
		<AppIcon name="plus" size={16} />
		Nouvelle campagne
	</Button>
</div>

