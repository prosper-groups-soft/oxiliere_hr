<script lang="ts">
	import type { FormHostConfig, FormInstance } from '../../core/types.js';
	import * as Sheet from '@/components/ui/sheet/index.js';
	import * as Dialog from '@/components/ui/dialog/index.js';
	import * as Card from '@/components/ui/card/index.js';
	import type { Snippet } from 'svelte';
	import { notification } from '@/hr/stores/notification.svelte';

	let {
		form,
		host,
		title,
		description,
		open = $bindable(true),
		onClose,
		footer,
		children
	}: {
		form: FormInstance<any>;
		host?: FormHostConfig;
		title?: string;
		description?: string;
		open?: boolean;
		onClose?: () => void;
		/** Barre d'actions rendue dans le footer de l'hôte (sheet/drawer/dialog uniquement). */
		footer?: Snippet;
		children: Snippet;
	} = $props();

	function onOpenChange(v: boolean) {
		if (v) {
			open = true;
			return;
		}
		const h = host as any;
		if (h?.confirmUnsavedOnClose && form.isDirty) {
			notification.confirm({
				title: 'Modifications non enregistrées',
				message: 'Voulez-vous fermer quand même ?',
				type: 'warning',
				yesText: 'Fermer',
				noText: 'Continuer l\u2019édition',
				onYes: () => {
					onClose?.();
					open = false;
				},
				onNo: () => {
					open = true;
				}
			});
			return;
		}
		onClose?.();
		open = false;
	}

	const widthCls: Record<string, string> = {
		sm: 'sm:max-w-sm',
		md: 'sm:max-w-lg',
		lg: 'sm:max-w-2xl',
		xl: 'sm:max-w-4xl',
		'2xl': 'sm:max-w-6xl',
		full: 'sm:max-w-[95vw]'
	};

	const dialogCls: Record<string, string> = {
		sm: 'sm:max-w-sm',
		md: 'sm:max-w-lg',
		lg: 'sm:max-w-2xl',
		xl: 'sm:max-w-4xl',
		full: 'sm:max-w-[95vw]'
	};

	// Résolution de largeur (api §3) : préréglages nommés ci-dessus ; toute
	// autre chaîne est passée telle quelle — classe Tailwind arbitraire acceptée
	// (ex: 'sm:max-w-100', 'sm:max-w-[100rem]').
	function resolveCls(map: Record<string, string>, key: string | undefined, fallback: string): string {
		const k = key ?? fallback;
		return map[k] ?? k;
	}
</script>

{#if !host || host.type === 'inline' || host.type === 'div' || host.type === 'card'}
	{#if !host || (host as any).variant === 'card' || host.type === 'card'}
		<Card.Root>
			{#if title || description}
				<Card.Header>
					{#if title}<Card.Title>{title}</Card.Title>{/if}
					{#if description}<Card.Description>{description}</Card.Description>{/if}
				</Card.Header>
			{/if}
			<Card.Content>
				{@render children()}
			</Card.Content>
		</Card.Root>
	{:else}
		<div class={(host as any).variant === 'bordered' ? 'rounded-lg border p-4' : ''}>
			{#if title}<h3 class="text-sm font-semibold">{title}</h3>{/if}
			{#if description}<p class="text-xs text-muted-foreground">{description}</p>{/if}
			{@render children()}
		</div>
	{/if}
{:else if host.type === 'sheet' || host.type === 'drawer'}
	<Sheet.Root open={open} onOpenChange={onOpenChange}>
		<Sheet.Content
			side={host.type === 'drawer' ? 'bottom' : (host.side ?? 'right')}
			class="flex h-full flex-col overflow-hidden p-0 {resolveCls(widthCls, (host as any).width, 'md')}"
		>
			<Sheet.Header class="border-b bg-slate-50/50 px-6 py-2.5">
				{#if title}
					<Sheet.Title class="text-left text-[1rem] font-bold text-slate-900">{title}</Sheet.Title>
				{/if}
			</Sheet.Header>
			<div class="custom-scrollbar flex-1 overflow-y-auto p-6 scroll-smooth">
				{@render children()}
			</div>
			{#if footer}
				<Sheet.Footer class="flex flex-row gap-3 border-t bg-slate-50/50 px-6 py-2.5">
					{@render footer()}
				</Sheet.Footer>
			{/if}
		</Sheet.Content>
	</Sheet.Root>
{:else if host.type === 'dialog' || host.type === 'modal'}
	<Dialog.Root open={open} onOpenChange={onOpenChange}>
		<Dialog.Content class="flex max-h-[85vh] flex-col overflow-hidden p-0 {resolveCls(dialogCls, (host as any).size, 'md')}">
			<Dialog.Header class="border-b bg-slate-50/50 px-6 py-2.5">
				{#if title}
					<Dialog.Title class="text-left text-[1rem] font-bold text-slate-900">{title}</Dialog.Title>
				{/if}
			</Dialog.Header>
			<div class="custom-scrollbar flex-1 overflow-y-auto p-6 scroll-smooth">
				{@render children()}
			</div>
			{#if footer}
				<Dialog.Footer class="flex flex-row gap-3 border-t bg-slate-50/50 px-6 py-2.5">
					{@render footer()}
				</Dialog.Footer>
			{/if}
		</Dialog.Content>
	</Dialog.Root>
{/if}
