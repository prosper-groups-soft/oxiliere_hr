<script lang="ts">
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { SeniorityLevelDefinition } from "../../../../types/types";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  let { level, index, onEdit, onDelete } = $props<{
    level: SeniorityLevelDefinition;
    index: number;
    onEdit?: (level: SeniorityLevelDefinition) => void;
    onDelete?: (level: SeniorityLevelDefinition) => void;
  }>();

</script>




<div 
  in:fly={{ y: 20, duration: 400, delay: index * 50, easing: cubicOut }}
  role="none" 
  onclick={() => onEdit?.(level)}
  class="group/row relative hover:bg-hover flex items-center w-full h-18.75! shrink-0 px-0 bg-white border-b border-slate-100 transition-colors duration-150 cursor-pointer overflow-hidden"
>
  <!-- Rank Icon (Avatar-like) -->
  <div class="flex items-center min-w-0 w-[30%] shrink-0 pl-4">
    <div class="h-11 w-11 rounded-lg text-indigo-600 flex items-center justify-center font-bold text-lg shadow-fine shrink-0 border border-indigo-700/10">
      {level.rank}
    </div>
    <div class="flex flex-col min-w-0 ml-3">
      <span class="text-sm text-muted-foreground mb-0.5">
        Expertise
      </span>
      <h3 class="font-medium text-[0.83rem] text-slate-900 truncate group-hover/row:text-primary transition-colors">
        {level.name}
      </h3>
    </div>
  </div>

  <!-- Requirements chips -->
  <div class="flex items-center min-w-0 flex-1 px-4 gap-1.5 overflow-scroll">
    {#each level.requirements.slice(0, 3) as req}
      <Badge variant="outline" class="text-slate-700 truncate  gap-1.5 px-3 py-1 font-normal rounded-lg bg-slate-50 border border-slate-200/50 text-[0.78rem]">
        <AppIcon name="circle-check" size={16} class="text-emerald-600/70" strokeWidth={2} />
        {req}
      </Badge>
    {/each}
    {#if level.requirements.length > 3}
      <span class="text-[0.7rem] text-slate-400 font-bold ml-1">+{level.requirements.length - 3}</span>
    {/if}
  </div>

  <!-- Actions -->
  <div class="flex items-center gap-1.5 pr-5" onclick={(e) => e.stopPropagation()} role="none">
    <button 
      onclick={() => onEdit?.(level)}
      class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-600 hover:text-slate-700 cursor-pointer outline-none"
      title="Modifier"
    >
      <AppIcon name="edit" size={16} />
    </button>
    <button 
      onclick={() => onDelete?.(level)}
      class="p-1.5 hover:bg-red-50 rounded-md transition-colors text-red-400 hover:text-red-600 cursor-pointer outline-none"
      title="Supprimer"
    >
      <AppIcon name="trash-2" size={16} />
    </button>
  </div>
</div>

