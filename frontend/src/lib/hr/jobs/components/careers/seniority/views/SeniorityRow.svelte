<script lang="ts">
  import { fade } from 'svelte/transition';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { SeniorityLevelDefinition } from "../../../../types/types";
  import { STATIC_SENIORITY_COLORS } from "../../../../stores/jobs.svelte";

  let { level, onEdit, onDelete } = $props<{
    level: SeniorityLevelDefinition;
    index: number;
    onEdit?: (level: SeniorityLevelDefinition) => void;
    onDelete?: (level: SeniorityLevelDefinition) => void;
  }>();

  // Extraire les classes de couleur pour le rang
  const colorClass = $derived(STATIC_SENIORITY_COLORS[level.level] || 'bg-slate-100 text-slate-700');
</script>


<div 
  role="none" 
  onclick={() => onEdit?.(level)}
  class="flex items-center gap-4 w-full py-3 px-4 pr-8 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer"
  in:fade={{ duration: 300 }}
>
  <!-- Rang avec couleur -->
  <div class="w-9 h-9 rounded-md flex items-center justify-center text-sm font-semibold shrink-0 {colorClass}">
    {level.rank}
  </div>

  <!-- Code et Label -->
  <div class="w-70 shrink-0">
    <div class="text-xs text-slate-500">{level.level}</div>
    <div class="text-sm font-medium text-slate-900">{level.label}</div>
  </div>

  <!-- Exigences et Actions regroupés -->
  <div class="flex items-center gap-4 flex-1 min-w-0 justify-between">
    <div class="min-w-0 flex-1 flex items-center gap-1.5">
      {#if level.requirements.length === 0}
        <span class="text-[0.82rem] text-slate-400">—</span>
      {:else}
        {#each level.requirements.slice(0, 3) as req}
          <span class="truncate text-[0.82rem] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full font-medium flex items-center justify-center gap-1.5">
            <AppIcon name="circle-check" size={16} class="text-emerald-500" strokeWidth={1.7} />
            {req}
          </span>
        {/each}
        {#if level.requirements.length > 3}
          <span class="text-slate-400 text-[0.82rem]">+{level.requirements.length - 3}</span>
        {/if}
      {/if}
    </div>
    
    <!-- Actions -->
    <div class="flex items-center gap-3 shrink-0" onclick={(e) => e.stopPropagation()} role="none">
      <button 
        onclick={() => onEdit?.(level)}
        class="text-slate-700 hover:text-indigo-600 cursor-pointer"
        title="Modifier"
      >
        <AppIcon name="edit" size={18} />
      </button>
      <button 
        onclick={() => onDelete?.(level)}
        class="text-red-500 hover:text-red-600 cursor-pointer"
        title="Supprimer"
      >
        <AppIcon name="trash-2" size={18} />
      </button>
    </div>
  </div>
</div>

