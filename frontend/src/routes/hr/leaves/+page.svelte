<script lang="ts">
  import { goto } from '$app/navigation';
  import { hr } from '@/constants/features/navigation';

  $effect(() => {
    goto(hr('/leaves/requests'), { replaceState: true });
  });
</script>

