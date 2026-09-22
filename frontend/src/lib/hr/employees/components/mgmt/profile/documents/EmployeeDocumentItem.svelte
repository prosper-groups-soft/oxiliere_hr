<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import TooltipWrapper from '@/components/shared/containers/TooltipWrapper.svelte';
  import { formatDate } from '@/utilities/common/date';
  import type { EmployeeDocument } from '@/hr/employees/types/types';
  import * as DropdownMenu from '@/components/ui/dropdown-menu';
  import { getMediaUrl } from "@/utilities/common/media";
  import { notification } from "@/stores/notification.svelte";
  import { DOCUMENT_TYPES } from "@/hr/employees/constants/documents";

  let { 
    doc, 
    onEdit,
    onDelete,
    onPreview,
    onReplace,
    isLast = false
  }: { 
    doc: EmployeeDocument, 
    onEdit: (doc: EmployeeDocument) => void,
    onDelete: (id: string, name: string) => void,
    onPreview: (doc: EmployeeDocument) => void,
    onReplace: (doc: EmployeeDocument, file: File) => void,
    isLast?: boolean
  } = $props();  

  const fileUrl = $derived(getMediaUrl(doc.file));
  
  const getDocTypeLabel = (value: string) => 
    DOCUMENT_TYPES.find(t => t.value === value)?.label || value;

  const fileIcon = $derived(() => {
    if (!doc.file) return "file-text";
    const ext = doc.file.split('.').pop()?.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'svg', 'webp'].includes(ext || '')) return "image";
    if (ext === 'pdf') return "file-text";
    return "file";
  });

  const subtitle = $derived.by(() => {
    let parts = [];
    if (doc.issue_date) parts.push(`Délivré le ${formatDate(doc.issue_date, false, false)}`);
    if (doc.expiry_date) parts.push(`Expire le ${formatDate(doc.expiry_date, false, false)}`);
    return parts.join(' • ') || getDocTypeLabel(doc.document_type);
  });

  function handleDownload() {
    if (!fileUrl) return;
    window.open(fileUrl, '_blank');
    notification.toast.success(`Ouverture du document...`);
  }

  function getFileColor(file: string | null) {
    if (!file) return 'text-slate-500 border-slate-100 bg-slate-50';
    const ext = file.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return 'text-indigo-500 border-indigo-100 bg-indigo-50/50';
    if (['jpg', 'jpeg', 'png', 'svg', 'webp'].includes(ext || '')) return 'text-emerald-500 border-emerald-100 bg-emerald-50/50';
    return 'text-slate-500 border-slate-100 bg-slate-50';
  }
</script>


{#snippet ActionButton(icon: string, label: string, onclick: () => void)}
  <TooltipWrapper content={label} side="top" asChild={true}>
    {#snippet children(props: Record<string, any>)}
      <Button 
        {...props} 
        variant="ghost" 
        size="icon" 
        class="h-8 w-8 hover:bg-white hover:text-primary rounded-md transition-all" 
        {onclick}
      >
        <AppIcon name={icon} size={18} />
      </Button>
    {/snippet}
  </TooltipWrapper>
{/snippet}


<div class="flex items-center justify-between gap-4 px-4 py-3 bg-white hover:bg-indigo-50/50 transition-all group shadow-none {!isLast ? 'border-b border-slate-100' : ''}">
  <div 
    class="flex items-center gap-4 min-w-0 cursor-pointer"
    onclick={() => onPreview(doc)}
    role="button"
    tabindex="0"
    onkeydown={(e) => e.key === 'Enter' && onPreview(doc)}
  >
    <div class="h-10 w-10 shrink-0 border rounded-lg flex items-center justify-center group-hover:bg-white group-hover:border-slate-200 transition-all {getFileColor(doc.file || '')}">
      <AppIcon name={fileIcon()} size={24} />
    </div>
    
    <div class="min-w-0">
      <div class="flex items-center gap-2 mb-0.5">
        <p class="font-bold text-[0.875rem] truncate text-slate-900 tracking-tight">
          {doc.document_number || getDocTypeLabel(doc.document_type)}
        </p>
        {#if doc.is_verified}
          <Badge class="bg-emerald-50 text-emerald-600 border-emerald-100 shadow-none text-[0.77rem] px-1.5 py-0 h-4 uppercase font-bold">
            Vérifié
          </Badge>
        {/if}
      </div>
      <p class="text-slate-600 text-[0.78rem] truncate flex items-center gap-2">
        <span class="font-medium text-slate-600 text-[0.85rem]">
          {getDocTypeLabel(doc.document_type)}
        </span>
        {#if subtitle}
          <span class="text-slate-300">•</span>
          <span class={doc.expiry_date && new Date(doc.expiry_date) < new Date() ? "text-red-500 font-medium text-[0.85rem]" : "text-[0.85rem]"}>
            {subtitle}
          </span>
        {/if}
      </p>
    </div>
  </div>

  <div class="flex items-center gap-1 shrink-0">
    <div class="flex items-center gap-1 pr-2 border-r border-slate-100">
      {@render ActionButton("eye", "Visualiser", () => onPreview(doc))}
      {@render ActionButton("download", "Télécharger", handleDownload)}
    </div>

    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild={true}>
        {#snippet child({ props: menuProps })}
          <Button 
            {...menuProps} 
            variant="ghost" 
            size="icon" 
            class="h-8 w-8 hover:bg-white hover:text-primary rounded-md transition-all ml-1"
            onclick={(e) => e.stopPropagation()}
          >
            <AppIcon name="more-vertical" size={18} />
          </Button>
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 min-w-40">
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); onEdit(doc); }} 
          class="gap-2 text-[0.84rem]! font-medium text-slate-700"
        >
          <AppIcon name="edit" size={16} />
          Modifier
        </DropdownMenu.Item>
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); document.getElementById(`replace-${doc.id}`)?.click(); }} 
          class="gap-2 text-[0.84rem]! font-medium text-slate-700"
        >
          <AppIcon name="upload" size={16} />
          Remplacer le fichier
        </DropdownMenu.Item>
        <DropdownMenu.Separator />
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); onDelete(doc.id, doc.document_number || getDocTypeLabel(doc.document_type)); }} 
          class="gap-2 text-red-600 hover:text-red-700! hover:bg-red-50! text-[0.84rem]! font-medium"
        >
          <AppIcon name="trash" size={16} class="text-inherit" />
          Supprimer
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
  <input 
    type="file" 
    class="hidden" 
    accept=".pdf,.jpg,.jpeg,.png,.webp" 
    onchange={(e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) onReplace(doc, file);
    }}
    id={`replace-${doc.id}`}
  />
</div>

