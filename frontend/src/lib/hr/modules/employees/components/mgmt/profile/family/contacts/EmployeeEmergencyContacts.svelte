<script lang="ts">
  import { slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Badge } from '@/components/ui/badge';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import type { EmployeeEmergencyContact, EmployeeFullProfile } from '@/hr/modules/employees/types/types';
  import EmptyButton from '@/hr/components/shared/containers/empty/EmptyButton.svelte';
  import EmergencyContactForm from './forms/EmergencyContactForm.svelte';
  import FamilyMemberRow from '../FamilyMemberRow.svelte';
  import { REVERSE_RELATION_MAPPING } from '@/hr/modules/employees/constants/mappings';
  import { useAddEmergencyContactMutation, useUpdateEmergencyContactMutation, useDeleteEmergencyContactMutation } from '@/hr/modules/employees/queries/familyQueries';

  
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

  // Dérivés pour formulaire unique hors boucle
  const editingContact = $derived(
    editingContactId ? (contacts.find((c: EmployeeEmergencyContact) => c.id === editingContactId) ?? null) : null
  );
  const isFormOpen = $derived(isAdding || editingContactId !== null);
  const isSaving = $derived($addMutation.isPending || $updateMutation.isPending);

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


<Card class="rounded-xl border-slate-200 bg-white overflow-hidden flex flex-col max-h-[calc(100vh-340px)] border-0 shadow-none">
  <CardHeader class="pb-1 border-b border-slate-50 shrink-0 border-0 shadow-none">
    <div class="flex items-center justify-between gap-3">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center shrink-0">
          <AppIcon name="shield-alert" size={16} class="text-emerald-600" />
        </span>
        Contacts d'urgence
        <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-0 rounded-full font-bold text-[0.70rem] px-2 py-0 h-5">
          {contactsCount}
        </Badge>
      </CardTitle>
      <button 
        onclick={handleAdd}
        disabled={isFormOpen}
        class="h-8 px-3.5 cursor-pointer bg-white border border-slate-200 rounded-full font-medium text-[0.84rem] text-slate-700 hover:border-emerald-200 hover:text-emerald-700 hover:bg-emerald-50/60 transition-all inline-flex items-center justify-center gap-1.5 shrink-0 shadow-fine disabled:opacity-40 disabled:cursor-not-allowed"
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
          {#key editingContactId ?? 'new'}
            <EmergencyContactForm 
              onSave={handleSave} 
              onCancel={handleCancelEdit} 
              initialData={editingContact}
              isLoading={isSaving} 
            />
          {/key}
        </div>
      {/if}

      <div class="flex flex-col gap-2">
        {#each contacts as contact (contact.id)}
          <div class:opacity-40={editingContactId === contact.id} class:rounded-xl={editingContactId === contact.id} class:ring-2={editingContactId === contact.id} class:ring-emerald-200={editingContactId === contact.id} class:ring-offset-1={editingContactId === contact.id} class:pointer-events-none={editingContactId === contact.id}>
            <FamilyMemberRow 
              icon="phone"
              iconClass={contact.is_primary ? "text-emerald-600" : "text-slate-400"}
              title={getContactName(contact)}
              subtitle={REVERSE_RELATION_MAPPING[contact.relation] || contact.relation || 'Relation non spécifiée'}
              onEdit={() => handleEdit(contact)}
              onDelete={() => handleDelete(contact.id)}
            >
              {#snippet badge()}
                {#if contact.is_primary}
                  <Badge class="bg-emerald-50 text-emerald-700 border-emerald-200/50 shadow-none font-bold text-[0.70rem] rounded-full px-2 py-0 h-5">
                    PRINCIPAL
                  </Badge>
                {:else}
                  <span class="text-[0.78rem] font-medium text-slate-500 bg-slate-50 border border-slate-100 rounded-full px-2 py-0.5">{contact.phone || 'Téléphone non défini'}</span>
                {/if}
              {/snippet}
            </FamilyMemberRow>
          </div>
        {:else}
          {#if !isFormOpen}
            <div class="py-8 flex items-center justify-center">
              <Empty 
                title="Aucun contact d'urgence enregistré" 
                description="Ajoutez les contacts d'urgence de cet employé à son profil."
                icon="phone-off"
                iconSize={24}
                iconStrokeWidth={1.1}
                iconClass="text-emerald-500"
              >
                <EmptyButton labelElement="un contact" onNew={handleAdd} />
              </Empty>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </CardContent>
</Card>

