<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import PhoneInput from "@/hr/components/ui/phone-input";
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
  import { cn } from "@/hr/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import * as Select from "@/components/ui/select";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import ValidationError from "@/hr/components/ui/validation-error";
  import { validateStep } from "../../../schemas/onboarding.schema";
  import { COUNTRY_OPTIONS, findCountry } from "../../../constants/countries";
  import CountryFlag from "@/hr/components/shared/country/CountryFlag.svelte";
  import { buildFullName } from "@/hr/utilities/common/employee.utils";
  import { useWorkSitesQuery } from "../../../../admin/company/queries/workSitesQueries";
  import type { WorkSite } from "../../../../admin/company/types/workSites.types";
  import { GENDER_MAPPING, MARITAL_STATUS_MAPPING, REVERSE_GENDER_MAPPING, REVERSE_MARITAL_STATUS_MAPPING, type BackendGenderValue, type BackendMaritalStatusValue } from "../../../constants/mappings";

  
  // Preview URL for the uploaded photo
  let photoPreviewUrl = $state<string | undefined>(undefined);

  function handlePhotoUpload(file: File) {
    if (photoPreviewUrl) URL.revokeObjectURL(photoPreviewUrl); // Libère l'ancienne
    onboardingStore.setIdentityField('profile_photo', file);
    photoPreviewUrl = URL.createObjectURL(file);
  }

  $effect(() => {
  const file = onboardingStore.data.identity.profile_photo;
  // Si on a un fichier mais pas encore d'URL de preview (ex: retour sur l'étape)
  if (file instanceof File && !photoPreviewUrl) {
    photoPreviewUrl = URL.createObjectURL(file);
    
    // Nettoyage de la mémoire quand le composant est détruit
    return () => URL.revokeObjectURL(photoPreviewUrl!);
  }
});

  // Full name for avatar fallback
  const fullName = $derived(
    `${buildFullName(onboardingStore.data.identity)}`.trim()
  );

  const palette = $derived(getAvatarPalette(fullName || 'Nouveau'));

  function mapGenderForBackend(gender: string): BackendGenderValue | '' {
    return (GENDER_MAPPING[gender as keyof typeof GENDER_MAPPING] || '') as BackendGenderValue | '';
  }

  function mapMaritalStatusForBackend(status: string): BackendMaritalStatusValue | '' {
    return (MARITAL_STATUS_MAPPING[status as keyof typeof MARITAL_STATUS_MAPPING] || '') as BackendMaritalStatusValue | '';
  }

  const workSitesQuery = useWorkSitesQuery(() => 1, () => 100);
  const workSites = $derived($workSitesQuery.data?.results || []);

  let validationErrors: Record<string, string> = $state({});

  $effect(() => {
    const validation = validateStep('identity', onboardingStore.data.identity);
    if (!validation.success) {
      const errors: Record<string, string> = {};
      validation.errors.forEach(error => {
        if (error.includes('prénom')) errors.first_name = error;
        else if (error.includes('nom')) errors.last_name = error;
        else if (error.includes('email')) errors.email = error;
        else if (error.includes('téléphone')) errors.phone = error;
        else if (error.includes('naissance')) errors.birthdate = error;
        else if (error.includes('site')) errors.work_site = error;
      });
      validationErrors = errors;
    } else {
      validationErrors = {};
    }
  });
</script>


{#snippet FieldGroup(
  id: string,
  label: string,
  placeholder: string,
  type = "text",
  value: string,
  onChange: (val: string) => void,
  height = "h-10",
)}
  <div class="space-y-1.5">
    <Label for={id} class="text-[0.83rem] text-slate-900 font-medium">
      {label}
    </Label>
    <Input
      {id}
      {type}
      {placeholder}
      {value}
      oninput={(e) => onChange(e.currentTarget.value)}
      class="{height} bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
    />
    <ValidationError errors={validationErrors} field={id} />
  </div>
{/snippet}


<Card class="border-slate-200 shadow-none rounded-none py-0 pb-3">
  <CardHeader class="px-0 pt-0">
    <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
      Informations personnelles
    </CardTitle>
    <CardDescription class="text-[0.835rem]">
      Saisissez les informations d'identité du nouveau collaborateur.
    </CardDescription>
  </CardHeader>
  
  <CardContent class="px-0 py-0 space-y-6">

    <!-- Photo de profil (centrée, premier contact visuel) -->
    <div class="flex flex-col items-center gap-3 pb-6 border-b border-slate-100">
      <AvatarGallery
        name={fullName || 'Nouveau'}
        src={photoPreviewUrl}
        class="h-32 w-32 rounded-2xl mx-auto"
        onUpload={handlePhotoUpload}
      >
        <Avatar class="h-32 w-32 rounded-2xl border-2 border-slate-200 shadow-sm">
          <AvatarImage src={photoPreviewUrl} alt={fullName} class="object-cover rounded-2xl" />
          <AvatarFallback class={cn("text-4xl font-bold rounded-2xl", palette.bg, palette.text)}>
            {fullName ? getInitials(...fullName.split(' ')) : 'NC'}
          </AvatarFallback>
        </Avatar>
      </AvatarGallery>
      <p class="text-[0.78rem] text-slate-500 text-center max-w-[200px]">
        Cliquez sur l'image pour modifier la photo de profil
      </p>
    </div>

    <!-- Section 1 : État civil -->
    <div class="space-y-4">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        État civil
      </h4>

      <!-- Ligne: Nom et Post-nom -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4.5">
        {@render FieldGroup(
          "last_name", "Nom *", "ex: KIBANGULA", "text",
          onboardingStore.data.identity.last_name,
          (v) => onboardingStore.setIdentityField('last_name', v)
        )}
        {@render FieldGroup(
          "middle_name", "Post-nom", "ex: MUSUYU", "text",
          onboardingStore.data.identity.middle_name,
          (v) => onboardingStore.setIdentityField('middle_name', v)
        )}
      </div>

      <!-- Ligne: Prénom et Date de naissance -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4.5">
        {@render FieldGroup(
          "first_name", "Prénom *", "ex: Prosper", "text",
          onboardingStore.data.identity.first_name,
          (v) => onboardingStore.setIdentityField('first_name', v)
        )}
        {@render FieldGroup(
          "birthdate", "Date de naissance *", "ex: 15/01/1990", "date",
          onboardingStore.data.identity.birthdate,
          (v) => onboardingStore.setIdentityField('birthdate', v)
        )}
      </div>

      <!-- Ligne: Genre, Nationalité, Situation -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4.5">
        <div class="space-y-1.5 w-full">
          <Label class="text-[0.83rem] text-slate-900 font-medium">Genre</Label>
          <Select.Root type="single" value={onboardingStore.data.identity.gender} onValueChange={(v) => onboardingStore.setIdentityField('gender', mapGenderForBackend(v))}>
            <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine font-normal text-sm w-full cursor-pointer">
              {REVERSE_GENDER_MAPPING[onboardingStore.data.identity.gender as keyof typeof REVERSE_GENDER_MAPPING] || "Sélectionner..."}
            </Select.Trigger>
            <Select.Content>
              <Select.SelectItem value="Homme">Homme</Select.SelectItem>
              <Select.SelectItem value="Femme">Femme</Select.SelectItem>
              <Select.SelectItem value="Non spécifié">Non spécifié</Select.SelectItem>
            </Select.Content>
          </Select.Root>
          <ValidationError errors={validationErrors} field="gender" />
        </div>

        <div class="space-y-1.5 w-full">
          <Label class="text-[0.83rem] text-slate-900 font-medium">Nationalité</Label>
          <Select.Root type="single" value={onboardingStore.data.identity.nationality} onValueChange={(v) => onboardingStore.setIdentityField('nationality', v)}>
            <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine font-normal text-sm w-full cursor-pointer flex items-center gap-2">
              {#if findCountry(onboardingStore.data.identity.nationality)}
                <CountryFlag code={findCountry(onboardingStore.data.identity.nationality)?.code} />
                <span class="text-sm">{findCountry(onboardingStore.data.identity.nationality)?.label}</span>
              {:else}
                <span class="text-sm">Sélectionner...</span>
              {/if}
            </Select.Trigger>
            <Select.Content class="max-h-60">
              {#each COUNTRY_OPTIONS as country}
                <Select.SelectItem value={country.value}>
                  <div class="flex items-center gap-2">
                    <CountryFlag code={country.code} />
                    <span class="text-sm">{country.label}</span>
                  </div>
                </Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
          <ValidationError errors={validationErrors} field="nationality" />
        </div>

        <div class="space-y-1.5 w-full">
          <Label class="text-[0.83rem] text-slate-900 font-medium">Situation matrimoniale</Label>
          <Select.Root type="single" value={onboardingStore.data.identity.marital_status} onValueChange={(v) => onboardingStore.setIdentityField('marital_status', mapMaritalStatusForBackend(v))}>
            <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine font-normal text-sm w-full cursor-pointer">
              {REVERSE_MARITAL_STATUS_MAPPING[onboardingStore.data.identity.marital_status as keyof typeof REVERSE_MARITAL_STATUS_MAPPING] || "Sélectionner..."}
            </Select.Trigger>
            <Select.Content>
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

    <!-- Section 2 : Contact professionnel -->
    <div class="space-y-4">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        Contact professionnel
      </h4>

      <!-- Ligne: Email, Téléphone, Site de travail -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4.5">
        {@render FieldGroup(
          "email", "Email professionnel *", "ex: prosper@oxiliere.com", "email",
          onboardingStore.data.identity.email,
          (v) => onboardingStore.setIdentityField('email', v),
          "h-9"
        )}
        <PhoneInput
          id="phone"
          label="Téléphone *"
          placeholder="Numéro de téléphone"
          value={onboardingStore.data.identity.phone}
          onChange={(v) => onboardingStore.setIdentityField('phone', v)}
          errors={validationErrors}
        />
        <div class="space-y-1.5 w-full">
          <Label class="text-[0.83rem] text-slate-900 font-medium">Site de travail *</Label>
          <Select.Root type="single" value={onboardingStore.data.identity.work_site} onValueChange={(v) => onboardingStore.setIdentityField('work_site', v)}>
            <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine font-normal text-sm w-full cursor-pointer">
              {workSites.find((s: WorkSite) => s.id === onboardingStore.data.identity.work_site)?.name || "Sélectionner..."}
            </Select.Trigger>
            <Select.Content class="max-h-60">
              {#each workSites as site}
                <Select.SelectItem value={site.id}>{site.name}</Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
          <ValidationError errors={validationErrors} field="work_site" />
        </div>
      </div>
    </div>

    <!-- Section 3 : Adresse (optionnel) -->
    <div class="space-y-4">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        Adresse (optionnel)
      </h4>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4.5">
        {@render FieldGroup(
          "address.number", "Numéro", "ex: 123", "text",
          onboardingStore.data.identity.address?.number || '',
          (v) => onboardingStore.setAddressField('number', v)
        )}
        {@render FieldGroup(
          "address.street", "Rue", "ex: Avenue de la Paix", "text",
          onboardingStore.data.identity.address?.street || '',
          (v) => onboardingStore.setAddressField('street', v)
        )}
        {@render FieldGroup(
          "address.municipality", "Commune", "ex: Kampemba", "text",
          onboardingStore.data.identity.address?.municipality || '',
          (v) => onboardingStore.setAddressField('municipality', v)
        )}
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4.5">
        {@render FieldGroup(
          "address.city", "Ville", "ex: Lubmbashi", "text",
          onboardingStore.data.identity.address?.city || '',
          (v) => onboardingStore.setAddressField('city', v)
        )}
        {@render FieldGroup(
          "address.province", "Province", "ex: Haut-Katanga", "text",
          onboardingStore.data.identity.address?.province || '',
          (v) => onboardingStore.setAddressField('province', v)
        )}
        <div class="space-y-1.5 w-full">
          <Label class="text-[0.83rem] text-slate-900 font-medium">Pays</Label>
          <Select.Root type="single" value={onboardingStore.data.identity.address?.country_code || ''} onValueChange={(v) => onboardingStore.setAddressField('country_code', v)}>
            <Select.Trigger class="h-10 bg-white border-slate-200 shadow-fine font-normal text-sm w-full cursor-pointer flex items-center gap-2">
              {#if findCountry(onboardingStore.data.identity.address?.country_code)}
                <CountryFlag code={findCountry(onboardingStore.data.identity.address?.country_code)?.code} />
                <span class="text-sm">{findCountry(onboardingStore.data.identity.address?.country_code)?.label}</span>
              {:else}
                <span class="text-sm">Sélectionner...</span>
              {/if}
            </Select.Trigger>
            <Select.Content class="max-h-60">
              {#each COUNTRY_OPTIONS as country}
                <Select.SelectItem value={country.value}>
                  <div class="flex items-center gap-2">
                    <CountryFlag code={country.code} />
                    <span class="text-sm">{country.label}</span>
                  </div>
                </Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>
      </div>
    </div>

  </CardContent>
</Card>
