<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utils";
  import { DEFAULT_PAGE_SIZE_OPTIONS, PAGINATION_LABELS } from "@/constants/pagination";

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
    unitLabel?: string; // Optionnel, ex: "profils", "documents"
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
</script>


<div class="flex items-center justify-between px-0 py-4 mt-0 border-t border-[#F3F4F6]">
  <div class="flex items-center gap-6">
    <div class="text-[11px] shrink-0 tracking-tight flex items-center gap-1">
      <span class="font-bold text-indigo-600 text-[13px] inline-block min-w-[1.2rem] text-center">
        {currentCount}
      </span>
      <span class="text-slate-600 font-normal text-[13px]">{PAGINATION_LABELS.SUR}</span>
      <span class="font-bold text-indigo-600 text-[13px] inline-block min-w-[1.2rem] text-center">
        {totalCount}
      </span>
      <span class="text-slate-600 font-normal text-[13px]">{unitLabel}</span>
    </div>

    <div class="h-4 w-[1px] bg-slate-300"></div>

    <div class="flex items-center gap-2">
      <span class="text-[11px] text-slate-700 font-medium uppercase tracking-wider">{PAGINATION_LABELS.LIGNES}</span>
      <div class="flex items-center bg-slate-50 p-0.5 rounded-lg border border-slate-100">
        {#each DEFAULT_PAGE_SIZE_OPTIONS as size}
          <button 
            class={cn(
              "h-6 px-2 text-[11px] cursor-pointer font-bold rounded-md transition-all",
              perPage === size 
                ? "bg-indigo-600 text-white shadow-sm shadow-indigo-100" 
                : "text-slate-500 hover:text-indigo-600"
            )}
            onclick={() => onPerPageChange(size)}
          >
            {size}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <div class="flex items-center gap-1.5">
    <Button 
      variant="ghost" 
      size="sm"
      class="h-8 w-8 p-0 text-slate-400 hover:text-indigo-600 rounded-[6px] border border-transparent hover:border-indigo-100 hover:bg-indigo-50/50 transition-all disabled:opacity-30 disabled:pointer-events-auto disabled:cursor-not-allowed"
      onclick={onPrev}
      disabled={currentPage === 1}
    >
      <AppIcon name="prev" size={18} class="shrink-0" />
    </Button>
    
    <div class="flex items-center gap-1.5 px-1">
      {#each Array(totalPages) as _, i}
        <Button 
          variant="ghost"
          size="sm"
          class={cn(
            "h-8 w-8 p-0 text-[12px] font-bold rounded-[6px] border transition-all",
            currentPage === i + 1 
              ? "bg-indigo-600 border-indigo-600 text-white shadow-indigo-200" 
              : "border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300"
          )}
          onclick={() => onPageChange(i + 1)}
        >
          <span class="inline-block w-4 text-center">{i + 1}</span>
        </Button>
      {/each}
    </div>

    <Button 
      variant="ghost" 
      size="sm"
      class="h-8 w-8 p-0 flex items-center justify-center text-slate-400 hover:text-indigo-600 rounded-[6px] border border-transparent hover:border-indigo-100 hover:bg-indigo-50/50 transition-all disabled:opacity-30 disabled:pointer-events-auto disabled:cursor-not-allowed"
      onclick={onNext}
      disabled={currentPage === totalPages}
    >
      <AppIcon name="next" size={18} class="shrink-0" />
    </Button>
  </div>
</div>

