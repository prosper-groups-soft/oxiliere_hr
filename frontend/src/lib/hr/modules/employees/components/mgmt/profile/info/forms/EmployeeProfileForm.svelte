<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { COUNTRY_OPTIONS } from "@/hr/modules/employees/constants/countries";
  import { GENDER_MAPPING, MARITAL_STATUS_MAPPING, REVERSE_GENDER_MAPPING, REVERSE_MARITAL_STATUS_MAPPING } from "@/hr/modules/employees/constants/mappings";
  import { useWorkSitesQuery } from "@/hr/modules/admin/company/queries/workSitesQueries";
  import {
    createForm, FormView,
    text, email, phone, date, select,
    validators
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { employee, onSave } = $props<{ employee: any; onSave: (data: any) => void }>();

  const workSitesQuery = useWorkSitesQuery(() => 1, () => 100);
  let workSites = $derived($workSitesQuery.data?.results ?? []);

  const GENDER_OPTIONS = [
    { value: 'MALE', label: 'Homme' },
    { value: 'FEMALE', label: 'Femme' },
    { value: 'NOT_SPECIFIED', label: 'Non spécifié' }
  ];
  const MARITAL_OPTIONS = [
    { value: 'SINGLE', label: 'Célibataire' },
    { value: 'MARRIED', label: 'Marié(e)' },
    { value: 'DIVORCED', label: 'Divorcé(e)' },
    { value: 'WIDOWED', label: 'Veuf(ve)' }
  ];

  const fields: FieldConfig[] = [
    text('last_name', { label: 'Nom', required: true, validators: [validators.required('Le nom est requis'), validators.maxLength(75, 'Max 75 caractères')] }),
    text('middle_name', { label: 'Post-nom', validators: [validators.maxLength(75, 'Max 75 caractères')] }),
    text('first_name', { label: 'Prénom', required: true, validators: [validators.required('Le prénom est requis'), validators.maxLength(75, 'Max 75 caractères')] }),
    date('birthdate', { label: 'Date de naissance' }),
    select('gender', { label: 'Genre', dataSource: { type: 'static', values: GENDER_OPTIONS } }),
    select('nationality', { label: 'Nationalité', dataSource: { type: 'static', values: COUNTRY_OPTIONS.map(c => ({ value: c.value, label: c.label })) } }),
    select('marital_status', { label: 'Situation matrimoniale', dataSource: { type: 'static', values: MARITAL_OPTIONS } }),
    email('email', { label: 'Email professionnel', required: true, validators: [validators.required("L'email est requis"), validators.email('Email invalide')] }),
    phone('phone', { label: 'Téléphone' }),
    select('work_site', {
      label: 'Site de travail',
      required: true,
      validators: [validators.required('Le site est requis')]
    }),
    text('address.number', { label: 'Numéro', validators: [validators.maxLength(5, 'Max 5 caractères')] }),
    text('address.street', { label: 'Avenue / Rue' }),
    text('address.municipality', { label: 'Commune' }),
    text('address.city', { label: 'Ville' }),
    text('address.province', { label: 'Province' }),
    select('address.country_code', { label: 'Pays', dataSource: { type: 'static', values: COUNTRY_OPTIONS.map(c => ({ value: c.value, label: c.label })) } })
  ];

  const form = createForm({
    id: 'employee-profile-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'inline', variant: 'plain' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Identité', fields: ['last_name', 'middle_name', 'first_name', 'birthdate', 'gender', 'nationality', 'marital_status'] },
        { title: 'Contact & Professionnel', fields: ['email', 'phone', 'work_site'] },
        { title: 'Adresse de résidence', fields: ['address.number', 'address.street', 'address.municipality', 'address.city', 'address.province', 'address.country_code'] }
      ]
    },
    onSubmit: async (data) => {
      // Map frontend labels back to backend enums for gender/marital
      const payload = {
        ...data,
        gender: data.gender ? GENDER_MAPPING[data.gender as keyof typeof GENDER_MAPPING] ?? data.gender : data.gender,
        marital_status: data.marital_status ? MARITAL_STATUS_MAPPING[data.marital_status as keyof typeof MARITAL_STATUS_MAPPING] ?? data.marital_status : data.marital_status
      };
      onSave(payload);
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Hydrate + workSite datasource
  $effect(() => {
    if (employee) {
      form.hydrate({
        last_name: employee.last_name ?? '',
        middle_name: employee.middle_name ?? '',
        first_name: employee.first_name ?? '',
        birthdate: employee.birthdate?.split('T')[0] ?? '',
        gender: REVERSE_GENDER_MAPPING[employee.gender as keyof typeof REVERSE_GENDER_MAPPING] ?? employee.gender ?? '',
        nationality: employee.nationality ?? '',
        marital_status: REVERSE_MARITAL_STATUS_MAPPING[employee.marital_status as keyof typeof REVERSE_MARITAL_STATUS_MAPPING] ?? employee.marital_status ?? '',
        email: employee.email ?? '',
        phone: employee.phone ?? '',
        work_site: employee.work_site_id ?? employee.work_site?.id ?? '',
        'address.number': employee.current_address?.number ?? '',
        'address.street': employee.current_address?.street ?? '',
        'address.municipality': employee.current_address?.municipality ?? '',
        'address.city': employee.current_address?.city ?? '',
        'address.province': employee.current_address?.province ?? '',
        'address.country_code': employee.current_address?.country_code ?? ''
      });
    }
  });
  $effect(() => {
    const opts = workSites.map((s: any) => ({ value: s.id, label: s.name }));
    form.setConfig({ fields: fields.map(f => f.id === 'work_site' ? { ...f, dataSource: { type: 'static', values: opts } } : f) as any });
  });

  export function submit() { form.submit(); }
</script>

<FormView {form} fields={fields} showSubmit={false} showReset={false} />
