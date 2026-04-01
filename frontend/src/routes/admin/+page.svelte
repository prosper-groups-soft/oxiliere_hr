<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { adminStore } from '$lib/features/admin/stores/admin.svelte';

  $effect(() => {
    if (browser) {
      if (adminStore.lastRoute) {
        goto(adminStore.lastRoute, { replaceState: true });
      } else {
        goto('/admin/audit', { replaceState: true });
      }
    }
  });
</script>

