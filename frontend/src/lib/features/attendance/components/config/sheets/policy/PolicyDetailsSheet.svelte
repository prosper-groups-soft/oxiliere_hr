<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import type { WorkPolicy } from "../../../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import PolicyVisualizer from "../../elements/PolicyVisualizer.svelte";


  type Policy = WorkPolicy;

  let { 
    open = $bindable(false),
    policy = $bindable<Policy | null>(null)
  } = $props<{ 
    open: boolean;
    policy: Policy | null;
  }>();

</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0 bg-white">
    
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold flex items-center gap-2.5">
        Détails du modèle de travail
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-8 pt-0 space-y-8 custom-scrollbar">
      {#if policy}
        <section class="space-y-4 px-2">
          <div>
            <h3 class="text-[1rem] font-bold text-slate-900 mb-1.5 leading-tight">{policy.name}</h3>
            <p class="text-[0.875rem] text-slate-500 leading-relaxed">{policy.description}</p>
          </div>
        </section>

        <PolicyVisualizer {policy} showDetails={true} />
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50">
      <Sheet.Close class="w-full">
        <button class="w-full h-11 rounded-lg bg-white border border-slate-200 text-[0.9rem] text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all cursor-pointer shadow-fine active:scale-[0.98] flex justify-center items-center gap-2">
          <AppIcon name="x" size={16} class="text-slate-400" />
          Fermer les détails
        </button>
      </Sheet.Close>
    </Sheet.Footer>

  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 5px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
</style>

