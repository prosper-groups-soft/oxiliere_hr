<script lang="ts">
  import BankingTabs from "@/features/banking/components/nav/BankingTabs.svelte";
  let { children } = $props();
</script>


<div class="flex flex-col h-full bg-white overflow-hidden">
  <BankingTabs />

  <main class="flex-1 overflow-hidden relative bg-white">
    {@render children?.()}
  </main>
</div>
