<script lang="ts">
  import { page } from "$app/state";
  import { browser } from "$app/environment";
  import { adminStore } from "$lib/features/admin/stores/admin.svelte";

  $effect(() => {
    if (browser) {
      adminStore.setLastRoute(page.url.pathname);
    }
  });

  let { children } = $props();
</script>

<div class="flex-1 overflow-hidden relative bg-white">
  {@render children?.()}
</div>
