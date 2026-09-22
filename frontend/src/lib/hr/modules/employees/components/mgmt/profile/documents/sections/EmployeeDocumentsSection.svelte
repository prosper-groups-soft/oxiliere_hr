<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import EmptyButton from '@/hr/components/shared/containers/empty/EmptyButton.svelte';
  import type { EmployeeDocument } from '@/hr/modules/employees/types/types';
  import EmployeeDocumentItem from '../items/EmployeeDocumentItem.svelte';
  import EmployeeDocumentForm from '../forms/EmployeeDocumentForm.svelte';

  
  type Props = {
    documents: EmployeeDocument[];
    isFormOpen: boolean;
    editingDocId: string | null;
    editingDocument: EmployeeDocument | null;
    isSaving: boolean;
    onAdd: () => void;
    onEdit: (doc: EmployeeDocument) => void;
    onDelete: (id: string, name: string) => void;
    onPreview: (doc: EmployeeDocument) => void;
    onReplace: (doc: EmployeeDocument, file: File) => void;
    onSave: (data: any) => void;
    onCancel: () => void;
  };

  let {
    documents,
    isFormOpen,
    editingDocId,
    editingDocument,
    isSaving,
    onAdd,
    onEdit,
    onDelete,
    onPreview,
    onReplace,
    onSave,
    onCancel
  }: Props = $props();
</script>

<Card class="rounded-xl border-slate-200 bg-white overflow-hidden flex flex-col max-h-[calc(100vh-340px)] border-0 shadow-none">
  <CardHeader class="pb-1 border-b border-slate-50 shrink-0 border-0 shadow-none">
    <div class="flex items-center justify-between gap-3">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-center shrink-0">
          <AppIcon name="files" size={16} class="text-amber-600" />
        </span>
        Documents administratifs
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-0 rounded-full font-bold text-[0.70rem] px-2 py-0 h-5">
          {documents.length}
        </Badge>
      </CardTitle>

      <button
        onclick={onAdd}
        disabled={isFormOpen}
        class="h-8 px-3.5 cursor-pointer bg-white border border-slate-200 rounded-full font-medium text-[0.84rem] text-slate-700 hover:border-amber-200 hover:text-amber-700 hover:bg-amber-50/60 transition-all inline-flex items-center justify-center gap-1.5 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <AppIcon name="plus" size={17} />
        Nouveau
      </button>
    </div>
  </CardHeader>

  <CardContent class="flex-1 flex flex-col pt-0 min-h-0 border-0 shadow-none">
    <div class="flex-1 overflow-y-auto custom-scrollbar min-h-0 -mx-1 px-1">
      {#if isFormOpen}
        <div class="pb-3" transition:slide={{ duration: 250, easing: cubicOut }}>
          {#key editingDocId ?? 'new'}
            <EmployeeDocumentForm
              initialData={editingDocument}
              onSave={onSave}
              onCancel={onCancel}
              isLoading={isSaving}
            />
          {/key}
        </div>
      {/if}

      <div class="flex flex-col gap-2">
        {#each documents as doc (doc.id)}
          <div
            class:opacity-40={editingDocId === doc.id}
            class:rounded-xl={editingDocId === doc.id}
            class:ring-2={editingDocId === doc.id}
            class:ring-amber-200={editingDocId === doc.id}
            class:ring-offset-1={editingDocId === doc.id}
            class:pointer-events-none={editingDocId === doc.id}
          >
            <EmployeeDocumentItem
              {doc}
              onEdit={onEdit}
              onDelete={onDelete}
              onPreview={onPreview}
              onReplace={onReplace}
            />
          </div>
        {:else}
          {#if !isFormOpen}
            <div class="py-8 flex items-center justify-center">
              <Empty
                title="Aucun document"
                description="Gérez les pièces justificatives et contrats."
                icon="files"
                iconSize={24}
                iconStrokeWidth={1.1}
                iconClass="text-amber-500"
              >
                <EmptyButton labelElement="un document" onNew={onAdd} />
              </Empty>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </CardContent>
</Card>
