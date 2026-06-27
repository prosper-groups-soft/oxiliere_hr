<script lang="ts">
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { scale, slide } from "svelte/transition";
  import { cn } from "@/utilities/common/css";

  let { 
    filters, 
    activeFiltersCount,
    getDisplayLabel = (key: string, value: any) => String(value),
    onRemove,
    onReset,
    class: className = "",
    badgeClass = ""
  } = $props<{
    filters: any;
    activeFiltersCount: number;
    getDisplayLabel?: (key: string, value: any) => string;
    onRemove: (key: string, value: any) => void;
    onReset: () => void;
    class?: string;
    badgeClass?: string;
  }>();
</script>


{#if activeFiltersCount > 0}
  <div class={cn("flex flex-wrap gap-2 items-center", className)} transition:slide={{ duration: 200 }}>
    <span class="text-[0.7rem] font-bold text-slate-500 uppercase tracking-tight mr-1">Filtres :</span>
    
    {#each Object.entries(filters).filter(([_, v]) => Array.isArray(v) && v.length > 0) as [key, values]}
      {#each (values as any[]) as value}
        <div transition:scale={{ duration: 150, start: 0.9 }}>
          <Badge class={cn(
            "bg-blue-50 text-blue-600 hover:bg-blue-100 border-blue-100/50 gap-1.5 px-2.5 py-px rounded-full text-[0.8rem] font-medium transition-all",
            badgeClass
          )}>
            {getDisplayLabel(key, value)}
            <button 
              onclick={() => onRemove(key, value)} 
              class="hover:opacity-70 cursor-pointer"
            >
              <AppIcon name="x" size={14} />
            </button>
          </Badge>
        </div>
      {/each}
    {/each}

    <button 
      onclick={onReset}
      class="text-[0.8rem] text-slate-400 hover:text-red-500 transition-colors ml-1 font-medium cursor-pointer"
    >
      Effacer tout
    </button>
  </div>
{/if}

