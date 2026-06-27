<script lang="ts">
  import type { Snippet } from 'svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import ConfirmAction from '@/components/shared/actions/ConfirmAction.svelte';

  let { 
    icon = 'user',
    iconClass = 'text-slate-500',
    title,
    subtitle,
    badge,
    onEdit,
    onDelete,
    isLast = false
  }: { 
    icon?: string,
    iconClass?: string,
    title: string,
    subtitle?: string,
    badge?: Snippet,
    onEdit: () => void,
    onDelete: () => void | Promise<void>,
    isLast?: boolean
  } = $props();

  let isConfirmingDelete = $state(false);
</script>


<div 
  class="grid grid-cols-[1fr_auto_auto] items-center gap-3 px-3 py-2.5 rounded-none! bg-white hover:bg-indigo-50/50 transition-all group shadow-none {!isLast ? 'border-b border-slate-100' : ''}" 
>
  <div class="flex items-center gap-3 min-w-0 cursor-pointer" onclick={onEdit} role="none">
    <div class="h-10 w-10 shrink-0 border border-slate-100 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-white group-hover:border-slate-200 transition-all">
      <AppIcon name={icon} size={20} class={iconClass} />
    </div>
    <div class="flex flex-col min-w-0 text-left">
      <p class="font-semibold text-[0.87rem] text-slate-800 truncate leading-tight">{title}</p>
      {#if subtitle}
        <p class="text-[0.85rem] text-slate-700 truncate mt-0.5">{subtitle}</p>
      {/if}
    </div>
  </div>
  
  <div class="px-1">
    {@render badge?.()}
  </div>

  <div class="flex items-center gap-0.5">
    <button
      class="p-1.5 rounded-md text-slate-400 hover:text-primary hover:bg-primary/5 transition-colors cursor-pointer"
      onclick={onEdit}
      title="Modifier"
    >
      <AppIcon name="edit" size={16} />
    </button>

    <ConfirmAction 
      isConfirming={isConfirmingDelete}
      onRequest={() => isConfirmingDelete = true}
      onConfirm={() => { onDelete(); isConfirmingDelete = false; }}
      onCancel={() => isConfirmingDelete = false}
      labels={{ action: '', confirm: '', cancel: '' }}
      icons={{ action: 'trash-2', confirm: 'check', cancel: 'x' }}
      variant="danger"
    />
  </div>
</div>
