<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";
  import { Button } from "@/components/ui/button";
  import { flip } from "svelte/animate";
  import { SUPPORTED_FILE_TYPES } from "@/constants/features/files";
  
  // Sub-components
  import DocumentForm from "../documents/forms/DocumentForm.svelte";
  import DocumentItem from "../documents/DocumentItem.svelte";


  const docTypes = [
    { value: "Identité", label: "Pièce d'identité" },
    { value: "Diplôme", label: "Diplôme / Formation" },
    { value: "Contrat", label: "Contrat / Avenant" },
    { value: "Santé", label: "Santé / Mutuelle" },
    { value: "RIB", label: "RIB / Coordonnées bancaires" },
    { value: "Justificatif", label: "Justificatif de domicile" },
    { value: "Autre", label: "Autre document" }
  ];

  let showAddForm = $state(false);
  const acceptedExtensions = SUPPORTED_FILE_TYPES.map(ext => `.${ext}`).join(",");
</script>


<Card class="border-slate-200 shadow-none rounded-none border-0 p-0">
  <CardHeader class="px-0 pt-0 pb-0">
    <div class="flex items-center justify-between">
      <div>
        <CardTitle class="text-md font-bold text-slate-900 tracking-tight">
          Documents
        </CardTitle>
        <CardDescription class="text-[0.835rem]">Gérez les pièces justificatives du dossier collaborateur.</CardDescription>
      </div>
      <Button 
        onclick={() => showAddForm = !showAddForm} 
        variant="default" 
        size="sm" 
        class="h-7.5 shadow-fine bg-primary text-white text-[0.8rem]"
      >
        <AppIcon name={showAddForm ? "close" : "plus"} size={17} />
        {showAddForm ? "Annuler" : "Ajouter un document"}
      </Button>
    </div>
  </CardHeader>

  <CardContent class="px-0 py-0 space-y-4">
    {#if showAddForm}
      <DocumentForm 
        onClose={() => showAddForm = false}
        {acceptedExtensions}
        {docTypes}
      />
    {/if}

    <div class="grid grid-cols-1 gap-3">
      {#each onboardingStore.data.documents as doc (doc.id)}
        <div animate:flip={{duration: 200}}>
          <DocumentItem 
            {doc} 
            {docTypes} 
            {acceptedExtensions} 
          />
        </div>
      {/each}

      {#if onboardingStore.data.documents.length === 0}
        <div class="py-36 flex flex-col items-center justify-center text-slate-500 bg-slate-50/50 rounded-lg border border-dashed border-slate-200 gap-3">
          <AppIcon name="files" size={32} strokeWidth={0.8} class="opacity-50" />
          <p class="text-[0.81rem]">Aucun document configuré</p>
        </div>
      {/if}
    </div>
  </CardContent>
</Card>

