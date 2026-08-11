<script lang="ts">
  import { Label } from '@/components/ui/label';
  import { cn } from '@/utilities/common/css';

  let {
    label,
    id,
    hint,
    class: className,
    children,
  }: {
    label: string;
    id?: string;
    hint?: string;
    class?: string;
    children?: import('svelte').Snippet;
  } = $props();
</script>


<div class={cn('space-y-1.5', className)}>
  <Label {id} class="block text-[0.78rem] font-bold text-slate-500 uppercase tracking-wider mb-1.5">
    {label}
  </Label>
  {@render children?.()}
  {#if hint}
    <p class="text-[0.82rem] text-slate-400 mt-0.5">{hint}</p>
  {/if}
</div>

