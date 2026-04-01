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

  // Jump to page input state
  let jumpInput = $state("");

  // Ellipsis logic
  const visiblePages = $derived.by(() => {
    const delta = 2; // Number of pages around current page
    const range: (number | string)[] = [];
    
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) range.push(i);
      return range;
    }

    range.push(1);

    if (currentPage > delta + 2) {
      range.push("...");
    }

    const start = Math.max(2, currentPage - delta);
    const end = Math.min(totalPages - 1, currentPage + delta);

    for (let i = start; i <= end; i++) {
        range.push(i);
    }

    if (currentPage < totalPages - (delta + 1)) {
      range.push("...");
    }

    range.push(totalPages);
    return range;
  });

  function handleJump(e: KeyboardEvent) {
    if (e.key === "Enter") {
      const page = parseInt(jumpInput);
      if (!isNaN(page) && page >= 1 && page <= totalPages) {
        onPageChange(page);
        jumpInput = "";
      }
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    // Only trigger if focus is inside the pagination component
    if (!(e.target instanceof HTMLElement) || !container?.contains(e.target)) return;

    if (e.key === "ArrowLeft") {
      if (currentPage > 1) onPrev();
    } else if (e.key === "ArrowRight") {
      if (currentPage < totalPages) onNext();
    }
  }

  let container = $state<HTMLElement>();
</script>


<svelte:window onkeydown={handleKeydown} />


<div 
  class="flex items-center justify-between px-0 py-2.5 mt-0"
  bind:this={container}
  role="navigation"
  aria-label="Pagination"
>
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

  <div class="flex items-center gap-4">
    <div class="flex items-center gap-1.5 bg-slate-50/50 p-1 rounded-lg border border-slate-100">
      <span class="text-[0.75rem] text-slate-500 font-medium pl-1">{PAGINATION_LABELS.GO_TO} :</span>
      <input 
        type="text" 
        placeholder={PAGINATION_LABELS.PAGE}
        bind:value={jumpInput}
        onkeydown={handleJump}
        class="h-6 w-12 text-[0.8rem] px-0.5 text-center bg-white border border-slate-200 rounded-md outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-400 transition-all font-medium text-slate-700"
      />
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
        {#each visiblePages as page}
          {#if page === "..."}
            <span class="text-slate-400 text-xs px-1 font-bold">...</span>
          {:else}
            <button 
              class={cn(
                "relative h-7 w-7 flex items-center justify-center font-bold rounded-md border text-[0.875rem] cursor-pointer",
                currentPage === page 
                  ? "text-white border-indigo-600 font-semibold transition-none bg-indigo-600" 
                  : "border-slate-200 text-slate-900 hover:bg-slate-50 hover:border-slate-300 transition-all"
              )}
              onclick={() => onPageChange(page as number)}
              aria-current={currentPage === page ? "page" : undefined}
            >
              <span class="z-10 text-[0.84rem]">{page}</span>

              {#if currentPage === page}
                <div 
                  in:receive={{ key: 'active-page' }}
                  out:send={{ key: 'active-page' }}
                  class="absolute inset-0 bg-indigo-600 rounded-[5px] -z-10"
                ></div>
              {/if}
            </button>
          {/if}
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
</div>

