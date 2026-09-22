<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { accessStore } from "../../../stores/accessStore.svelte";
  import {
    createForm, FormView,
    text, email, password, switchField, select,
    validators, cancel, invariant
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open, onOpenChange, onSubmit }: {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSubmit: (data: any) => void;
  } = $props();

  let innerOpen = $derived(open);

  const userFields: FieldConfig[] = [
    email('email', {
      label: 'Email',
      required: true,
      placeholder: 'jean.mukendi@oxiliere.com',
      validators: [validators.required("L'email est requis"), validators.email("Email invalide")]
    }),
    text('firstName', {
      out: 'first_name',
      label: 'Prénom',
      required: true,
      placeholder: 'Jean',
      validators: [validators.required('Le prénom est requis')]
    }),
    text('lastName', {
      out: 'last_name',
      label: 'Nom',
      required: true,
      placeholder: 'Mukendi',
      validators: [validators.required('Le nom est requis')]
    }),
    password('password', {
      label: 'Mot de passe',
      required: true,
      placeholder: '••••••••',
      validators: [validators.required('Le mot de passe est requis'), validators.minLength(8, 'Au moins 8 caractères')]
    }),
    password('confirmPassword', {
      label: 'Confirmer le mot de passe',
      required: true,
      placeholder: '••••••••',
      validators: [validators.required('La confirmation est requise')]
    }),
    switchField('isActive', { out: 'is_active', label: 'Compte actif', defaultValue: true }),
    switchField('isAdmin', { out: 'is_admin', label: 'Administrateur', help: "Accès complet à l'administration", defaultValue: false }),
    switchField('isOwner', { out: 'is_owner', label: 'Propriétaire', help: 'Contrôle total du système', defaultValue: false }),
    select('groups', {
      label: 'Groupes',
      placeholder: 'Sélectionner des groupes...',
      dataSource: { type: 'static', values: [] },
      behaviors: [{ type: 'multiSelect' }]
    })
  ];

  const form = createForm({
    id: 'access-user-create-form',
    fields: userFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-md' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Informations', fields: ['email', 'firstName', 'lastName'] },
        { title: 'Mot de passe', fields: ['password', 'confirmPassword'] },
        { title: 'Statut', fields: ['isActive'] },
        { title: 'Permissions', fields: ['isAdmin', 'isOwner'] },
        { title: 'Groupes', fields: ['groups'] }
      ]
    },
    validators: [
      invariant((values) => {
        if (values.password !== values.confirmPassword) return { valid: false, field: 'confirmPassword' };
        return { valid: true };
      }, 'Les mots de passe ne correspondent pas')
    ],
    onSubmit: async (data) => {
      await onSubmit({
        email: data.email,
        first_name: data.first_name,
        last_name: data.last_name,
        password: data.password,
        is_active: data.is_active,
        is_admin: data.is_admin,
        is_owner: data.is_owner,
        groups: data.groups ?? []
      });
      onOpenChange(false);
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });

  // Sync group options from store
  $effect(() => {
    const groups = accessStore.groups;
    const field = form.getField('groups');
    // update dataSource dynamically via setConfig fallback — recreate if needed
    if (field && groups) {
      // @ts-ignore — patch dataSource for static select
      form.setConfig({ fields: userFields.map(f => f.id === 'groups' ? { ...f, dataSource: { type: 'static', values: groups.map((g: any) => ({ value: g.slug, label: g.name })) } } : f) as any });
    }
  });

  function handleOpenChange(v: boolean) {
    onOpenChange(v);
    if (!v) form.reset();
  }
</script>

<FormView
  {form}
  fields={userFields}
  open={innerOpen}
  onOpenChange={handleOpenChange}
  title="Nouvel utilisateur"
  submitLabel="Créer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => onOpenChange(false) })]}
/>
