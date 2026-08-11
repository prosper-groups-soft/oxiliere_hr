<script lang="ts">
  import { cn } from "@/utilities/common/css";

  const {
    loading = false,
    class: classNames = "",
  }: {
    /** Affiche/masque la barre de chargement */
    loading?: boolean;
    /** Classes additionnelles pour le conteneur */
    class?: string;
  } = $props();
</script>


{#if loading}
  <div class={cn("h-0.5 bg-slate-100 overflow-hidden", classNames)}>
    <div class="h-full bg-primary animate-[loadingSlide_1.2s_ease-in-out_infinite] rounded-full" style="width: 30%"></div>
  </div>
{/if}


<style>
  :global {
    @keyframes loadingSlide {
      0% { transform: translateX(-100%); }
      50% { transform: translateX(200%); }
      100% { transform: translateX(400%); }
    }
  }
</style>
