<script lang="ts">
	import { cn } from "@/utilities/common/css";

  const {
    text = "Chargement...",
    class: classNames,
    textPosition = 'bottom'
  }: {
    text?: string,
    class?: string,
    textPosition?: 'bottom' | 'top' | 'left' | 'right'
  } = $props();

  const flexDirection = $derived({
    bottom: 'flex-col',
    top: 'flex-col-reverse',
    left: 'flex-row-reverse',
    right: 'flex-row'
  }[textPosition]);

  const textMargin = $derived({
    bottom: 'mt-2',
    top: 'mb-2',
    left: 'mr-2',
    right: 'ml-2'
  }[textPosition]);
</script>


<div class={cn("flex items-center justify-center", flexDirection)}>
  <div class={cn("animate-spin rounded-full size-5 border-b-2 border-gray-600", classNames)}></div>
  {#if text}
    <span class={cn("text-[0.84rem] text-slate-300", textMargin)}>{text}</span>
  {/if}
</div>

