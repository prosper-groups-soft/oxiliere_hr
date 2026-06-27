<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  interface Props {
    isConfirming: boolean;
    onRequest: () => void;
    onConfirm: () => void;
    onCancel: () => void;
    labels?: {
      action?: string;
      confirm?: string;
      cancel?: string;
    };
    icons?: {
      action?: string;
      confirm?: string;
      cancel?: string;
    };
    variant?: 'danger' | 'warning' | 'neutral';
  }

  let { 
    isConfirming,
    onRequest,
    onConfirm,
    onCancel,
    labels = {
      action: 'Retirer',
      confirm: 'Confirmer',
      cancel: ''
    },
    icons = {
      action: 'x',
      confirm: 'check',
      cancel: 'x'
    },
    variant = 'danger'
  }: Props = $props();

  const variantClasses = {
    danger: {
      action: 'hover:bg-rose-50 text-red-600 hover:text-red-500',
      confirm: 'bg-rose-100 text-rose-600 hover:bg-rose-200',
      cancel: 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    },
    warning: {
      action: 'hover:bg-amber-50 text-amber-600 hover:text-amber-600',
      confirm: 'bg-amber-100 text-amber-600 hover:bg-amber-200',
      cancel: 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    },
    neutral: {
      action: 'hover:bg-slate-100 text-slate-600 hover:text-slate-700',
      confirm: 'bg-slate-200 text-slate-600 hover:bg-slate-300',
      cancel: 'bg-slate-100 text-slate-600 hover:bg-slate-200'
    }
  };
</script>


{#if isConfirming}
  <div class="flex items-center gap-0.5" transition:slide={{ duration: 200, easing: cubicOut, axis: 'x' }}>
    <button
      type="button"
      onmousedown={(e) => e.preventDefault()}
      class="{labels.confirm ? 'px-3 py-1' : 'p-1.5'} flex gap-2 items-center justify-center rounded-md transition-colors text-[0.87rem] font-medium cursor-pointer {variantClasses[variant].confirm}"
      onclick={onConfirm}
    >
      <AppIcon name={icons.confirm || 'check'} size={18} />
      {labels.confirm}
    </button>
    <button
      type="button"
      onmousedown={(e) => e.preventDefault()}
      class="p-1.5 rounded-md transition-colors cursor-pointer {variantClasses[variant].cancel}"
      onclick={onCancel}
    >
      <AppIcon name={icons.cancel || 'x'} size={18} />
    </button>
  </div>
{:else}
  <button
    type="button"
    onmousedown={(e) => e.preventDefault()}
    class="flex items-center gap-1 {labels.action ? 'px-2' : 'p-1'} py-1 rounded-md transition-colors cursor-pointer {variantClasses[variant].action}"
    onclick={onRequest}
    transition:slide={{ duration: 200, easing: cubicOut, axis: 'x' }}
  >
    <AppIcon name={icons.action || 'trash-2'} size={18} />
    {#if labels.action}
      <span class="text-[0.87rem] font-medium">{labels.action}</span>
    {/if}
  </button>
{/if}
