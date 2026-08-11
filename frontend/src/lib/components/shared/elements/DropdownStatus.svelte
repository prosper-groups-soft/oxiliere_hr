<script lang="ts">
	import { Select as SelectPrimitive } from "bits-ui";
	import { SelectContent, SelectItem } from "@/components/ui/select";
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import { cn } from "@/utilities/common/css";

	let {
		value = $bindable(''),
		options = [] as { value: string; label: string }[],
		placeholder = "Statut",
		showAllOption = true,
		allLabel = "Tous",
		class: className = "",
	}: {
		value: string;
		options: { value: string; label: string }[];
		placeholder?: string;
		showAllOption?: boolean;
		allLabel?: string;
		class?: string;
	} = $props();
</script>


<SelectPrimitive.Root bind:value>
	<SelectPrimitive.Trigger
		class={cn(
			"flex items-center justify-between gap-2 h-9.5 bg-[#f5f6f7] border border-slate-100 rounded-[18px] px-3 text-[0.9rem]",
			"data-placeholder:text-slate-400 cursor-pointer select-none whitespace-nowrap min-w-[140px]",
			"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20 transition-all",
			className
		)}
	>
		<SelectPrimitive.Value {placeholder} />
		<ChevronDownIcon class="size-4 opacity-50 shrink-0" />
	</SelectPrimitive.Trigger>

	<SelectContent>
		{#if showAllOption}
			<SelectItem value="">{allLabel}</SelectItem>
		{/if}
		{#each options as opt}
			<SelectItem value={opt.value}>{opt.label}</SelectItem>
		{/each}
	</SelectContent>
</SelectPrimitive.Root>
