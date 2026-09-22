<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { fade } from "svelte/transition";
  import { get_file_size } from "@/utilities/common/fs";
  import { DOCUMENT_TYPES } from "@/hr/employees/constants/documents";
  import type { EmployeeDocument } from "@/hr/employees/types/types";

  interface Props {
    onSave: (data: any) => void;
    onCancel: () => void;
    initialData?: EmployeeDocument | null;
    isLoading?: boolean;
  }

  let { onSave, onCancel, initialData = null, isLoading = false }: Props = $props();

  let formData = $state({
    document_type: "OTHER",
    document_number: "",
    issue_date: "",
    expiry_date: "",
    file: null as File | string | null,
  });

  let isProcessing = $state(false);

  // Sync initial data if editing
  $effect(() => {
    if (initialData) {
      formData.document_type = initialData.document_type;
      formData.document_number = initialData.document_number || "";
      formData.issue_date = initialData.issue_date ? initialData.issue_date.split('T')[0] : "";
      formData.expiry_date = initialData.expiry_date ? initialData.expiry_date.split('T')[0] : "";
      formData.file = initialData.file || null;
    }
  });

  const docTypeLabel = $derived(
    DOCUMENT_TYPES.find((t) => t.value === formData.document_type)?.label ?? "Sélectionner..."
  );

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      isProcessing = true;
      const file = input.files[0];
      setTimeout(() => {
        formData.file = file;
        isProcessing = false;
      }, 500);
    }
  }

  function handleSubmit(e?: Event) {
    if (e) e.preventDefault();
    if (!formData.file && !initialData) return;
    
    const submissionData = {
        ...formData,
        issue_date: formData.issue_date && formData.issue_date.trim() !== '' ? formData.issue_date : undefined,
        expiry_date: formData.expiry_date && formData.expiry_date.trim() !== '' ? formData.expiry_date : undefined
    };

    onSave(submissionData);
  }
</script>


<form 
  id="document-form" 
  onsubmit={handleSubmit} 
  class="p-4 bg-slate-50/80 border border-slate-200 rounded-xl space-y-4 shadow-inner-soft"
>
  <div class="grid grid-cols-4 gap-3 items-end">
    
    <!-- Type de document -->
    <div class="space-y-1 col-span-1">
      <Label class="text-[0.84rem] text-slate-500">Catégorie *</Label>
      <Select.Root type="single" bind:value={formData.document_type}>
        <Select.Trigger class="h-9 bg-white border-slate-200 rounded-md w-full shadow-fine font-medium text-[0.85rem]">
          {docTypeLabel}
        </Select.Trigger>
        <Select.Content class="z-100">
          {#each DOCUMENT_TYPES as type}
            <Select.SelectItem value={type.value} label={type.label} class="text-[0.85rem]">
              {type.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>

    <!-- Numéro du document -->
    <div class="space-y-1 col-span-1">
      <Label class="text-[0.84rem] text-slate-500">Nom / Référence du document</Label>
      <Input 
        bind:value={formData.document_number}
        placeholder="ex: Attestation de domicile, N° Passeport..."
        class="h-9 bg-white border-slate-200 rounded-md shadow-fine text-[0.85rem]"
      />
    </div>

    <div class="space-y-1 col-span-1">
      <Label class="text-[0.84rem] text-slate-500">Délivré le (optionel)</Label>
      <Input 
        type="date"
        bind:value={formData.issue_date}
        class="h-9 bg-white border-slate-200 rounded-md shadow-fine text-[0.85rem]"
      />
    </div>
    <div class="space-y-1 col-span-1">
      <Label class="text-[0.84rem] text-slate-500">Expire le (optionel)</Label>
      <Input 
        type="date"
        bind:value={formData.expiry_date}
        class="h-9 bg-white border-slate-200 rounded-md shadow-fine text-[0.85rem]"
      />
    </div>

    <!-- Upload Fichier -->
    {#if !initialData}
    <div class="space-y-1.5 col-span-4">
      <Label class="text-[0.84rem] text-slate-500">Fichier</Label>
      <div class="space-y-3 w-full">
        <input type="file" id="mgmt-file" class="hidden" accept=".pdf,.jpg,.jpeg,.png,.webp" onchange={handleFileChange} />
        <label 
          for="mgmt-file" 
          class="flex items-center gap-2 w-full cursor-pointer px-3 py-2 border border-slate-200 hover:bg-indigo-50/50 bg-white rounded-md text-[0.84rem] font-medium transition-all text-slate-700 shadow-fine active:bg-indigo-100"
        >
          {#if isProcessing}
            <AnimateSpin class="size-4" text="Analyse..." textPosition="right" />
          {:else}
            <AppIcon name="upload" size={16} />
            {formData.file ? "Changer le fichier" : "Parcourir les fichiers..."}
          {/if}
        </label>

        {#if formData.file}
          <div class="flex items-center justify-between gap-3 p-3 bg-white border border-slate-200 rounded-lg shadow-fine animate-in fade-in slide-in-from-top-2 duration-300" transition:fade>
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 flex items-center justify-center bg-emerald-50 text-emerald-600 rounded-full border border-emerald-100">
                <AppIcon name="check" size={16} />
              </div>
              <div class="flex flex-col min-w-0">
                <span class="text-[0.82rem] font-semibold text-slate-900 truncate tracking-tight">{typeof formData.file === 'string' ? 'Document enregistré' : formData.file.name}</span>
                <span class="text-[0.77rem] text-slate-500">
                  {typeof formData.file !== 'string' ? `${get_file_size(formData.file)} • ` : ''}Prêt à être ajouté
                </span>
              </div>
            </div>
            <button 
              type="button"
              class="h-8 w-8 p-0 flex items-center justify-center text-red-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
              onclick={() => formData.file = null}
            >
              <AppIcon name="trash" size={16} />
            </button>
          </div>
        {/if}
      </div>
    </div>
    {/if}
  </div>

  <div class="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
    <button type="button" onclick={onCancel} class="px-4 py-1.5 text-[0.84rem] font-medium rounded-md text-slate-700 hover:text-slate-700 transition-colors flex items-center justify-center gap-1.5 cursor-pointer">
      <AppIcon name="x" size={17} class="text-slate-400" />
      Annuler
    </button>
    <button 
      type="submit" 
      disabled={isLoading}
      class="px-6 py-1.5 bg-primary text-white rounded-md text-[0.84rem] font-medium shadow-fine hover:bg-primary/90 transition-all flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
    >
      {#if isLoading}
        <AnimateSpin class="size-3 border-white" text="" />
      {:else}
        <AppIcon name="check" size={17} />
      {/if}
      {initialData ? "Mettre à jour" : "Enregistrer"}
    </button>
  </div>
</form>

