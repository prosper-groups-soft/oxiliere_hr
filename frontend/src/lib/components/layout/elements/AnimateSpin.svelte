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


<div class="flex items-center justify-center space-x-1">
  <div class={cn("animate-spin rounded-full size-5 border-b-2 border-gray-600", classNames)}></div>
  <span class={text ? 'ml-2 text-sm': ''}>{text}</span>
</div>

