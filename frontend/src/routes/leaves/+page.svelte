<script lang="ts">
  import { goto } from '$app/navigation';

  $effect(() => {
    goto('/leaves/requests', { replaceState: true });
  });
</script>
