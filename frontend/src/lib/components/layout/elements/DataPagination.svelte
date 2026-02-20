<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { crossfade } from 'svelte/transition';
  import { cubicInOut } from 'svelte/easing';
  import { 
    DEFAULT_PAGE_SIZE_OPTIONS, 
    PAGINATION_LABELS 
  } from "@/constants/ui/pagination";

  interface Props {
    currentCount: number;
    totalCount: number;
    currentPage: number;
    totalPages: number;
    perPage: number;
    onPageChange: (page: number) => void;
    onPerPageChange: (size: number) => void;
    onNext: () => void;
    onPrev: () => void;
    unitLabel?: string;
  }

  let { 
    currentCount, 
    totalCount, 
    currentPage, 
    totalPages, 
    perPage, 
    onPageChange, 
    onPerPageChange, 
    onNext, 
    onPrev,
    unitLabel = PAGINATION_LABELS.PROFILS
  }: Props = $props();

  // Sliding background animation
  const [send, receive] = crossfade({
    duration: 250,
    easing: cubicInOut
  });
</script>


<div class="flex items-center justify-between px-0 py-4 mt-0 border-t border-[#F3F4F6]">
  <div class="flex items-center gap-6">
    <div class="text-[0.875rem] shrink-0 tracking-tight flex items-center gap-1">
      <span class="font-bold text-indigo-600 text-[0.875rem] inline-block min-w-[1.2rem] text-center">
        {currentCount}
      </span>
      <span class="text-slate-800 font-normal text-[0.875rem]">{PAGINATION_LABELS.SUR}</span>
      <span class="font-bold text-indigo-600 text-[0.875rem] inline-block min-w-[1.2rem] text-center">
        {totalCount}
      </span>
      <span class="text-slate-800 font-normal text-[0.875rem]">{unitLabel}</span>
    </div>

    <div class="h-4 w-px bg-slate-300"></div>

    <div class="flex items-center gap-2">
      <span class="text-[0.8rem] text-slate-700 font-medium uppercase tracking-wider">{PAGINATION_LABELS.LIGNES}</span>
      <div class="relative flex items-center p-0.5 rounded-lg border border-slate-300 bg-white">
        {#each DEFAULT_PAGE_SIZE_OPTIONS as size}
          <button 
            class={cn(
              "relative h-6.5 w-6.5 text-[0.8rem] cursor-pointer rounded-md transition-colors z-10",
              perPage === size ? "text-white font-semibold" : "text-slate-600 hover:text-indigo-600"
            )}
            onclick={() => onPerPageChange(size)}
          >
            {size}

            {#if perPage === size}
              <div 
                in:receive={{ key: 'active-size' }}
                out:send={{ key: 'active-size' }}
                class="absolute inset-0 bg-indigo-600 rounded-md -z-10"
              ></div>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <div class="flex items-center gap-1.5">
    <Button 
      variant="ghost" 
      size="sm"
      class="h-7 w-7 p-0 hover:text-indigo-600 rounded-md border border-transparent hover:border-indigo-100 hover:bg-indigo-50/50 transition-all disabled:opacity-30 disabled:cursor-not-allowed disabled:pointer-events-auto"
      onclick={onPrev}
      disabled={currentPage === 1}
    >
      <AppIcon name="prev" size={18} class="shrink-0" />
    </Button>
    
    <div class="flex items-center gap-1.5 px-1">
      {#each Array(totalPages) as _, i}
        {@const pageNum = i + 1}
        <button 
          class={cn(
            "relative h-7 w-7 flex items-center justify-center font-bold rounded-md border text-[0.875rem] cursor-pointer",
            currentPage === pageNum 
              ? "text-white border-indigo-600 font-semibold transition-none bg-indigo-600" 
              : "border-slate-200 text-slate-900 hover:bg-slate-50 hover:border-slate-300 transition-all"
          )}
          onclick={() => onPageChange(pageNum)}
        >
          <span class="z-10 text-[0.84rem]">{pageNum}</span>

          {#if currentPage === pageNum}
            <div 
              in:receive={{ key: 'active-page' }}
              out:send={{ key: 'active-page' }}
              class="absolute inset-0 bg-indigo-600 rounded-[5px] -z-10"
            ></div>
          {/if}
        </button>
      {/each}
    </div>

    <Button 
      variant="ghost" 
      size="sm"
      class="h-7 w-7 p-0 flex items-center justify-center hover:text-indigo-600 rounded-md border border-transparent hover:border-indigo-100 hover:bg-indigo-50/50 transition-all disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-auto"
      onclick={onNext}
      disabled={currentPage === totalPages}
    >
      <AppIcon name="next" size={18} class="shrink-0" />
    </Button>
  </div>
</div>

