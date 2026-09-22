<script lang="ts">
  import AttendanceTabs from "@/hr/attendance/components/nav/AttendanceTabs.svelte";
  let { children } = $props();
</script>

<div class="flex flex-col h-full bg-white overflow-hidden">
  <AttendanceTabs />

  <main class="flex-1 overflow-hidden relative bg-white">
    {@render children?.()}
  </main>
</div>

