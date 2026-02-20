<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import ConfirmDialog from '@/components/shared/modals/AlertDialog.svelte'; 

  let { 
    icon = 'user',
    iconClass = 'text-slate-600',
    title,
    subtitle,
    badge,
    onEdit,
    onDelete
  }: { 
    icon?: string,
    iconClass?: string,
    title: string,
    subtitle?: string,
    badge?: Snippet,
    onEdit: () => void,
    onDelete: () => void | Promise<void>
  } = $props();

  let isDeleteDialogOpen = $state(false);
</script>

<ConfirmDialog
  bind:isOpen={isDeleteDialogOpen}
  type="danger"
  title="Confirmer la suppression"
  message="Êtes-vous sûr de vouloir supprimer {title} ? Cette action est irréversible."
  yesText="Supprimer"
  noText="Annuler"
  onYes={onDelete} 
/>

<div class="grid grid-cols-[1fr_auto_auto] items-center gap-4 p-3.5 rounded-xl bg-white border border-transparent hover:border-primary/20 hover:bg-slate-50/50 transition-all group shadow-soft">
  <div class="flex items-center gap-4 min-w-0">
    <div class="h-11 w-11 shrink-0 border border-slate-100 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-white transition-colors">
      <AppIcon name={icon} size={22} class={iconClass} />
    </div>
    <div class="flex flex-col min-w-0 text-left"> <p class="font-bold text-[0.9rem] text-slate-800 truncate leading-tight">{title}</p>
      {#if subtitle}
        <p class="text-[0.8rem] text-slate-500 truncate mt-1">{subtitle}</p>
      {/if}
    </div>
  </div>
  
  <div class="px-2">
    {@render badge?.()}
  </div>

  <div class="flex items-center">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        {#snippet child({ props })}
          <Button 
            {...props}
            variant="ghost" 
            size="icon" 
            class="h-8 w-8 text-slate-400 hover:text-primary hover:bg-primary/5 rounded-full transition-all data-[state=open]:bg-slate-100"
          >
            <AppIcon name="more-horizontal" size={19} />
            <span class="sr-only">Actions</span>
          </Button>
        {/snippet}
      </DropdownMenu.Trigger>
      
      <DropdownMenu.Content align="end" class="min-w-40 shadow-xl border-slate-100">
        <DropdownMenu.Label class="text-[0.7rem]! uppercase tracking-widest text-slate-400 font-bold px-2 py-1.5">
          Options
        </DropdownMenu.Label>
        <DropdownMenu.Separator />
        
        <DropdownMenu.Group>
          <DropdownMenu.Item onclick={onEdit} class="cursor-pointer gap-2 py-2">
            <AppIcon name="edit" size={19} class="text-slate-500" />
            <span class="text-sm">Modifier</span>
          </DropdownMenu.Item>
                    
          <DropdownMenu.Item 
            onclick={() => isDeleteDialogOpen = true} 
            class="cursor-pointer gap-2 py-2 text-red-600 hover:bg-red-50! hover:text-red-700!"
          >
            <AppIcon name="trash" size={19} class="text-red-600" />
            <span class="text-sm font-medium">Supprimer</span>
          </DropdownMenu.Item>
        </DropdownMenu.Group>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
</div>

