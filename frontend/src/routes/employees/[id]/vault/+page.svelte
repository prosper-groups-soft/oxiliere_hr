<script lang="ts">
	import DocumentPreview from '@/features/employees/components/details/documents/DocumentPreview.svelte';
  import EmployeeDocumentForm from '@/features/employees/components/details/documents/forms/EmployeeDocumentForm.svelte';
  import EmployeeActionSheet from '@/features/employees/components/details/ui/EmployeeActionSheet.svelte';
  import EmployeeDocument from '@/features/employees/components/details/documents/EmployeeDocument.svelte';
  import { page } from '$app/state';
  import { ui } from "@/stores/ui.svelte"; 
  import { employeeStore } from '@/features/employees/stores/employees.svelte';
  import { documentStore } from '@/features/employees/stores/documents.svelte';
  import { Button } from '@/components/ui/button';
  import { flip } from 'svelte/animate';
  import { fade } from 'svelte/transition';
  
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import Empty from '@/components/shared/containers/Empty.svelte';
  
  import { getFileIconName, getStatusConfig } from '@/utilities/common/fs';
  import type { Document } from '@/features/employees/types/types';

  const employeeId = $derived(page.params.id);
  const employee = $derived(employeeId ? employeeStore.getById(employeeId) : undefined);
  const documents = $derived(documentStore.getDocuments());

  let isSheetOpen = $state(false);
  let editingDoc = $state<Document | undefined>(undefined);

  function handleAdd() {
    editingDoc = undefined;
    isSheetOpen = true;
  }

  $effect(() => {
    ui.setActions(uploadAction);
    return () => ui.setActions(null);
  });

  function handleEdit(doc: Document) {
    editingDoc = doc;
    isSheetOpen = true;
  }

  function handleDelete(id: number | string, name: string) {
    if (confirm(`Voulez-vous vraiment supprimer "${name}" ?`)) {
      documentStore.deleteDocument(id);
    }
  }

  function handleSave(docData: any) {
    if (editingDoc) {
      documentStore.updateDocument(editingDoc.id, docData);
    } else {
      documentStore.addDocument(docData);
    }
    isSheetOpen = false;
  }
</script>

{#snippet uploadAction()}
  <Button size="sm" class="h-6 gap-2 px-3 bg-primary hover:bg-primary/90" onclick={handleAdd}>
    <AppIcon name="cloud-upload" size={19} />
    <span class="hidden sm:inline text-sm font-medium">Téléverser</span>
  </Button>
{/snippet}

{#if employee}
  <DocumentPreview />
  
  <div class="flex flex-col h-full overflow-hidden">
    <div class="h-[calc(100vh-47vh)] overflow-y-auto pr-2 custom-scrollbar">
      {#if documents.length > 0}
        <div class="divide-y border border-slate-100 rounded-xl bg-white shadow-sm mb-4">
          {#each documents as doc (doc.id)}
            {@const config = getStatusConfig(doc)}
            {@const fileIcon = getFileIconName(doc.type)}
            
            <div animate:flip={{ duration: 300 }} transition:fade>
              <EmployeeDocument 
                {doc} 
                {config} 
                {fileIcon}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            </div>
          {/each}
        </div>
      {:else}
        <div class="h-full flex items-center justify-center py-20">
          <Empty 
            title="Coffre-fort vide" 
            description="Aucun document n'a été déposé pour cet employé."
            icon="file"
          >
            <Button variant="outline" size="sm" onclick={handleAdd} class="gap-2 mt-4">
              <AppIcon name="plus" size={18} />
              Ajouter un document
            </Button>
          </Empty>
        </div>
      {/if}
    </div>
  </div>

  <EmployeeActionSheet 
    bind:open={isSheetOpen} 
    title={editingDoc ? "Modifier le document" : "Nouveau document"}
  >
    {#if isSheetOpen}
      <EmployeeDocumentForm 
        initialData={editingDoc}
        onSave={handleSave}
      />
    {/if}

    {#snippet footer()}
      <Button type="submit" form="doc-form" class="w-full">
        {editingDoc ? "Mettre à jour" : "Téléverser dans le coffre"}
      </Button>
    {/snippet}
  </EmployeeActionSheet>
{:else}
  <div class="h-full flex items-center justify-center">
    <AnimateSpin text="Récupération des documents..." />
  </div>
{/if}


<style>
  /* Style scrollbar */
  .custom-scrollbar::-webkit-scrollbar {
    width: 5px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>

