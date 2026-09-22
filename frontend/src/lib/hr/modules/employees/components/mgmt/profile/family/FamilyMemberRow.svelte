<script lang="ts">
  import type { Snippet } from 'svelte';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import ConfirmAction from '@/hr/components/shared/actions/ConfirmAction.svelte';


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
  class="group grid grid-cols-[1fr_auto_auto] items-center gap-3 p-3.5 rounded-xl bg-white border border-slate-200 shadow-fine hover:border-violet-200 hover:shadow-sm transition-all" 
>
  <div class="flex items-center gap-3 min-w-0 cursor-pointer" onclick={onEdit} role="none">
    <div class="h-9 w-9 shrink-0 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center group-hover:bg-white group-hover:border-violet-100 transition-colors">
      <AppIcon name={icon} size={18} class={iconClass} />
    </div>
    <div class="flex flex-col min-w-0 text-left">
      <p class="font-bold text-[0.88rem] text-slate-900 truncate leading-tight tracking-tight">{title}</p>
      {#if subtitle}
        <p class="text-[0.85rem] text-slate-500 truncate mt-0.5">{subtitle}</p>
      {/if}
    </div>
  </div>
  
  <div class="px-1 flex items-center gap-1.5 flex-wrap justify-end">
    {@render badge?.()}
  </div>

  <div class="flex items-center gap-1 shrink-0">
    <button
      class="h-8 w-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-violet-600 hover:bg-violet-50 border border-transparent hover:border-violet-100 transition-colors cursor-pointer"
      onclick={onEdit}
      title="Modifier"
    >
      <AppIcon name="edit" size={18} />
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

