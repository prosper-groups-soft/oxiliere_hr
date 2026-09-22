<script lang="ts">
	import CampaignRow from './CampaignRow.svelte';
	import type { Campaign } from '../../../types/types';


	let {
		campaigns,
		onEdit,
		onActivate,
		onClose,
		isActivating,
		isClosing,
	}: {
		campaigns: Campaign[];
		onEdit: (campaign: Campaign) => void;
		onActivate: (campaignId: string) => void;
		onClose: (campaignId: string) => void;
		isActivating: boolean;
		isClosing: boolean;
	} = $props();
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
	<!-- Column Headers -->
	<div class="sticky top-0 z-10 flex items-center h-9 px-6 bg-white border-b border-slate-100">
		<span class="w-[24%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Campagne</span>
		<span class="w-[32%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Objectifs &amp; Compétences</span>
		<span class="w-[16%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Participants</span>
		<span class="w-[16%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Évaluateurs</span>
		<span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-2">Actions</span>
	</div>

	<div class="flex-1 overflow-auto">
		{#each campaigns as campaign (campaign.id)}
			<CampaignRow
				{campaign}
				{onEdit}
				{onActivate}
				{onClose}
				{isActivating}
				{isClosing}
			/>
		{/each}
	</div>
</div>
