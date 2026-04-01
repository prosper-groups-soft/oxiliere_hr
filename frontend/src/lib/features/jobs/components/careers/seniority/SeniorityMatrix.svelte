<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import type { SeniorityLevelDefinition } from "../../../types/types";
  import SeniorityRow from "./views/SeniorityRow.svelte";

  let { onEdit, onDelete, onNew } = $props<{ 
    onEdit?: (level: SeniorityLevelDefinition) => void
    onDelete?: (level: SeniorityLevelDefinition) => void
    onNew?: () => void
  }>();

  const levels = $derived(
    [...jobsStore.seniorityLevels].sort((a, b) => a.rank - b.rank)
  );
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  {#if levels.length === 0}
    <div class="flex-1 flex items-center justify-center">
      <Empty 
        title="Aucun niveau défini" 
        description="Créez les paliers de carrière pour structurer votre entreprise."
        icon="layers"
        iconStrokeWidth={1}
        iconClass="text-indigo-600"
      >
        <EmptyButton labelElement="un niveau" onNew={onNew} />
      </Empty>
    </div>
  {:else}
    <!-- Area: Scrollable List -->
    <div class="flex-1 overflow-auto custom-scrollbar">
      {#each levels as level, i (level.id)}
        <SeniorityRow {level} index={i} {onEdit} {onDelete} />
      {/each}
    </div>

    <!-- Area: Fixed Footer (Add New) -->
    <button 
      onclick={onNew}
      class="group flex items-center justify-between p-4 bg-slate-50/50 hover:bg-slate-50 transition-all cursor-pointer border-t border-slate-200 h-16 shrink-0"
    >
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-lg border-2 border-dashed border-slate-200 text-slate-400 flex items-center justify-center transition-all group-hover:border-indigo-300 group-hover:bg-indigo-50 group-hover:text-indigo-500">
          <AppIcon name="plus" size={18} />
        </div>
        <div class="text-left">
          <span class="block text-[0.85rem] font-medium text-slate-500 group-hover:text-slate-700 transition-colors">Ajouter un nouveau palier</span>
          <span class="text-[0.65rem] font-medium text-slate-400 group-hover:text-slate-400 uppercase tracking-widest">Échelon de carrière</span>
        </div>
      </div>
      <div class="text-slate-200 group-hover:text-indigo-400 transition-colors pr-2">
        <AppIcon name="chevron-right" size={20} />
      </div>
    </button>
  {/if}
</div>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 5px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>

