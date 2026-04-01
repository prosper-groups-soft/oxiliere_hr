<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import type { EmergencyContact } from "../../../types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { cn } from "@/utilities/common/css";

  interface Props {
    contact: EmergencyContact;
  }

  let { contact }: Props = $props();

  function togglePrimary() {
    const data = onboardingStore.data;
    if (!contact.primary) {
      // We are turning it ON: unmark all others first
      data.family.emergencyContacts.forEach(c => {
        if (c.primary) onboardingStore.updateEmergencyContact(c.id as string, { primary: false });
      });
      // Then mark the selected one
      onboardingStore.updateEmergencyContact(contact.id as string, { primary: true });
    } else {
      // We are turning it OFF
      onboardingStore.updateEmergencyContact(contact.id as string, { primary: false });
    }
  }

  function removeContact() {
    onboardingStore.removeEmergencyContact(contact.id as string);
  }
</script>


<div 
  class="flex items-center justify-between p-3.5 bg-white border border-slate-200 rounded-lg transition-all hover:border-slate-300 shadow-fine group"
>
  <div class="flex items-center gap-4">
    <div class="w-10 h-10 bg-slate-50 text-slate-500 rounded-md flex items-center justify-center border border-slate-100 shrink-0">
      <AppIcon name="phone" size={20} />
    </div>
    <div>
      <div class="flex items-center gap-2">
        <p class="font-semibold text-slate-900 text-[0.85rem] tracking-tight">{contact.name}</p>
        <span class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest px-1.5 py-0.5 bg-slate-50 rounded border border-slate-100">{contact.relation}</span>
        {#if contact.primary}
          <span class="text-[0.65rem] font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100">PRINCIPAL</span>
        {/if}
      </div>
      <p class="text-[0.75rem] text-slate-500 mt-0.5">{contact.phone}</p>
    </div>
  </div>
  <div class="flex items-center gap-2">
    <Button 
      onclick={togglePrimary} 
      variant="ghost" 
      size="icon" 
      class={cn("h-8 w-8", contact.primary ? "text-blue-600 bg-blue-50" : "text-slate-400 hover:text-blue-600 hover:bg-blue-50")}
      title={contact.primary ? "Retirer la priorité" : "Définir comme prioritaire"}
    >
      <AppIcon name="star" size={16} fill={contact.primary ? "currentColor" : "none"} />
    </Button>
    <Button onclick={removeContact} size="icon" variant="ghost" class="h-8 w-8 text-red-400 hover:text-red-600 hover:bg-red-50">
      <AppIcon name="trash" size={19} />
    </Button>
  </div>
</div>

