<script lang="ts">
  import { onboardingStore, type DocumentItem } from "../../../stores/onboarding.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import { Button } from "@/components/ui/button";
  import { fade } from "svelte/transition";
  import { get_file_size } from "@/hr/utilities/common/fs";
  import { SUPPORTED_FILE_TYPES } from "@/hr/constants/navigation/files";
  import { DOCUMENT_TYPES } from "../../../constants/documents";
  import * as Select from "@/components/ui/select";

  interface Props {
    doc: DocumentItem;
    acceptedExtensions: string;
  }

  let { doc, acceptedExtensions }: Props = $props();

  let isEditing = $state(false);
  let editType = $state("");
  let isProcessing = $state(false);

  // Récupère le libellé du type de document pour l'affichage
  const getDocTypeLabel = (value: string) => 
    DOCUMENT_TYPES.find(t => t.value === value)?.label || value;

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      isProcessing = true;
      const file = input.files[0];
      
      // Simulation d'un petit délai pour le feedback visuel
      setTimeout(() => {
        onboardingStore.updateDocument(doc.id, { file });
        isProcessing = false;
      }, 600);
    }
  }

  function startEditing() {
    editType = doc.document_type;
    isEditing = true;
  }

  function saveEdit() {
    onboardingStore.updateDocument(doc.id, { 
      document_type: editType as any
    });
    isEditing = false;
  }

  function deleteDocument() {
    onboardingStore.removeDocument(doc.id);
  }
</script>

<div class="flex items-center justify-between p-3.5 bg-white border border-slate-200 rounded-lg transition-all hover:border-slate-300 shadow-fine group">
  
  <!-- Partie Gauche : Icône et Infos -->
  <div class="flex items-center gap-4 flex-1 min-w-0">
    <div class="w-10 h-10 bg-slate-50 text-slate-500 rounded-md flex items-center justify-center border border-slate-100 shrink-0">
      <AppIcon 
        name={doc.file ? "check" : "file-text"} 
        size={20} 
        class={doc.file ? "text-green-600" : ""} 
      />
    </div>
    
    <div class="flex-1 min-w-0">
      {#if isEditing}
        <div class="flex gap-3" in:fade={{ duration: 150 }}>
          <Select.Root type="single" bind:value={editType}>
            <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full max-w-[200px] shadow-fine font-normal text-sm">
              {getDocTypeLabel(editType) || "Choisir un type"}
            </Select.Trigger>
            <Select.Content>
              {#each DOCUMENT_TYPES as type}
                <Select.SelectItem value={type.value} label={type.label}>
                  {type.label}
                </Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>
      {:else}
        <!-- Mode Affichage -->
        <div class="flex items-center gap-3">
          <p class="font-semibold text-slate-900 text-[0.87rem] tracking-tight truncate">
            {doc.file?.name || "Document sans fichier"}
          </p>
          <span class="text-[0.75rem] font-medium text-slate-400 px-2 py-0.5 bg-slate-100 rounded-full border border-slate-200">
            {getDocTypeLabel(doc.document_type)}
          </span>
        </div>

        {#if doc.file}
          <p class="text-[0.75rem] text-green-600 font-medium flex items-center gap-1.5 mt-1">
            <AppIcon name="check" size={13} />
            {get_file_size(doc.file)}
          </p>
          
          <!-- Métadonnées optionnelles (Dates) -->
          {#if doc.issue_date || doc.expiry_date}
            <div class="text-slate-500 mt-1 flex flex-wrap gap-x-4 gap-y-1">
              {#if doc.issue_date}
                <span class="flex items-center gap-1.5 text-[0.76rem]">
                  <AppIcon name="calendar" size={14} />
                  Délivré le {new Date(doc.issue_date).toLocaleDateString('fr-FR')}
                </span>
              {/if}
              {#if doc.expiry_date}
                <span class="flex items-center gap-1.5 text-amber-600 text-[0.76rem]">
                  <AppIcon name="circle-alert" size={14} />
                  Expire le {new Date(doc.expiry_date).toLocaleDateString('fr-FR')}
                </span>
              {/if}
            </div>
          {/if}
        {:else}
          <p class="text-[0.73rem] text-slate-500 mt-1">
            Aucun fichier ({SUPPORTED_FILE_TYPES.join(', ').toUpperCase()}, Max 5Mo)
          </p>
        {/if}
      {/if}
    </div>
  </div>
  
  <!-- Partie Droite : Actions -->
  <div class="flex items-center gap-2 ml-4">
    {#if isEditing}
      <Button onclick={saveEdit} size="icon" variant="ghost" class="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50">
        <AppIcon name="check" size={16} />
      </Button>
      <Button onclick={() => isEditing = false} size="icon" variant="ghost" class="h-8 w-8 text-slate-400 hover:text-slate-600">
        <AppIcon name="x" size={16} />
      </Button>
    {:else}
      <input 
        type="file" 
        id="file-{doc.id}" 
        class="hidden" 
        accept={acceptedExtensions}
        onchange={handleFileChange}
      />
      <label 
        for="file-{doc.id}" 
        class="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 rounded-md text-[0.78rem] font-medium transition-all cursor-pointer text-slate-700 bg-white shadow-fine active:scale-95 flex items-center gap-1.5"
      >
        {#if isProcessing}
          <AnimateSpin class="size-3" text="Chargement" textPosition="right" />
        {:else}
          {doc.file ? "Remplacer" : "Choisir"}
        {/if}
      </label>

      <div class="flex h-8 border-l border-slate-100 ml-2 pl-2 gap-1">
        <Button onclick={startEditing} size="icon" variant="ghost" class="h-8 w-8 text-slate-500 hover:text-slate-600 hover:bg-slate-50">
          <AppIcon name="edit" size={18} />
        </Button>
        <Button onclick={deleteDocument} size="icon" variant="ghost" class="h-8 w-8 text-red-400 hover:text-red-600 hover:bg-red-50">
          <AppIcon name="trash" size={19} class="size-[19px]" />
        </Button>
      </div>
    {/if}
  </div>
</div>

