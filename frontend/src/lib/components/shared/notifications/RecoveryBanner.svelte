<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { slide } from "svelte/transition";

  let { 
    message, 
    onRestore, 
    onIgnore,
    restoreLabel = "Restaurer",
    ignoreLabel = "Ignorer"
  } = $props<{
    message: string;
    onRestore: () => void;
    onIgnore: () => void;
    restoreLabel?: string;
    ignoreLabel?: string;
  }>();
</script>


<div 
  transition:slide
  class="bg-blue-50/80 border-b border-blue-100 px-4 py-2 flex items-center justify-center gap-4 transition-all"
>
  <AppIcon name="info" size={16} class="text-blue-500 shrink-0" />
  <span class="text-[0.82rem] text-blue-900 font-medium truncate">
    {message}
  </span>
  <div class="flex gap-2 shrink-0">
    <Button 
      variant="outline" 
      size="sm" 
      onclick={onRestore}
      class="h-6.5 text-[0.75rem] py-0 bg-white border-blue-200 text-blue-600 hover:bg-blue-50 transition-all font-semibold"
    >
      {restoreLabel}
    </Button>
    <Button 
      variant="ghost" 
      size="sm" 
      onclick={onIgnore}
      class="h-6.5 text-[0.75rem] py-0 text-slate-400 hover:text-slate-600 hover:bg-transparent transition-all font-medium"
    >
      {ignoreLabel}
    </Button>
  </div>
</div>

