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
  import { slide } from "svelte/transition";
  import { SUPPORTED_FILE_TYPES } from "@/constants/features/files";
  
  // Sub-components
  import DocumentForm from "../documents/forms/DocumentForm.svelte";
  import DocumentItem from "../documents/DocumentItem.svelte";
  

  let showAddForm = $state(false);
  const acceptedExtensions = SUPPORTED_FILE_TYPES.map(ext => `.${ext}`).join(",");
</script>


<Card class="border-slate-200 shadow-none rounded-none border-0 p-0">
  <CardHeader class="px-0 pt-0 pb-0">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
          <AppIcon name="files" size={20} class="text-slate-500" />
        </div>
        <div>
          <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
            Documents
          </CardTitle>
          <CardDescription class="text-[0.835rem]">
            Gérez les pièces justificatives du dossier collaborateur.
          </CardDescription>
        </div>
      </div>
      <Button 
        onclick={() => showAddForm = !showAddForm} 
        variant="outline" 
        size="sm" 
        class="h-8 border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-[0.8rem] shadow-fine"
      >
        <AppIcon name={showAddForm ? "x" : "plus"} size={17} />
        {showAddForm ? "Annuler" : "Nouveau"}
      </Button>
    </div>
  </CardHeader>

  <CardContent class="px-0 py-0 space-y-2">
    {#if showAddForm}
      <div transition:slide={{ duration: 250 }}>
        <DocumentForm 
          onClose={() => showAddForm = false}
          {acceptedExtensions}
        />
      </div>
    {/if}

    <div class="grid grid-cols-1 gap-3">
      {#each onboardingStore.data.documents as doc (doc.id)}
        <div animate:flip={{duration: 200}}>
          <DocumentItem 
            {doc} 
            {acceptedExtensions} 
          />
        </div>
      {/each}

      {#if onboardingStore.data.documents.length === 0 && !showAddForm}
        <div class="py-20 flex flex-col items-center justify-center text-slate-600 bg-slate-50/40 rounded-xl border border-dashed border-slate-200 gap-2">
          <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-slate-100 shadow-sm mb-1">
            <AppIcon name="files" size={24} strokeWidth={1.5} class="opacity-50" />
          </div>
          <p class="text-[0.83rem] font-medium">Aucun document configuré</p>
          <p class="text-[0.8rem] opacity-70">Téléchargez les pièces justificatives nécessaires.</p>
        </div>
      {/if}
    </div>
  </CardContent>
</Card>

