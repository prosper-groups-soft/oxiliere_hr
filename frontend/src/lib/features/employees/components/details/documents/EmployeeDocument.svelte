<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import { Card, CardContent } from '@/components/ui/card';
  import TooltipWrapper from '@/components/shared/containers/TooltipWrapper.svelte';
  import { formatDate } from '@/utilities/common/date';
  import type { Document } from '../../../types/types';
  import * as DropdownMenu from '@/components/ui/dropdown-menu';
  import { toast } from '@/utilities/ui/toast';
  import { previewStore } from "../../../stores/preview.svelte";

  let { 
    doc, 
    config, 
    fileIcon,
    onEdit,
    onDelete
  }: { 
    doc: Document, 
    config: any,
    fileIcon: string,
    onEdit: (doc: Document) => void,
    onDelete: (id: number | string, name: string) => void
  } = $props();  

  function handleView() {
    previewStore.open(doc);
    //toast.info(`Ouverture de ${doc.name}...`);
  }

  function handleDownload() {
    toast.success(`${doc.name} prêt pour le téléchargement`);
  }
</script>


{#snippet ActionButton(icon: string, label: string, onclick: () => void)}
  <TooltipWrapper content={label} side="top" asChild={true}>
    {#snippet children(props: Record<string, any>)}
      <Button 
        {...props} 
        variant="ghost" 
        size="icon" 
        class="h-8 w-8 hover:bg-white hover:text-primary rounded-full shadow-sm sm:shadow-none" 
        {onclick}
      >
        <AppIcon name={icon} size={20} />
      </Button>
    {/snippet}
  </TooltipWrapper>
{/snippet}


{#snippet MoreActionsTrigger(menuProps: Record<string, any>)}
  <TooltipWrapper content="Plus" side="top" asChild={true}>
    {#snippet children(tooltipProps)}
      <Button 
        {...tooltipProps}
        {...menuProps} 
        variant="ghost" 
        size="icon" 
        class="h-8 w-8 hover:bg-white hover:text-primary rounded-full shadow-sm sm:shadow-none"
      >
        <AppIcon name="more-vertical" size={20} />
      </Button>
    {/snippet}
  </TooltipWrapper>
{/snippet}


<Card class="group transition-all duration-200 shadow-none border-b rounded-none hover:bg-slate-50/50">
  <CardContent class="px-0 pl-3 grid grid-cols-12 items-center gap-4">
    <div class="col-span-12 sm:col-span-5 flex items-center gap-3 min-w-0">
      <div class="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 group-hover:bg-primary/10 group-hover:text-primary transition-colors shrink-0">
        <AppIcon name={fileIcon} size={22} />
      </div>
      
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2 mb-0.5">
          <p class="font-semibold text-[0.85rem] truncate text-slate-900">{doc.name}</p>
          <Badge variant="outline" class="text-[0.8rem] px-1.5 py-0 uppercase font-bold shrink-0">
            {doc.type}
          </Badge>
        </div>
        <p class="text-slate-600 text-[0.81rem] truncate max-w-100">
          {doc.size} • {doc.expiry ? `Expire le ${formatDate(doc.expiry, false, false)}` : 'Sans expiration'}
        </p>
      </div>
    </div>

    <div class="hidden sm:flex col-span-4 items-center pl-2">
      <Badge class="flex items-center gap-1.5 {config.class} border shadow-none px-2.5 py-0.5 rounded-full">
        {#if config.icon}
          <AppIcon name={config.icon} size={20} />
        {/if}
        {config.label}
      </Badge>
    </div>

    <div class="col-span-12 sm:col-span-3 flex items-center justify-end gap-1 px-2">
      <div class="flex items-center gap-1">
        {@render ActionButton("eye", "Visualiser", handleView)}
        {@render ActionButton("download", "Télécharger", handleDownload)}

        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild={true}>
            {#snippet child({ props: menuProps })}
              {@render MoreActionsTrigger(menuProps)}
            {/snippet}
          </DropdownMenu.Trigger>
          <DropdownMenu.Content align="end">
            <DropdownMenu.Item onclick={() => onEdit(doc)} class="gap-2">
              <AppIcon name="edit" size={18} />
              Modifier
            </DropdownMenu.Item>
            <DropdownMenu.Item onclick={() => onDelete(doc.id, doc.name)} class="gap-2 text-red-600 hover:text-red-700! hover:bg-red-50!">
              <AppIcon name="trash" size={18} class="text-inherit" />
              Supprimer
            </DropdownMenu.Item>
          </DropdownMenu.Content>
        </DropdownMenu.Root>
      </div>
    </div>
  </CardContent>
</Card>

