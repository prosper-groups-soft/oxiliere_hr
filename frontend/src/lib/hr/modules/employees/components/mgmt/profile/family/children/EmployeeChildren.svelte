<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import EmptyButton from '@/hr/components/shared/containers/empty/EmptyButton.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Badge } from '@/components/ui/badge';
  import { formatDate, calculateAge } from '@/hr/utilities/common/date';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import type { EmployeeChild, EmployeeFullProfile } from '@/hr/modules/employees/types/types';
  import ChildForm from './forms/ChildForm.svelte';
  import FamilyMemberRow from '../FamilyMemberRow.svelte';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import { useAddChildMutation, useUpdateChildMutation, useDeleteChildMutation } from '@/hr/modules/employees/queries/familyQueries';


  let { employee } = $props<{ employee: EmployeeFullProfile }>();
  let isAdding = $state(false);
  let editingChildId = $state<string | null>(null);

  // TanStack Queries - pass handleCancelEdit as onSuccess callback
  function handleCancelEdit() {
    isAdding = false;
    editingChildId = null;
  }

  const addMutation = $derived(useAddChildMutation(employee.id, handleCancelEdit));
  const updateMutation = $derived(useUpdateChildMutation(employee.id, handleCancelEdit));
  const deleteMutation = $derived(useDeleteChildMutation(employee.id));

  const children = $derived(employee.children || []);

  // Dérivés pour formulaire unique hors boucle (même pattern que Education)
  const editingChild = $derived(
    editingChildId ? (children.find((c: EmployeeChild) => c.id === editingChildId) ?? null) : null
  );
  
  const isFormOpen = $derived(isAdding || editingChildId !== null);
  const isSaving = $derived($addMutation.isPending || $updateMutation.isPending);

  function getChildName(child: EmployeeChild): string {
    return child.last_name || 'Enfant sans nom';
  }

  function getGenderLabel(gender?: string): string {
    switch (gender) {
      case 'MALE': return 'Garçon';
      case 'FEMALE': return 'Fille';
      case 'NOT_SPECIFIED': return 'Non spécifié';
      default: return '-';
    }
  }

  function getSubtitle(child: EmployeeChild): string {
    const parts: string[] = [];
    if (child.gender) parts.push(getGenderLabel(child.gender));
    if (child.birthdate) parts.push(`Né(e) le ${formatDate(child.birthdate, false, false)}`);
    return parts.join(' \u00b7 ') || 'Date inconnue';
  }

  // --- Handlers ---
  function handleAdd() {
    editingChildId = null;
    isAdding = true;
  }

  function handleEdit(child: EmployeeChild) {
    isAdding = false;
    editingChildId = child.id;
  }

  function handleDelete(id: string) {
    $deleteMutation.mutate(id);
  }

  function handleSave(childData: any) {
    if (editingChildId) {
      $updateMutation.mutate({ childId: editingChildId, data: childData });
    } else {
      $addMutation.mutate(childData);
    }
  }
</script>


<Card class="rounded-xl border-slate-200 bg-white overflow-hidden flex flex-col max-h-[calc(100vh-340px)] border-0 shadow-none">
  <CardHeader class="pb-1 border-b border-slate-50 shrink-0 border-0 shadow-none">
    <div class="flex items-center justify-between gap-3">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-center shrink-0">
          <AppIcon name="baby" size={16} class="text-sky-600" />
        </span>
        Enfants
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-0 rounded-full font-bold text-[0.70rem] px-2 py-0 h-5">
          {children.length}
        </Badge>
      </CardTitle>
      <button 
        onclick={handleAdd}
        disabled={isFormOpen}
        class="h-8 px-3.5 cursor-pointer bg-white border border-slate-200 rounded-full font-medium text-[0.84rem] text-slate-700 hover:border-sky-200 hover:text-sky-700 hover:bg-sky-50/60 transition-all inline-flex items-center justify-center gap-1.5 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
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
          {#key editingChildId ?? 'new'}
            <ChildForm 
              onSave={handleSave} 
              onCancel={handleCancelEdit} 
              initialData={editingChild}
              isLoading={isSaving} 
              error={editingChildId ? $updateMutation.error : $addMutation.error}
            />
          {/key}
        </div>
      {/if}

      <div class="flex flex-col gap-2">
        {#each children as child (child.id)}
          <div class:opacity-40={editingChildId === child.id} class:rounded-xl={editingChildId === child.id} class:ring-2={editingChildId === child.id} class:ring-sky-200={editingChildId === child.id} class:ring-offset-1={editingChildId === child.id} class:pointer-events-none={editingChildId === child.id}>
            <FamilyMemberRow 
              icon="baby"
              iconClass={child.gender === 'MALE' ? 'text-blue-500' : child.gender === 'FEMALE' ? 'text-pink-500' : 'text-slate-400'}
              title={getChildName(child)}
              subtitle={getSubtitle(child)}
              onEdit={() => handleEdit(child)}
              onDelete={() => handleDelete(child.id)}
            >
              {#snippet badge()}
                {#if child.is_dependent}
                  <Badge class="bg-amber-50 text-amber-700 border-amber-200/50 shadow-none font-semibold text-[0.70rem] rounded-full px-2 py-0 h-5">
                    {'\u00c0 charge'}
                  </Badge>
                {/if}
                {#if child.birthdate}
                  <Badge class="bg-slate-100 text-slate-600 border-slate-200/50 shadow-none font-semibold text-[0.70rem] rounded-full px-2 py-0 h-5">
                    {calculateAge(child.birthdate)} ans
                  </Badge>
                {/if}
              {/snippet}
            </FamilyMemberRow>
          </div>
        {:else}
          {#if !isFormOpen}
            <div class="py-8 flex items-center justify-center">
              <Empty 
                title="Aucun enfant enregistré" 
                description="Ajoutez les enfants de cet employé à son profil."
                icon="users"
                iconSize={24}
                iconStrokeWidth={1.1}
                iconClass="text-sky-500"
              >
                <EmptyButton labelElement="un enfant" onNew={handleAdd} />
              </Empty>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </CardContent>
</Card>
