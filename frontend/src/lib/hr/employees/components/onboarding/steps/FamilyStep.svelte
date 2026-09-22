<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";
  import { flip } from "svelte/animate";
  import { slide } from "svelte/transition";

  // Sub-components
  import EmergencyContactItem from "../family/EmergencyContactItem.svelte";
  import FamilyMemberItem from "../family/FamilyMemberItem.svelte";
  import ContactForm from "../family/forms/ContactForm.svelte";
  import ChildForm from "../family/forms/ChildForm.svelte";

  // Forms state
  let showAddContact = $state(false);
  let showAddChild = $state(false);
</script>


<div class="space-y-8">
  <!-- Emergency Contacts -->
  <Card class="border-slate-200 shadow-none rounded-none border-0 p-0">
    <CardHeader class="px-0 pt-0 pb-0">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
            <AppIcon name="shield-alert" size={20} class="text-slate-500" />
          </div>
          <div>
            <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
              Contacts d'urgence
            </CardTitle>
            <CardDescription class="text-[0.835rem]">
              Personnes à prévenir en priorité absolue.
            </CardDescription>
          </div>
        </div>
        <Button 
          onclick={() => showAddContact = !showAddContact} 
          variant="outline" 
          size="sm" 
          class="h-8 border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-[0.8rem] shadow-fine"
        >
          <AppIcon name={showAddContact ? "x" : "plus"} size={17} />
          {showAddContact ? "Annuler" : "Nouveau"}
        </Button>
      </div>
    </CardHeader>

    <CardContent class="px-0 py-0 space-y-2">
      {#if showAddContact}
        <div transition:slide={{ duration: 250 }}>
          <ContactForm onClose={() => showAddContact = false} />
        </div>
      {/if}

      <div class="grid grid-cols-1 gap-3">
        {#each onboardingStore.data.family.emergencyContacts as contact (contact.id)}
          <div animate:flip={{duration: 200}}>
            <EmergencyContactItem {contact} />
          </div>
        {/each}

        {#if onboardingStore.data.family.emergencyContacts.length === 0 && !showAddContact}
          <div class="py-10 flex flex-col items-center justify-center text-slate-600 bg-slate-50/40 rounded-xl border border-dashed border-slate-200 gap-2">
            <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-slate-100 shadow-sm mb-1">
              <AppIcon name="phone" size={24} strokeWidth={1.5} class="opacity-50" />
            </div>
            <p class="text-[0.83rem] font-medium">Aucun contact ajouté</p>
            <p class="text-[0.8rem] opacity-70">Ajoutez au moins un contact prioritaire.</p>
          </div>
        {/if}
      </div>
    </CardContent>
  </Card>

  <!-- Children -->
  <Card class="border-slate-200 shadow-none rounded-none border-0 p-0 pt-4">
    <CardHeader class="px-0 pt-0 pb-0">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
            <AppIcon name="users" size={20} class="text-slate-500" />
          </div>
          <div>
            <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
              Ayants droit & Famille
            </CardTitle>
            <CardDescription class="text-[0.835rem]">Gérez les membres de la famille.</CardDescription>
          </div>
        </div>
        <Button 
          onclick={() => showAddChild = !showAddChild} 
          variant="outline" 
          size="sm" 
          class="h-8 shadow-fine border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-[0.8rem]"
        >
          <AppIcon name={showAddChild ? "x" : "plus"} size={17} />
          {showAddChild ? "Annuler" : "Nouveau"}
        </Button>
      </div>
    </CardHeader>

    <CardContent class="px-0 py-0 space-y-2">
      {#if showAddChild}
        <div transition:slide={{ duration: 250 }}>
          <ChildForm onClose={() => showAddChild = false} />
        </div>
      {/if}

      <div class="grid grid-cols-1 gap-3">
        {#each onboardingStore.data.family.children as member (member.id)}
          <div animate:flip={{duration: 200}}>
            <FamilyMemberItem {member} />
          </div>
        {/each}

        {#if onboardingStore.data.family.children.length === 0 && !showAddChild}
          <div class="py-10 flex flex-col items-center justify-center text-slate-600 bg-slate-50/40 rounded-xl border border-dashed border-slate-200 gap-2">
            <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-slate-100 shadow-sm mb-1">
              <AppIcon name="users" size={24} strokeWidth={1.5} class="opacity-50" />
            </div>
            <p class="text-[0.83rem] font-medium">Aucun membre de famille</p>
            <p class="text-[0.8rem] opacity-70">Ajoutez les enfants ou ayants droit.</p>
          </div>
        {/if}
      </div>
    </CardContent>
  </Card>
</div>

