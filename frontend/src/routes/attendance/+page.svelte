<script lang="ts">
  import { goto } from '$app/navigation';

  // Redirect to the default tab if someone navigates to /attendance directly
  $effect(() => {
    goto('/attendance/register', { replaceState: true });
  });
</script>
