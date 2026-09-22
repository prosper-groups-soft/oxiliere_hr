<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import type { EmployeeFullProfile, EmployeeEducation } from "@/hr/modules/employees/types/types";
  import { notification } from "@/hr/stores/notification.svelte";
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import EmptyButton from '@/hr/components/shared/containers/empty/EmptyButton.svelte';
  import { useAddEducationMutation, useUpdateEducationMutation, useDeleteEducationMutation } from '@/hr/modules/employees/queries/educationQueries';  
  import EmployeeEducationItem from "./items/EmployeeEducationItem.svelte";
  import EmployeeEducationForm from "./forms/EmployeeEducationForm.svelte";


  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  // States
  let isAdding = $state(false);
  let editingEdId = $state<string | null>(null);

  const educations = $derived(employee.educations || []);

  // Mutations
  const addMutation = $derived(useAddEducationMutation(employee.id, handleCancelEdit));
  const updateMutation = $derived(useUpdateEducationMutation(employee.id, handleCancelEdit));
  const deleteMutation = $derived(useDeleteEducationMutation(employee.id));

  // Dérivés pour le formulaire unique hors boucle (même pattern que WorkSiteForm)
  const editingEducation = $derived(
    editingEdId ? (educations.find((e: EmployeeEducation) => e.id === editingEdId) ?? null) : null
  );
  const isFormOpen = $derived(isAdding || editingEdId !== null);
  const isSaving = $derived($addMutation.isPending || $updateMutation.isPending);

  function handleAdd() {
    editingEdId = null;
    isAdding = true;
  }

  function handleEdit(ed: EmployeeEducation) {
    isAdding = false;
    editingEdId = ed.id;
  }

  function handleCancelEdit() {
    isAdding = false;
    editingEdId = null;
  }

  function handleDelete(id: string, degree: string) {
    notification.confirm({
      title: 'Supprimer l\'éducation',
      message: `Voulez-vous vraiment supprimer le diplôme "${degree}" ? Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => {
        $deleteMutation.mutate(id);
      }
    });
  }

  async function handleSave(data: any) {
    if (editingEdId) {
      $updateMutation.mutate({ educationId: editingEdId, data });
    } else {
      $addMutation.mutate(data);
    }
  }
</script>


<Card class="rounded-xl border-slate-200 bg-white overflow-hidden flex flex-col max-h-[calc(100vh-340px)] border-0 shadow-none">
  <CardHeader class="pb-1 border-b border-slate-50 shrink-0 border-0 shadow-none">
    <div class="flex items-center justify-between gap-3">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center shrink-0">
          <AppIcon name="graduation-cap" size={16} class="text-violet-600" />
        </span>
        Parcours académique
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-0 rounded-full font-bold text-[0.70rem] px-2 py-0 h-5">
          {educations.length}
        </Badge>
      </CardTitle>
      
      <button 
        onclick={handleAdd}
        disabled={isFormOpen}
        class="h-8 px-3.5 cursor-pointer bg-white border border-slate-200 rounded-full font-medium text-[0.84rem] text-slate-700 hover:border-violet-200 hover:text-violet-700 hover:bg-violet-50/60 transition-all inline-flex items-center justify-center gap-1.5 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <AppIcon name="plus" size={17} />
        Ajouter
      </button>
    </div>
  </CardHeader>

  <CardContent class="flex-1 flex flex-col pt-0 min-h-0 border-0 shadow-none">
    <div class="flex-1 overflow-y-auto custom-scrollbar min-h-0 -mx-1 px-1">

      {#if isFormOpen}
        <div class="pb-3" transition:slide={{ duration: 250, easing: cubicOut }}>
          {#key editingEdId ?? 'new'}
            <EmployeeEducationForm 
              initialData={editingEducation} 
              onSave={handleSave} 
              onCancel={handleCancelEdit} 
              isLoading={isSaving} 
            />
          {/key}
        </div>
      {/if}

      <div class="flex flex-col gap-2">
        {#each educations as ed (ed.id)}
          <div class:opacity-40={editingEdId === ed.id} class:rounded-xl={editingEdId === ed.id} class:ring-2={editingEdId === ed.id} class:ring-violet-200={editingEdId === ed.id} class:ring-offset-1={editingEdId === ed.id} class:pointer-events-none={editingEdId === ed.id}>
            <EmployeeEducationItem 
              {ed}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          </div>
        {:else}
          {#if !isFormOpen}
            <div class="py-8 flex items-center justify-center">
              <Empty 
                title="Aucune éducation" 
                description="Ajoutez des diplômes ou qualifications pour cet employé."
                icon="graduation-cap"
                iconSize={24}
                iconStrokeWidth={1.1}
                iconClass="text-violet-500"
              >
                <EmptyButton labelElement="une éducation" onNew={handleAdd} />
              </Empty>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </CardContent>
</Card>

