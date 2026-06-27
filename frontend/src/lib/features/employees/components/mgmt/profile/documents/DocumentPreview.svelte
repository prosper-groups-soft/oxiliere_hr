<script lang="ts">
  import * as Dialog from "@/components/ui/dialog";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { EmployeeDocument } from "@/features/employees/types/types";
  import { getMediaUrl } from "@/utilities/common/media";
  import { DOCUMENT_TYPES } from "@/features/employees/constants/documents";

  interface Props {
    doc: EmployeeDocument | null;
    isOpen: boolean;
    onClose: () => void;
  }

  let { doc, isOpen, onClose }: Props = $props();

  const getDocTypeLabel = (value?: string) => 
    DOCUMENT_TYPES.find(t => t.value === value)?.label || value || "Document";

  const fileUrl = $derived(getMediaUrl(doc?.file));
  
  const isImage = $derived(() => {
    if (!doc?.file) return false;
    const ext = doc.file.split('.').pop()?.toLowerCase() || '';
    return ['jpg', 'jpeg', 'png', 'svg', 'webp'].includes(ext);
  });

  const isPdf = $derived(() => {
    if (!doc?.file) return false;
    return doc.file.toLowerCase().endsWith('.pdf');
  });
</script>


<Dialog.Root bind:open={isOpen} onOpenChange={(open) => !open && onClose()}>

  <Dialog.Portal>
    <Dialog.Overlay class="bg-black/60" />
    
    <Dialog.Content class="sm:max-w-[90vw] h-[85vh] p-0 flex flex-col overflow-hidden border-none shadow-2xl">
      
      <Dialog.Header class="px-6 py-4 border-b border-slate-100 space-y-0 flex-row items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-slate-100 rounded-lg text-primary">
            <AppIcon name="file-text" size={20} />
          </div>
          <div class="flex flex-col gap-1">
            <Dialog.Title class="text-[0.95rem] font-bold text-slate-900 leading-none">
              {doc?.document_number || getDocTypeLabel(doc?.document_type)}
            </Dialog.Title>
            <Dialog.Description class="text-[0.75rem] text-slate-500 uppercase tracking-wider font-medium">
              {getDocTypeLabel(doc?.document_type)}
            </Dialog.Description>
          </div>
        </div>
      </Dialog.Header>

      <div class="flex-1 bg-slate-50 overflow-hidden flex items-center justify-center p-4">
        {#if doc}
          {#if isImage()}
            <img 
              src={fileUrl} 
              alt={doc.document_type} 
              class="max-w-full max-h-full object-contain rounded-md shadow-sm"
            />
          {:else if isPdf()}
            <object 
              data={fileUrl} 
              type="application/pdf" 
              aria-label="Aperçu du document PDF"
              class="w-full h-full rounded-md shadow-inner bg-white"
            >
              <p class="text-slate-500">Aperçu impossible. 
                <a href={fileUrl} target="_blank" class="text-primary underline">Télécharger le document</a>
              </p>
            </object>
          {:else}
            <div class="flex flex-col items-center text-center max-w-xs">
              <div class="p-6 bg-white rounded-3xl shadow-sm mb-6">
                <AppIcon name="eye-off" size={48} class="text-slate-200" />
              </div>
              <p class="text-slate-900 font-bold text-sm">Aperçu indisponible</p>
              <Button variant="outline" class="mt-6 gap-2 border-slate-200 shadow-soft" onclick={() => window.open(fileUrl, '_blank')}>
                <AppIcon name="download" size={16} />
                Télécharger
              </Button>
            </div>
          {/if}
        {/if}
      </div>

      <Dialog.Footer class="px-6 py-3 border-t border-slate-100 bg-white shrink-0">
        <Button 
          variant="ghost" 
          size="sm" 
          onclick={onClose} 
          class="border border-slate-200 bg-white shadow-soft transition-all font-medium px-6 h-8"
        >
          Fermer
        </Button>
      </Dialog.Footer>
      
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>


<style>
  /* Ensure the default Shadcn close button (Dialog.Content) is discrete 
    or hide it if your design uses the "Close" button at the bottom. */
  :global([data-dialog-close]) {
    outline: none;
  }
</style>
