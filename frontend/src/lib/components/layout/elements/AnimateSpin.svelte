<script lang="ts">
	import { cn } from "@/utilities/common/css";

  const {
    text = "Chargement...",
    class: classNames
  }: {
    text?: string,
    class?: string
  } = $props();
</script>


<div class="flex items-center flex-col justify-center space-x-1">
  <div class={cn("animate-spin rounded-full size-5 border-b-2 border-gray-600", classNames)}></div>
  <span class={text ? 'ml-2 text-[0.84rem] text-slate-300 mt-2.5': ''}>{text}</span>
</div>

