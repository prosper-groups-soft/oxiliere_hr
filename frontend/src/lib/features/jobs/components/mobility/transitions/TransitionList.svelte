<script lang="ts">
  import type { Transition } from "../../../types/types";
  import TransitionItem from "./TransitionItem.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";

  let { 
    transitions = [],
    onEdit,
    onNew
  } = $props<{ 
    transitions: Transition[],
    onEdit: (trans: Transition) => void,
    onNew?: () => void
  }>();
</script>


<div class="overflow-hidden flex flex-col h-full flex-1">
  {#each transitions as trans (trans.id)}
    <TransitionItem transition={trans} {onEdit} />
  {:else}
    <div class="flex flex-col items-center justify-center flex-1">
      <Empty 
        title="Aucun mouvement" 
        description="L'historique des changements est vide." 
        icon="history" 
        iconStrokeWidth={1}
        iconClass="text-primary"
      >
        {#if onNew}
          <EmptyButton labelElement="un mouvement" {onNew} />
        {/if}
      </Empty>
    </div>
  {/each}
</div>
