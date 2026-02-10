<script lang="ts">
	import '@/css/app.css';
	import { browser } from '$app/environment';
	import PageLayout from '@/components/layout/containers/PageLayout.svelte';
	import { Toaster } from '@/components/ui/sonner';
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
	import type { Snippet } from 'svelte';
	import AppModeWatcher from './AppModeWatcher.svelte';

	let { children }: { children: Snippet } = $props();

	const queryClient = new QueryClient({
		defaultOptions: {
			queries: {
				retry: false,
				enabled: browser,
			},
		}
	});
</script>


<QueryClientProvider client={queryClient}>
	<AppModeWatcher />
	<PageLayout>
		{@render children()}
	</PageLayout>
	<Toaster richColors class="z-50" />
</QueryClientProvider>


