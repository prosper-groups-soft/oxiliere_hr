<script lang="ts">
  import {
    Card,
    CardContent,
    CardHeader,
    CardTitle
  } from '@/components/ui/card';
  import { Button } from '@/components/ui/button';
  import { Badge } from '@/components/ui/badge';
  import { familyStore } from '@/features/employees/stores/family.svelte';
  import { formatDate, calculateAge } from '@/utilities/common/date';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { Employee, Child } from '../../../types/types';
  import EmployeeActionSheet from '../ui/EmployeeActionSheet.svelte';
  import EmployeeChildForm from './forms/EmployeeChildForm.svelte';
  import FamilyMemberRow from './FamilyMemberRow.svelte';

  let { employee } = $props<{ employee: Employee }>();
  let isSheetOpen = $state(false);
  let editingChild = $state<Child | null>(null);

  // --- Logique métier pour la barre de progression ---
  const MAX_CHILDREN_ALLOWANCE = 4; // Seuil typique pour les primes/quotas
  const quotaPercentage = $derived(Math.min((familyStore.countChildren / MAX_CHILDREN_ALLOWANCE) * 100, 100));

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
    if (confirm(`Voulez-vous vraiment supprimer ${name} ?`)) {
      familyStore.deleteChild(id);
    }
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


{#snippet addButton()}
  <button 
    onclick={handleAdd}
    class="mt-4 w-full py-4 cursor-pointer border-2 border-dashed border-slate-200 rounded-2xl text-sm text-slate-500 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50/30 transition-all flex items-center justify-center gap-2 font-bold shrink-0 group shadow-sm hover:shadow-md"
  >
    <div class="p-1 bg-slate-100 rounded-full group-hover:bg-indigo-100 transition-colors">
      <AppIcon name="plus" size={18} class="group-hover:text-indigo-600" />
    </div>
    Ajouter un membre
  </button>
{/snippet}



<Card class="flex flex-col h-[calc(100vh-340px)] overflow-hidden shadow-none! py-0">
  <CardHeader class="border-b border-slate-50 bg-white shrink-0 py-1!">
    <div class="flex items-center justify-between">
      <CardTitle class="text-[1.1rem] font-extrabold flex items-center gap-3 text-slate-800">
        <div class="p-2 bg-pink-50 rounded-lg">
          <AppIcon name="baby" size={22} class="text-pink-500" />
        </div>
        Enfants
      </CardTitle>
      <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-none font-bold">
        {familyStore.countChildren}
      </Badge>
    </div>
  </CardHeader>

  <div class="px-6 py-3 bg-slate-50/50 border-b border-slate-100 shrink-0">
    <div class="flex items-center justify-between mb-2">
      <span class="text-[0.65rem] font-bold text-slate-500 uppercase tracking-widest">
        Suivi des allocations familiales
      </span>
      <span class="text-[0.7rem] font-bold {familyStore.countChildren > MAX_CHILDREN_ALLOWANCE ? 'text-amber-600' : 'text-slate-700'}">
        {familyStore.countChildren} / {MAX_CHILDREN_ALLOWANCE} enfants
      </span>
    </div>
    <div class="h-2 w-full bg-slate-200 rounded-full overflow-hidden shadow-inner">
      <div 
        class="h-full bg-primary transition-all duration-700 ease-out rounded-full" 
        style="width: {quotaPercentage}%"
      ></div>
    </div>
  </div>
  
  <CardContent class="flex-1 flex flex-col p-4 min-h-0">
    <div class="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar min-h-0">
      {#each familyStore.getChildren() as child (child.id)}
        <FamilyMemberRow 
          icon="baby"
          iconClass={child.gender === 'F' ? 'text-pink-400' : 'text-blue-400'}
          title={child.name}
          subtitle="Né(e) le {formatDate(child.birthDate, false, false)}"
          onEdit={() => handleEdit(child)}
          onDelete={() => handleDelete(child.id, child.name)}
        >
          {#snippet badge()}
            <Badge class="bg-emerald-50 text-emerald-600 border-emerald-100/50 shadow-none font-bold text-[0.7rem]">
              {calculateAge(child.birthDate)} ANS
            </Badge>
          {/snippet}
        </FamilyMemberRow>
      {:else}
        <div class="h-full flex flex-col items-center justify-center py-10 border border-dashed border-slate-100 rounded-2xl bg-slate-50/30">
          <AppIcon name="users" size={40} class="text-slate-200 mb-3" />
          <p class="text-xs text-slate-400 font-medium">Aucun enfant enregistré</p>
        </div>
      {/each}
    </div>
    
    <div class="shrink-0 pt-2 bg-white">
      {@render addButton()}
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
    <Button type="submit" form="child-form" class="flex-1 bg-primary! shadow-soft">
      {editingChild ? "Enregistrer les modifications" : "Ajouter au profil"}
    </Button>
  {/snippet}
</EmployeeActionSheet>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #f1f5f9; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #e2e8f0; }
</style>

