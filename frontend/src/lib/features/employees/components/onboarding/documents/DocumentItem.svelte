<script lang="ts">
  import { 
    onboardingStore, 
    type DocumentItem 
  } from "../../../stores/onboarding.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import * as Select from "@/components/ui/select";
  import { fade } from "svelte/transition";
  import { get_file_size } from "@/utilities/common/fs";
  import { SUPPORTED_FILE_TYPES } from "@/constants/features/files";

  interface Props {
    doc: DocumentItem;
    docTypes: { value: string; label: string }[];
    acceptedExtensions: string;
  }

  let { doc, docTypes, acceptedExtensions }: Props = $props();

  let isEditing = $state(false);
  let editLabel = $state("");
  let editType = $state("");

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      onboardingStore.updateDocument(doc.id, { file: input.files[0] });
    }
  }

  function saveEdit() {
    onboardingStore.updateDocument(
      doc.id, { 
        label: editLabel, 
        type: editType 
      });
    isEditing = false;
  }

  function startEditing() {
    editLabel = doc.label;
    editType = doc.type;
    isEditing = true;
  }

  function deleteDocument() {
    onboardingStore.removeDocument(doc.id);
  }
</script>


<div 
  class="flex items-center justify-between p-3.5 bg-white border border-slate-200 rounded-lg transition-all hover:border-slate-300 shadow-fine group"
>
  <div class="flex items-center gap-4 flex-1">
    <div class="w-10 h-10 bg-slate-50 text-slate-500 rounded-md flex items-center justify-center border border-slate-100 shrink-0">
      <AppIcon name={doc.file ? "check" : "file-text"} size={20} class={doc.file ? "text-green-600" : ""} />
    </div>
    
    {#if isEditing}
      <div class="flex-1 grid grid-cols-2 gap-2" in:fade>
        <Input bind:value={editLabel} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
        <Select.Root type="single" bind:value={editType}>
          <Select.Trigger class="h-8 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-xs">
            {docTypes.find(t => t.value === editType)?.label ?? "Type"}
          </Select.Trigger>
          <Select.Content>
            {#each docTypes as type}
              <Select.SelectItem value={type.value} label={type.label}>
                {type.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>
    {:else}
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <p class="font-semibold text-slate-900 text-[0.85rem] tracking-tight truncate">{doc.label}</p>
          <span class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-widest px-1.5 py-0.5 bg-slate-100 rounded border border-slate-200">{doc.type}</span>
        </div>
        {#if doc.file}
          <p class="text-[0.71rem] text-green-600 font-medium flex items-center gap-1.5 mt-0.5">
            <AppIcon name="check" size={12} />
            {doc.file.name} ({get_file_size(doc.file)})
          </p>
        {:else}
          <p class="text-[0.7rem] text-slate-500 mt-0.5">Aucun fichier sélectionné ({SUPPORTED_FILE_TYPES.join(', ').toUpperCase()}, Max 5Mo)</p>
        {/if}
      </div>
    {/if}
  </div>
  
  <div class="flex items-center gap-2 ml-4">
    {#if isEditing}
      <Button onclick={saveEdit} size="icon" variant="ghost" class="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50">
        <AppIcon name="check" size={16} />
      </Button>
      <Button onclick={() => isEditing = false} size="icon" variant="ghost" class="h-8 w-8 text-slate-400 hover:text-slate-600">
        <AppIcon name="close" size={16} />
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
        class="px-3 py-1 border border-slate-200 hover:bg-slate-50 rounded-md text-[0.75rem] font-medium transition-all cursor-pointer text-slate-700 bg-white shadow-fine active:scale-95"
      >
        {doc.file ? "Remplacer" : "Choisir"}
      </label>

      <div class="flex h-8 border-l border-slate-100 ml-1 pl-1">
        <Button onclick={startEditing} size="icon" variant="ghost" class="h-8 w-8 text-slate-500 hover:text-slate-600">
          <AppIcon name="edit" size={18.5} />
        </Button>
        <Button onclick={deleteDocument} size="icon" variant="ghost" class="h-8 w-8 text-red-400 hover:text-red-600 hover:bg-red-50">
          <AppIcon name="trash" size={18.5} />
        </Button>
      </div>
    {/if}
  </div>
</div>

