<script lang="ts">
  import { goto } from '$app/navigation';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import CandidateRow from './views/candidate/CandidateRow.svelte';
  import type { Candidate } from '../../types/types';

  let { candidates, stageConfig } = $props<{
    candidates: Candidate[];
    stageConfig: Record<string, { label: string, color: string }>;
  }>();
</script>


<div class="flex-1 overflow-y-auto min-h-0 pr-1 custom-scrollbar">
  {#if candidates.length === 0}
    <div class="flex-1 flex items-center justify-center">
      <Empty 
        title="Aucun candidat" 
        description="Commencez par ajouter des candidats à votre pipeline de recrutement."
        icon="users"
        iconStrokeWidth={1}
        iconClass="text-slate-400"
      >
        <EmptyButton labelElement="le pipeline" onNew={() => goto('/recruitment/pipeline')} />
      </Empty>
    </div>
  {:else}
    <div class="divide-y divide-slate-100">
      {#each candidates as candidate (candidate.id)}
        <CandidateRow {candidate} {stageConfig} />
      {/each}
    </div>
  {/if}
</div>


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>

