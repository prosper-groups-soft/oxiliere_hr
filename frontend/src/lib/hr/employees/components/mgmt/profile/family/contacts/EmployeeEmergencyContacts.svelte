<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle 
  } from '@/components/ui/card';
  import { Badge } from '@/components/ui/badge';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { 
    EmployeeEmergencyContact, 
    EmployeeFullProfile 
  } from '@/hr/employees/types/types';
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import EmergencyContactForm from './forms/EmergencyContactForm.svelte';
  import FamilyMemberRow from '../FamilyMemberRow.svelte';
  import { REVERSE_RELATION_MAPPING } from '@/hr/employees/constants/mappings';
  import { 
    useAddEmergencyContactMutation, 
    useUpdateEmergencyContactMutation, 
    useDeleteEmergencyContactMutation 
  } from '@/hr/employees/queries/familyQueries';

  let { employee } = $props<{ employee: EmployeeFullProfile }>();
  let isAdding = $state(false);
  let editingContactId = $state<string | null>(null);

  // TanStack Queries - pass handleCancelEdit as onSuccess callback
  function handleCancelEdit() {
    isAdding = false;
    editingContactId = null;
  }

  const addMutation = $derived(useAddEmergencyContactMutation(employee.id, handleCancelEdit));
  const updateMutation = $derived(useUpdateEmergencyContactMutation(employee.id, handleCancelEdit));
  const deleteMutation = $derived(useDeleteEmergencyContactMutation(employee.id));

  const contacts = $derived(employee.emergency_contacts || []);
  const contactsCount = $derived(contacts.length);

  function getContactName(contact: EmployeeEmergencyContact): string {
    return contact.last_name || 'Contact sans nom';
  }

  // --- Handlers ---
  function handleAdd() {
    editingContactId = null;
    isAdding = true;
  }

  function handleEdit(contact: EmployeeEmergencyContact) {
    isAdding = false;
    editingContactId = contact.id;
  }

  function handleDelete(id: string) {
    $deleteMutation.mutate(id);
  }

  function handleSave(contactData: any) {
    if (editingContactId) {
      $updateMutation.mutate({ contactId: editingContactId, data: contactData });
    } else {
      $addMutation.mutate(contactData);
    }
  }
</script>


<Card class="flex flex-col h-[calc(100vh-355px)] overflow-hidden shadow-none! py-0">
  <CardHeader class="border-b border-slate-100 bg-white shrink-0 py-1! px-2">
    <div class="flex items-center justify-between pl-2">
      <CardTitle class="text-[0.95rem] font-bold flex items-center justify-center gap-3 text-slate-800">
        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
          <AppIcon name="shield-alert" size={20} class="text-slate-500" />
        </div>
        Contacts d'urgence
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-none rounded-full font-bold text-[0.75rem]">
          {contactsCount}
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
          <EmergencyContactForm 
            onSave={handleSave} 
            onCancel={handleCancelEdit} 
            isLoading={$addMutation.isPending} 
          />
        </div>
      {/if}

      {#each contacts as contact, index (contact.id)}
        {#if editingContactId === contact.id}
          <div class="p-2" transition:slide={{ duration: 250, easing: cubicOut }}>
            <EmergencyContactForm 
              onSave={handleSave} 
              onCancel={handleCancelEdit} 
              initialData={contact} 
              isLoading={$updateMutation.isPending} 
            />
          </div>
        {:else}
          <FamilyMemberRow 
            icon="phone"
            iconClass={contact.is_primary ? "text-primary" : "text-slate-400"}
            title={getContactName(contact)}
            subtitle={REVERSE_RELATION_MAPPING[contact.relation] || contact.relation || 'Relation non spécifiée'}
            onEdit={() => handleEdit(contact)}
            onDelete={() => handleDelete(contact.id)}
            isLast={index === contacts.length - 1}
          >
            {#snippet badge()}
              {#if contact.is_primary}
                <Badge class="bg-primary/10 text-primary border-primary/20 shadow-none font-semibold text-[0.68rem] tracking-tight px-2">
                  PRINCIPAL
                </Badge>
              {:else}
                <span class="text-[0.8rem] text-slate-500">{contact.phone || 'Téléphone non défini'}</span>
              {/if}
            {/snippet}
          </FamilyMemberRow>
        {/if}
      {:else}
        {#if !isAdding}
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
        {/if}
      {/each}
    </div>
  </CardContent>
</Card>



