<script lang="ts">
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { positionsStore } from "../../../stores/positionsStore.svelte";
  import type { JobPosition } from "../../../types/types";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import PositionCard from "./views/PositionCard.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";

  let {
    onEdit,
    onDelete,
    onNew
  } = $props<{
    onEdit?: (pos: JobPosition) => void,
    onDelete?: (pos: JobPosition) => void,
    onNew?: () => void
  }>();
</script>


<div class="flex-1 overflow-auto custom-scrollbar flex flex-col">
  <FilterChips 
    filters={positionsStore.filters}
    activeFiltersCount={positionsStore.activeFiltersCount}
    getDisplayLabel={(key, value) => key === 'department' ? (jobsStore.getDepartmentById(value)?.name || value) : (jobsStore.seniorityLabels[value] || value)}
    onRemove={(key, value) => positionsStore.toggleFilter(key as any, value)}
    onReset={() => positionsStore.resetFilters()}
    class="bg-white/40 border-b border-slate-100/60 sticky top-0 z-10 backdrop-blur-sm py-3"
    badgeClass="bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border-indigo-100/50 text-[0.78rem]"
  />

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 flex-1">
    {#each positionsStore.filteredPositions as pos, i (pos.id)}
      <div class="col-span-full p-4 gap-5">
        <PositionCard {pos} index={i} {onEdit} {onDelete} />
      </div>
    {:else}
      <div class="col-span-full flex items-center justify-center">
        <Empty 
          title="Aucun poste ne correspond"
          description="Ajustez vos filtres ou créez un nouveau poste."
          icon="inbox"
          iconStrokeWidth={1}
          iconClass="text-primary"
        >
          <EmptyButton labelElement="un poste" onNew={onNew} />
        </Empty>
      </div>
    {/each}

    <!-- Add New Card Skeleton (Seniority Style) -->
    {#if positionsStore.filteredPositions.length > 0}
      <button 
        onclick={onNew}
        class="group relative border-2 border-dashed border-slate-200 rounded-[24px] p-5 flex flex-col items-center justify-center gap-3 hover:border-primary/30 hover:bg-white transition-all duration-300 min-h-[280px] cursor-pointer"
      >
        <div class="h-12 w-12 rounded-2xl bg-slate-50 text-slate-300 flex items-center justify-center transition-all duration-300 group-hover:bg-primary/5 group-hover:text-primary group-hover:scale-110">
          <AppIcon name="plus" size={24} />
        </div>
        <div class="text-center">
          <span class="block text-[0.9rem] font-black text-slate-400 group-hover:text-slate-600 transition-colors">Nouveau poste</span>
          <span class="text-[0.7rem] font-bold text-slate-300 group-hover:text-slate-400 uppercase tracking-widest">Fiche de carrière</span>
        </div>
      </button>
    {/if}
  </div>
</div>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 5px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>

