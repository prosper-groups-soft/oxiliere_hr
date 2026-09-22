<script lang="ts">
	import PerformanceTabs from "@/hr/performance/components/nav/PerformanceTabs.svelte";
	let { children } = $props();
</script>


<div class="flex flex-col h-full bg-white overflow-hidden">
	<PerformanceTabs />

	<main class="flex-1 overflow-hidden relative bg-white">
		{@render children?.()}
	</main>
</div>

