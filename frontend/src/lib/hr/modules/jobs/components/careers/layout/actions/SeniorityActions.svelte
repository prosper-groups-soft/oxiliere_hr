<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";

  let { 
    isResetting = false, 
    onAdd, 
    onReset 
  } = $props<{ 
    isResetting?: boolean;
    onAdd: () => void;
    onReset?: () => void;
  }>();
</script>


<div class="flex items-center gap-2">
  {#if onReset}
    <Button 
      variant="ghost" 
      onclick={onReset}
      size="sm"
      class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
    >
      {#if isResetting}
        <AnimateSpin class="size-3" text="" />
      {:else}
        <AppIcon name="rotate" size={14} />
      {/if}
      Réinitialiser
    </Button>

    <div class="w-px h-5 bg-slate-200 mx-1"></div>

  {/if}
  <Button onclick={onAdd} variant="default" class="h-7 px-3 text-[0.85rem] text-white shadow-fine rounded-lg transition-all">
    <AppIcon name="plus" size={17} />
    Nouveau palier
  </Button>
</div>


<style>
  @keyframes spin-once {
    from { transform: rotate(0deg); }
    to { transform: rotate(-360deg); }
  }
</style>

