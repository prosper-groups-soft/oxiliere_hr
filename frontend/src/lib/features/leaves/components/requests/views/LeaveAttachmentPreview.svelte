<script lang="ts">
  import * as Dialog from "@/components/ui/dialog";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { FILE_TYPES } from "@/constants/features/files";

  
  let {
    fileUrl,
    onClose,
  }: {
    fileUrl: string | undefined;
    onClose: () => void;
  } = $props();

  const ext = $derived(
    fileUrl ? fileUrl.split('.').pop()?.toLowerCase() || '' : ''
  );

  const fileInfo = $derived(FILE_TYPES[ext] ?? FILE_TYPES.unknown);

  const isImage = $derived(fileInfo.type === 'Image');
  const isPdf = $derived(fileInfo.type === 'Document PDF');
</script>


<Dialog.Root open={true} onOpenChange={(open) => !open && onClose()}>
  <Dialog.Portal>
    <Dialog.Overlay class="bg-black/60" />

    <Dialog.Content class="sm:max-w-[58vw] h-[85vh] p-0 flex flex-col overflow-hidden border-none shadow-xl">

      <Dialog.Header class="px-6 py-4 border-b border-slate-100 space-y-0 flex-row items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-rose-100 rounded-lg text-rose-600">
            <AppIcon name="file-text" size={20} />
          </div>
          <div class="flex flex-col gap-1">
            <Dialog.Title class="text-[0.95rem] font-bold text-slate-900 leading-none">
              Justificatif médical
            </Dialog.Title>
            <Dialog.Description class="text-[0.75rem] text-slate-500 uppercase tracking-wider font-medium">
              Pièce jointe du congé maladie
            </Dialog.Description>
          </div>
        </div>
      </Dialog.Header>

      <div class="flex-1 bg-slate-50 overflow-hidden flex items-center justify-center p-4">
        {#if isImage}
          <img
            src={fileUrl}
            alt="Justificatif médical"
            class="max-w-full max-h-full object-contain rounded-md shadow-sm"
          />
        {:else if isPdf}
          <object
            data={fileUrl}
            type="application/pdf"
            aria-label="Aperçu du justificatif médical"
            class="w-full h-full rounded-md shadow-inner bg-white"
          >
            <div class="text-slate-500 text-[0.85rem] flex flex-col items-center justify-center text-center gap-3 h-full">
              <div class="rounded-full p-4">
                <AppIcon name="circle-x" size={32} />
              </div>
              <span class="text-[0.85rem]">
                Aperçu impossible.
              </span>
              <a href={fileUrl} target="_blank" class="text-primary underline text-[0.85rem] flex gap-1 items-center justify-center">
                <AppIcon name="download" size={16} />
                Télécharger le document
              </a>
            </div>
          </object>
        {:else}
          <div class="flex flex-col items-center justify-center text-center max-w-full">
            <div class="p-6 bg-white rounded-3xl shadow-sm mb-6">
              <AppIcon name="eye-off" size={48} class="text-slate-200" />
            </div>
            <p class="text-slate-900 font-bold text-sm">Aperçu indisponible</p>
            <Button
              variant="outline"
              class="mt-6 gap-2 border-slate-200 shadow-fine text-[0.85rem]"
              onclick={() => window.open(fileUrl, '_blank')}
            >
              <AppIcon name="download" size={16} />
              Télécharger
            </Button>
          </div>
        {/if}
      </div>

      <Dialog.Footer class="px-6 py-2.5 border-t border-slate-100 bg-white shrink-0">
        <Button
          variant="ghost"
          size="sm"
          onclick={onClose}
          class="border border-slate-200 bg-white shadow-fine transition-all font-medium px-8! h-8 text-[0.85rem] flex gap-1 justify-center items-center"
        >
          <AppIcon name="x" size={16} class="text-slate-300" />
          Fermer
        </Button>
      </Dialog.Footer>

    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

