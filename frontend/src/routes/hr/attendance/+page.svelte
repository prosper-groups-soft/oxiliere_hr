<script lang="ts">
  import { goto } from '$app/navigation';
  import { hr } from '@/constants/features/navigation';

  // Redirect to the default tab if someone navigates to /attendance directly
  $effect(() => {
    goto(hr('/attendance/register'), { replaceState: true });
  });
</script>
