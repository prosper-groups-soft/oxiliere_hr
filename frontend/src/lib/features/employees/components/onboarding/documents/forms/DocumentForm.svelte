<script lang="ts">
  import { onboardingStore } from "../../../../stores/onboarding.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { fade, slide } from "svelte/transition";
  import { get_file_size } from "@/utilities/common/fs";
  import { DOCUMENT_TYPES } from "../../../../constants/documents";

  interface Props {
    onClose: () => void;
    acceptedExtensions: string;
  }

  let { onClose, acceptedExtensions }: Props = $props();

  let newDoc = $state<{
    document_number: string;
    type: string;
    file: File | null;
    issue_date: string | null;
    expiry_date: string | null;
  }>({
    document_number: "",
    type: "OTHER",
    file: null,
    issue_date: null,
    expiry_date: null
  });

  let isProcessing = $state(false);

  const docTypeLabel = $derived(
    DOCUMENT_TYPES.find((t) => t.value === newDoc.type)?.label ?? "Sélectionner..."
  );

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      isProcessing = true;
      const file = input.files[0];
      
      // Simulation d'un petit délai pour le feedback visuel
      setTimeout(() => {
        newDoc.file = file;
        isProcessing = false;
      }, 600);
    }
  }

  function handleSubmit() {
    if (!newDoc.document_number) return;
    if (!newDoc.file) return;
    onboardingStore.addDocument({
      id: `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file: newDoc.file,
      document_type: newDoc.type as any,
      document_number: newDoc.document_number,
      issue_date: newDoc.issue_date || undefined,
      expiry_date: newDoc.expiry_date || undefined
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
      <Label class="text-[0.82rem] text-slate-900 font-medium">Nom / Référence du document</Label>
      <Input 
        bind:value={newDoc.document_number}
        placeholder="ex: Attestation de domicile, N° Passeport..."
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
          {#each DOCUMENT_TYPES as type}
            <Select.SelectItem value={type.value} label={type.label}>
              {type.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>

    <div class="space-y-1.5">
      <Label class="text-[0.82rem] text-slate-900 font-medium">Date de délivrance (optionnel)</Label>
      <Input 
        type="date"
        bind:value={newDoc.issue_date}
        class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine font-normal text-sm"
      />
    </div>

    <div class="space-y-1.5">
      <Label class="text-[0.82rem] text-slate-900 font-medium">Date d'expiration (optionnel)</Label>
      <Input 
        type="date"
        bind:value={newDoc.expiry_date}
        class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine font-normal text-sm"
      />
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
          class="flex items-center gap-2 w-full cursor-pointer px-3 py-2 border border-slate-200 hover:bg-white rounded-md text-[0.82rem] font-medium transition-all text-slate-700 bg-white shadow-fine active:bg-indigo-100"
        >
          {#if isProcessing}
            <AnimateSpin class="size-4" text="Chargement" textPosition="right" />
          {:else}
            <AppIcon name="upload" size={16} />
            {newDoc.file ? "Changer le fichier" : "Parcourir les fichiers..."}
          {/if}
        </label>

        {#if newDoc.file}
          <div class="flex items-center justify-between gap-3 p-3 bg-white border border-slate-200 rounded-lg shadow-fine animate-in fade-in slide-in-from-top-2 duration-300" transition:fade>
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 flex items-center justify-center bg-green-50 text-green-600 rounded-full border border-green-100">
                <AppIcon name="check" size={16} />
              </div>
              <div class="flex flex-col min-w-0">
                <span class="text-[0.82rem] font-semibold text-slate-900 truncate tracking-tight">{newDoc.file.name}</span>
                <span class="text-[0.77rem] text-slate-500">{get_file_size(newDoc.file)} • Prêt à être ajouté</span>
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
      onclick={handleSubmit} 
      disabled={!newDoc.document_number || !newDoc.file || isProcessing}
      size="sm"
      class="h-8 bg-primary hover:bg-primary/90 text-white px-6 shadow-fine flex items-center gap-1.5"
    >
      {#if isProcessing}
        <AnimateSpin class="size-3" text="" />
      {:else}
        <AppIcon name="plus" size={15} />
      {/if}
      Ajouter
    </Button>
  </div>
</div>

