<script lang="ts">
  import { goto } from '$app/navigation';

  $effect(() => {
    goto('/performance/campaigns', { replaceState: true });
  });
</script>
