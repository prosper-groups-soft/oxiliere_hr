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
  import type { EmployeeFullProfile, EmployeeEducation } from "@/hr/employees/types/types";
  import { notification } from "@/stores/notification.svelte";
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import { 
    useAddEducationMutation, 
    useUpdateEducationMutation, 
    useDeleteEducationMutation
  } from '@/hr/employees/queries/educationQueries';
  
  // Components
  import EmployeeEducationItem from "./EmployeeEducationItem.svelte";
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


<Card class="py-4 flex flex-col h-[calc(100vh-355px)] overflow-y-scroll shadow-none!">
  <CardHeader class="bg-white shrink-0 px-4">
    <div class="flex items-center justify-between px-2.5">
      <CardTitle class="text-[0.95rem] font-bold flex items-center justify-center gap-3 text-slate-800">
        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
          <AppIcon name="graduation-cap" size={20} class="text-slate-500" />
        </div>
        Parcours académique
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-none rounded-full font-bold text-[0.75rem]">
          {educations.length}
        </Badge>
      </CardTitle>
      
      <button 
        onclick={handleAdd}
        disabled={isAdding}
        class="px-3 py-1 cursor-pointer border border-slate-200 rounded-lg font-medium text-[0.84rem]! text-slate-600 hover:border-primary/30 hover:text-primary hover:bg-primary/5 transition-all flex items-center justify-center gap-2 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <AppIcon name="plus" size={17} />
        Ajouter
      </button>
    </div>
  </CardHeader>

  <CardContent class="flex-1 flex flex-col pt-0 min-h-0">
    <div class="flex-1 overflow-y-auto custom-scrollbar min-h-0">
      
      {#if isAdding}
        <div class="p-2 pt-2" transition:slide={{ duration: 250, easing: cubicOut }}>
          <EmployeeEducationForm 
            onSave={handleSave} 
            onCancel={handleCancelEdit} 
            isLoading={$addMutation.isPending || $updateMutation.isPending} 
          />
        </div>
      {/if}

      <div class="flex flex-col">
        {#each educations as ed, index (ed.id)}
          {#if editingEdId === ed.id}
            <div class="p-2" transition:slide={{ duration: 250, easing: cubicOut }}>
              <EmployeeEducationForm 
                initialData={ed} 
                onSave={handleSave} 
                onCancel={handleCancelEdit} 
                isLoading={$addMutation.isPending || $updateMutation.isPending} 
              />
            </div>
          {:else}
            <EmployeeEducationItem 
              {ed}
              onEdit={handleEdit}
              onDelete={handleDelete}
              isLast={index === educations.length - 1}
            />
          {/if}
        {:else}
          {#if !isAdding}
            <div class="h-full flex items-center justify-center">
              <Empty 
                title="Aucune éducation" 
                description="Ajoutez des diplômes ou qualifications pour cet employé."
                icon="graduation-cap"
                iconSize={24}
                iconStrokeWidth={1.1}
                iconClass="text-primary"
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




