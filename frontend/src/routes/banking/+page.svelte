<script lang="ts">
  import { goto } from '$app/navigation';

  // Redirect to the default sub-route
  $effect(() => {
    goto('/banking/accounts', { replaceState: true });
  });
</script>
