<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import type { RecruitmentCampaign } from "@/hr/modules/recruitment/types/types";
  import { CAMPAIGN_STATUS_OPTIONS } from "@/hr/modules/recruitment/constants/recruitment";
  import { useCreateJobOfferMutation, useUpdateJobOfferMutation } from "@/hr/modules/recruitment/queries/recruitmentQueries";
  import { useQueryClient } from '@tanstack/svelte-query';
  import { usePositionsQuery } from "@/hr/modules/jobs/queries/jobQueries";
  import { useWorkSitesQuery } from "@/hr/modules/admin/company/queries/workSitesQueries";
  import { useAllEmployees } from "@/hr/modules/employees/queries/employeeQueries";
  import {
    createForm, FormView,
    text, textarea, select, date, number, switchField,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), campaign = $bindable(null) } = $props<{ open: boolean; campaign?: RecruitmentCampaign | null }>();

  const createMutation = useCreateJobOfferMutation();
  const updateMutation = useUpdateJobOfferMutation();
  const queryClient = useQueryClient();
  const positionsQuery = usePositionsQuery();
  const workSitesQuery = useWorkSitesQuery(() => 1, () => 200);
  const employeesQuery = useAllEmployees();

  let positions = $derived($positionsQuery.data ?? []);
  let workSites = $derived($workSitesQuery.data?.results ?? []);
  let employees = $derived($employeesQuery.data ?? []);

  const fields: FieldConfig[] = [
    text('title', { label: 'Titre de la campagne', required: true, placeholder: 'ex: Recrutement Tech Q3', validators: [validators.required('Le titre est requis')] }),
    select('location', { label: 'Localisation', placeholder: 'Sélectionner...', dataSource: { type: 'static', values: [] } }),
    select('status', {
      label: 'Statut',
      required: true,
      defaultValue: 'DRAFT',
      dataSource: { type: 'static', values: CAMPAIGN_STATUS_OPTIONS.map(o => ({ value: o.value, label: o.label })) }
    }),
    select('recruiterId', { label: 'Recruteur', placeholder: 'Sélectionner un recruteur', dataSource: { type: 'static', values: [] } }),
    select('positionIds', {
      label: 'Postes',
      placeholder: 'Sélectionner des postes...',
      behaviors: [{ type: 'multiSelect' }]
    }),
    date('endDate', { out: 'end_date', label: 'Date de fin' }),
    date('publishedAt', { out: 'published_at', label: 'Date de publication' }),
    number('maxApplications', { label: 'Max candidatures', min: 1, placeholder: 'Illimité' }),
    switchField('isPublished', { out: 'is_published', label: 'Publier immédiatement', defaultValue: false }),
    switchField('isActive', { out: 'is_active', label: 'Campagne active', defaultValue: true }),
    textarea('description', { label: 'Description du besoin', placeholder: "Détails sur le poste, l'équipe..." })
  ];

  const form = createForm({
    id: 'recruitment-campaign-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Campagne', fields: ['title', 'location', 'status', 'recruiterId'] },
        { title: 'Postes & Planning', fields: ['positionIds', 'endDate', 'publishedAt', 'maxApplications'] },
        { title: 'Publication', fields: ['isPublished', 'isActive'] },
        { title: 'Description', fields: ['description'] }
      ]
    },
    onSubmit: async (data) => {
      const posIds: string[] = Array.isArray(data.positionIds) ? data.positionIds : (data.positionIds ? [data.positionIds] : []);
      const payload = {
        title: data.title,
        target_position_ids: posIds,
        position_slots: Object.fromEntries(posIds.map(id => [id, 1])),
        location: data.location,
        status: data.status,
        description: data.description,
        slots: posIds.length,
        end_date: data.endDate || undefined,
        published_at: data.publishedAt || undefined,
        is_published: data.isPublished,
        is_active: data.isActive,
        max_applications: data.maxApplications ? Number(data.maxApplications) : undefined,
        recruiter_id: data.recruiterId || undefined
      };
      if (campaign) await $updateMutation.mutateAsync({ offerId: campaign.id, data: payload } as any);
      else await $createMutation.mutateAsync(payload as any);
      await queryClient.invalidateQueries({ queryKey: ['recruitment'] });
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Dynamic datasources
  $effect(() => {
    const posOpts = positions.map(p => ({ value: p.id, label: p.name }));
    const siteOpts = workSites.map((s: any) => ({ value: s.name, label: s.name }));
    const empOpts = employees.map((e: any) => ({ value: String(e.id), label: e.name }));
    form.setConfig({ fields: fields.map(f => {
      if (f.id === 'positionIds') return { ...f, dataSource: { type: 'static', values: posOpts } };
      if (f.id === 'location') return { ...f, dataSource: { type: 'static', values: siteOpts } };
      if (f.id === 'recruiterId') return { ...f, dataSource: { type: 'static', values: empOpts } };
      return f;
    }) as any });
  });

  const entity = $derived(campaign ? {
    title: campaign.title ?? '',
    location: campaign.location ?? '',
    status: campaign.status ?? 'DRAFT',
    recruiterId: campaign.hiringManagerId ?? '',
    positionIds: campaign.jobIds ?? [],
    endDate: campaign.closeDate?.split('T')[0] ?? '',
    publishedAt: campaign.openDate?.split('T')[0] ?? '',
    maxApplications: campaign.maxApplications ?? '',
    isPublished: campaign.isPublished ?? false,
    isActive: campaign.isActive ?? true,
    description: campaign.description ?? ''
  } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={campaign ? 'Modifier la campagne' : 'Nouvelle campagne'}
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
