<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle 
  } from "@/components/ui/card";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { EmployeeFullProfile, EmployeeDocument } from "@/hr/employees/types/types";
  import { notification } from "@/stores/notification.svelte";
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import { 
    useAddDocumentMutation, 
    useUpdateDocumentMutation, 
    useDeleteDocumentMutation,
    useReplaceDocumentFileMutation
  } from '@/hr/employees/queries/documentQueries';
  
  // Components
  import EmployeeDocumentItem from "./EmployeeDocumentItem.svelte";
  import EmployeeDocumentForm from "./forms/EmployeeDocumentForm.svelte";
  import DocumentPreview from "./DocumentPreview.svelte";

  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  // States
  let isAdding = $state(false);
  let editingDocId = $state<string | null>(null);
  let activePreviewDoc = $state<EmployeeDocument | null>(null);
  let isPreviewOpen = $state(false);

  const documents = $derived(employee.documents || []);

  // Mutations
  const addMutation = $derived(useAddDocumentMutation(employee.id, handleCancelEdit));
  const updateMutation = $derived(useUpdateDocumentMutation(employee.id, handleCancelEdit));
  const deleteMutation = $derived(useDeleteDocumentMutation(employee.id));
  const replaceMutation = $derived(useReplaceDocumentFileMutation(employee.id));

  function handleAdd() {
    editingDocId = null;
    isAdding = true;
  }

  function handleEdit(doc: EmployeeDocument) {
    isAdding = false;
    editingDocId = doc.id;
  }

  function handleCancelEdit() {
    isAdding = false;
    editingDocId = null;
  }

  function handlePreview(doc: EmployeeDocument) {
    activePreviewDoc = doc;
    isPreviewOpen = true;
  }

  function handleReplace(doc: EmployeeDocument, file: File) {
    notification.confirm({
      title: 'Remplacer le fichier',
      message: `Voulez-vous remplacer le fichier du document "${doc.document_number || doc.document_type}" ?`,
      yesText: 'Remplacer',
      onYes: () => {
        $replaceMutation.mutate({ documentId: doc.id, file });
      }
    });
  }

  function handleDelete(id: string, name: string) {
    notification.confirm({
      title: 'Supprimer le document',
      message: `Voulez-vous vraiment supprimer le document "${name}" ? Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => {
        $deleteMutation.mutate(id);
      }
    });
  }

  async function handleSave(data: any) {
    if (editingDocId) {
      if (data.file instanceof File) {
        // Si un nouveau fichier est fourni, on doit le traiter comme un nouvel upload (ou une mise à jour via FormData)
        // Ici, on utilise addDocument si l'API le permet, ou on doit ajouter une mutation d'update complète
        notification.toast.error("La mise à jour de fichier n'est pas encore supportée directement.");
      } else {
        $updateMutation.mutate({ documentId: editingDocId, data });
      }
    } else {
      $addMutation.mutate(data);
    }
  }
</script>


<Card class="py-4 flex flex-col h-[calc(100vh-355px)] overflow-y-scroll shadow-none!">
  <CardHeader class="bg-white shrink-0 px-4">
    <div class="flex items-center justify-between px-2.5">
      <CardTitle class="text-[0.95rem] font-bold flex items-center justify-center gap-3 text-slate-800">
        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
          <AppIcon name="files" size={20} class="text-slate-500" />
        </div>
        Documents administratifs
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-none rounded-full font-bold text-[0.75rem]">
          {documents.length}
        </Badge>
      </CardTitle>
      
      <button 
        onclick={handleAdd}
        disabled={isAdding}
        class="px-3 py-1 cursor-pointer border border-slate-200 rounded-lg font-medium text-[0.84rem]! text-slate-600 hover:border-primary/30 hover:text-primary hover:bg-primary/5 transition-all flex items-center justify-center gap-2 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <AppIcon name="plus" size={17} />
        Nouveau
      </button>
    </div>
  </CardHeader>

  <CardContent class="flex-1 flex flex-col pt-0 min-h-0">
    <div class="flex-1 overflow-y-auto custom-scrollbar min-h-0">
      
      {#if isAdding}
        <div class="p-2 pt-2" transition:slide={{ duration: 250, easing: cubicOut }}>
          <EmployeeDocumentForm 
            onSave={handleSave} 
            onCancel={handleCancelEdit} 
            isLoading={$addMutation.isPending || $updateMutation.isPending} 
          />
        </div>
      {/if}

      <div class="flex flex-col">
        {#each documents as doc, index (doc.id)}
          {#if editingDocId === doc.id}
            <div class="p-2" transition:slide={{ duration: 250, easing: cubicOut }}>
              <EmployeeDocumentForm 
              initialData={doc} 
              onSave={handleSave} 
              onCancel={handleCancelEdit} 
              isLoading={$addMutation.isPending || $updateMutation.isPending} 
            />
            </div>
          {:else}
            <EmployeeDocumentItem 
              {doc}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onPreview={handlePreview}
              onReplace={handleReplace}
              isLast={index === documents.length - 1}
            />
          {/if}
        {:else}
          {#if !isAdding}
            <div class="h-full flex items-center justify-center py-20">
              <Empty 
                title="Aucun document" 
                description="Gérez les pièces justificatives et contrats."
                icon="files"
                iconSize={28}
                iconStrokeWidth={1.3}
                iconClass="text-primary"
              >
                <EmptyButton labelElement="un document" onNew={handleAdd} />
              </Empty>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </CardContent>
</Card>


<!-- Modal de prévisualisation -->
<DocumentPreview 
  doc={activePreviewDoc}
  isOpen={isPreviewOpen}
  onClose={() => isPreviewOpen = false}
/>




