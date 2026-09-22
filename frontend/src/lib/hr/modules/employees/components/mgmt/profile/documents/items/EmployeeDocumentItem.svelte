<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import TooltipWrapper from '@/hr/components/shared/containers/TooltipWrapper.svelte';
  import { formatDate } from '@/hr/utilities/common/date';
  import type { EmployeeDocument } from '@/hr/modules/employees/types/types';
  import * as DropdownMenu from '@/components/ui/dropdown-menu';
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { notification } from "@/hr/stores/notification.svelte";
  import { DOCUMENT_TYPES } from "@/hr/modules/employees/constants/documents";

  
  let { 
    doc, 
    onEdit,
    onDelete,
    onPreview,
    onReplace
  }: { 
    doc: EmployeeDocument, 
    onEdit: (doc: EmployeeDocument) => void,
    onDelete: (id: string, name: string) => void,
    onPreview: (doc: EmployeeDocument) => void,
    onReplace: (doc: EmployeeDocument, file: File) => void
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
    if (!file) return 'text-slate-400 border-slate-200 bg-slate-50';
    const ext = file.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return 'text-indigo-500 border-indigo-100 bg-indigo-50';
    if (['jpg', 'jpeg', 'png', 'svg', 'webp'].includes(ext || '')) return 'text-emerald-500 border-emerald-100 bg-emerald-50';
    return 'text-slate-400 border-slate-200 bg-slate-50';
  }
</script>


{#snippet ActionButton(icon: string, label: string, onclick: () => void)}
  <TooltipWrapper content={label} side="top" asChild={true}>
    {#snippet children(props: Record<string, any>)}
      <Button 
        {...props} 
        variant="ghost" 
        size="icon" 
        class="h-8 w-8 rounded-lg border border-transparent hover:border-amber-100 hover:bg-amber-50 hover:text-amber-700 text-slate-400 transition-colors" 
        {onclick}
      >
        <AppIcon name={icon} size={18} />
      </Button>
    {/snippet}
  </TooltipWrapper>
{/snippet}


<div class="group flex items-center justify-between gap-3 p-3.5 rounded-xl bg-white border border-slate-200 shadow-fine hover:border-amber-200 hover:shadow-sm transition-all">
  <div 
    class="flex items-center gap-3.5 min-w-0 cursor-pointer"
    onclick={() => onPreview(doc)}
    role="button"
    tabindex="0"
    onkeydown={(e) => e.key === 'Enter' && onPreview(doc)}
  >
    <span class="h-9 w-9 shrink-0 rounded-lg border flex items-center justify-center group-hover:bg-white transition-colors {getFileColor(doc.file || '')}">
      <AppIcon name={fileIcon()} size={16} />
    </span>
    
    <div class="min-w-0">
      <div class="flex items-center gap-2">
        <p class="font-bold text-[0.88rem] truncate text-slate-900 tracking-tight leading-tight">
          {doc.document_number || getDocTypeLabel(doc.document_type)}
        </p>
        {#if doc.is_verified}
          <Badge class="bg-emerald-50 text-emerald-700 border-emerald-100 shadow-none text-[0.70rem] rounded-full px-2 py-0 h-5 font-bold">
            Vérifié
          </Badge>
        {/if}
      </div>
      <p class="text-slate-500 text-[0.78rem] truncate flex items-center gap-1.5 mt-0.5">
        <span class="font-medium text-slate-600 text-[0.82rem]">
          {getDocTypeLabel(doc.document_type)}
        </span>
        {#if subtitle && subtitle !== getDocTypeLabel(doc.document_type)}
          <span class="h-1 w-1 rounded-full bg-slate-300 shrink-0"></span>
          <span class={doc.expiry_date && new Date(doc.expiry_date) < new Date() ? "text-red-500 font-medium text-[0.82rem]" : "text-[0.82rem] text-slate-500"}>
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
      <DropdownMenu.Trigger>
        {#snippet child({ props: menuProps })}
          <Button 
            {...menuProps} 
            variant="ghost" 
            size="icon" 
            class="h-8 w-8 rounded-lg border border-transparent hover:border-slate-200 hover:bg-slate-50 text-slate-400 hover:text-slate-600 transition-colors ml-1"
            onclick={(e) => e.stopPropagation()}
          >
            <AppIcon name="more-vertical" size={18} />
          </Button>
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="w-48 p-1 z-100 bg-white border-slate-100 shadow-fine rounded-xl">
        <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
          Actions
        </DropdownMenu.Label>
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); onEdit(doc); }} 
          class="text-[0.86rem] py-1.5 cursor-pointer flex items-center gap-2"
        >
          <AppIcon name="edit" size={17} class="text-slate-500" />
          Modifier
        </DropdownMenu.Item>
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); document.getElementById(`replace-${doc.id}`)?.click(); }} 
          class="text-[0.86rem] py-1.5 cursor-pointer flex items-center gap-2"
        >
          <AppIcon name="upload" size={17} class="text-slate-500" />
          Remplacer le fichier
        </DropdownMenu.Item>
        <DropdownMenu.Separator />
        <DropdownMenu.Item 
          onclick={(e) => { e.stopPropagation(); onDelete(doc.id, doc.document_number || getDocTypeLabel(doc.document_type)); }} 
          class="text-[0.86rem] py-1.5 cursor-pointer flex items-center gap-2 text-red-600 hover:bg-red-50/30! hover:text-red-700!"
        >
          <AppIcon name="trash" size={17} class="text-inherit" />
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

