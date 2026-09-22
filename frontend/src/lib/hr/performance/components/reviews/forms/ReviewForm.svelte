<script lang="ts">
	import { Button } from '@/components/ui/button';
	import { Input } from '@/components/ui/input';
	import { Label } from '@/components/ui/label';
	import { Textarea } from '@/components/ui/textarea';
	import GoalEditor from './GoalEditor.svelte';
	import SkillEditor from './SkillEditor.svelte';
	import type { Goal, Skill } from '../../../types/types';

	interface ReviewFormData {
		employeeId: string;
		reviewerId?: string;
		reviewPeriodStart: string;
		reviewPeriodEnd: string;
		goals: Goal[];
		skills: Skill[];
		employeeComment: string;
		reviewerComment: string;
		overallRating?: number;
	}

	let {
		data = $bindable({
			employeeId: '',
			reviewerId: '',
			reviewPeriodStart: '',
			reviewPeriodEnd: '',
			goals: [] as Goal[],
			skills: [] as Skill[],
			employeeComment: '',
			reviewerComment: '',
			overallRating: undefined as number | undefined,
		} as ReviewFormData),
		onSubmit,
		submitLabel = 'Enregistrer',
		isSubmitting = false,
		employeeOptions = $bindable([] as { value: string; label: string }[]),
	}: {
		data?: ReviewFormData;
		onSubmit?: (data: ReviewFormData) => void;
		submitLabel?: string;
		isSubmitting?: boolean;
		employeeOptions?: { value: string; label: string }[];
	} = $props();
</script>


<form
	onsubmit={(e) => {
		e.preventDefault();
		onSubmit?.(data);
	}}
	class="space-y-6"
>
	<!-- Période -->
	<div class="grid grid-cols-2 gap-4">
		<div class="space-y-1.5">
			<Label for="period-start">Début période</Label>
			<Input
				id="period-start"
				type="date"
				bind:value={data.reviewPeriodStart}
				required
			/>
		</div>
		<div class="space-y-1.5">
			<Label for="period-end">Fin période</Label>
			<Input
				id="period-end"
				type="date"
				bind:value={data.reviewPeriodEnd}
				required
			/>
		</div>
	</div>

	<!-- Employé (si création admin) -->
	{#if employeeOptions.length > 0}
		<div class="space-y-1.5">
			<Label for="employee-select">Employé</Label>
			<select
				id="employee-select"
				bind:value={data.employeeId}
				class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-base shadow-fine transition-colors md:text-sm"
				required
			>
				<option value="">Sélectionner un employé</option>
				{#each employeeOptions as opt}
					<option value={opt.value}>{opt.label}</option>
				{/each}
			</select>
		</div>
	{/if}

	<!-- Note globale -->
	<div class="space-y-1.5">
		<Label for="overall-rating">Note globale</Label>
		<select
			id="overall-rating"
			bind:value={data.overallRating}
			class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-base shadow-fine transition-colors md:text-sm"
		>
			<option value={undefined}>—</option>
			{#each [1, 2, 3, 4, 5] as n}
				<option value={n}>{n}/5</option>
			{/each}
		</select>
	</div>

	<!-- Goals -->
	<GoalEditor bind:goals={data.goals} />

	<!-- Skills -->
	<SkillEditor bind:skills={data.skills} />

	<!-- Commentaires -->
	<div class="space-y-1.5">
		<Label for="employee-comment">Commentaire employé</Label>
		<Textarea
			id="employee-comment"
			bind:value={data.employeeComment}
			placeholder="Auto-évaluation..."
		/>
	</div>

	<div class="space-y-1.5">
		<Label for="reviewer-comment">Commentaire évaluateur</Label>
		<Textarea
			id="reviewer-comment"
			bind:value={data.reviewerComment}
			placeholder="Évaluation..."
		/>
	</div>

	<!-- Submit -->
	<div class="flex justify-end gap-3">
		<Button type="submit" disabled={isSubmitting}>
			{isSubmitting ? 'Enregistrement...' : submitLabel}
		</Button>
	</div>
</form>
