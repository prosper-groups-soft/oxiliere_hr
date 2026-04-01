<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import type { EmergencyContact, Child } from "../../../types/types";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import * as Select from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";
  import { slide } from "svelte/transition";
  import { flip } from "svelte/animate";

  // Sub-components
  import EmergencyContactItem from "../family/EmergencyContactItem.svelte";
  import FamilyMemberItem from "../family/FamilyMemberItem.svelte";

  const relationTypes = [
    { value: "Conjoint", label: "Conjoint(e)" },
    { value: "Parent", label: "Parent" },
    { value: "Enfant", label: "Enfant" },
    { value: "Frère/Sœur", label: "Frère / Sœur" },
    { value: "Ami", label: "Ami(e)" },
    { value: "Autre", label: "Autre" }
  ];

  // Forms state
  let showAddContact = $state(false);
  let showAddChild = $state(false);

  // New item state
  let newContact = $state<Partial<EmergencyContact>>({
    name: "",
    relation: "Conjoint",
    phone: "",
    primary: false
  });

  let newChild = $state<Partial<Child>>({
    name: "",
    birthDate: "",
    gender: "M"
  });

  const currentRelationLabel = $derived(
    relationTypes.find(r => r.value === newContact.relation)?.label || "Sélectionner..."
  );

  function addContact() {
    if (!newContact.name || !newContact.phone) return;
    
    if (newContact.primary) {
      onboardingStore.data.family.emergencyContacts.forEach(c => {
        if (c.primary) onboardingStore.updateEmergencyContact(c.id as string, { primary: false });
      });
    }

    onboardingStore.addEmergencyContact({
      id: crypto.randomUUID(),
      name: newContact.name,
      relation: newContact.relation || "Contact",
      phone: newContact.phone,
      primary: newContact.primary || onboardingStore.data.family.emergencyContacts.length === 0
    } as EmergencyContact);
    newContact = { name: "", relation: "Conjoint", phone: "", primary: false };
    showAddContact = false;
  }

  function addChild() {
    if (!newChild.name || !newChild.birthDate) return;
    onboardingStore.addChild({
      id: crypto.randomUUID(),
      name: newChild.name,
      birthDate: newChild.birthDate,
      gender: newChild.gender || "M"
    } as Child);
    newChild = { name: "", birthDate: "", gender: "M" };
    showAddChild = false;
  }
</script>


{#snippet contactForm()}
  <div transition:slide class="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Nom complet</Label>
        <Input bind:value={newContact.name} placeholder="ex: KIBANGULA MUSUYU Prosper" class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
      </div>
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Relation</Label>
        <Select.Root type="single" bind:value={newContact.relation}>
          <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm">
            {currentRelationLabel}
          </Select.Trigger>
          <Select.Content>
            {#each relationTypes as rel}
              <Select.SelectItem value={rel.value} label={rel.label}>
                {rel.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Téléphone</Label>
        <Input bind:value={newContact.phone} placeholder="ex: +243 000 000 000" class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
      </div>
      <div class="flex items-end pb-2">
        <div class="flex items-center space-x-2">
          <Checkbox id="primary" bind:checked={newContact.primary} />
          <Label for="primary" class="text-[0.83rem] font-medium leading-none cursor-pointer">Contact prioritaire</Label>
        </div>
      </div>
    </div>
    <div class="flex justify-end">
      <Button onclick={addContact} disabled={!newContact.name || !newContact.phone} size="sm" class="h-8 cursor-pointer bg-slate-900 hover:bg-slate-800 text-white px-6">
        Confirmer l'ajout
      </Button>
    </div>
  </div>
{/snippet}


{#snippet childForm()}
  <div transition:slide class="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4 mb-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Prénom & Nom</Label>
        <Input bind:value={newChild.name} placeholder="ex: KIBANGULA MUSUYU Prosper" class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
      </div>
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Date de naissance</Label>
        <Input bind:value={newChild.birthDate} type="date" class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
      </div>
    </div>
    <div class="flex justify-end pt-2">
      <Button onclick={addChild} disabled={!newChild.name || !newChild.birthDate} size="sm" class="h-8 bg-slate-900 hover:bg-slate-800 text-white px-6">
        Confirmer l'ajout
      </Button>
    </div>
  </div>
{/snippet}


<div class="space-y-8">
  <!-- Emergency Contacts -->
  <Card class="border-slate-200 shadow-none rounded-none border-0 p-0">
    <CardHeader class="px-0 pt-0 pb-0">
      <div class="flex items-center justify-between">
        <div>
          <CardTitle class="text-md font-bold text-slate-900 tracking-tight">
            Contacts d'urgence
          </CardTitle>
          <CardDescription class="text-[0.835rem]">Personnes à prévenir en priorité absolue.</CardDescription>
        </div>
        <Button 
          onclick={() => showAddContact = !showAddContact} 
          variant="default" 
          size="sm" 
          class="h-7.5 border-slate-200 bg-primary text-white text-[0.8rem]"
        >
          <AppIcon name={showAddContact ? "close" : "plus"} size={17} />
          {showAddContact ? "Annuler" : "Ajouter un contact"}
        </Button>
      </div>
    </CardHeader>

    <CardContent class="px-0 py-0 space-y-4">
      {#if showAddContact}
        {@render contactForm()}
      {/if}

      <div class="grid grid-cols-1 gap-3">
        {#each onboardingStore.data.family.emergencyContacts as contact (contact.id)}
          <div animate:flip={{duration: 200}}>
            <EmergencyContactItem {contact} />
          </div>
        {/each}

        {#if onboardingStore.data.family.emergencyContacts.length === 0 && !showAddContact}
          <div class="py-12 flex flex-col items-center justify-center text-slate-500 bg-slate-50/50 rounded-lg border border-dashed border-slate-200 gap-2">
            <AppIcon name="phone" size={28} strokeWidth={0.8} class="opacity-60" />
            <p class="text-[0.81rem]">Aucun contact ajouté</p>
          </div>
        {/if}
      </div>
    </CardContent>
  </Card>

  <!-- Children -->
  <Card class="border-slate-200 shadow-none rounded-none border-0 p-0 pt-4">
    <CardHeader class="px-0 pt-0 pb-0">
      <div class="flex items-center justify-between">
        <div>
          <CardTitle class="text-md font-bold text-slate-900 tracking-tight">
            Ayants droit & Famille
          </CardTitle>
          <CardDescription class="text-[0.835rem]">Gérez les membres de la famille.</CardDescription>
        </div>
        <Button 
          onclick={() => showAddChild = !showAddChild} 
          variant="default" 
          size="sm" 
          class="h-7.5 shadow-fine border-slate-200 bg-primary text-white text-[0.8rem]"
        >
          <AppIcon name={showAddChild ? "close" : "plus"} size={17} />
          {showAddChild ? "Annuler" : "Ajouter un membre"}
        </Button>
      </div>
    </CardHeader>

    <CardContent class="px-0 py-0 space-y-4">
      {#if showAddChild}
        {@render childForm()}
      {/if}

      <div class="grid grid-cols-1 gap-3">
        {#each onboardingStore.data.family.children as member (member.id)}
          <div animate:flip={{duration: 200}}>
            <FamilyMemberItem {member} />
          </div>
        {/each}

        {#if onboardingStore.data.family.children.length === 0 && !showAddChild}
          <div class="py-12 flex flex-col items-center justify-center text-slate-500 bg-slate-50/50 rounded-lg border border-dashed border-slate-200 gap-3">
            <AppIcon name="users" size={28} strokeWidth={0.8} class="opacity-60" />
            <p class="text-[0.81rem]">Aucun membre de famille</p>
          </div>
        {/if}
      </div>
    </CardContent>
  </Card>
</div>

