<script lang="ts">
  import type { Transition } from "../../../types/types";
  import TransitionItem from "./TransitionItem.svelte";
  import { fade } from "svelte/transition";

  
  let {
    transitions = [],
    onEdit,
    onDelete
  } = $props<{
    transitions: Transition[],
    onEdit: (trans: Transition) => void,
    onDelete?: (trans: Transition) => void,
  }>();
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  <div class="flex-1 overflow-auto custom-scrollbar flex flex-col" style="--scrollbar-size: 5px" in:fade={{ duration: 200 }}>
      
      <!-- Column Headers -->
      <div class="sticky top-0 z-10 flex items-center h-8! px-6 bg-white border-b border-slate-100">
        <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Type</span>
        <span class="w-[16%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Origine</span>
        <span class="w-[2%]"></span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Destination</span>
        <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Motif</span>
        <span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-4">Date</span>
        <span class="w-[6%]"></span>
      </div>

      <div class="flex-1">
        {#each transitions as trans, i (trans.id)}
          <TransitionItem transition={trans} index={i} {onEdit} {onDelete} />
        {/each}
      </div>

    </div>
</div>

