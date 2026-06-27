<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { Snippet } from 'svelte';
  import { fade, scale } from 'svelte/transition';

  interface Props {
    src?: string;
    name: string;
    class?: string;
    iconSize?: number;
    iconStroke?: number;
    disableUploadHover?: boolean;
    onUpload: (file: File) => void;
    children: Snippet;
  }

  let { 
    src,
    name, 
    class: className, 
    iconSize = 22,
    iconStroke = 2.2, 
    disableUploadHover = false,
    onUpload, 
    children 
  }: Props = $props();
  
  let isExpanded = $state(false);
  let fileInput: HTMLInputElement | undefined = $state();

  function toggleExpand() {
    if (disableUploadHover) return;
    isExpanded = !isExpanded;
  }

  function triggerUpload() {
    fileInput?.click();
  }

  function handleFileChange(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files?.[0]) {
      onUpload(target.files[0]);
      isExpanded = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && isExpanded) isExpanded = false;
  }
</script>


<svelte:window onkeydown={handleKeydown} />

<button 
  type="button"
  class={cn(
    "relative group transition-all duration-300 block p-0 border-none bg-transparent cursor-pointer overflow-hidden", 
    className // On laisse className gérer la forme (ex: rounded-2xl)
  )}
  onclick={toggleExpand}
  aria-label="Voir la photo de profil de {name}"
>
  {@render children()}
  
  {#if !disableUploadHover}
    <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
      <div class="animate-pulse-icon text-white bg-white/20 p-2 rounded-full backdrop-blur-sm">
        <AppIcon name="camera" color="white" strokeWidth={iconStroke} size={iconSize} />
      </div>
    </div>
  {/if}
</button>

{#if isExpanded}
  <div 
    transition:fade={{ duration: 200 }}
    class="fixed inset-0 bg-black/70 flex flex-col items-center justify-center p-4 cursor-default z-100000"
    onclick={toggleExpand}
    role="presentation"
  >
    <button 
      type="button"
      class="absolute top-6 right-6 text-white/70 hover:text-white transition-colors cursor-pointer z-100000"
      onclick={(e) => {
        e.stopPropagation();
        toggleExpand();
      }}
    >
       <AppIcon name="x" size={32} strokeWidth={1.5} />
    </button>

    <div 
      transition:scale={{ duration: 300, start: 0.9 }}
      class="relative max-w-lg w-full aspect-square bg-slate-100 rounded-2xl overflow-hidden shadow-2xl border-4 border-white/10 z-100000"
      onclick={(e) => e.stopPropagation()}
      role="none" 
    >
      {#if src}
        <img src={src} alt={name} class="h-full w-full object-cover" />
      {:else}
        <div class="h-full w-full flex items-center justify-center bg-slate-200 text-slate-500">
          <AppIcon name="user" size={80} />
        </div>
      {/if}
    </div>

    <div 
      transition:fade={{ delay: 200 }}
      class="mt-8 flex gap-4 z-100000"
      onclick={(e) => e.stopPropagation()}
      role="none"
    >
      <input bind:this={fileInput} type="file" accept="image/*" class="hidden" onchange={handleFileChange} />
      <Button variant="outline" size="sm" onclick={() => isExpanded = false} class="gap-2 px-6">
        <AppIcon name="x" size={17} class="text-slate-400" />
        Fermer
      </Button>
      <Button size="sm" onclick={triggerUpload} class="gap-2 px-6">
        <AppIcon name="camera" size={17} />
        Modifier
      </Button>
    </div>
  </div>
{/if}


<style>
  @keyframes pulse-icon {
    0%, 100% {
      transform: scale(0.9);
    }
    50% {
      transform: scale(1.1);
    }
  }

  .group:hover .animate-pulse-icon {
    animation: pulse-icon 1.5s infinite ease-in-out;
  }
</style>

