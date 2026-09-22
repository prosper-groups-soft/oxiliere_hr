<script lang="ts">
	// EmployeePicker (lot P3) — renderer riche des types `employee`/`manager`
	// (api §14 : defaultRenderer du registre). Autonome volontairement : le
	// SelectPicker générique (forms/) reste simple, le rendu métier (photo,
	// sous-titre, matricule) vit ici côté module propriétaire de la source.
	// Réutilise la logique de chargement partagée (createBusinessOptions) et les
	// primitives Select — aucun couplage inversé vers forms/.
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { resolveTypeEntity } from '@/hr/forms/core/typeRegistry.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
	import { getMediaUrl } from '@/hr/utilities/common/media';
	import { getInitials } from '@/hr/utilities/common/string';
	import { getAvatarPalette } from '@/hr/utilities/common/func';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
	import { buildFullName } from '@/hr/utilities/common/employee.utils';
	import { getEmployeeStatusConfig, getEmployeeStatusDotConfig } from '@/hr/modules/employees/constants/employeeStatus';

	let {
		config,
		field,
		form
	}: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// Rendu + spécificités orgUnit ; source/cascade déléguées à business-options.svelte.ts.
	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	const isMultiple = $derived(biz.isMultiple);
	// Les options du moteur portent aussi sublabel/raw (mapping de defineBusinessType)
	const allOpts = $derived(biz.allOpts as Opt[]);
	const isManager = $derived(config.type === 'manager');
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(Array.isArray(field.value) ? field.value.map((v) => String(v)) : []);
	const typeaheadItems = $derived(allOpts.map((o) => ({ value: String(o.value), label: o.label })));

	type Opt = { label: string; value: unknown; sublabel?: string; raw?: any };

	// ── Lecture data-aware de l'entité brute (EmployeeOut liste / profil résolu / mocks) ──
	function photoOf(raw: any): string | undefined {
		const p = raw?.profile_photo || raw?.avatar_url || raw?.avatarUrl || raw?.user?.photo;
		return p ? getMediaUrl(p) : undefined;
	}

	function statusOf(raw: any): string | undefined {
		return raw?.current_status?.status ?? (raw?.status || undefined);
	}

	function fullNameOf(o: Opt): string {
		// EmployeeRow : last/middle/first — mais la liste ne renvoie pas `name`.
		return buildFullName(o.raw) || o.label;
	}

	function jobTitleOf(raw: any): string | undefined {
		const job = raw?.job_title ?? raw?.jobTitle;
		return job ? String(job) : undefined;
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

	// ── Hydratation : valeur définie mais option absente (chargement lazy) ──
	// → resolve via le registre du type (data-aware) pour un trigger parlant.
	let resolved = $state<{ id: string; label: string; photo?: string; status?: string; job?: string } | null>(null);

	$effect(() => {
		const id = singleVal;
		if (!id || isMultiple || allOpts.some((o) => String(o.value) === id)) {
			resolved = null;
			return;
		}
		let alive = true;
		resolveTypeEntity(config.type, id)
			.then((p: any) => {
				if (!alive) return;
				resolved = {
					id,
					label: buildFullName(p) ?? p.name ?? id,
					photo: photoOf(p),
					status: statusOf(p),
					job: jobTitleOf(p)
				};
			})
			.catch(() => {
				if (alive) resolved = { id, label: id, photo: undefined };
			});
		return () => {
			alive = false;
		};
	});

	const selectedOpt = $derived(allOpts.find((o) => String(o.value) === singleVal));
	const triggerLabel = $derived(selectedOpt ? fullNameOf(selectedOpt) : resolved?.label ?? '');
	const triggerPhoto = $derived(photoOf(selectedOpt?.raw) ?? resolved?.photo);
	const triggerStatus = $derived(statusOf(selectedOpt?.raw) ?? resolved?.status);
	const triggerDot = $derived(getEmployeeStatusDotConfig(triggerStatus));
	const triggerJob = $derived(jobTitleOf(selectedOpt?.raw) ?? resolved?.job ?? undefined);

	function onQueryInput(e: Event) {
		biz.onSearchInput((e.currentTarget as HTMLInputElement).value);
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#snippet employeeRow(o: Opt)}
		{@const fullName = fullNameOf(o)}
		{@const statusCfg = getEmployeeStatusConfig(statusOf(o.raw))}
		{@const dotCfg = getEmployeeStatusDotConfig(statusOf(o.raw))}
		{@const rowPalette = getAvatarPalette(fullName || '')}
		{@const jobLine = jobTitleOf(o.raw)}
		<Select.Item value={String(o.value)} label={o.label} class="py-2">
			<span class="flex w-full items-center gap-2.5">
				<span class="relative shrink-0">
					<Avatar class="h-8 w-8 border border-slate-200">
						{#if photoOf(o.raw)}<AvatarImage src={photoOf(o.raw)} alt={fullName} class="object-cover" />{/if}
						<AvatarFallback class={rowPalette.bg + ' text-[0.77rem] font-bold'}>
							{getInitials(o.raw?.last_name, o.raw?.middle_name, o.raw?.first_name) || '—'}
						</AvatarFallback>
					</Avatar>
					<span
						class="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border border-white {dotCfg.color}"
						title={dotCfg.title}
					></span>
				</span>
				<span class="min-w-0 flex-1 leading-tight">
					<span class="flex items-center gap-1">
						{#if isManager}<AppIcon name="crown" size={14} class="shrink-0 text-amber-500" />{/if}
						<span class="truncate font-medium text-sm">{fullName}</span>
					</span>
					<span class="mt-0.5 flex items-center gap-1 text-muted-foreground">
						{#if jobLine}
							<span class="truncate text-[0.8rem]">{jobLine}</span>
						{:else}
							<AppIcon name="briefcase" size={14} class="shrink-0 text-slate-300" />
							<span class="text-slate-400 text-[0.8rem]">Fonction non affectée</span>
						{/if}
					</span>
				</span>
				<span class="ml-auto flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[0.7rem] font-semibold {statusCfg.bg} {statusCfg.color}">
					<span class="h-1.5 w-1.5 rounded-full {statusCfg.dot}"></span>
					{statusCfg.label}
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
			onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full min-w-0 text-sm" size="sm">
				{#if multiVals.length === 0}
					{#if biz.loading}
						<AnimateSpin class="size-3 border-slate-400" text="" />
					{:else}
						<span class="flex items-center gap-2 text-sm">
							<span class="text-sm">{config.placeholder || 'Sélectionner…'}</span>
						</span>
					{/if}
				{:else}
					<span class="flex w-full min-w-0 flex-nowrap items-center gap-1 overflow-hidden">
						{#each multiVals.slice(0, 2) as v (v)}
							{@const opt = allOpts.find((o) => String(o.value) === v)}
							{@const chipName = opt ? fullNameOf(opt) : v}
							<span class="flex min-w-0 items-center gap-1 rounded-full bg-muted py-0.5 pl-0.5 pr-1.5 text-xs">
								<Avatar class="h-5 w-5 border border-slate-200">
									{#if opt && photoOf(opt.raw)}
										<AvatarImage src={photoOf(opt.raw)} alt={chipName} class="object-cover" />
									{/if}
									<AvatarFallback class="text-[0.77rem] font-bold">
										{opt ? getInitials(opt.raw?.last_name, opt.raw?.middle_name, opt.raw?.first_name) || '—' : '—'}
									</AvatarFallback>
								</Avatar>
								<span class="truncate text-[0.77rem]">{chipName}</span>
							</span>
						{/each}
						{#if multiVals.length > 2}
							<span class="shrink-0 rounded-full bg-muted px-1.5 py-0.5 text-[0.85rem] text-muted-foreground">
								+{multiVals.length - 2}
							</span>
						{/if}
					</span>
				{/if}
			</Select.Trigger>
			<Select.Content
				class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0"
			>
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input
						type="text"
						placeholder="Rechercher…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
						oninput={onQueryInput}
					/>
				</div>
				{#each allOpts as o (String(o.value))}
					{@render employeeRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4">
						<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
					</p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun résultat</p>
				{/if}
				{#if biz.hasMore}
					<div class="flex justify-end px-4 pb-1.5">
						<button
							type="button"
							class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline"
							onclick={() => biz.loadMore()}
						>
							Voir plus +
						</button>
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
			onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		>
		<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
			<span class="flex w-full items-center gap-2 text-sm">
				<span class="relative shrink-0">
						<Avatar class="h-7 w-7 border border-slate-200">
							{#if triggerPhoto}<AvatarImage src={triggerPhoto} alt={triggerLabel} class="object-cover" />{/if}
							<AvatarFallback class="text-[0.77rem] bg-muted text-slate-400">
								<AppIcon name="user" size={14} class="text-slate-400" />
							</AvatarFallback>
						</Avatar>
						{#if triggerLabel}
							<span
								class="absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full border border-white {triggerDot.color}"
								title={triggerDot.title}
							></span>
						{/if}
					</span>
					{#if triggerLabel}
						<span class="flex min-w-0 flex-1 items-center gap-2">
							{#if isManager}<AppIcon name="crown" size={12} class="shrink-0 text-amber-500" />{/if}
							<span class="truncate text-sm font-medium">{triggerLabel}</span>
							{#if triggerJob}
								<span class="hidden truncate text-xs text-muted-foreground sm:inline">{triggerJob}</span>
							{/if}
						</span>
						{@const triggerStatusCfg = getEmployeeStatusConfig(triggerStatus)}
						<span class="ml-auto flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[0.65rem] font-semibold {triggerStatusCfg.bg} {triggerStatusCfg.color}">
							<span class="h-1.5 w-1.5 rounded-full {triggerStatusCfg.dot}"></span>
							{triggerStatusCfg.label}
						</span>
					{:else if biz.loading}
						<AnimateSpin class="size-3 border-slate-400" text="Chargement des employés" textPosition="right" />
					{:else}
						<span class="text-sm">{config.placeholder || 'Sélectionner…'}</span>
					{/if}
				</span>
			</Select.Trigger>
			<Select.Content
				class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0"
			>
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input
						type="text"
						placeholder="Rechercher…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
						oninput={onQueryInput}
					/>
				</div>
				{#each allOpts as o (String(o.value))}
					{@render employeeRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4">
						<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
					</p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun résultat</p>
				{/if}
				{#if biz.hasMore}
					<div class="flex justify-end px-4 pb-1.5">
						<button
							type="button"
							class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline"
							onclick={() => biz.loadMore()}
						>
							Voir plus +
						</button>
					</div>
				{/if}
						</Select.Content>
					</Select.Root>
				{/if}
	<FieldMessages {config} {field} />
</div>
