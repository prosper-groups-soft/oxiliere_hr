<script lang="ts">
  import CycleVisualizer from "@/features/attendance/components/config/CycleVisualizer.svelte";
  import ConfigActions from "@/features/attendance/components/config/actions/ConfigActions.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';


  // Enregistrer les actions dans l'en-tête via le store ui
  $effect(() => {
    ui.addActions('config-actions', AttendanceConfigActions);
    return () => ui.removeActions('config-actions');
  });
</script>


{#snippet AttendanceConfigActions()}
  <ConfigActions />
{/snippet}


<div in:fly={{ y: 3, duration: 300, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }} class="h-full">
  <CycleVisualizer />
</div>

