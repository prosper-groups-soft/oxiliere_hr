<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import ValidationError from "@/components/ui/validation-error";
  import { COUNTRY_OPTIONS } from '@/features/employees/constants/countries';
  import { getMediaUrl } from "@/utilities/common/media";
  import type { BankInstitution } from "../../../types/types";


  let {
    open = $bindable(false),
    institution = $bindable(null),
    onCreate,
    onUpdate,
    onUploadLogo,
  }: {
    open: boolean;
    institution: BankInstitution | null;
    onCreate?: (data: {
      name: string;
      shortName: string;
      country: string;
      type: 'bank' | 'mobile_money';
      swiftCode: string;
      isActive: boolean;
    }) => Promise<BankInstitution | void>;
    onUpdate?: (id: string, data: {
      name: string;
      shortName: string;
      country: string;
      type: 'bank' | 'mobile_money';
      swiftCode: string;
      isActive: boolean;
    }) => Promise<BankInstitution | void>;
    onUploadLogo?: (bankId: string, file: File) => Promise<void>;
  } = $props();

  let formData = $state({
    name: "",
    shortName: "",
    country: "CD",
    type: "bank" as 'bank' | 'mobile_money',
    swiftCode: "",
    isActive: true,
  });

  let formLogo = $state<File | null>(null);
  let formLogoPreview = $state("");

  let validationErrors = $state<Record<string, string>>({});
  let isSaving = $state(false);
  let errorMessage = $state('');

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};
    if (!formData.name.trim()) {
      validationErrors.name = 'Le nom est requis';
    }
    if (!formData.shortName.trim()) {
      validationErrors.shortName = 'Le nom court est requis';
    } else if (formData.shortName.trim().length > 10) {
      validationErrors.shortName = 'Le nom court ne doit pas dépasser 10 caractères';
    }
    if (!formData.country.trim()) {
      validationErrors.country = 'Le pays est requis';
    }
    if (formData.type === 'bank' && formData.swiftCode.trim()) {
      const swift = formData.swiftCode.trim();
      if (swift.length !== 8 && swift.length !== 11) {
        validationErrors.swiftCode = 'Le code SWIFT doit faire exactement 8 ou 11 caractères';
      }
    }
    return Object.keys(validationErrors).length === 0;
  }

  $effect(() => {
    if (open) {
      validationErrors = {};
      errorMessage = '';
      formLogo = null;
      formLogoPreview = "";

      if (institution) {
        formData = {
          name: institution.name,
          shortName: institution.shortName,
          country: institution.country,
          type: institution.type,
          swiftCode: institution.swiftCode || "",
          isActive: institution.isActive,
        };
      } else {
        resetForm();
      }
    }
  });

  let existingLogoUrl = $derived(institution ? getMediaUrl(institution.logoUrl) : '');

  function resetForm() {
    formData = {
      name: "",
      shortName: "",
      country: "CD",
      type: "bank",
      swiftCode: "",
      isActive: true,
    };
  }

  function handleLogoSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      formLogo = target.files[0];
      formLogoPreview = URL.createObjectURL(target.files[0]);
    }
  }

  function clearLogo() {
    formLogo = null;
    formLogoPreview = "";
  }

  async function handleSubmit() {
    if (!validateForm()) return;

    isSaving = true;
    try {
      let createdId: string | null = null;

      if (institution) {
        // Update mode
        await onUpdate?.(institution.id, { ...formData });
        createdId = institution.id;
      } else {
        // Create mode
        const result = await onCreate?.({ ...formData });
        createdId = result?.id || null;
      }

      // Upload logo if one was selected and we have a bank ID
      if (formLogo && createdId) {
        await onUploadLogo?.(createdId, formLogo);
      }

      open = false;
      institution = null;
      resetForm();
    } catch {
      // Error toast already handled by mutation
    } finally {
      isSaving = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white h-full">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900 text-left">
        {institution ? "Modifier l'Institution" : "Nouvelle Institution"}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
      <div class="space-y-4">
        <div class="space-y-2">
          <Label for="name" class="text-[0.875rem] font-medium text-slate-700">Nom de l'institution <span class="text-rose-500">*</span></Label>
          <Input
            id="name"
            bind:value={formData.name}
            placeholder="Ex: Equity BCDC..."
            oninput={() => clearValidationError('name')}
            class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
          />
          <ValidationError errors={validationErrors} field="name" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="shortName" class="text-[0.875rem] font-medium text-slate-700">Nom court <span class="text-rose-500">*</span></Label>
            <Input
              id="shortName"
              bind:value={formData.shortName}
              placeholder="Ex: Equity..."
              oninput={() => clearValidationError('shortName')}
              class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]"
              maxlength={10}
            />
            <ValidationError errors={validationErrors} field="shortName" />
          </div>
          <div class="space-y-2">
            <Label for="country" class="text-[0.875rem] font-medium text-slate-700">Pays <span class="text-rose-500">*</span></Label>
            <Select.Root type="single" bind:value={formData.country}>
              <Select.Trigger class="h-10 border-slate-200 bg-white shadow-fine flex items-center justify-start gap-2 text-left text-[0.875rem] w-full">
                {#if formData.country}
                  <span class="text-lg shrink-0">{COUNTRY_OPTIONS.find(c => c.value === formData.country)?.flag}</span>
                  <span class="text-sm truncate">{COUNTRY_OPTIONS.find(c => c.value === formData.country)?.label || "Sélectionner..."}</span>
                {:else}
                  <span class="text-sm">Sélectionner...</span>
                {/if}
              </Select.Trigger>
              <Select.Content class="bg-white border-slate-100 shadow-fine z-100 max-h-60">
                {#each COUNTRY_OPTIONS as country}
                  <Select.Item value={country.value}>
                    <div class="flex items-start justify-start gap-2">
                      <span class="text-sm">{country.flag}</span>
                      <span class="text-sm">{country.label}</span>
                    </div>
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
            <ValidationError errors={validationErrors} field="country" />
          </div>
        </div>
      </div>

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
            <Input 
              id="swift" 
              bind:value={formData.swiftCode} 
              placeholder="Ex: EQUIBCKI..." 
              oninput={() => clearValidationError('swiftCode')}
              class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem] uppercase" 
              maxlength={11}
            />
            <ValidationError errors={validationErrors} field="swiftCode" />
          </div>
        {/if}
      </div>

      <!-- Logo upload -->
      <div class="space-y-3">
        <Label for="logo" class="text-[0.875rem] font-medium text-slate-700">Logo de l'institution</Label>
        <div class="flex items-center gap-4">
          <div class="relative h-16 w-16 rounded-xl overflow-hidden bg-white border border-slate-200 shrink-0 flex items-center justify-center">
            {#if formLogoPreview}
              <img src={formLogoPreview} alt="Aperçu" class="h-full w-full object-cover" />
            {:else if existingLogoUrl}
              <img src={existingLogoUrl} alt={institution?.name} class="h-full w-full object-cover" />
            {:else}
              <AppIcon name="image" size={24} class="text-slate-300" />
            {/if}
          </div>
          <label class="cursor-pointer flex-1">
            <input
              type="file"
              accept="image/*"
              onchange={handleLogoSelect}
              class="hidden"
            />
            <div class="flex items-center gap-2 px-4 py-2.5 border-2 border-dashed border-slate-200 rounded-lg hover:border-primary/40 hover:bg-primary/5 transition-all cursor-pointer">
              <AppIcon name="upload" size={18} class="text-slate-400" />
              <span class="text-[0.82rem] text-slate-500">
                {formLogo ? formLogo.name : 'Cliquez pour sélectionner un logo'}
              </span>
            </div>
          </label>
          {#if formLogo}
            <button onclick={clearLogo} class="p-1.5 text-slate-400 hover:text-red-500 transition-colors cursor-pointer shrink-0">
              <AppIcon name="x" size={16} />
            </button>
          {/if}
        </div>
      </div>

      <!-- Statut actif -->
      <div class="flex items-center justify-between p-4 rounded-xl bg-slate-50/50 border border-slate-100">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg bg-emerald-50 text-emerald-500">
            <AppIcon name="power" size={18} />
          </div>
          <div>
            <p class="text-[0.85rem] font-semibold text-slate-700">Institution active</p>
            <p class="text-[0.78rem] text-slate-500">Désactivez pour suspendre l'utilisation de cette institution</p>
          </div>
        </div>
        <Switch bind:checked={formData.isActive} class="cursor-pointer" />
      </div>

    </div>

    
    <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer" onclick={() => institution = null}>
          <AppIcon name="x" size={17} class="text-slate-300" />
          Annuler
        </Button>
      </Sheet.Close>
      <Button
        onclick={handleSubmit}
        disabled={isSaving}
        class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer gap-2"
      >
        {#if isSaving}
          <AnimateSpin class="border-white size-3" text="" />
        {:else}
          <AppIcon name="check" size={17} />
        {/if}
        {institution ? "Mettre à jour" : "Enregistrer"}
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>





