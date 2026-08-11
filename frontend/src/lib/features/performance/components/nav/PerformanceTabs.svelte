<script lang="ts">
	import AppIcon from '@/components/layout/elements/AppIcon.svelte';
	import * as Tabs from '@/components/ui/tabs';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { cn } from '@/utilities/common/css';
  

	const TABS = [
		{ id: 'campaigns', label: 'Campagnes', icon: 'flag', path: '/performance/campaigns' },
		{ id: 'reviews', label: 'Évaluations', icon: 'file-text', path: '/performance/reviews' },
	];

	const activeTabId = $derived.by(() => {
		const tab = TABS.find(t => page.url.pathname.startsWith(t.path));
		return tab?.id || 'campaigns';
	});

	function handleTabChange(value: string) {
		const tab = TABS.find(t => t.id === value);
		if (tab) goto(tab.path);
	}

	interface ITabElements {
		[key: string]: HTMLElement | null;
	}

	let tabElements = $state<ITabElements>({
		campaigns: null,
		reviews: null,
	});
	let indicatorStyle = $state('');

	$effect(() => {
		const activeEl = tabElements[activeTabId];
		if (activeEl) {
			indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
		}
	});
</script>


<div class="bg-white border-b border-slate-100">
	<div class="px-5">
		<Tabs.Root value={activeTabId} onValueChange={handleTabChange}>
			<Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none">
				{#each TABS as tab}
					<Tabs.Trigger
						value={tab.id}
						bind:ref={tabElements[tab.id]}
						class={cn(
							"relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
							"rounded-none border-none px-1 pb-2.5 pt-2 outline-none focus-visible:ring-0",
							"font-bold group cursor-pointer text-slate-800",
							"data-[state=active]:text-primary data-[state=active]:bg-transparent",
							"data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
							"data-[state=active]:focus:bg-transparent"
						)}
					>
						<AppIcon name={tab.icon} size={18} class="text-slate-500 group-data-[state=active]:text-primary" />
						<span class="text-[0.879rem] tracking-tight">{tab.label}</span>
					</Tabs.Trigger>
				{/each}

				<!-- Sliding Indicator -->
				<div
					class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10"
					style={indicatorStyle}
				></div>
			</Tabs.List>
		</Tabs.Root>
	</div>
</div>

