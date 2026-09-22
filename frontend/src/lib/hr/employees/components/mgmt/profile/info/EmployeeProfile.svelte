<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle
  } from '@/components/ui/card';
  import type { EmployeeFullProfile } from '@/hr/employees/types/types';
  import { COUNTRY_OPTIONS } from '@/hr/employees/constants/countries';
  import { cn } from '@/utilities/common/css';
  import { buildFullName } from "@/utilities/common/employee.utils";
  import {
    REVERSE_GENDER_MAPPING,
    REVERSE_MARITAL_STATUS_MAPPING
  } from '@/hr/employees/constants/mappings';


  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  const fullName = $derived(buildFullName(employee));

  const formattedBirthdate = $derived(() => {
    if (!employee.birthdate) return '-';
    return new Date(employee.birthdate).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  });

  const formattedHireDate = $derived(() => {
    if (!employee.hire_date) return '-';
    return new Date(employee.hire_date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  });

  const genderLabel = $derived(
    REVERSE_GENDER_MAPPING[employee.gender as keyof typeof REVERSE_GENDER_MAPPING] || employee.gender || '-'
  );

  const maritalStatusLabel = $derived(
    REVERSE_MARITAL_STATUS_MAPPING[employee.marital_status as keyof typeof REVERSE_MARITAL_STATUS_MAPPING] || employee.marital_status || '-'
  );

  const nationalityLabel = $derived(() => {
    if (!employee.nationality) return '-';
    const country = COUNTRY_OPTIONS.find(c => c.value === employee.nationality);
    return country ? `${country.flag} ${country.label}` : employee.nationality;
  });
</script>


<div class="space-y-0.5">
  <!-- Identité -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="user" size={18} />
        Identité
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Nom complet</div>
          <p class="text-sm text-slate-900 mt-1">{fullName}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Matricule</div>
          <p class="text-sm text-slate-900 mt-1">{employee.matricule}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Date de naissance</div>
          <p class="text-sm text-slate-900 mt-1">{formattedBirthdate()}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Genre</div>
          <p class="text-sm text-slate-900 mt-1">{genderLabel}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Nationalité</div>
          <p class="text-sm text-slate-900 mt-1">{nationalityLabel()}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Situation matrimoniale</div>
          <p class="text-sm text-slate-900 mt-1">{maritalStatusLabel}</p>
        </div>
      </div>
    </CardContent>
  </Card>

  <!-- Contact -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="mail" size={18} />
        Contact
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Email professionnel</div>
          <p class="text-sm text-slate-900 mt-1">{employee.email}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Téléphone</div>
          <p class="text-sm text-slate-900 mt-1">{employee.phone || '-'}</p>
        </div>
      </div>
    </CardContent>
  </Card>

  <!-- Adresse -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="map-pin" size={18} />
        Adresse
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          {#if employee.current_address}
            <div class="space-y-2">
              <div class="text-sm text-slate-900">
                {employee.current_address.number} {employee.current_address.street}
              </div>
              <div class="text-sm text-slate-900">
                {employee.current_address.municipality}, {employee.current_address.city}
              </div>
              <div class="text-sm text-slate-900">
                {employee.current_address.province}
              </div>
              <div class="text-sm text-slate-900">
                {#if employee.current_address.country_code}
                  {@const country = COUNTRY_OPTIONS.find(c => c.value === employee.current_address.country_code)}
                  {country ? `${country.flag} ${country.label}` : employee.current_address.country_code}
                {/if}
              </div>
            </div>
          {:else}
            <p class="text-sm text-slate-500">Aucune adresse enregistrée</p>
          {/if}
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">
            Site de travail 
          </div>
          <div class="text-sm">{employee.work_site || '-'}</div>
        </div>
        
      </div>
    </CardContent>
  </Card>

  <!-- Informations professionnelles -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="briefcase" size={18} />
        Informations professionnelles
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Date d'embauche</div>
          <p class="text-sm text-slate-900 mt-1">{formattedHireDate()}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Statut</div>
          <div class="flex items-center gap-2 mt-1">
            <div class={cn(
              "h-2 w-2 rounded-full",
              employee.is_active ? "bg-emerald-500" : "bg-slate-400"
            )}></div>
            <span class="text-sm text-slate-700">
              {employee.is_active ? 'Actif' : 'Inactif'}
            </span>
          </div>
        </div>
        {#if employee.termination_date}
          <div>
            <div class="text-sm font-medium text-slate-500">Date de fin</div>
            <p class="text-sm text-slate-900 mt-1">
              {new Date(employee.termination_date).toLocaleDateString('fr-FR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              })}
            </p>
          </div>
        {/if}
      </div>
      {#if employee.description}
        <div>
          <div class="text-sm font-medium text-slate-500">Description</div>
          <p class="text-sm text-slate-900 mt-1">{employee.description}</p>
        </div>
      {/if}
    </CardContent>
  </Card>
</div>

