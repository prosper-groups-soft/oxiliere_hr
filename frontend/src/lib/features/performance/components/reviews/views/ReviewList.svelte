<script lang="ts">
	import ReviewRow from './ReviewRow.svelte';
	import { fade } from 'svelte/transition';
	import type { PerformanceReview } from '../../../types/types';


	let {
		reviews,
		mode = 'all',
		onSelect,
		selectedId,
		onView,
		onSelfAssess,
		onEvaluate,
		onSubmitEmployee,
		onSubmitManager,
		onCalibrate,
		onAcknowledge,
		onDispute,
		onDelete,
	}: {
		reviews: PerformanceReview[];
		mode?: 'employee' | 'manager' | 'all';
		onSelect?: (review: PerformanceReview) => void;
		selectedId?: string | null;
		onView?: (review: PerformanceReview) => void;
		onSelfAssess?: (review: PerformanceReview) => void;
		onEvaluate?: (review: PerformanceReview) => void;
		onSubmitEmployee?: (review: PerformanceReview) => void;
		onSubmitManager?: (review: PerformanceReview) => void;
		onCalibrate?: (review: PerformanceReview) => void;
		onAcknowledge?: (review: PerformanceReview) => void;
		onDispute?: (review: PerformanceReview) => void;
		onDelete?: (review: PerformanceReview) => void;
	} = $props();
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">

	<!-- Column Headers -->
	<div class="sticky top-0 z-10 flex items-center h-9 px-6 bg-white border-b border-slate-100" in:fade={{ duration: 200 }}>
		<span class="w-[22%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé évalué</span>
		<span class="w-[18%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Evaluateur</span>
		<span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
		<span class="w-[16%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Campagne</span>
		<span class="w-[18%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Score</span>
		<span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Resultat</span>
		<span class="w-[8%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-2">Derniere activite</span>
		<span class="w-[6%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-end">Actions</span>
	</div>

	<div class="flex-1 overflow-auto">
		{#each reviews as review (review.id)}
			<ReviewRow
				{review}
				{mode}
				selected={review.id === selectedId}
				onClick={onSelect ? () => onSelect(review) : undefined}
				onView={onView ? () => onView(review) : undefined}
				onSelfAssess={onSelfAssess ? () => onSelfAssess(review) : undefined}
				onEvaluate={onEvaluate ? () => onEvaluate(review) : undefined}
				onSubmitEmployee={onSubmitEmployee ? () => onSubmitEmployee(review) : undefined}
				onSubmitManager={onSubmitManager ? () => onSubmitManager(review) : undefined}
				onCalibrate={onCalibrate ? () => onCalibrate(review) : undefined}
				onAcknowledge={onAcknowledge ? () => onAcknowledge(review) : undefined}
				onDispute={onDispute ? () => onDispute(review) : undefined}
				onDelete={onDelete ? () => onDelete(review) : undefined}
			/>
		{/each}
	</div>
</div>

