<script lang='ts'>
  import { getOrganizationName } from "@/stores/auth";

  const {title} : {title: string} = $props();
</script>

<svelte:head>
  <title>{title} | {getOrganizationName()}</title>
</svelte:head>
