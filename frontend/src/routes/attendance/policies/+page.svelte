<script lang="ts">
  import PolicyManager from "@/features/attendance/components/config/PolicyManager.svelte";
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
</script>

<div in:fly={{ y: 3, duration: 300, delay: 100, easing: cubicOut }} out:fade={{ duration: 200 }} class="h-full">
  <PolicyManager />
</div>
