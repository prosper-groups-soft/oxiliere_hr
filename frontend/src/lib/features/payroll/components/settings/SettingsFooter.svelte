<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';

  
  let {
    isSaving,
    canSave,
    onSave,
    onCancel,
  }: {
    isSaving: boolean;
    canSave: boolean;
    onSave: () => void;
    onCancel: () => void;
  } = $props();
</script>


<footer class="shrink-0 px-6 py-3 border-t border-slate-200 bg-white/95 backdrop-blur-sm sticky bottom-0 z-20">
  <div class="max-w-4xl mx-auto flex items-center justify-end gap-2.5">
    <Button
      variant="outline"
      size="sm"
      class="h-9 px-5 text-[0.84rem] rounded-lg"
      onclick={onCancel}
      disabled={isSaving}
    >
      <AppIcon name="x" size={16} class="text-slate-300" />
      Annuler
    </Button>
    <Button
      variant="default"
      size="sm"
      class="h-9 px-5 text-[0.84rem] shadow-fine rounded-lg"
      onclick={onSave}
      disabled={isSaving || !canSave}
    >
      {#if isSaving}
        <AnimateSpin text="" class="size-3 border-white" />
      {:else}
        <AppIcon name="save" size={16} />
      {/if}
      Enregistrer
    </Button>
  </div>
</footer>

