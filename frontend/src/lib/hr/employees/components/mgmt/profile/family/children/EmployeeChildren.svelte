<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import {
    Card,
    CardContent,
    CardHeader,
    CardTitle
  } from '@/components/ui/card';
  import { Badge } from '@/components/ui/badge';
  import { formatDate, calculateAge } from '@/utilities/common/date';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { EmployeeChild, EmployeeFullProfile } from '@/hr/employees/types/types';
  import ChildForm from './forms/ChildForm.svelte';
  import FamilyMemberRow from '../FamilyMemberRow.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import { 
    useAddChildMutation, 
    useUpdateChildMutation, 
    useDeleteChildMutation 
  } from '@/hr/employees/queries/familyQueries';

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


<Card class="flex flex-col h-[calc(100vh-355px)] overflow-hidden shadow-none! py-0">
  <CardHeader class="border-b border-slate-100 bg-white shrink-0 py-1! px-2">
    <div class="flex items-center justify-between pl-2">
      <CardTitle class="text-[0.95rem] font-bold flex items-center justify-center gap-3 text-slate-800">
        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
          <AppIcon name="baby" size={20} class="text-slate-500" />
        </div>
        Enfants
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-none rounded-full font-bold text-[0.75rem]">
          {children.length}
        </Badge>
      </CardTitle>
      <button 
        onclick={handleAdd}
        disabled={isAdding}
        class="px-3 py-1 cursor-pointer border border-slate-200 rounded-lg text-[0.8rem]! text-slate-600 hover:border-primary/30 hover:text-primary hover:bg-primary/5 transition-all flex items-center justify-center gap-2 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <AppIcon name="plus" size={16} />
        Nouveau
      </button>
    </div>
  </CardHeader>
  
  <CardContent class="flex-1 flex flex-col p-2 pt-0 min-h-0">
    <div class="flex-1 overflow-y-auto pr-1 custom-scrollbar min-h-0">

      {#if isAdding}
        <div class="p-2 pt-2" transition:slide={{ duration: 250, easing: cubicOut }}>
          <ChildForm 
            onSave={handleSave} 
            onCancel={handleCancelEdit} 
            isLoading={$addMutation.isPending} 
            error={$addMutation.error}
          />
        </div>
      {/if}

      {#each children as child, index (child.id)}
        {#if editingChildId === child.id}
          <div class="p-2" transition:slide={{ duration: 250, easing: cubicOut }}>
            <ChildForm 
              onSave={handleSave} 
              onCancel={handleCancelEdit} 
              initialData={child} 
              isLoading={$updateMutation.isPending}
              error={$updateMutation.error}
            />
          </div>
        {:else}
          <FamilyMemberRow 
            icon="baby"
            iconClass={child.gender === 'MALE' ? 'text-blue-400' : child.gender === 'FEMALE' ? 'text-pink-400' : 'text-slate-400'}
            title={getChildName(child)}
            subtitle={getSubtitle(child)}
            onEdit={() => handleEdit(child)}
            onDelete={() => handleDelete(child.id)}
            isLast={index === children.length - 1}
          >
            {#snippet badge()}
              {#if child.is_dependent}
                <Badge class="bg-amber-50 text-amber-700 border-amber-200/50 shadow-none font-semibold text-[0.75rem]">
                  {'\u00c0 charge'}
                </Badge>
              {/if}
              {#if child.birthdate}
                <Badge class="bg-slate-100 text-slate-600 border-slate-200/50 shadow-none font-semibold text-[0.8rem]">
                  {calculateAge(child.birthdate)} ans
                </Badge>
              {/if}
            {/snippet}
          </FamilyMemberRow>
        {/if}
      {:else}
        {#if !isAdding}
          <div class="h-full flex items-center justify-center">
            <Empty 
              title="Aucun enfant enregistré" 
              description="Ajoutez les enfants de cet employé à son profil."
              icon="users"
              iconSize={24}
              iconStrokeWidth={1.1}
              iconClass="text-primary"
            >
              <EmptyButton labelElement="un enfant" onNew={handleAdd} />
            </Empty>
          </div>
        {/if}
      {/each}
    </div>
  </CardContent>
</Card>




