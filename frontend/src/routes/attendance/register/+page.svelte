<script lang="ts">
  import DailyRegister from "@/features/attendance/components/register/DailyRegister.svelte";
  import RegisterActions from "@/features/attendance/components/register/actions/RegisterActions.svelte";
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { ui } from "@/stores/ui.svelte";

  $effect(() => {
    ui.addActions('policies-actions', AttendanceRegisterActions);
    return () => ui.removeActions('policies-actions');
  });
</script>


<div in:fly={{ y: 3, duration: 300, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }} class="h-full">
  <DailyRegister />
</div>


{#snippet AttendanceRegisterActions()}
  <RegisterActions />
{/snippet}

