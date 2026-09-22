<script lang="ts">
  import { onboardingStore } from "../../../../stores/onboarding.svelte";
  import type { EmergencyContact } from "../../../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import * as Select from "@/components/ui/select";
  import { slide } from "svelte/transition";
  import PhoneInput from "@/components/ui/phone-input";

  import { RELATION_TYPES } from "@/hr/employees/constants/mappings";

  interface Props {
    onClose: () => void;
  }

  let { onClose }: Props = $props();

  let newContact = $state<Partial<EmergencyContact>>({
    name: "",
    relation: "SPOUSE",
    phone: "",
    primary: false
  });

  const currentRelationLabel = $derived(
    RELATION_TYPES.find(r => r.value === newContact.relation)?.label || "Sélectionner..."
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
      relation: newContact.relation || "SPOUSE",
      phone: newContact.phone,
      primary: newContact.primary || onboardingStore.data.family.emergencyContacts.length === 0
    } as EmergencyContact);
    
    newContact = { name: "", relation: "SPOUSE", phone: "", primary: false };
    onClose();
  }
</script>


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
          {#each RELATION_TYPES as rel}
            <Select.SelectItem value={rel.value} label={rel.label}>
              {rel.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>
    <div class="space-y-1.5">
      <PhoneInput 
        id="contact-phone" 
        label="Téléphone" 
        value={newContact.phone || ""} 
        onChange={(v) => newContact.phone = v} 
      />
    </div>
    <div class="flex items-center justify-start">
      <div class="flex items-center space-x-2">
        <Checkbox id="primary" class="cursor-pointer bg-white" bind:checked={newContact.primary} />
        <Label for="primary" class="text-[0.83rem] font-medium leading-none cursor-pointer">Contact prioritaire</Label>
      </div>
    </div>
  </div>
  <div class="flex justify-end pt-2 gap-2">
    <Button 
      variant="ghost" 
      onclick={onClose} 
      class="h-8 text-[0.8rem] text-slate-500 hover:text-slate-700 hover:bg-slate-100 px-4 flex items-center gap-1.5"
    >
      <AppIcon name="x" size={15} class="text-slate-500" />
      Annuler
    </Button>
    <Button 
      onclick={addContact} 
      disabled={!newContact.name || !newContact.phone} 
      size="sm" 
      class="h-8 cursor-pointer bg-primary hover:bg-primary/90 text-white px-6 shadow-fine flex items-center gap-1.5"
    >
      <AppIcon name="plus" size={15} />
      Ajouter
    </Button>
  </div>
</div>
