<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { hr } from '@/constants/features/navigation';

  $effect(() => {
    if (browser) goto(hr('/admin/users'), { replaceState: true });
  });
</script>

