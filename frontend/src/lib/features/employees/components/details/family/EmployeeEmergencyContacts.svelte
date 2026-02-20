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
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { Employee, EmergencyContact } from '../../../types/types';
  import EmployeeActionSheet from '../ui/EmployeeActionSheet.svelte';
  import EmployeeEmergencyContactForm from './forms/EmployeeEmergencyContactForm.svelte';
  import FamilyMemberRow from './FamilyMemberRow.svelte';

  let { employee } = $props<{ employee: Employee }>();
  let isSheetOpen = $state(false);
  let editingContact = $state<EmergencyContact | null>(null);

  // --- Logique métier : Vérification de conformité ---
  const hasPrimaryContact = $derived(familyStore.getEmergencyContacts().some(c => c.primary));
  const contactsCount = $derived(familyStore.getEmergencyContacts().length);

  // --- Handlers ---
  function handleAdd() {
    editingContact = null;
    isSheetOpen = true;
  }

  function handleEdit(contact: EmergencyContact) {
    editingContact = contact;
    isSheetOpen = true;
  }

  function handleDelete(id: number | string, name: string) {
    if (confirm(`Voulez-vous vraiment supprimer le contact ${name} ?`)) {
      familyStore.deleteEmergencyContact(id);
    }
  }

  function handleSave(contactData: any) {
    if (editingContact) {
      familyStore.updateEmergencyContact(editingContact.id, contactData);
    } else {
      familyStore.addEmergencyContact(contactData);
    }
    isSheetOpen = false;
  }
</script>


{#snippet addButton()}
  <button 
    onclick={handleAdd}
    class="mt-4 w-full py-4 cursor-pointer border-2 border-dashed border-slate-200 rounded-2xl text-sm text-slate-500 hover:border-red-200 hover:text-red-600 hover:bg-red-50/30 transition-all flex items-center justify-center gap-2 font-bold shrink-0 group shadow-sm hover:shadow-md"
  >
    <div class="p-1 bg-slate-100 rounded-full group-hover:bg-red-100 transition-colors">
      <AppIcon name="plus" size={18} />
    </div>
    Ajouter un contact
  </button>
{/snippet}


<Card class="flex flex-col h-[calc(100vh-340px)] overflow-hidden shadow-none! py-0">
  <CardHeader class="pb-4 border-b border-slate-50 bg-white shrink-0 py-1!">
    <div class="flex items-center justify-between">
      <CardTitle class="text-[1.1rem] font-extrabold flex items-center gap-3 text-slate-800">
        <div class="p-2 bg-red-50 rounded-lg">
          <AppIcon name="shield-alert" size={22} class="text-red-600" />
        </div>
        Contacts d'urgence
      </CardTitle>
      <Badge variant="secondary" class="bg-red-50 text-red-700 border-none font-bold">
        {contactsCount}
      </Badge>
    </div>
  </CardHeader>

  {#if contactsCount > 0 && !hasPrimaryContact}
    <div class="px-6 py-2.5 bg-amber-50 border-b border-amber-100 shrink-0 flex items-center gap-2">
      <AppIcon name="alert-triangle" size={16} class="text-amber-600" />
      <span class="text-[0.7rem] font-bold text-amber-700 uppercase tracking-tight">
        Veuillez définir un contact principal
      </span>
    </div>
  {:else if contactsCount === 0}
    <div class="px-6 py-2.5 bg-red-50 border-b border-red-100 shrink-0 flex items-center gap-2">
      <AppIcon name="info" size={16} class="text-red-600" />
      <span class="text-[0.7rem] font-bold text-red-700 uppercase tracking-tight">
        Données obligatoires manquantes
      </span>
    </div>
  {/if}
  
  <CardContent class="flex-1 flex flex-col p-4 min-h-0">
    <div class="flex-1 overflow-y-auto space-y-3 pr-1 custom-scrollbar min-h-0">
      {#each familyStore.getEmergencyContacts() as contact (contact.id)}
        <FamilyMemberRow 
          icon="phone"
          iconClass={contact.primary ? "text-red-600" : "text-slate-400"}
          title={contact.name}
          subtitle={contact.relation}
          onEdit={() => handleEdit(contact)}
          onDelete={() => handleDelete(contact.id, contact.name)}
        >
          {#snippet badge()}
            {#if contact.primary}
              <Badge class="bg-red-600 text-white border-none shadow-sm font-bold text-[0.65rem] tracking-tighter px-2">
                PRINCIPAL
              </Badge>
            {:else}
               <span class="text-[0.8rem] text-slate-800">{contact.phone}</span>
            {/if}
          {/snippet}
        </FamilyMemberRow>
      {:else}
        <div class="h-full flex flex-col items-center justify-center py-10 border border-dashed border-slate-100 rounded-2xl bg-slate-50/30 text-center px-6">
          <div class="p-4 bg-white rounded-full shadow-sm mb-3">
            <AppIcon name="phone-off" size={32} class="text-slate-200" />
          </div>
          <p class="text-[0.8rem] text-slate-500 font-bold">Aucun contact de secours</p>
          <p class="text-[0.7rem] text-slate-400 mt-1">Essentiel en cas d'accident ou de malaise au travail.</p>
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
  title={editingContact ? "Modifier le contact" : "Nouveau contact d'urgence"} 
>
  {#if isSheetOpen}
    <EmployeeEmergencyContactForm onSave={handleSave} initialData={editingContact} />
  {/if}
  
  {#snippet footer()}
    <Button type="submit" form="contact-form" class="flex-1 bg-primary! shadow-soft">
      {editingContact ? "Mettre à jour" : "Enregistrer le contact"}
    </Button>
  {/snippet}
</EmployeeActionSheet>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #f1f5f9; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #e2e8f0; }
</style>

