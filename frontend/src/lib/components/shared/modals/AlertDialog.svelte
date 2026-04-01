<script lang="ts" module>
  import { tv, type VariantProps } from 'tailwind-variants';

  /**
   * Style variants using Tailwind Variants
   */
  export const alertDialogVariants = tv({
    slots: {
      iconContainer: 'flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-white z-10 transition-transform duration-300',
      confirmButton: 'inline-flex h-9 w-full sm:w-[50%] rounded-md text-sm font-medium shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all outline-none focus-visible:ring-2 focus-visible:ring-offset-2 items-center justify-center min-w-[150px] cursor-pointer hover:brightness-110'
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

  export type AlertDialogVariant = VariantProps<typeof alertDialogVariants>['type'];
</script>


<script lang="ts">
  import * as AlertDialog from '$lib/components/ui/alert-dialog';
  import { Spinner } from '$lib/components/ui/spinner';
  import { isPromise } from '$lib/utilities/common/func';
  import { cn } from '@/utilities/common/css';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { tick } from 'svelte';

  interface Props {
    title: string;
    message: string;
    type?: AlertDialogVariant;
    isOpen: boolean;
    show_icon?: boolean;
    onYes?: (() => void) | (() => Promise<any>);
    onNo?: (() => void) | (() => Promise<any>);
    yesText?: string;
    noText?: string;
    showCancel?: boolean;
    autoCloseMs?: number;
    class?: string;
  }

  let {
    title, message, type = 'info', isOpen = $bindable(false),
    show_icon = true, onYes, onNo, yesText = 'Confirmer',
    noText = 'Annuler', showCancel = true, autoCloseMs = 10000, class: className = ''
  }: Props = $props();

  // Internal State
  let loading = $state(false);
  let isPulsing = $state(false);
  let progress = $state(100);

  // SVG Progress Circle Math
  const stroke = 6;
  const normalizedRadius = 45; // Radius within 100x100 viewBox
  const circumference = normalizedRadius * 2 * Math.PI;

  const baseColors = { 
    info: '#3b82f6', danger: '#fca5a5', warning: '#f59e0b', success: '#10b981' 
  };

  const progressColors = {
    info: '#3b82f6', danger: '#ef4444', warning: '#f59e0b', success: '#10b981'
  };

  // Reactive Derived Values
  const strokeDashoffset = $derived(circumference - (progress / 100) * circumference);
  const activeColor = $derived(baseColors[type ?? 'info']);
  const progressColor = $derived(progressColors[type ?? 'info']);

  /**
   * Main logic effect: handle auto-close and body scrolling
   */
  $effect(() => {
    if (isOpen) {
      document.body.style.pointerEvents = 'auto'; // Re-enable interaction blocked by library
      
      if (autoCloseMs > 0) {
        const start = Date.now();
        const interval = setInterval(() => {
          const elapsed = Date.now() - start;
          progress = Math.max(0, 100 - (elapsed / autoCloseMs) * 100);
          if (progress <= 0) { 
            clearInterval(interval); 
            handleNo(); 
          }
        }, 50);
        return () => clearInterval(interval);
      }
    } else {
      progress = 100;
    }
  });

  /**
   * Triggers the visual pulse on the dialog borders
   */
  async function triggerPulse() {
    isPulsing = false;
    await tick();
    isPulsing = true;
  }

  /**
   * Execution logic for Confirm (Yes) button
   */
  async function handleYes() {
    if (!onYes) return (isOpen = false);
    const result = onYes();
    if (isPromise(result)) {
      loading = true;
      try { await result; isOpen = false; }
      finally { loading = false; }
    } else { isOpen = false; }
  }

  /**
   * Execution logic for Cancel (No) button or Timeout
   */
  function handleNo() {
    onNo?.();
    isOpen = false;
  }

  const styles = $derived(alertDialogVariants({ type }));
</script>


<AlertDialog.Root bind:open={isOpen}>
  <AlertDialog.Content
    onOutsideClick={triggerPulse}
    onInteractOutside={(e) => e.preventDefault()}
    style="--pulse-color: {activeColor}80; --active-color: {activeColor};"
    class={cn(
      'z-50 shadow-2xl bg-white px-0 py-7 border-none rounded-2xl transition-all duration-300',
      isPulsing && 'pulse-animation',
      className
    )}
    onanimationend={() => (isPulsing = false)}
  >
    <div class="flex flex-col items-center text-center space-y-3">
      {#if show_icon}
        <!-- Container with Flex centering for the Icon and Absolute for SVG -->
        <div class="relative h-26 w-26 flex items-center justify-center">
          {#if autoCloseMs > 0}
            <!-- SVG uses viewBox 100 100 for perfect relative centering -->
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
          {/if}
          
          <div class={cn(styles.iconContainer(), isPulsing && 'icon-shake-animation')}>
            <AppIcon 
              name={type === 'danger' ? 'shield-alert' : type === 'warning' ? 'alert-triangle' : type === 'success' ? 'circle-check' : 'info'} 
              size={44} 
              strokeWidth={0.8}
              style="color: var(--active-color)"
            />
          </div>
        </div>
      {/if}

      <div class="space-y-2 mt-2">
        <AlertDialog.Title class="text-[0.95rem] font-bold text-slate-900 tracking-tight leading-none">
          {title}
        </AlertDialog.Title>
        <AlertDialog.Description class="text-slate-600 text-[0.86rem] max-w-md mx-auto leading-relaxed">
          {message}
        </AlertDialog.Description>
      </div>

      <AlertDialog.Footer class="w-full flex flex-col sm:flex-row sm:justify-center items-center gap-3 mt-4">
        {#if showCancel}
          <button 
            type="button" 
            onclick={handleNo} 
            class="h-8 text-[0.85rem] font-medium rounded-lg shadow-fine hover:bg-slate-50 border border-slate-200 transition-all cursor-pointer w-[40%]!"
          >
            {noText}
          </button>
        {/if}
        <button 
          type="button" 
          onclick={handleYes} 
          disabled={loading} 
          class={cn(styles.confirmButton(), 'h-8 text-[0.85rem] rounded-lg w-[40%]!')}
        >
          {#if loading}<Spinner size="xs" class="border-white" />{/if}
          {yesText}
        </button>
      </AlertDialog.Footer>
    </div>
  </AlertDialog.Content>
</AlertDialog.Root>


<style>
  /* Border Pulse (3 steps ripple) */
  :global(.pulse-animation) { 
    animation: multiPulseShadow 0.6s ease-in-out !important; 
  }
  
  /* Icon micro-interaction */
  :global(.icon-shake-animation) { 
    animation: iconShake 0.6s ease-in-out !important; 
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

