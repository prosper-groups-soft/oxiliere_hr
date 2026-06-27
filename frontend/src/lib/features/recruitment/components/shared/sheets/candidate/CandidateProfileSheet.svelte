<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import CandidateProfile from "../../../profile/CandidateProfile.svelte";

  let {
    open = $bindable(false),
    candidateId = $bindable(''),
  } = $props<{
    open?: boolean;
    candidateId?: string;
  }>();
</script>


<Sheet.Root bind:open>
  <Sheet.Content
    side="right"
    class="sm:max-w-160 bg-white p-0 flex flex-col h-full overflow-hidden"
  >
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50 flex items-start justify-between">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900">
        Profil du candidat
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto">
      {#if candidateId}
        <CandidateProfile {candidateId} />
      {:else}
        <div class="text-sm text-slate-400 px-1 flex gap-1.5 justify-center items-center">
          <AppIcon name="circle-x" size={16} class="text-slate-300"/>
          Aucun candidat sélectionné
        </div>
      {/if}
    </div>
  </Sheet.Content>
</Sheet.Root>
