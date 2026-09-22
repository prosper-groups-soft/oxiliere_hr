<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { recruitmentStore } from "@/hr/modules/recruitment/stores/recruitment.svelte";
  import type { Candidate } from "@/hr/modules/recruitment/types/types";
  import { CANDIDATE_SOURCE_OPTIONS, CANDIDATE_GENDER_OPTIONS } from '@/hr/modules/recruitment/constants/recruitment';
  import { useCreateCandidateMutation, useUpdateCandidateMutation, useUploadCandidatePhotoMutation, useUploadCandidateResumeMutation } from "@/hr/modules/recruitment/queries/recruitmentQueries";
  import {
    createForm, FormView,
    text, email, phone, select, textarea, file,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), candidate = $bindable(null), campaignId = null } = $props<{ open: boolean; candidate?: Candidate | null; campaignId?: string | null }>();

  const createMutation = useCreateCandidateMutation();
  const updateMutation = useUpdateCandidateMutation();
  const uploadPhotoMutation = useUploadCandidatePhotoMutation();
  const uploadResumeMutation = useUploadCandidateResumeMutation();

  const fields: FieldConfig[] = [
    text('lastName', { out: 'lastName', label: 'Nom', required: true, validators: [validators.required('Le nom est requis')] }),
    text('middleName', { label: 'Post-nom' }),
    text('firstName', { out: 'firstName', label: 'Prénom', required: true, validators: [validators.required('Le prénom est requis')] }),
    email('email', { label: 'Email', required: true, validators: [validators.required("L'email est requis"), validators.email('Email invalide')] }),
    phone('phone', { label: 'Téléphone' }),
    text('linkedinUrl', { label: 'Profil LinkedIn', placeholder: 'https://linkedin.com/in/...' }),
    select('gender', {
      label: 'Genre',
      defaultValue: 'NOT_SPECIFIED',
      dataSource: { type: 'static', values: CANDIDATE_GENDER_OPTIONS.map(o => ({ value: o.value, label: o.label })) }
    }),
    select('source', {
      label: 'Source',
      defaultValue: 'DIRECT',
      dataSource: { type: 'static', values: CANDIDATE_SOURCE_OPTIONS.map(o => ({ value: o.value, label: o.label })) }
    }),
    text('location', { label: 'Localisation', placeholder: 'Paris, France' }),
    text('experience', { label: 'Expérience', placeholder: 'ex: 5 ans' }),
    text('skills', { label: 'Compétences (séparées par virgule)', placeholder: 'ex: JavaScript, Gestion...' }),
    file('photo', { label: 'Photo de profil', accept: 'image/*' }),
    file('resume', { label: 'CV / Résumé', accept: '.pdf,.doc,.docx,.png,.jpg,.jpeg' }),
    textarea('summary', { label: 'Résumé du profil', placeholder: 'Aperçu rapide...' }),
    textarea('notes', { label: 'Notes internes', placeholder: 'Observations...' })
  ];

  const form = createForm({
    id: 'candidate-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-145' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Identité', fields: ['lastName', 'middleName', 'firstName', 'email', 'phone', 'linkedinUrl', 'gender'] },
        { title: 'Profil', fields: ['source', 'location', 'experience', 'skills'] },
        { title: 'Fichiers', fields: ['photo', 'resume'] },
        { title: 'Notes', fields: ['summary', 'notes'] }
      ]
    },
    onSubmit: async (data, extra) => {
      const skillsArr = data.skills ? String(data.skills).split(',').map((s: string) => s.trim()).filter(Boolean) : [];
      const photoFile = extra?.files?.photo?.[0] as File | undefined;
      const resumeFile = extra?.files?.resume?.[0] as File | undefined;

      if (candidate) {
        await $updateMutation.mutateAsync({
          candidateId: candidate.id,
          data: {
            firstName: data.firstName, middleName: data.middleName, lastName: data.lastName,
            email: data.email, phone: data.phone, linkedinProfile: data.linkedinUrl,
            source: data.source, gender: data.gender, location: data.location,
            experience: data.experience, summary: data.summary, skills: skillsArr, notes: data.notes,
            offerId: campaignId || recruitmentStore.activeCampaignId || undefined
          }
        });
        if (photoFile) await $uploadPhotoMutation.mutateAsync({ candidateId: candidate.id, file: photoFile });
        if (resumeFile) await $uploadResumeMutation.mutateAsync({ candidateId: candidate.id, file: resumeFile });
      } else {
        const result = await $createMutation.mutateAsync({
          firstName: data.firstName, middleName: data.middleName, lastName: data.lastName,
          email: data.email, phone: data.phone, linkedinProfile: data.linkedinUrl,
          source: data.source, gender: data.gender, location: data.location,
          experience: data.experience, summary: data.summary, skills: skillsArr, notes: data.notes,
          campaignId: campaignId || recruitmentStore.activeCampaignId || '',
          resumeFile: resumeFile
        } as any) as Candidate | null;
        if (result && photoFile) await $uploadPhotoMutation.mutateAsync({ candidateId: result.id, file: photoFile });
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  const entity = $derived(candidate ? {
    lastName: candidate.lastName, middleName: candidate.middleName ?? '', firstName: candidate.firstName,
    email: candidate.email, phone: candidate.phone ?? '', linkedinUrl: candidate.linkedinUrl ?? '',
    gender: candidate.gender ?? 'NOT_SPECIFIED', source: candidate.source ?? 'DIRECT',
    location: candidate.location ?? '', experience: candidate.experience ?? '',
    skills: (candidate.skills ?? []).join(', '), summary: candidate.summary ?? '', notes: candidate.notes ?? ''
  } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={candidate ? 'Modifier le candidat' : 'Nouveau candidat'}
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
