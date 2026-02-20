<script lang="ts">
  import PageActions from "./PageActions.svelte";
  import type { Snippet } from 'svelte';

  interface Props {
    title?: string;
    actions?: Snippet | null;
  }

  let { title = "", actions }: Props = $props();
</script>


<div class="flex items-center justify-between h-10 px-5 border-b border-[#F3F4F6] bg-white overflow-hidden">
  <!-- LEFT: Stable Title -->
  <h1 class="text-[0.9rem] font-bold tracking-tight text-slate-800 truncate">
    {title}
  </h1>

  <!-- RIGHT: Delegated Actions -->
  <PageActions extraActions={actions} />
</div>

