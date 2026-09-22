<script lang="ts">
  import { goto } from '$app/navigation';
  import { hr } from '@/constants/features/navigation';

  // Redirect to the default sub-route
  $effect(() => {
    goto(hr('/banking/accounts'), { replaceState: true });
  });
</script>
