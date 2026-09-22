<script lang="ts">
  import { goto } from "$app/navigation";
  import { browser } from "$app/environment";
  import { HR_BASE } from '@/constants/features/navigation';
  $effect(() => { 
    if (browser) 
      goto(HR_BASE, { replaceState: true }); 
  });
</script>

