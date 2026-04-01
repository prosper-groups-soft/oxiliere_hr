<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { bankingStore } from "../../../stores/banking.svelte";
  import { toast } from "svelte-sonner";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { BankInstitution } from "../../../types/types";

  let { open = $bindable(false), institution = $bindable(null) }: { open: boolean, institution: BankInstitution | null } = $props();

  let formData = $state({
    name: "",
    shortName: "",
    country: "RDC",
    type: "bank" as 'bank' | 'mobile_money',
    swiftCode: "",
    logoUrl: ""
  });

  // Load data for editing
  $effect(() => {
    if (institution) {
      formData = {
        name: institution.name,
        shortName: institution.shortName,
        country: institution.country,
        type: institution.type,
        swiftCode: institution.swiftCode || "",
        logoUrl: institution.logoUrl || ""
      };
    } else {
      resetForm();
    }
  });

  function resetForm() {
    formData = {
      name: "",
      shortName: "",
      country: "RDC",
      type: "bank",
      swiftCode: "",
      logoUrl: ""
    };
  }

  function handleSubmit() {
    if (!formData.name || !formData.shortName || !formData.country) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    if (institution) {
      bankingStore.updateInstitution(institution.id, formData);
      toast.success("Institution mise à jour");
    } else {
      bankingStore.addInstitution(formData);
      toast.success("Institution ajoutée");
    }

    open = false;
    institution = null;
    resetForm();
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md p-0 overflow-hidden flex flex-col bg-white h-full">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900 text-left">
        {institution ? "Modifier l'Institution" : "Nouvelle Institution"}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
      <!-- Section 1: Informations Générales -->
      <div class="space-y-4">
        
        <div class="space-y-2">
          <Label for="name" class="text-[0.875rem] font-medium text-slate-700">Nom de l'institution <span class="text-rose-500">*</span></Label>
          <Input id="name" bind:value={formData.name} placeholder="Ex: Equity BCDC..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="shortName" class="text-[0.875rem] font-medium text-slate-700">Nom court <span class="text-rose-500">*</span></Label>
            <Input id="shortName" bind:value={formData.shortName} placeholder="Ex: Equity..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
          </div>
          <div class="space-y-2">
            <Label for="country" class="text-[0.875rem] font-medium text-slate-700">Pays <span class="text-rose-500">*</span></Label>
            <Input id="country" bind:value={formData.country} placeholder="Ex: RDC..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
          </div>
        </div>
      </div>

      <!-- Section 2: Type et SWIFT -->
      <div class="space-y-4">        
        <div class="space-y-2">
          <Label class="text-[0.875rem] font-medium text-slate-700">Type d'entité</Label>
          <Select.Root type="single" bind:value={formData.type}>
            <Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine flex items-center gap-2 text-[0.875rem]">
              {formData.type === 'bank' ? 'Banque Classique' : 'Mobile Money'}
            </Select.Trigger>
            <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
              <Select.Item value="bank" label="Banque Classique">Banque Classique</Select.Item>
              <Select.Item value="mobile_money" label="Mobile Money">Mobile Money</Select.Item>
            </Select.Content>
          </Select.Root>
        </div>

        {#if formData.type === 'bank'}
          <div class="space-y-2">
            <Label for="swift" class="text-[0.875rem] font-medium text-slate-700">Code SWIFT / BIC</Label>
            <Input id="swift" bind:value={formData.swiftCode} placeholder="Ex: EQUIBCKI..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem] uppercase" />
          </div>
        {/if}
      </div>

      <!-- Section 3: Apparence -->
      <div class="space-y-4">        
        <div class="space-y-2">
          <Label for="logo" class="text-[0.875rem] font-medium text-slate-700">URL du Logo (Optionnel)</Label>
          <Input id="logo" bind:value={formData.logoUrl} placeholder="https://..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      <Button 
        onclick={handleSubmit}
        class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer"
      >
        <AppIcon name="check" size={18} />
        {institution ? "Mettre à jour" : "Enregistrer"}
      </Button>
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer" onclick={() => institution = null}>
          Annuler
        </Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

