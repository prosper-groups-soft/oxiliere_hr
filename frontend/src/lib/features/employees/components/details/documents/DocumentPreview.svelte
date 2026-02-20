<script lang="ts">
  import * as Dialog from "@/components/ui/dialog";
  import { previewStore } from "../../../stores/preview.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";

  // Derived state to react to store changes
  const doc = $derived(previewStore.activeDoc);
</script>


<Dialog.Root bind:open={previewStore.isOpen}>
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
              {doc?.name}
            </Dialog.Title>
            <Dialog.Description class="text-[0.75rem] text-slate-500 uppercase tracking-wider font-medium">
              {doc?.size} • {doc?.type}
            </Dialog.Description>
          </div>
        </div>
      </Dialog.Header>

      <div class="flex-1 bg-slate-50 overflow-hidden flex items-center justify-center p-4">
        {#if doc}
          {#if ['jpg', 'jpeg', 'png', 'svg'].includes(doc.type.toLowerCase())}
            <img 
              src={doc.url} 
              alt={doc.name} 
              class="max-w-full max-h-full object-contain rounded-md shadow-sm"
            />
          {:else if doc.type.toLowerCase() === 'pdf'}
            <iframe 
              src={doc.url} 
              title={doc.name}
              class="w-full h-full border-none rounded-md shadow-inner bg-white"
            ></iframe>
          {:else}
            <div class="flex flex-col items-center text-center max-w-xs">
              <div class="p-6 bg-white rounded-3xl shadow-sm mb-6">
                <AppIcon name="eye-off" size={48} class="text-slate-200" />
              </div>
              <p class="text-slate-900 font-bold text-sm">Aperçu indisponible</p>
              <Button variant="outline" class="mt-6 gap-2 border-slate-200 shadow-soft">
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
          onclick={() => previewStore.close()} 
          class="border border-slate-200 bg-white shadow-soft transition-all"
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
