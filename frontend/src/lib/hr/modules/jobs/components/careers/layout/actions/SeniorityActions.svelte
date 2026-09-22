<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  let { isResetting=false, onAdd, onReset, filterState } = $props<{ isResetting?:boolean; onAdd:()=>void; onReset?:()=>void; filterState?:any }>();
</script>

<ActionBar>
  {#if onReset}
    <Button variant="ghost" onclick={onReset} size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100">
      {#if isResetting}<AnimateSpin class="size-3" text="" />{:else}<AppIcon name="rotate" size={14} />{/if} Réinitialiser
    </Button>
    <div class="w-px h-5 bg-slate-200 mx-1"></div>
  {/if}
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.85rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={17} />Nouveau palier</Button>
</ActionBar>
