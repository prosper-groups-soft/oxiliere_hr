<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { page } from '$app/state';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from "@/components/ui/button";
  import { Separator } from "@/components/ui/separator";
  import { ui } from "@/stores/ui.svelte";

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
        class="h-8 px-2 flex items-center gap-2 hidden text-slate-400 hover:text-slate-600 hover:bg-slate-100/50 group transition-all"
      >
        <AppIcon name="prev" size={16} class="group-hover:-translate-x-0.5 transition-transform" />
        <span class="text-[0.65rem] font-bold uppercase tracking-widest opacity-70 group-hover:opacity-100">
          Retour
        </span>
      </Button>
    </div>
    
    <!-- Separator logic: visible if there is at least one action in the stack -->
    {#if ui.pageActions.length > 0}
      <Separator orientation="vertical" class="h-4 bg-slate-200 mx-1.5 hidden" />
    {/if}
  {/if}
    
  <!-- 
    DYNAMIC ACTION STACK 
    We iterate through the array of snippets registered in the UI store.
    This prevents child tabs from overwriting parent actions.
  -->
  <div class="flex items-center gap-2 mr-1">
    {#each ui.pageActions as actionSnippet}
      <div in:fade={{ duration: 200 }}>
        {@render actionSnippet()}
      </div>
    {/each}
  </div>
</div>

