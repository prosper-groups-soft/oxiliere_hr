<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import type { EmployeeFullProfile } from '@/hr/modules/employees/types/types';
  import CountryPill from '@/hr/components/shared/country/CountryPill.svelte';
  import { cn } from '@/hr/utilities/common/css';
  import { buildFullName } from "@/hr/utilities/common/employee.utils";
  import { REVERSE_GENDER_MAPPING, REVERSE_MARITAL_STATUS_MAPPING } from '@/hr/modules/employees/constants/mappings';


  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  const fullName = $derived(buildFullName(employee));

  const formattedBirthdate = $derived(() => {
    if (!employee.birthdate) return '-';
    return new Date(employee.birthdate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  });

  const formattedHireDate = $derived(() => {
    if (!employee.hire_date) return '-';
    return new Date(employee.hire_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  });

  const genderLabel = $derived(
    REVERSE_GENDER_MAPPING[employee.gender as keyof typeof REVERSE_GENDER_MAPPING] || employee.gender || '-'
  );

  const maritalStatusLabel = $derived(
    REVERSE_MARITAL_STATUS_MAPPING[employee.marital_status as keyof typeof REVERSE_MARITAL_STATUS_MAPPING] || employee.marital_status || '-'
  );
</script>


{#snippet Field(label: string, value: string)}
  <div class="space-y-1">
    <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">{label}</div>
    <p class="text-[0.86rem] font-medium text-slate-900 leading-snug wrap-break-word">{value}</p>
  </div>
{/snippet}


<div class="space-y-4">
  <!-- Identité -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
          <AppIcon name="user" size={16} class="text-indigo-600" />
        </span>
        Identité
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Nom complet", fullName ?? '-')}
        {@render Field("Matricule", employee.matricule || '-')}
        {@render Field("Date de naissance", formattedBirthdate())}
        {@render Field("Genre", genderLabel)}
        <div class="space-y-1">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">Nationalité</div>
          <div class="pt-0.5">
            <CountryPill code={employee.nationality} />
          </div>
        </div>
        {@render Field("Situation matrimoniale", maritalStatusLabel)}
      </div>
    </CardContent>
  </Card>

  <!-- Contact -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center shrink-0">
          <AppIcon name="mail" size={16} class="text-emerald-600" />
        </span>
        Contact
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Email professionnel", employee.email || '-')}
        {@render Field("Téléphone", employee.phone || '-')}
        <div class="hidden lg:block"></div>
      </div>
    </CardContent>
  </Card>

  <!-- Adresse -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-center shrink-0">
          <AppIcon name="map-pin" size={16} class="text-sky-600" />
        </span>
        Adresse
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <div class="space-y-1 lg:col-span-2">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">Adresse actuelle</div>
          {#if employee.current_address}
            <div class="text-[0.86rem] font-medium text-slate-900 leading-relaxed">
              <div class="text-[0.86rem]">
                {[employee.current_address.number, employee.current_address.street].filter(Boolean).join(' ') || '-'}
              </div>
              <div class="text-slate-600 text-[0.86rem]">
                {[employee.current_address.municipality, employee.current_address.city].filter(Boolean).join(', ') || '-'}
              </div>
              <div class="text-slate-600 text-[0.86rem]">
                {employee.current_address.province || '-'}
              </div>
              {#if employee.current_address.country_code}
                <div class="mt-2">
                  <CountryPill code={employee.current_address.country_code} />
                </div>
              {/if}
            </div>
          {:else}
            <p class="text-[0.86rem] text-slate-500">Aucune adresse enregistrée</p>
          {/if}
        </div>
        {@render Field("Site de travail", employee.work_site || '-')}
      </div>
    </CardContent>
  </Card>

  <!-- Informations professionnelles -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-center shrink-0">
          <AppIcon name="briefcase" size={16} class="text-amber-600" />
        </span>
        Informations professionnelles
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4 space-y-5">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Date d'embauche", formattedHireDate())}
        <div class="space-y-1">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">Statut</div>
          <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-[0.84rem] font-medium {employee.is_active ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-slate-50 border-slate-200 text-slate-600'}">
            <span class={cn("h-2 w-2 rounded-full", employee.is_active ? "bg-emerald-500" : "bg-slate-400")}></span>
            {employee.is_active ? 'Actif' : 'Inactif'}
          </div>
        </div>
        {#if employee.termination_date}
          {@render Field("Date de fin", new Date(employee.termination_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }))}
        {:else}
          <div class="hidden lg:block"></div>
        {/if}
      </div>
      {#if employee.description}
        <div class="rounded-lg bg-slate-50/70 border border-slate-100 p-4">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400 mb-2">Description</div>
          <p class="text-[0.86rem] text-slate-700 leading-relaxed">{employee.description}</p>
        </div>
      {/if}
    </CardContent>
  </Card>
</div>

