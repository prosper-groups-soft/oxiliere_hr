<script lang="ts">
	import type { FieldConfig, FormInstance, LayoutConfig } from '../../core/types.js';
	import { fieldKey } from '../../core/createForm.svelte.js';
	import FieldRenderer from '../renderers/FieldRenderer.svelte';
	import Button from '@/components/ui/button/button.svelte';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';

	let {
		form,
		fields,
		layout
	}: {
		form: FormInstance<any>;
		fields: FieldConfig[];
		layout: LayoutConfig;
	} = $props();

	const byKey = $derived(new Map(fields.map((f) => [fieldKey(f), f])));

	function fieldOf(key: string) {
		return form.getField(key);
	}

	const SPAN_MD: Record<number, string> = {
		1: 'md:col-span-1', 2: 'md:col-span-2', 3: 'md:col-span-3', 4: 'md:col-span-4',
		5: 'md:col-span-5', 6: 'md:col-span-6', 7: 'md:col-span-7', 8: 'md:col-span-8',
		9: 'md:col-span-9', 10: 'md:col-span-10', 11: 'md:col-span-11', 12: 'md:col-span-12'
	};

	function keysOf(node: LayoutConfig): string[] {
		switch (node.type) {
			case 'row': return node.columns.flatMap((c) => c.fields);
			case 'column': return Array.isArray(node.fields) ? node.fields : keysOf(node.fields);
			case 'group': return node.groups.flatMap((g) => g.fields);
			case 'section': return node.sections.flatMap((s) => (Array.isArray(s.fields) ? s.fields : keysOf(s.fields)));
			case 'card': return Array.isArray(node.fields) ? node.fields : keysOf(node.fields);
			case 'tabs': return node.tabs.flatMap((t) => (Array.isArray(t.fields) ? t.fields : keysOf(t.fields)));
			case 'stepper': return node.steps.flatMap((s) => (Array.isArray(s.fields) ? s.fields : keysOf(s.fields)));
			case 'accordion': return node.items.flatMap((i) => (Array.isArray(i.fields) ? i.fields : keysOf(i.fields)));
		}
	}

	let stepIdx = $state(0);
	let stepError = $state<string | null>(null);

	async function goStep(dir: 1 | -1, stepsLen: number) {
		stepError = null;
		if (dir === 1) {
			const node = layout as Extract<LayoutConfig, { type: 'stepper' }>;
			const step = node.steps[stepIdx];
			const keys = Array.isArray(step.fields) ? step.fields : keysOf(step.fields);
			let ok = true;
			for (const k of keys) {
				const f = fieldOf(k);
				if (f && f.isVisible) {
					const valid = await f.validate();
					if (!valid) ok = false;
				}
			}
			if (!ok) { stepError = 'Veuillez corriger les erreurs avant de continuer.'; return; }
		}
		stepIdx = Math.min(Math.max(stepIdx + dir, 0), stepsLen - 1);
	}

	let openSections = $state<Record<string, boolean>>({});
	function sectionId(s: { id?: string; title: string }, idx: number) {
		return s.id ?? `${idx}-${s.title}`;
	}
	function isSectionOpen(s: { id?: string; title: string; defaultCollapsed?: boolean }, idx: number) {
		const id = sectionId(s, idx);
		return openSections[id] ?? !s.defaultCollapsed;
	}

	let openItems = $state<Record<string, boolean>>({});

	let tabValue = $state<string>('');
	$effect(() => {
		if (layout.type === 'tabs' && !tabValue) tabValue = layout.tabs[0]?.id ?? layout.tabs[0]?.label ?? '';
	});
	function activeTab(node: Extract<LayoutConfig, { type: 'tabs' }>) {
		return node.tabs.find((t) => (t.id ?? t.label) === tabValue) ?? node.tabs[0];
	}
</script>

{#snippet renderFields(keys: string[])}
	{#each keys as k (k)}
		{@const cfg = byKey.get(k)}
		{@const inst = fieldOf(k)}
		{#if cfg && inst}
			<FieldRenderer config={cfg} field={inst} {form} />
		{/if}
	{/each}
{/snippet}

{#snippet renderNode(node: LayoutConfig)}
	{#if node.type === 'row'}
		<div class="grid grid-cols-12 gap-4">
			{#each node.columns as col, i (i)}
				<div class="col-span-12 {SPAN_MD[col.span ?? 12] ?? SPAN_MD[12]}">
					<div class="grid gap-4">{@render renderFields(col.fields)}</div>
				</div>
			{/each}
		</div>
	{:else if node.type === 'column'}
		<div class="grid gap-4">
			{#if Array.isArray(node.fields)}{@render renderFields(node.fields)}
			{:else}{@render renderNode(node.fields)}{/if}
		</div>
	{:else if node.type === 'group'}
		<div class="grid gap-6">
			{#each node.groups as g (g.id ?? g.label)}
				<fieldset class="grid gap-4 rounded-lg border p-4">
					{#if g.label}<legend class="-ml-1 px-1 text-sm font-semibold">{g.label}</legend>{/if}
					{@render renderFields(g.fields)}
				</fieldset>
			{/each}
		</div>
	{:else if node.type === 'section'}
		<div class="grid gap-4">
			{#each node.sections as s, si (sectionId(s, si))}
				{@const open = isSectionOpen(s, si)}
				{@const sid = sectionId(s, si)}
				{#if s.collapsible}
					<div class="rounded-lg border">
						<button
							type="button"
							class="flex w-full cursor-pointer items-center justify-between px-4 py-3 text-left hover:bg-muted/50"
							onclick={() => (openSections[sid] = !open)}
							aria-expanded={open}
						>
							<span>
								<span class="block text-sm font-semibold">{s.title}</span>
								{#if s.description}<span class="block text-xs text-muted-foreground">{s.description}</span>{/if}
							</span>
							<ChevronDownIcon class="size-4 shrink-0 text-muted-foreground transition-transform {open ? 'rotate-180' : ''}" />
						</button>
						{#if open}
							<div class="px-4 pb-4"><div class="grid gap-4 pt-1">
								{#if Array.isArray(s.fields)}{@render renderFields(s.fields)}
								{:else}{@render renderNode(s.fields)}{/if}
							</div></div>
						{/if}
					</div>
				{:else}
					<section class="grid gap-4">
						<div>
							<h3 class="text-sm font-semibold">{s.title}</h3>
							{#if s.description}<p class="text-xs text-muted-foreground">{s.description}</p>{/if}
						</div>
						{#if Array.isArray(s.fields)}{@render renderFields(s.fields)}
						{:else}{@render renderNode(s.fields)}{/if}
					</section>
				{/if}
			{/each}
		</div>
	{:else if node.type === 'card'}
		<div class="rounded-xl border bg-card text-card-foreground shadow">
			{#if node.title || node.description}
				<div class="flex flex-col gap-1.5 p-6 pb-2">
					{#if node.title}<h3 class="font-semibold leading-none tracking-tight">{node.title}</h3>{/if}
					{#if node.description}<p class="text-sm text-muted-foreground">{node.description}</p>{/if}
				</div>
			{/if}
			<div class="grid gap-4 p-6 pt-2">
				{#if Array.isArray(node.fields)}{@render renderFields(node.fields)}
				{:else}{@render renderNode(node.fields)}{/if}
			</div>
		</div>
	{:else if node.type === 'tabs'}
		{@const tb = activeTab(node)}
		<div class="flex flex-col gap-2">
			<div class="inline-flex h-9 w-fit items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground" role="tablist">
				{#each node.tabs as t (t.id ?? t.label)}
					{@const v = t.id ?? t.label}
					<button
						type="button" role="tab" aria-selected={tabValue === v}
						class="inline-flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1 text-sm font-medium whitespace-nowrap transition-colors {tabValue === v ? 'bg-background text-foreground shadow' : 'hover:text-foreground'}"
						onclick={() => (tabValue = v)}
					>{t.label}</button>
				{/each}
			</div>
			{#if tb}
				<div class="grid gap-4 pt-2" role="tabpanel">
					{#if Array.isArray(tb.fields)}{@render renderFields(tb.fields)}
					{:else}{@render renderNode(tb.fields)}{/if}
				</div>
			{/if}
		</div>
	{:else if node.type === 'accordion'}
		<div class="grid gap-3">
			{#each node.items as item (item.id ?? item.title)}
				{@const id = item.id ?? item.title}
				{@const open = !!openItems[id]}
				<div class="rounded-lg border">
					<button
						type="button"
						class="flex w-full cursor-pointer items-center justify-between px-4 py-3 text-left hover:bg-muted/50"
						aria-expanded={open}
						onclick={() => {
							if (node.multiple) openItems[id] = !openItems[id];
							else openItems = open ? {} : { [id]: true };
						}}
					>
						<span class="text-sm font-semibold">{item.title}</span>
						<ChevronDownIcon class="size-4 shrink-0 text-muted-foreground transition-transform {open ? 'rotate-180' : ''}" />
					</button>
					{#if open}
						<div class="px-4 pb-4"><div class="grid gap-4 pt-1">
							{#if Array.isArray(item.fields)}{@render renderFields(item.fields)}
							{:else}{@render renderNode(item.fields)}{/if}
						</div></div>
					{/if}
				</div>
			{/each}
		</div>
	{:else if node.type === 'stepper'}
		{@const steps = node.steps}
		{@const step = steps[stepIdx]}
		<ol class="mb-4 flex flex-wrap items-center gap-2">
			{#each steps as s, i (s.id ?? s.label)}
				<li class="flex items-center gap-2">
					<button
						type="button"
						class="flex size-7 items-center justify-center rounded-full border text-xs font-semibold {i === stepIdx
							? 'border-primary bg-primary text-primary-foreground'
							: i < stepIdx
								? 'border-primary text-primary'
								: 'text-muted-foreground'}"
						onclick={() => { stepIdx = i; stepError = null; }}
					>{i + 1}</button>
					<span class="text-xs {i === stepIdx ? 'font-semibold' : 'text-muted-foreground'}">{s.label}</span>
					{#if i < steps.length - 1}<span class="mx-1 h-px w-6 bg-border"></span>{/if}
				</li>
			{/each}
		</ol>
		{#if step}
			<div class="grid gap-4">
				{#if step.description}<p class="text-xs text-muted-foreground">{step.description}</p>{/if}
				{#if Array.isArray(step.fields)}{@render renderFields(step.fields)}
				{:else}{@render renderNode(step.fields)}{/if}
			</div>
		{/if}
		{#if stepError}<p class="mt-2 text-xs text-destructive" role="alert">{stepError}</p>{/if}
		<div class="mt-4 flex items-center justify-between gap-2">
			<Button type="button" variant="outline" disabled={stepIdx === 0} onclick={() => goStep(-1, steps.length)}>Précédent</Button>
			{#if stepIdx < steps.length - 1}
				<Button type="button" onclick={() => goStep(1, steps.length)}>Suivant</Button>
			{:else}
				<span class="text-xs text-muted-foreground">Dernière étape — utilisez « Soumettre » ci-dessous.</span>
			{/if}
		</div>
	{/if}
{/snippet}

{@render renderNode(layout)}
