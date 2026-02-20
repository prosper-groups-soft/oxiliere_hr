<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { page } from '$app/state';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from "@/components/ui/button";
  import { Separator } from "@/components/ui/separator";
  import type { Snippet } from 'svelte';

  interface Props {
    extraActions?: Snippet | null; // To add page-specific buttons
  }

  let { extraActions }: Props = $props();

  // Navigation logic
  const canGoBack = $derived(page.url.pathname !== '/');
  const handleBack = () => window.history.back();
</script>


<div class="flex items-center gap-1.5 shrink-0 h-full">

  <!-- Minimalist Back Button -->
  {#if canGoBack}
    <div in:scale={{ duration: 200, start: 0.95 }} out:fade={{ duration: 150 }}>
      <Button 
        variant="ghost" 
        size="sm" 
        onclick={handleBack}
        class="h-8 px-2 flex items-center gap-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100/50 group transition-all"
      >
        <AppIcon name="prev" size={16} class="group-hover:-translate-x-0.5 transition-transform" />
        <span class="text-[0.65rem] font-bold uppercase tracking-widest opacity-70 group-hover:opacity-100">
          Back
        </span>
      </Button>
    </div>
    {#if extraActions}
      <Separator orientation="vertical" class="h-4 bg-slate-200 mx-1.5" />
    {/if}
  {/if}
    
  <!-- Area for specific actions (Snippet) -->
  {#if extraActions}
    <div class="flex items-center gap-1 mr-1">
      {@render extraActions()}
    </div>
  {/if}
</div>

