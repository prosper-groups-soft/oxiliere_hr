<script lang="ts">
  import { onboardingStore } from "../../../../stores/onboarding.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { fade, slide } from "svelte/transition";
  import { get_file_size } from "@/utilities/common/fs";

  interface Props {
    onClose: () => void;
    acceptedExtensions: string;
    docTypes: { value: string; label: string }[];
  }

  let { onClose, acceptedExtensions, docTypes }: Props = $props();

  let newDoc = $state<{
    label: string;
    type: string;
    file: File | null;
  }>({
    label: "",
    type: "Autre",
    file: null
  });

  const docTypeLabel = $derived(
    docTypes.find((t) => t.value === newDoc.type)?.label ?? "Sélectionner..."
  );

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      newDoc.file = input.files[0];
    }
  }

  function handleSubmit() {
    if (!newDoc.label) return;
    onboardingStore.addDocument({
      id: crypto.randomUUID(),
      label: newDoc.label,
      type: newDoc.type,
      file: newDoc.file
    });
    onClose();
  }
</script>


<div 
  transition:slide
  class="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4 mb-6"
>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="space-y-1.5">
      <Label class="text-[0.82rem] text-slate-900 font-medium">Nom du document</Label>
      <Input 
        bind:value={newDoc.label}
        placeholder="ex: Attestation de domicile"
        class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
      />
    </div>

    <div class="space-y-1.5">
      <Label class="text-[0.82rem] text-slate-900 font-medium">Type/Catégorie</Label>
      <Select.Root type="single" bind:value={newDoc.type}>
        <Select.Trigger class="h-9.5 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm">
          {docTypeLabel}
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

    <div class="space-y-1.5 md:col-span-2">
      <Label class="text-[0.82rem] text-slate-900 font-medium">Fichier</Label>
      <div class="space-y-3">
        <input 
          type="file" 
          id="new-file" 
          class="hidden" 
          accept={acceptedExtensions}
          onchange={handleFileChange}
        />
        <label 
          for="new-file" 
          class="flex items-center gap-2 w-full cursor-pointer px-3 py-2 border border-slate-200 hover:bg-white rounded-md text-[0.82rem] font-medium transition-all text-slate-700 bg-white shadow-fine active:scale-[0.99]"
        >
          <AppIcon name="upload" size={16} />
          {newDoc.file ? "Changer le fichier" : "Parcourir les fichiers..."}
        </label>

        {#if newDoc.file}
          <div class="flex items-center justify-between gap-3 p-3 bg-white border border-slate-200 rounded-lg shadow-sm animate-in fade-in slide-in-from-top-2 duration-300" transition:fade>
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 flex items-center justify-center bg-green-50 text-green-600 rounded-full border border-green-100">
                <AppIcon name="check" size={16} />
              </div>
              <div class="flex flex-col min-w-0">
                <span class="text-[0.82rem] font-semibold text-slate-900 truncate tracking-tight">{newDoc.file.name}</span>
                <span class="text-[0.74rem] text-slate-500">{get_file_size(newDoc.file)} • Prêt à être ajouté</span>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              class="h-8 w-8 p-0! text-red-400 hover:text-red-500 hover:bg-red-50"
              onclick={() => newDoc.file = null}
            >
              <AppIcon name="trash" size={19} class="size-[19px]" />
            </Button>
          </div>
        {/if}
      </div>
    </div>
  </div>

  <div class="flex justify-end pt-2">
    <Button 
      onclick={handleSubmit} 
      disabled={!newDoc.label}
      size="sm"
      class="h-8 bg-slate-900 hover:bg-slate-800 text-white px-6"
    >
      Confirmer l'ajout
    </Button>
  </div>
</div>

