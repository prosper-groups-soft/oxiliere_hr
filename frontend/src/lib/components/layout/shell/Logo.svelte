<script lang="ts">
  import { onMount } from 'svelte';
  import { cn } from "@/utilities/common/css";
  
  // --- Props ---
  let { expanded }: { expanded: boolean } = $props();

  // --- Hydration Safety ---
  // We initialize as 'mounted = false' to match the Server Render initially
  let mounted = $state(false);

  onMount(() => {
    mounted = true;
  });

  // Optimization: Preload both images to avoid "flicker" on toggle
  const logoLarge = "/images/logo-15.png";
  const logoSmall = "/images/logo-1.png";
</script>


<!-- Preloading hint for the browser (hidden) -->
<div class="hidden">
  <img src={logoLarge} alt="" />
  <img src={logoSmall} alt="" />
</div>


<img
  class={cn(
    "h-10 object-contain transition-all duration-300", 
    expanded 
      ? "object-left -ml-0.75 mr-0.75 w-auto" 
      : "w-5 object-center"
  )}
  src={!mounted || expanded ? logoLarge : logoSmall}
  alt="Oxiliere Logo"
/>

