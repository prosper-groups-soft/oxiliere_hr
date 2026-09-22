<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  
  let showLegalBanner = $state(true);
  let isClosing = $state(false);
  let progress = $state(0);

  // Auto-fill progress bar and close banner when full
  $effect(() => {
    if (!showLegalBanner || isClosing) return;

    const duration = 6000;
    const interval = 16;
    const step = 100 / (duration / interval);

    const timer = setInterval(() => {
      progress += step;
      if (progress >= 100) {
        progress = 100;
        clearInterval(timer);
        isClosing = true;
        setTimeout(() => {
          showLegalBanner = false;
          isClosing = false;
          progress = 0;
        }, 300);
      }
    }, interval);

    return () => clearInterval(timer);
  });

  function closeBanner() {
    isClosing = true;
    setTimeout(() => {
      showLegalBanner = false;
      isClosing = false;
      progress = 0;
    }, 300);
  }
</script>


{#if showLegalBanner}
  <div
    transition:slide={{ duration: 400, easing: cubicOut }}
    class={cn(
      "relative bg-amber-50/40 border-b border-amber-100 px-6 pr-8 py-1 flex items-center justify-start gap-3 overflow-hidden transition-all",
      isClosing && "opacity-0"
    )}
  >
    <!-- Progress fill background -->
    <div
      class="absolute top-0 left-0 h-full bg-amber-100/70 transition-all ease-linear"
      style="width: {progress}%;"
    ></div>

    <button
      aria-label="Fermer la bannière"
      onclick={closeBanner}
      class="shrink-0 p-1 text-amber-400 hover:text-amber-600 hover:bg-amber-100 rounded transition-all cursor-pointer z-10"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
    <div class="flex items-center gap-3 flex-1 justify-start z-10">
      <div class="w-5 h-5 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
        <span class="text-amber-600 text-xs font-bold">i</span>
      </div>
      <span class="text-[0.82rem] text-amber-900 leading-relaxed">
        Ces règles s'appliquent au calcul des heures travaillées et à la détection des retards et
        absences pour tous les employés.
      </span>
    </div>
  </div>
{/if}
