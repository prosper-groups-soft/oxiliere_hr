<script lang="ts">
  import { tv } from 'tailwind-variants';
  import { notification } from '@/stores/notification.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { isPromise } from '@/utilities/common/func';
  import { cn } from '@/utilities/common/css';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Label } from '@/components/ui/label';
  import { Textarea } from '@/components/ui/textarea';
  import { tick } from 'svelte';
  import { fade, scale } from "svelte/transition";


  export const alertDialogVariants = tv({
    slots: {
      iconContainer: 'flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-white z-10 transition-transform duration-300',
      confirmButton: 'inline-flex h-9 w-full sm:w-[50%] rounded-lg shadow-fine disabled:opacity-50 disabled:cursor-not-allowed transition-all outline-none focus-visible:ring-2 focus-visible:ring-offset-2 items-center justify-center min-w-[150px] cursor-pointer hover:brightness-110'
    },
    variants: {
      type: {
        info: { iconContainer: 'text-blue-600', confirmButton: 'bg-blue-600 text-white focus-visible:ring-blue-500' },
        danger: { iconContainer: 'text-red-600', confirmButton: 'bg-red-600 text-white focus-visible:ring-red-500' },
        warning: { iconContainer: 'text-amber-600', confirmButton: 'bg-amber-600 text-white focus-visible:ring-amber-500' },
        success: { iconContainer: 'text-green-600', confirmButton: 'bg-green-600 text-white focus-visible:ring-green-500' }
      }
    },
    defaultVariants: { type: 'info' }
  });

  const req = $derived(notification.confirmRequest);

  let isOpen = $state(false);
  let loading = $state(false);
  let isPulsing = $state(false);
  let progress = $state(100);
  let paused = $state(false);
  let start = $state(0);
  let accumulatedMs = $state(0);
  let resumeTimestamp = $state(0);

  const stroke = 6;
  const normalizedRadius = 45;
  const circumference = normalizedRadius * 2 * Math.PI;

  const baseColors = {
    info: '#3b82f6', danger: '#fca5a5', warning: '#f59e0b', success: '#10b981'
  };

  const progressColors = {
    info: '#3b82f6', danger: '#ef4444', warning: '#f59e0b', success: '#10b981'
  };

  const strokeDashoffset = $derived(circumference - (progress / 100) * circumference);
  const activeColor = $derived(baseColors[req?.type ?? 'info']);
  const progressColor = $derived(progressColors[req?.type ?? 'info']);
  const styles = $derived(alertDialogVariants({ type: req?.type ?? 'info' }));

  $effect(() => {
    isOpen = req !== null;
  });

  $effect(() => {
    if (isOpen) {
      document.body.style.pointerEvents = 'auto';

      if (!loading) {
        start = Date.now();
        accumulatedMs = 0;
        paused = false;

        const interval = setInterval(() => {
          if (loading) return;
          if (paused) return;

          const totalElapsed = accumulatedMs + (Date.now() - start);
          progress = Math.max(0, 100 - (totalElapsed / 10000) * 100);
          if (progress <= 0) {
            clearInterval(interval);
            handleNo();
          }
        }, 50);
        return () => clearInterval(interval);
      }
    } else {
      progress = 100;
      start = 0;
      accumulatedMs = 0;
      paused = false;
      notification._close();
    }
  });

  function togglePause() {
    if (paused) {
      // Resuming: add the pause duration to accumulated and reset start
      accumulatedMs += Date.now() - resumeTimestamp;
      start = Date.now();
      paused = false;
    } else {
      // Pausing: capture timestamp
      resumeTimestamp = Date.now();
      paused = true;
    }
  }

  async function triggerPulse() {
    isPulsing = false;
    await tick();
    isPulsing = true;
  }

  async function handleYes() {
    if (!req?.onYes) return (isOpen = false);
    const result = req.onYes(req.inputValue);
    if (isPromise(result)) {
      loading = true;
      try { await result; isOpen = false; }
      finally { loading = false; }
    } else { isOpen = false; }
  }

  function handleNo() {
    if (loading) return;
    req?.onNo?.();
    isOpen = false;
  }

  function handleBackdropClick() {
    triggerPulse();
  }
</script>


{#if isOpen}
  <div
    transition:fade={{ duration: 200 }}
    class="fixed inset-0 bg-black/70 flex flex-col items-center justify-center p-4 cursor-default z-50"
    onclick={handleBackdropClick}
    role="presentation"
  >
    <div
      transition:scale={{ duration: 300, start: 0.9 }}
      style="--pulse-color: {activeColor}80; --active-color: {activeColor};"
      class={cn(
        'relative max-w-lg w-full shadow-2xl bg-white px-0 py-7 border-none rounded-2xl transition-all duration-300',
        isPulsing && 'pulse-animation'
      )}
      onanimationend={() => (isPulsing = false)}
      onclick={(e: Event) => e.stopPropagation()}
      role="none"
    >
      <div class="flex flex-col items-center text-center space-y-3" transition:fade={{ duration: 300, delay: 50 }}>
        <div class="relative h-26 w-26 flex items-center justify-center">
          <svg class="absolute inset-0 -rotate-90 transform z-0 w-full h-full" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r={normalizedRadius} fill="transparent" stroke="#f1f5f9" stroke-width={stroke} />
            <circle
              cx="50" cy="50" r={normalizedRadius}
              fill="transparent"
              stroke={progressColor}
              stroke-width={stroke}
              stroke-dasharray={circumference}
              stroke-dashoffset={strokeDashoffset}
              stroke-linecap="round"
              class="transition-all duration-150 ease-linear"
            />
          </svg>

          <div class={cn(styles.iconContainer(), isPulsing && 'icon-shake-animation')}>
            <AppIcon
              name={req?.type === 'danger' ? 'shield-alert' : req?.type === 'warning' ? 'triangle-alert' : req?.type === 'success' ? 'circle-check' : 'info'}
              size={44}
              strokeWidth={0.8}
              style="color: var(--active-color)"
            />
          </div>

          <!-- Pause/Play overlay -->
          <button
            onclick={(e: Event) => { e.stopPropagation(); togglePause(); }}
            class="pause-btn"
            title={paused ? 'Reprendre le compte à rebours' : 'Mettre en pause le compte à rebours'}
          >
            <AppIcon name={paused ? 'play' : 'pause'} size={14} class="text-white" />
          </button>
        </div>

        <div class="space-y-2 mt-2">
          <h3 class="text-[0.96rem] font-semibold text-slate-900">
            {req?.title ?? ''}
          </h3>
          <p class="text-slate-600 text-[0.86rem] max-w-md mx-auto leading-relaxed confirm-message">
            {@html req?.message ?? ''}
          </p>

          {#if req?.inputLabel}
            <div class="px-4 text-left">
              <Label class="text-[0.82rem]">{req.inputLabel}</Label>
              <Textarea
                bind:value={req.inputValue}
                rows={3}
                placeholder="Entrez votre commentaire..."
                class="mt-1.5"
              />
            </div>
          {/if}
        </div>

        <div class="w-full flex flex-col sm:flex-row sm:justify-center items-center gap-3 mt-4">
          <button
            type="button"
            onclick={handleNo}
            class="h-9 text-[0.88rem] rounded-lg shadow-fine hover:bg-slate-50 border border-slate-200 transition-all! cursor-pointer w-[40%]! flex items-center justify-center gap-2"
          >
            <AppIcon name="x" class="text-slate-300" />
            {req?.noText ?? 'Annuler'}
          </button>
          <button
            type="button"
            onclick={handleYes}
            disabled={loading}
            class={cn(styles.confirmButton(), 'h-9 text-[0.88rem] rounded-lg w-[40%]! transition-all! flex items-center justify-center gap-2', loading && 'cursor-wait')}
          >
            {#if loading}
              <AnimateSpin text="" class="border-white size-3" />
            {:else}
              <AppIcon name="check" class="text-white" />
            {/if}

            <span class='{loading ? "opacity-90" : ""} text-[0.88rem]'>
              {req?.yesText ?? 'Confirmer'}
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}


<style>
  :global(.pulse-animation) {
    animation: multiPulseShadow 0.6s ease-in-out !important;
  }

  :global(.icon-shake-animation) {
    animation: iconShake 0.6s ease-in-out !important;
  }

  :global(.pause-btn) {
    position: absolute;
    bottom: -2px;
    right: -2px;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: 2.5px solid rgba(255,255,255,0.9);
    background: rgba(0,0,0,0.3);
    backdrop-filter: blur(4px);
    transition: background 0.2s, transform 0.15s;
    z-index: 10;
  }
  :global(.pause-btn:hover) {
    background: rgba(0,0,0,0.55);
    transform: scale(1.08);
  }

  :global(.confirm-message strong) {
    font-weight: 700 !important;
    color: #1e293b !important;
    font-size: 0.95rem;
  }

  @keyframes multiPulseShadow {
    0% { box-shadow: 0 0 0 0 var(--pulse-color); }
    30% { box-shadow: 0 0 0 15px var(--pulse-color); }
    50% { box-shadow: 0 0 0 30px transparent; }
    70% { box-shadow: 0 0 0 20px var(--pulse-color); }
    100% { box-shadow: 0 0 0 0 transparent; }
  }

  @keyframes iconShake {
    0%, 100% { transform: rotate(0deg) scale(1); }
    25% { transform: rotate(-15deg) scale(1.15); }
    75% { transform: rotate(15deg) scale(1.15); }
  }
</style>

