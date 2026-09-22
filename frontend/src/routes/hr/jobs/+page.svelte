<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { hr } from '@/constants/features/navigation';

  onMount(() => {
    goto(hr('/jobs/chart'), { replaceState: true });
  });
</script>


<div class="h-full flex items-center justify-center">
  <AnimateSpin text="Rédirection" />
</div>

