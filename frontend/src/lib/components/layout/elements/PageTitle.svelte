<script lang="ts">
  import { auth } from "@/hr/auth/stores/auth.svelte";

  const { title }: { title: string } = $props();
</script>


<svelte:head>
  <title>{title} | {auth.organizationName}</title>
</svelte:head>

