<script lang="ts">
	import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import {
    Card,
    CardContent,
    CardHeader,
    CardTitle
  } from '@/components/ui/card';
  import { Button } from '@/components/ui/button';
  import { Badge } from '@/components/ui/badge';
  import { familyStore } from '@/features/employees/stores/family.svelte';
  import { notification } from '@/stores/notification.svelte';
  import { formatDate, calculateAge } from '@/utilities/common/date';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { Employee, Child } from '@/features/employees/types/types';
  import EmployeeActionSheet from '../../sheets/EmployeeActionSheet.svelte';
  import EmployeeChildForm from './EmployeeChildForm.svelte';
  import FamilyMemberRow from '../FamilyMemberRow.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';

  let { employee } = $props<{ employee: Employee }>();
  let isSheetOpen = $state(false);
  let editingChild = $state<Child | null>(null);

  // --- Handlers ---
  function handleAdd() {
    editingChild = null;
    isSheetOpen = true;
  }

  function handleEdit(child: Child) {
    editingChild = child;
    isSheetOpen = true;
  }

  function handleDelete(id: number | string, name: string) {
    notification.confirm({
      title: 'Supprimer l\'enfant',
      message: `Voulez-vous vraiment supprimer ${name} ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => familyStore.deleteChild(id),
    });
  }

  function handleSave(childData: any) {
    if (editingChild) {
      familyStore.updateChild(editingChild.id, childData);
    } else {
      familyStore.addChild(childData);
    }
    isSheetOpen = false;
  }
</script>


<Card class="flex flex-col h-[calc(100vh-355px)] overflow-hidden shadow-none! py-0">
  <CardHeader class="border-b border-slate-100 bg-white shrink-0 py-1! px-2">
    <div class="flex items-center justify-between">
      <CardTitle class="text-[1rem] font-bold flex items-center justify-center gap-3 text-slate-800">
        <div class="p-2 bg-pink-50 rounded-lg">
          <AppIcon name="baby" size={22} class="text-pink-500" />
        </div>
        Enfants
        <Badge variant="secondary" class="bg-slate-100 text-slate-700 border-none rounded-full font-bold">
          {familyStore.countChildren}
        </Badge>
      </CardTitle>
      <button 
        onclick={handleAdd}
        class="px-3 py-1 cursor-pointer border border-slate-200 rounded-lg text-[0.8rem]! text-slate-700 hover:border-indigo-200 hover:text-indigo-600 hover:bg-indigo-50 transition-all flex items-center justify-center gap-2 shrink-0 group shadow-fine"
      >
        <AppIcon name="plus" size={17} />
        Nouveau
      </button>
    </div>
  </CardHeader>
  
  <CardContent class="flex-1 flex flex-col p-2 pt-0 min-h-0">
    <div class="flex-1 overflow-y-auto pr-1 custom-scrollbar min-h-0">
      {#each familyStore.getChildren() as child, index (child.id)}
        <FamilyMemberRow 
          icon="baby"
          iconClass={child.gender === 'F' ? 'text-pink-400' : 'text-blue-400'}
          title={child.name}
          subtitle="Né(e) le {formatDate(child.birthDate, false, false)}"
          onEdit={() => handleEdit(child)}
          onDelete={() => handleDelete(child.id, child.name)}
          isLast={index === familyStore.getChildren().length - 1}
        >
          {#snippet badge()}
            <Badge class="bg-emerald-50 text-emerald-600 border-emerald-100/50 shadow-none font-bold text-[0.7rem]">
              {calculateAge(child.birthDate)} ANS
            </Badge>
          {/snippet}
        </FamilyMemberRow>
      {:else}
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
      {/each}
    </div>
  </CardContent>
</Card>


<EmployeeActionSheet 
  bind:open={isSheetOpen} 
  title={editingChild ? "Modifier l'enfant" : "Ajouter un enfant"} 
>
  {#if isSheetOpen}
    <EmployeeChildForm onSave={handleSave} initialData={editingChild} />
  {/if}

  {#snippet footer()}
    <Button type="submit" form="child-form" class="flex-1 bg-primary! shadow-fine h-9">
      {#if editingChild}
        <AppIcon name="check" size={17} />
        Enregistrer
      {:else}
        <AppIcon name="plus" size={17} />
        Ajouter au profil
      {/if}
    </Button>
  {/snippet}
</EmployeeActionSheet>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #f1f5f9; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #e2e8f0; }
</style>

