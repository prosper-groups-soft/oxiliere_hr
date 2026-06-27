<script lang="ts">
  import LeavesTabs from "@/features/leaves/components/nav/LeavesTabs.svelte";
  let { children } = $props();
</script>


<div class="flex flex-col h-full bg-white overflow-hidden">
  <LeavesTabs />

  <main class="flex-1 overflow-hidden relative bg-white">
    {@render children?.()}
  </main>
</div>

