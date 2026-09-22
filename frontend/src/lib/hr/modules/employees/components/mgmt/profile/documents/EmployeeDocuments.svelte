<script lang="ts">
  import type { EmployeeFullProfile, EmployeeDocument } from "@/hr/modules/employees/types/types";
  import { notification } from "@/hr/stores/notification.svelte";
  import { useAddDocumentMutation, useUpdateDocumentMutation, useDeleteDocumentMutation, useReplaceDocumentFileMutation } from '@/hr/modules/employees/queries/documentQueries';
  import DocumentPreview from "./preview/DocumentPreview.svelte";
  import EmployeeDocumentsSection from "./sections/EmployeeDocumentsSection.svelte";
  import EmployeePayslipsSection from "./sections/EmployeePayslipsSection.svelte";


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

  const editingDocument = $derived(
    editingDocId ? (documents.find((d: EmployeeDocument) => d.id === editingDocId) ?? null) : null
  );
  const isFormOpen = $derived(isAdding || editingDocId !== null);
  const isSaving = $derived($addMutation.isPending || $updateMutation.isPending);

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
        notification.toast.error("La mise à jour de fichier n'est pas encore supportée directement.");
      } else {
        $updateMutation.mutate({ documentId: editingDocId, data });
      }
    } else {
      $addMutation.mutate(data);
    }
  }
</script>


<EmployeeDocumentsSection
  {documents}
  {isFormOpen}
  {editingDocId}
  {editingDocument}
  {isSaving}
  onAdd={handleAdd}
  onEdit={handleEdit}
  onDelete={handleDelete}
  onPreview={handlePreview}
  onReplace={handleReplace}
  onSave={handleSave}
  onCancel={handleCancelEdit}
/>

<EmployeePayslipsSection employeeId={employee.id} />

<!-- Modal de prévisualisation -->
<DocumentPreview 
  doc={activePreviewDoc}
  isOpen={isPreviewOpen}
  onClose={() => isPreviewOpen = false}
/>

