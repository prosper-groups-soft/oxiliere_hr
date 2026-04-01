<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";

  let { 
    isResetting = false, 
    onAdd, 
    onReset 
  } = $props<{ 
    isResetting: boolean;
    onAdd: () => void;
    onReset: () => void;
  }>();
</script>


<div class="flex items-center gap-2">
  <Button 
    variant="outline" 
    onclick={onReset}
    class="h-7 px-3 text-[0.78rem] font-medium border-slate-200 text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition-all rounded-lg"
  >
    <div class={isResetting ? "animate-spin-once" : ""}>
      <AppIcon name="rotate" size={14} />
    </div>
    Défauts
  </Button>
  <Button onclick={onAdd} variant="default" class="h-7 px-3 text-[0.78rem] text-white shadow-fine rounded-lg transition-all">
    <AppIcon name="plus" size={17} />
    Nouveau palier
  </Button>
</div>


<style>
  @keyframes spin-once {
    from { transform: rotate(0deg); }
    to { transform: rotate(-360deg); }
  }

  .animate-spin-once {
    animation: spin-once 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }
</style>

