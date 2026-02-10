<script lang="ts">
	import { cn } from "@/utils";

  const {
    text = "Chargement...",
    class: classNames
  }: {
    text?: string,
    class?: string
  } = $props();
</script>


<div class="flex items-center justify-center space-x-1">
  <div class={cn("animate-spin rounded-full size-5 border-b-2 border-white", classNames)}></div>
  <span class={text ? 'ml-2': ''}>{text}</span>
</div>

