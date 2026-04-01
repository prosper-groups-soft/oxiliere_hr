<script lang="ts">
  import PayrollTabs from "@/features/payroll/components/nav/PayrollTabs.svelte";
  let { children } = $props();
</script>


<div class="flex flex-col h-full bg-white overflow-hidden">
  <PayrollTabs />

  <main class="flex-1 overflow-hidden relative bg-white">
    {@render children?.()}
  </main>
</div>

