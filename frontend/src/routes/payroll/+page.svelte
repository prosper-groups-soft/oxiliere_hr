<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';

  onMount(() => {
    goto('/payroll/payslips');
  });
</script>

<div class="flex items-center justify-center h-full">
  <AnimateSpin text="Rédirection" />
</div>



