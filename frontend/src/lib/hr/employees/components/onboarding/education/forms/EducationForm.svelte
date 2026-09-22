<script lang="ts">
  import { onboardingStore } from "../../../../stores/onboarding.svelte";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { preventNonNumeric } from "@/utilities/common/number";
  import * as Select from "@/components/ui/select";
  import { ACADEMIC_LEVELS } from "@/hr/employees/constants/education";
  import { z } from 'zod';
  import { educationSchema } from "@/hr/employees/schemas/education.schema";
  import ValidationError from "@/components/ui/validation-error";
  import { cn } from "@/utilities/common/css";
  import type { OnboardingEducationItem } from "@/hr/employees/types/types";


  interface Props {
    onClose: () => void;
    initialData?: OnboardingEducationItem | null;
    editIndex?: number | null;
  }

  let { onClose, initialData = null, editIndex = null }: Props = $props();

  let formData = $state({
    institute: '',
    degree: '',
    major: '',
    start_year: '',
    end_year: '',
    location: ''
  });

  // Initialize form with initial data if editing
  $effect(() => {
    if (initialData) {
      formData = {
        institute: initialData.institute,
        degree: initialData.degree,
        major: initialData.major || '',
        start_year: initialData.start_year?.toString() || '',
        end_year: initialData.end_year?.toString() || '',
        location: initialData.location || ''
      };
    }
  });

  const degreeLabel = $derived(
    ACADEMIC_LEVELS.find((l) => l.value === formData.degree)?.label ?? "Sélectionner..."
  );

  // --- Validation state ---
  let validationErrors = $state<Record<string, string>>({});

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};

    const result = educationSchema.safeParse({
      degree: formData.degree || undefined,
      institute: formData.institute,
      major: formData.major || undefined,
      location: formData.location || undefined,
      start_year: formData.start_year || undefined,
      end_year: formData.end_year || undefined
    });

    if (!result.success) {
      result.error.issues.forEach((err: z.core.$ZodIssue) => {
        const field = err.path.join('.');
        validationErrors = { ...validationErrors, [field]: err.message };
      });
      return false;
    }

    return true;
  }

  function handleSubmit(e: Event) {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const submissionData: OnboardingEducationItem = {
      degree: formData.degree,
      institute: formData.institute,
      major: formData.major || undefined,
      location: formData.location || undefined,
      start_year: formData.start_year ? Number(formData.start_year) : undefined,
      end_year: formData.end_year ? Number(formData.end_year) : undefined
    };

    // Add or update in store
    if (editIndex !== null) {
      onboardingStore.updateEducation(editIndex, submissionData);
    } else {
      onboardingStore.addEducation(submissionData);
    }

    // Reset form
    formData = {
      institute: '',
      degree: '',
      major: '',
      start_year: '',
      end_year: '',
      location: ''
    };
    validationErrors = {};
    onClose();
  }
</script>


<form onsubmit={handleSubmit} class="bg-white rounded-xl border border-slate-200 shadow-fine overflow-hidden">
  <div class="p-5 space-y-4">
    <!-- Degree & Institute -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="space-y-1.5">
        <Label class="text-[0.8rem] font-bold text-slate-700">
          Diplôme / Titre <span class="text-red-500">*</span>
        </Label>
        <Select.Root type="single" bind:value={formData.degree} onValueChange={() => clearValidationError('degree')}>
          <Select.Trigger class={cn(
            "h-9 bg-white border-slate-200 rounded-md w-full shadow-fine text-[0.85rem]",
            validationErrors.degree && "border-red-500"
          )}>
            {degreeLabel}
          </Select.Trigger>
          <Select.Content class="z-100">
            {#each ACADEMIC_LEVELS as level}
              <Select.SelectItem value={level.value} label={level.label} class="text-[0.85rem]">
                {level.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <ValidationError errors={validationErrors} field="degree" />
      </div>

      <div class="space-y-1.5">
        <Label class="text-[0.8rem] font-bold text-slate-700">
          Institution / École <span class="text-red-500">*</span>
        </Label>
        <Input 
          bind:value={formData.institute} 
          oninput={() => clearValidationError('institute')}
          placeholder="Ex: Université de Paris" 
          class={cn("h-9", validationErrors.institute && "border-red-500")}
        />
        <ValidationError errors={validationErrors} field="institute" />
      </div>
    </div>

    <!-- Major & Location -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="space-y-1.5">
        <Label class="text-[0.8rem] font-bold text-slate-700">
          Spécialité / Domaine
        </Label>
        <Input 
          bind:value={formData.major} 
          placeholder="Ex: Génie Logiciel" 
          class="h-9"
        />
      </div>

      <div class="space-y-1.5">
        <Label class="text-[0.8rem] font-bold text-slate-700">
          Lieu (Ville, Pays)
        </Label>
        <Input 
          bind:value={formData.location} 
          placeholder="Ex: Paris, France" 
          class="h-9"
        />
      </div>
    </div>

    <!-- Years -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="space-y-1.5 md:col-span-2">
        <Label class="text-[0.8rem] font-bold text-slate-700">
          Année de début
        </Label>
        <Input 
          type="number"
          min="1950"
          max="2099"
          onkeydown={preventNonNumeric}
          oninput={() => clearValidationError('start_year')}
          bind:value={formData.start_year} 
          placeholder="Ex: 2018" 
          class={cn("h-9", validationErrors.start_year && "border-red-500")}
        />
        <ValidationError errors={validationErrors} field="start_year" />
      </div>

      <div class="space-y-1.5 md:col-span-2">
        <Label class="text-[0.8rem] font-bold text-slate-700">
          Année de fin
        </Label>
        <Input 
          type="number"
          min="1950"
          max="2099"
          onkeydown={preventNonNumeric}
          oninput={() => clearValidationError('end_year')}
          bind:value={formData.end_year} 
          placeholder="Ex: 2021" 
          class={cn("h-9", validationErrors.end_year && "border-red-500")}
        />
        <ValidationError errors={validationErrors} field="end_year" />
      </div>
    </div>
  </div>

  <div class="px-5 py-3.5 border-t border-slate-100 bg-slate-50/80 flex items-center justify-end gap-2.5">
    <Button 
      type="button" 
      variant="outline" 
      onclick={onClose}
      class="h-8.5 px-4 text-[0.84rem]"
    >
      <AppIcon name="x" size={17} class="text-slate-400" />
      Annuler
    </Button>
    <Button 
      type="submit" 
      class="h-8.5 px-5 text-[0.84rem] bg-primary"
    >
      <AppIcon name="check" size={17} />
      Ajouter
    </Button>
  </div>
</form>

