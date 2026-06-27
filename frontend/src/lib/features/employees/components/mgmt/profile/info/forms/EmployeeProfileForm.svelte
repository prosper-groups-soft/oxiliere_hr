<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import PhoneInput from "@/components/ui/phone-input";
  import * as Select from "@/components/ui/select";
  import ValidationError from "@/components/ui/validation-error";
  import { COUNTRY_OPTIONS } from "@/features/employees/constants/countries";
  import { useWorkSitesQuery } from "@/features/admin/settings/queries/workSitesQueries";
  import type { WorkSite } from "@/features/admin/settings/types/workSites.types";
  import {
    GENDER_MAPPING,
    MARITAL_STATUS_MAPPING,
    REVERSE_GENDER_MAPPING,
    REVERSE_MARITAL_STATUS_MAPPING,
    type BackendGenderValue,
    type BackendMaritalStatusValue
  } from "@/features/employees/constants/mappings";
  import { identitySchema, validateStep } from "@/features/employees/schemas/onboarding.schema";
  import { notification } from "@/stores/notification.svelte";

  let { employee, onSave } = $props();

  // --- ÉTAT DU FORMULAIRE ---
  let formData = $state({
    id: '',
    first_name: '',
    last_name: '',
    middle_name: '',
    birthdate: '',
    email: '',
    phone: '',
    gender: '' as BackendGenderValue,
    nationality: '',
    marital_status: '' as BackendMaritalStatusValue,
    work_site: '',
    address: {
      number: '',
      street: '',
      municipality: '',
      city: '',
      province: '',
      country_code: ''
    }
  });

  $effect(() => {
    if (employee) {
      formData.id = employee.id;
      formData.first_name = employee.first_name || '';
      formData.last_name = employee.last_name || '';
      formData.middle_name = employee.middle_name || '';
      formData.birthdate = employee.birthdate ? employee.birthdate.split('T')[0] : '';
      formData.email = employee.email || '';
      formData.phone = employee.phone || '';
      formData.gender = employee.gender as BackendGenderValue || '';
      formData.nationality = employee.nationality || '';
      formData.marital_status = employee.marital_status as BackendMaritalStatusValue || '';
      formData.work_site = employee.work_site_id || employee.work_site?.id || '';
      
      formData.address = {
        number: employee.current_address?.number || '',
        street: employee.current_address?.street || '',
        municipality: employee.current_address?.municipality || '',
        city: employee.current_address?.city || '',
        province: employee.current_address?.province || '',
        country_code: employee.current_address?.country_code || ''
      };
    }
  });

  // --- LOGIQUE DÉPENDANTE ---
  const workSitesQuery = useWorkSitesQuery(() => 1, () => 100);
  const workSites = $derived($workSitesQuery.data?.results || []);

  // --- VALIDATION RÉACTIVE ---
  let validationErrors: Record<string, string> = $state({});
  let isValid = $state(true);

  $effect(() => {
    // On valide l'objet formData (sans l'ID qui n'est pas dans le schéma d'identité)
    const { id, ...dataToValidate } = formData;
    const validation = identitySchema.safeParse(dataToValidate);
    
    if (!validation.success) {
      const errors: Record<string, string> = {};
      validation.error.issues.forEach(issue => {
        const path = issue.path.join('.');
        errors[path] = issue.message;
      });
      validationErrors = errors;
      isValid = false;
    } else {
      validationErrors = {};
      isValid = true;
    }
  });

  // Fonction de soumission exposée au parent
  export function submit() {
    if (!isValid) {
      notification.toast.error("Veuillez corriger les erreurs avant d'enregistrer");
      return;
    }
    onSave(formData);
  }

  // Mappings Helpers
  function mapGender(v: string) { 
    formData.gender = GENDER_MAPPING[v as keyof typeof GENDER_MAPPING] as BackendGenderValue; 
  }
  function mapMarital(v: string) { 
    formData.marital_status = MARITAL_STATUS_MAPPING[v as keyof typeof MARITAL_STATUS_MAPPING] as BackendMaritalStatusValue; 
  }
</script>


{#snippet FieldGroup(id: string, label: string, placeholder: string, type: string, value: string, fieldPath: string)}
  <div class="space-y-1.5">
    <Label for={id} class="text-[0.83rem] text-slate-900 font-medium">{label}</Label>
    <Input
      {id}
      {type}
      {placeholder}
      {value}
      oninput={(e) => {
        if (fieldPath.includes('.')) {
          const [parent, child] = fieldPath.split('.');
          (formData as any)[parent][child] = e.currentTarget.value;
        } else {
          (formData as any)[fieldPath] = e.currentTarget.value;
        }
      }}
      class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
    />
    <ValidationError errors={validationErrors} field={fieldPath} />
  </div>
{/snippet}


<div class="p-1 space-y-1">
  
  <!-- Section: Identité -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Informations d'identité
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      {@render FieldGroup("last_name", "Nom *", "Nom", "text", formData.last_name, "last_name")}
      {@render FieldGroup("middle_name", "Post-nom", "Post-nom", "text", formData.middle_name, "middle_name")}
      {@render FieldGroup("first_name", "Prénom *", "Prénom", "text", formData.first_name, "first_name")}
      {@render FieldGroup("birthdate", "Date de naissance *", "", "date", formData.birthdate, "birthdate")}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- Genre -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Genre</Label>
        <Select.Root type="single" value={REVERSE_GENDER_MAPPING[formData.gender]} onValueChange={mapGender}>
          <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine text-sm w-full">
            {REVERSE_GENDER_MAPPING[formData.gender] || "Sélectionner..."}
          </Select.Trigger>
          <Select.Content class="z-100">
            <Select.SelectItem value="Homme">Homme</Select.SelectItem>
            <Select.SelectItem value="Femme">Femme</Select.SelectItem>
            <Select.SelectItem value="Non spécifié">Non spécifié</Select.SelectItem>
          </Select.Content>
        </Select.Root>
        <ValidationError errors={validationErrors} field="gender" />
      </div>

      <!-- Nationalité -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Nationalité</Label>
        <Select.Root type="single" value={formData.nationality} onValueChange={(v) => formData.nationality = v}>
          <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine text-sm w-full flex items-center gap-2">
            {#if formData.nationality}
              <span class="text-sm">{COUNTRY_OPTIONS.find(c => c.value === formData.nationality)?.flag}</span>
              <span class="truncate text-sm">{COUNTRY_OPTIONS.find(c => c.value === formData.nationality)?.label}</span>
            {:else}
              <span class="text-slate-500 text-sm">Sélectionner...</span>
            {/if}
          </Select.Trigger>
          <Select.Content class="max-h-64 z-100">
            {#each COUNTRY_OPTIONS as country}
              <Select.SelectItem value={country.value}>{country.flag} {country.label}</Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <ValidationError errors={validationErrors} field="nationality" />
      </div>

      <!-- État Civil -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Situation matrimoniale</Label>
        <Select.Root type="single" value={REVERSE_MARITAL_STATUS_MAPPING[formData.marital_status]} onValueChange={mapMarital}>
          <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine text-sm w-full">
            {REVERSE_MARITAL_STATUS_MAPPING[formData.marital_status] || "Sélectionner..."}
          </Select.Trigger>
          <Select.Content class="z-100">
            <Select.SelectItem value="Célibataire">Célibataire</Select.SelectItem>
            <Select.SelectItem value="Marié(e)">Marié(e)</Select.SelectItem>
            <Select.SelectItem value="Divorcé(e)">Divorcé(e)</Select.SelectItem>
            <Select.SelectItem value="Veuf(ve)">Veuf(ve)</Select.SelectItem>
          </Select.Content>
        </Select.Root>
        <ValidationError errors={validationErrors} field="marital_status" />
      </div>
    </div>
  </div>

  <!-- Section: Contact & Pro -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Contact & Professionnel
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      {@render FieldGroup("email", "Email professionnel *", "email@compagnie.com", "email", formData.email, "email")}
      <PhoneInput
        id="phone"
        label="Téléphone *"
        value={formData.phone.replace(/\s/g, '')}
        onChange={(v) => formData.phone = v.replace(/\s/g, '')}
      />
    </div>
    <div class="space-y-1.5">
      <Label class="text-[0.83rem] text-slate-900 font-medium">Site de travail *</Label>
      <Select.Root type="single" value={formData.work_site} onValueChange={(v) => formData.work_site = v}>
        <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine text-sm w-full">
          {workSites.find((s: WorkSite) => s.id === formData.work_site)?.name || "Sélectionner un site..."}
        </Select.Trigger>
        <Select.Content class="z-100">
          {#each workSites as site}
            <Select.SelectItem value={site.id}>{site.name}</Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
      <ValidationError errors={validationErrors} field="work_site" />
    </div>
  </div>

  <!-- Section: Adresse -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Adresse de résidence
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      {@render FieldGroup("addr_num", "Numéro", "123", "text", formData.address.number, "address.number")}
      {@render FieldGroup("addr_street", "Avenue / Rue", "Avenue...", "text", formData.address.street, "address.street")}
      {@render FieldGroup("addr_mun", "Commune", "Commune", "text", formData.address.municipality, "address.municipality")}
      {@render FieldGroup("addr_city", "Ville", "Ville", "text", formData.address.city, "address.city")}
      {@render FieldGroup("addr_prov", "Province", "Province", "text", formData.address.province, "address.province")}
      
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">Pays</Label>
        <Select.Root type="single" value={formData.address.country_code} onValueChange={(v) => formData.address.country_code = v}>
          <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine text-sm w-full flex items-center gap-2">
            {#if formData.address.country_code}
              <span class="text-sm">
                {COUNTRY_OPTIONS.find(c => c.value === formData.address.country_code)?.flag}
              </span>
              <span class="truncate text-sm">
                {COUNTRY_OPTIONS.find(c => c.value === formData.address.country_code)?.label}
              </span>
            {:else}
              <span class="text-slate-500 text-sm">Sélectionner...</span>
            {/if}
          </Select.Trigger>
          <Select.Content class="max-h-64 z-100">
            {#each COUNTRY_OPTIONS as country}
              <Select.SelectItem value={country.value}>{country.flag} {country.label}</Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <ValidationError errors={validationErrors} field="address.country_code" />
      </div>
    </div>
  </div>
</div>

