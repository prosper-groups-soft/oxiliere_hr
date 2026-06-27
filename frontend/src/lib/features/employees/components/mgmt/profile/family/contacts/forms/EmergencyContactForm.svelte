<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import * as Select from "@/components/ui/select";
  import { notification } from "@/stores/notification.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import PhoneInput from "@/components/ui/phone-input";
  import type { EmployeeEmergencyContact } from "@/features/employees/types/types";
  import { RELATION_TYPES } from "@/features/employees/constants/mappings";
  import { emergencyContactSchema } from "@/features/employees/schemas/family.schema";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';


  let { onSave, onCancel, initialData = null, isLoading = false } = $props<{ 
    onSave: (contact: Omit<EmployeeEmergencyContact, 'id'>) => void,
    onCancel: () => void,
    initialData?: EmployeeEmergencyContact | null,
    isLoading?: boolean
  }>();

  let name = $state("");
  let relation = $state("SPOUSE");
  let phone = $state("");
  let isPrimary = $state(false);

  $effect(() => {
    if (initialData) {
      name = initialData.last_name ?? "";
      relation = initialData.relation ?? "";
      phone = initialData.phone ?? "";
      isPrimary = initialData.is_primary ?? false;
    }
  });

  const currentRelationLabel = $derived(
    RELATION_TYPES.find(r => r.value === relation)?.label || 'Sélectionner...'
  );

  function handleSubmit() {
    const formData = {
      last_name: name.trim(),
      relation,
      phone,
      is_primary: isPrimary
    };

    const result = emergencyContactSchema.safeParse(formData);

    if (!result.success) {
      const errorMsg = result.error.issues[0].message;
      notification.toast.error(errorMsg);
      return;
    }

    onSave(result.data as any);
  }
</script>


<form 
  id="contact-form" 
  class="p-3 bg-slate-50/80 border border-slate-200 rounded-lg space-y-3" 
  onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}
>
  <div class="grid grid-cols-3 gap-x-4 gap-y-3 items-end">
    <div class="col-span-1 space-y-1">
      <Label for="contact-name" class="text-[0.8rem] text-slate-500">Nom complet *</Label>
      <Input id="contact-name" bind:value={name} placeholder="Nom du contact" class="h-8 text-[0.85rem] bg-white border-slate-200 rounded-md shadow-fine" />
    </div>
    <div class="col-span-1 space-y-1">
      <Label class="text-[0.8rem] text-slate-500">Relation *</Label>
      <Select.Root type="single" bind:value={relation}>
        <Select.Trigger class="h-8 text-[0.85rem] bg-white border-slate-200 rounded-md w-full shadow-fine font-normal">
          {currentRelationLabel}
        </Select.Trigger>
        <Select.Content>
          {#each RELATION_TYPES as rel}
            <Select.SelectItem value={rel.value} label={rel.label}>
              {rel.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>
    <div class="col-span-full">
      <PhoneInput 
        id="contact-phone" 
        label="Téléphone *" 
        value={phone} 
        onChange={(v) => phone = v}
        labelClass="text-[0.8rem] text-slate-500 font-normal"
        inputClass="text-[0.85rem]"
      />
    </div>
  </div>

  <div class="flex items-center justify-between pt-1">
    <div class="flex items-center gap-2">
      <Checkbox id="contact-primary" class="bg-white" bind:checked={isPrimary} />
      <Label for="contact-primary" class="text-[0.8rem] text-slate-600 cursor-pointer leading-none">
        Contact principal
      </Label>
    </div>

    <div class="flex items-center gap-2">
      <button 
        type="button" 
        disabled={isLoading}
        class="px-3 py-1.5 text-[0.8rem] font-medium text-slate-500 hover:text-slate-700 hover:bg-slate-100 flex items-center gap-1.5 rounded-md transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        onclick={onCancel}
      >
        <AppIcon name="x" size={15} class="text-slate-400" />
        Annuler
      </button>
      <button 
        type="submit" 
        disabled={isLoading}
        class="px-3 py-1.5 text-[0.8rem] font-medium text-white bg-primary hover:bg-primary/90 rounded-md transition-colors cursor-pointer flex items-center gap-1.5 shadow-fine disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {#if isLoading}
          <AnimateSpin text="" class="size-3 border-white"/>
        {:else}
          <AppIcon name={initialData ? 'check' : 'plus'} size={15} />
        {/if}
        {initialData ? 'Enregistrer' : 'Ajouter'}
      </button>
    </div>
  </div>
</form>
