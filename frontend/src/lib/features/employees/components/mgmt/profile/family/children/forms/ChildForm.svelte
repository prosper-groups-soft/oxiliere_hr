<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { notification } from "@/stores/notification.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { EmployeeChild } from "@/features/employees/types/types";
  import { childSchema } from "@/features/employees/schemas/family.schema";
  import ValidationError from "@/components/ui/validation-error";

  
  let { onSave, onCancel, initialData = null, isLoading = false, error = null } = $props<{ 
    onSave: (child: Omit<EmployeeChild, 'id'>) => void,
    onCancel: () => void,
    initialData?: EmployeeChild | null,
    isLoading?: boolean,
    error?: any
  }>();

  let name = $state("");
  let birthdate = $state("");
  let gender = $state<"MALE" | "FEMALE" | "NOT_SPECIFIED">("MALE");
  let isDependent = $state(true);

  let validationErrors = $state<Record<string, string>>({});

  const formData = $derived({
    last_name: name.trim(),
    birthdate: birthdate || undefined,
    gender,
    is_dependent: isDependent
  });

  $effect(() => {
    const result = childSchema.safeParse(formData);
    if (!result.success) {
      const errors: Record<string, string> = {};
      result.error.issues.forEach((issue) => {
        const path = issue.path[0] as string;
        if (!errors[path]) errors[path] = issue.message;
      });
      validationErrors = errors;
    } else {
      validationErrors = {};
    }
  });

  $effect(() => {
    if (error) {
      // Si Axios/Fetch error: on extrait response.data
      const errorData = error.response?.data || error.data || error;
      validationErrors = { ...validationErrors, ...errorData };
    }
  });

  $effect(() => {
    if (initialData) {
      name = initialData.last_name ?? "";
      birthdate = initialData.birthdate ?? "";
      gender = (initialData.gender as any) ?? "MALE";
      isDependent = initialData.is_dependent ?? true;
    }
  });

  function handleSubmit() {
    const result = childSchema.safeParse(formData);

    if (!result.success) {
      const errors: Record<string, string> = {};
      result.error.issues.forEach((issue) => {
        const path = issue.path[0] as string;
        if (!errors[path]) errors[path] = issue.message;
      });
      validationErrors = errors;
      notification.toast.error("Veuillez corriger les erreurs dans le formulaire");
      return;
    }

    validationErrors = {};
    onSave(result.data as any);
  }
</script>


<form 
  id="child-form" 
  class="p-3 bg-slate-50/80 border border-slate-200 rounded-lg space-y-3" 
  onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}
>
  <div class="grid grid-cols-4 gap-2 items-end">
    <div class="space-y-1 flex flex-col">
      <Label for="child-name" class="text-[0.75rem] text-slate-500">Nom *</Label>
      <Input id="child-name" bind:value={name} placeholder="Nom de l'enfant" class="h-8 text-[0.85rem] bg-white border-slate-200 rounded-md shadow-fine" />
    </div>
    <div class="space-y-1 flex flex-col">
      <Label for="child-birthdate" class="text-[0.75rem] text-slate-500">Date de naissance</Label>
      <Input id="child-birthdate" type="date" bind:value={birthdate} class="h-8 text-[0.85rem] bg-white border-slate-200 rounded-md shadow-fine" />
    </div>
    <div class="space-y-1">
      <Label class="text-[0.75rem] text-slate-500">Genre</Label>
      <div class="flex gap-3 h-8 items-center">
        <label class="flex items-center gap-1.5 cursor-pointer">
          <input type="radio" value="MALE" bind:group={gender} class="w-3.5 h-3.5 accent-primary" />
          <span class="text-[0.82rem] text-slate-600">M</span>
        </label>
        <label class="flex items-center gap-1.5 cursor-pointer">
          <input type="radio" value="FEMALE" bind:group={gender} class="w-3.5 h-3.5 accent-primary" />
          <span class="text-[0.82rem] text-slate-600">F</span>
        </label>
      </div>
    </div>
    <div class="flex items-center h-8">
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" bind:checked={isDependent} class="w-3.5 h-3.5 accent-primary rounded" />
        <span class="text-[0.82rem] text-slate-600">À charge</span>
      </label>
    </div>
  </div>

  <div class="space-y-1 px-1">
    <ValidationError errors={validationErrors} field="last_name" />
    <ValidationError errors={validationErrors} field="birthdate" />
    <ValidationError errors={validationErrors} field="gender" />
  </div>

  <div class="flex items-center justify-end gap-2 pt-1">
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
</form>
