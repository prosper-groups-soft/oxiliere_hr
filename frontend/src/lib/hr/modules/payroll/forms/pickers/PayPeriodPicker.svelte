<script lang="ts">
	// PayPeriodPicker — renderer riche du type `payroll` (périodes de paie).
	// Data-aware : lit le `raw` PayrollRunApiOut (period_label, start/end_date,
	// status, employee_count, gross_total). Même pattern que EmployeePicker :
	// createBusinessOptions pour la source, resolveTypeEntity pour l'hydratation.
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { resolveTypeEntity } from '@/hr/forms/core/typeRegistry.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
	import {
		RUN_LIST_STATUS_LABELS,
		RUN_LIST_STATUS_COLORS,
		backendToRunListStatus,
		periodLabelFromDates,
		type PayrollRunApiOut
	} from '@/hr/modules/payroll/types/types.js';
	import { cn } from '@/hr/utilities/common/css';

	let {
		config,
		field,
		form
	}: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	const isMultiple = $derived(biz.isMultiple);
	const allOpts = $derived(biz.allOpts as Opt[]);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(Array.isArray(field.value) ? field.value.map((v) => String(v)) : []);
	const typeaheadItems = $derived(allOpts.map((o) => ({ value: String(o.value), label: o.label })));

	type Opt = { label: string; value: unknown; sublabel?: string; raw?: PayrollRunApiOut | any };

	function rawOf(o: Opt | undefined): PayrollRunApiOut | undefined {
		return o?.raw as PayrollRunApiOut | undefined;
	}

	function periodLabel(raw?: PayrollRunApiOut): string {
		if (!raw) return '';
		// period_label backend = "YYYY-MM-DD - YYYY-MM-DD" brut → on préfère
		// toujours le libellé reformatté quand start/end sont disponibles.
		if (raw.start_date && raw.end_date) return periodLabelFromDates(raw.start_date, raw.end_date);
		return raw.period_label || raw.code;
	}

	function labelOf(o: Opt): string {
		const raw = rawOf(o);
		return (raw && periodLabel(raw)) || o.label;
	}

	function dateRange(raw?: PayrollRunApiOut): string {
		if (!raw?.start_date || !raw?.end_date) return '';
		return `${fmtDay(raw.start_date)} → ${fmtDay(raw.end_date)}`;
	}

	function periodDays(raw?: PayrollRunApiOut): number {
		if (!raw?.start_date || !raw?.end_date) return 0;
		const ms =
			new Date(raw.end_date + 'T00:00:00').getTime() - new Date(raw.start_date + 'T00:00:00').getTime();
		return ms >= 0 ? Math.round(ms / 86400000) + 1 : 0;
	}

	function fmtDay(v?: string): string {
		if (!v) return '—';
		const d = new Date(v.slice(0, 10) + 'T00:00:00');
		if (Number.isNaN(d.getTime())) return v.slice(0, 10);
		return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
	}

	function money(v: number | null | undefined): string {
		const n = Number(v);
		if (!Number.isFinite(n) || n === 0) return '';
		return n.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
	}

	function statusKey(raw?: PayrollRunApiOut): keyof typeof RUN_LIST_STATUS_LABELS {
		return backendToRunListStatus(raw?.status ?? 'DRAFT');
	}

	function handleSingle(v: string | undefined) {
		const next = v ?? '';
		field.setValue(next || null);
		config.onChange?.(next || null);
	}

	function handleMulti(v: string[] | undefined) {
		const next = v ?? [];
		field.setValue(next);
		config.onChange?.(next);
	}

	// ── Hydratation : valeur définie mais option absente → resolve via registre ──
	let resolved = $state<PayrollRunApiOut | null>(null);

	$effect(() => {
		const id = singleVal;
		if (!id || isMultiple || allOpts.some((o) => String(o.value) === id)) {
			resolved = null;
			return;
		}
		let alive = true;
		resolveTypeEntity<PayrollRunApiOut>(config.type, id)
			.then((p) => {
				if (!alive) return;
				resolved = p;
			})
			.catch(() => {
				if (alive) resolved = null;
			});
		return () => {
			alive = false;
		};
	});

	const selectedOpt = $derived(allOpts.find((o) => String(o.value) === singleVal));
	const triggerRaw = $derived(rawOf(selectedOpt) ?? resolved ?? undefined);
	const triggerLabel = $derived(triggerRaw ? periodLabel(triggerRaw) : (selectedOpt ? labelOf(selectedOpt) : resolved ? periodLabel(resolved) : ''));
	const triggerRange = $derived(dateRange(triggerRaw));
	const triggerDays = $derived(periodDays(triggerRaw));

	function onQueryInput(e: Event) {
		biz.onSearchInput((e.currentTarget as HTMLInputElement).value);
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#snippet periodRow(o: Opt)}
		{@const raw = rawOf(o)}
		{@const sk = statusKey(raw)}
		{@const sc = RUN_LIST_STATUS_COLORS[sk]}
		{@const days = periodDays(raw)}
		{@const gross = raw ? money(raw.gross_total) : ''}
		<Select.Item value={String(o.value)} label={labelOf(o)} class="py-2">
			<span class="flex w-full items-center gap-2.5">
				<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
					<AppIcon name="calendar-range" size={15} class="text-slate-500" />
				</span>
				<span class="min-w-0 flex-1 leading-tight">
					<span class="truncate text-sm font-medium capitalize">{labelOf(o)}</span>
					<span class="mt-0.5 flex items-center gap-1 text-muted-foreground">
						{#if raw?.start_date}
							<span class="truncate text-[0.8rem]">{dateRange(raw)}{#if days > 0} · {days}j{/if}</span>
						{:else}
							<span class="truncate text-[0.8rem] text-slate-400">{raw?.code ?? ''}</span>
						{/if}
					</span>
				</span>
				<span class="ml-auto flex shrink-0 flex-col items-end gap-1">
					<span class={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[0.65rem] font-semibold', sc.bg, sc.text)}>
						<span class={cn('h-1.5 w-1.5 rounded-full', sc.dot)}></span>
						{RUN_LIST_STATUS_LABELS[sk]}
					</span>
					{#if gross}
						<span class="text-[0.7rem] font-medium text-slate-500">{gross}</span>
					{:else if raw?.employee_count}
						<span class="text-[0.7rem] text-slate-400">{raw.employee_count} empl.</span>
					{/if}
				</span>
			</span>
		</Select.Item>
	{/snippet}

	{#if isMultiple}
		<Select.Root
			type="multiple"
			value={multiVals}
			onValueChange={handleMulti}
			disabled={field.isDisabled || biz.loading}
			onOpenChange={(open) => open && biz.ensureLoaded()}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full min-w-0 text-sm" size="sm">
				{#if multiVals.length === 0}
					{#if biz.loading}
						<AnimateSpin class="size-3 border-slate-400" text="" />
					{:else}
						<span class="text-sm">{config.placeholder || 'Sélectionner une période…'}</span>
					{/if}
				{:else}
					<span class="flex w-full min-w-0 items-center gap-1 overflow-hidden">
						<AppIcon name="calendar-range" size={14} class="shrink-0 text-slate-400" />
						<span class="truncate text-sm">{multiVals.length} période{multiVals.length > 1 ? 's' : ''}</span>
					</span>
				{/if}
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} oninput={onQueryInput} />
				</div>
				{#each allOpts as o (String(o.value))}
					{@render periodRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucune période</p>
				{/if}
				{#if biz.hasMore}
					<div class="flex justify-end px-4 pb-1.5">
						<button type="button" class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline" onclick={() => biz.loadMore()}>Voir plus +</button>
					</div>
				{/if}
			</Select.Content>
		</Select.Root>
	{:else}
		<Select.Root
			type="single"
			value={singleVal}
			onValueChange={handleSingle}
			disabled={field.isDisabled || biz.loading}
			items={typeaheadItems}
			allowDeselect={!config.required}
			onOpenChange={(open) => open && biz.ensureLoaded()}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex w-full items-center gap-2 text-sm">
					<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
						<AppIcon name="calendar-range" size={14} class="text-slate-500" />
					</span>
					{#if triggerLabel}
						<span class="flex min-w-0 flex-1 items-center gap-2">
							<span class="truncate text-sm font-medium capitalize">{triggerLabel}</span>
							{#if triggerRange}
								<span class="hidden truncate text-xs text-muted-foreground sm:inline">{triggerRange}{#if triggerDays > 0} · {triggerDays}j{/if}</span>
							{/if}
						</span>
						{@const tsk = statusKey(triggerRaw)}
						{@const tsc = RUN_LIST_STATUS_COLORS[tsk]}
						<span class={cn('ml-auto hidden shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[0.65rem] font-semibold sm:inline-flex', tsc.bg, tsc.text)}>
							<span class={cn('h-1.5 w-1.5 rounded-full', tsc.dot)}></span>
							{RUN_LIST_STATUS_LABELS[tsk]}
						</span>
					{:else if biz.loading}
						<AnimateSpin class="size-3 border-slate-400" text="Chargement des périodes" textPosition="right" />
					{:else}
						<span class="text-sm">{config.placeholder || 'Sélectionner une période…'}</span>
					{/if}
				</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} oninput={onQueryInput} />
				</div>
				{#each allOpts as o (String(o.value))}
					{@render periodRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucune période</p>
				{/if}
				{#if biz.hasMore}
					<div class="flex justify-end px-4 pb-1.5">
						<button type="button" class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline" onclick={() => biz.loadMore()}>Voir plus +</button>
					</div>
				{/if}
			</Select.Content>
		</Select.Root>
	{/if}
	<FieldMessages {config} {field} />
</div>
