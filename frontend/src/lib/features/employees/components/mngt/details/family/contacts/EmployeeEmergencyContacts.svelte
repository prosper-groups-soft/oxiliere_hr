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
  import { notification } from '@/stores/notification.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { Employee, EmergencyContact } from '@/features/employees/types/types';
	import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import EmployeeActionSheet from '../../sheets/EmployeeActionSheet.svelte';
  import EmployeeEmergencyContactForm from './EmployeeEmergencyContactForm.svelte';
  import FamilyMemberRow from '../FamilyMemberRow.svelte';

  let { employee } = $props<{ employee: Employee }>();
  let isSheetOpen = $state(false);
  let editingContact = $state<EmergencyContact | null>(null);

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
    notification.confirm({
      title: 'Supprimer le contact',
      message: `Voulez-vous vraiment supprimer le contact ${name} ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => familyStore.deleteEmergencyContact(id),
    });
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


<Card class="flex flex-col h-[calc(100vh-355px)] overflow-hidden shadow-none! py-0">
  <CardHeader class="pb-4 border-b border-slate-50 bg-white shrink-0 py-1! px-2">
    <div class="flex items-center justify-between">
      <CardTitle class="text-[1rem] font-bold flex items-center justify-center gap-3 text-slate-800">
        <div class="p-2 bg-red-50 rounded-lg">
          <AppIcon name="shield-alert" size={22} class="text-red-600" />
        </div>
        Contacts d'urgence
        <Badge variant="secondary" class="bg-red-50 text-red-700 border-none rounded-full font-bold">
          {contactsCount}
        </Badge>
      </CardTitle>
      <button 
        onclick={handleAdd}
        class="px-3 py-1 cursor-pointer border border-slate-200 rounded-lg text-[0.8rem]! text-slate-700 hover:border-red-200 hover:text-red-600 hover:bg-red-50 transition-all flex items-center justify-center gap-2 shrink-0 group shadow-fine"
      >
        <AppIcon name="plus" size={17} />
        Nouveau
      </button>
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
  
  <CardContent class="flex-1 flex flex-col p-2 pt-0 min-h-0">
    <div class="flex-1 overflow-y-auto pr-1 custom-scrollbar min-h-0">
      {#each familyStore.getEmergencyContacts() as contact, index (contact.id)}
        <FamilyMemberRow 
          icon="phone"
          iconClass={contact.primary ? "text-red-600" : "text-slate-400"}
          title={contact.name}
          subtitle={contact.relation}
          onEdit={() => handleEdit(contact)}
          onDelete={() => handleDelete(contact.id, contact.name)}
          isLast={index === familyStore.getEmergencyContacts().length - 1}
        >
          {#snippet badge()}
            {#if contact.primary}
              <Badge class="bg-red-600 text-white border-none shadow-fine font-bold text-[0.65rem] tracking-tighter px-2">
                PRINCIPAL
              </Badge>
            {:else}
               <span class="text-[0.8rem] text-slate-800">{contact.phone}</span>
            {/if}
          {/snippet}
        </FamilyMemberRow>
      {:else}
        <div class="h-full flex items-center justify-center">
          <Empty 
            title="Aucun contact d'urgence enregistré" 
            description="Ajoutez les contacts d'urgence de cet employé à son profil."
            icon="phone-off"
            iconSize={24}
            iconStrokeWidth={1.1}
            iconClass="text-primary"
          >
            <EmptyButton labelElement="un contact" onNew={handleAdd} />
          </Empty>
        </div>
      {/each}
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
    <Button type="submit" form="contact-form" class="flex-1 bg-primary! shadow-fine h-9">
      {#if editingContact}
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

