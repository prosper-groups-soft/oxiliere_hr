<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { toast as sonnerToast } from 'svelte-sonner';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { cn } from '@/utilities/common/css';

  let { 
    id,
    message, 
    type = 'success', 
    duration = 5000 
  } = $props<{
    id: string | number;
    message: string;
    type?: 'success' | 'error' | 'info';
    duration?: number;
  }>();

  let remaining = $state(0);
  let isPaused = $state(false);
  let startTime = $state(Date.now());
  let interval: any;

  $effect(() => {
    remaining = duration;
    startTime = Date.now();
  });

  function update() {
    if (isPaused || !id) return;
    const now = Date.now();
    const elapsed = now - startTime;
    remaining = Math.max(0, duration - elapsed);

    if (remaining <= 0) {
      sonnerToast.dismiss(id);
    }
  }

  onMount(() => {
    interval = setInterval(update, 50);
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
  });

  const progress = $derived((remaining / duration) * 100);
  const secondsLeft = $derived(Math.ceil(remaining / 1000));

  const config = $derived.by(() => {
    switch (type) {
      case 'error': 
        return { icon: 'alert', color: 'text-red-600', bar: 'bg-red-600' };
      case 'info': 
        return { icon: 'info', color: 'text-blue-600', bar: 'bg-blue-600' };
      default: 
        return { icon: 'check', color: 'text-emerald-600', bar: 'bg-emerald-600' };
    }
  });

  function togglePause() {
    if (isPaused) {
      startTime = Date.now() - (duration - remaining);
      isPaused = false;
    } else {
      isPaused = true;
    }
  }
</script>

<div class="relative w-full bg-white dark:bg-slate-900 border rounded-xl shadow-lg overflow-hidden min-w-100">
  <div class="p-4 flex items-start gap-3">
    <div class={cn("mt-0.5", config.color)}>
      <AppIcon name={config.icon} size={40} strokeWidth={1} />
    </div>
    
    <div class="flex-1 space-y-2">
      <div class="flex items-center justify-between">
        <p class="font-bold text-slate-900 text-[0.9rem] dark:text-white leading-tight">
          {message}
        </p>
        <div class="flex items-center gap-1">
          <button 
            onclick={() => sonnerToast.dismiss(id)}
            class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors text-slate-500 cursor-pointer"
          >
            <AppIcon name="x" size={20} />
          </button>
        </div>
      </div>
      
      <p class="text-sm text-slate-700 leading-normal">
        Fermeture dans <span class="font-bold text-sm text-slate-700 dark:text-slate-300">{secondsLeft}</span> secondes. 
        <button 
          onclick={togglePause}
          class="font-bold hover:underline cursor-pointer ml-1 text-sm"
        >
          {isPaused ? 'Reprendre.' : 'Arrêter.'}
        </button>
      </p>
    </div>
  </div>

  <div class="absolute bottom-0 left-0 h-1 w-full bg-slate-100 dark:bg-slate-800">
    <div 
      class={cn("absolute bottom-0 left-0 h-full transition-all duration-75 ease-linear", config.bar)}
      style="width: {progress}%"
    ></div>
  </div>
</div>

