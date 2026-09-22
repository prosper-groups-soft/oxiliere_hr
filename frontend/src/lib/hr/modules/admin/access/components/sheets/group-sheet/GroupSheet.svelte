<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import type { Group } from "../../../types/access.types";
  import { useRolesQuery, useCreateGroupMutation, useUpdateGroupMutation } from "../../../queries/accessQueries.svelte";
  import {
    createForm, FormView,
    text, select,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), group }: { open: boolean; group?: Group | null } = $props();

  const rolesQuery = useRolesQuery();
  let roles = $derived($rolesQuery.data ?? []);
  const createMutation = useCreateGroupMutation();
  const updateMutation = useUpdateGroupMutation();
  const isEdit = $derived(!!group);

  const fields: FieldConfig[] = [
    text('name', { label: 'Nom du groupe', required: true, placeholder: 'ex: Managers RH', validators: [validators.required('Le nom est requis')] }),
    text('slug', {
      label: 'Identifiant (Slug)',
      required: true,
      placeholder: 'ex: hr_managers',
      disabled: isEdit,
      validators: [validators.required("L'identifiant est requis"), validators.regex(/^[a-z0-9_]+$/, 'Slug invalide (a-z, 0-9, _)')]
    }),
    select('roles', {
      label: 'Rôles assignés',
      placeholder: 'Sélectionner des rôles...',
      behaviors: [{ type: 'multiSelect' }]
    })
  ];

  const form = createForm({
    id: 'group-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-lg' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Groupe', fields: ['name', 'slug'] },
        { title: 'Rôles', fields: ['roles'] }
      ]
    },
    onSubmit: async (data) => {
      const rolesArr: string[] = Array.isArray(data.roles) ? data.roles : (data.roles ? [data.roles] : []);
      if (isEdit && group) {
        await $updateMutation.mutateAsync({ slug: group.slug, data: { name: data.name, roles: rolesArr } });
        notification.toast.success("Groupe mis à jour avec succès.");
      } else {
        await $createMutation.mutateAsync({ name: data.name, slug: data.slug, roles: rolesArr });
        notification.toast.success("Groupe créé avec succès.");
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    const opts = roles.map((r: any) => ({ value: r.slug, label: r.name }));
    form.setConfig({ fields: fields.map(f => f.id === 'roles' ? { ...f, dataSource: { type: 'static', values: opts } } : f) as any });
  });

  const entity = $derived(group ? { name: group.name, slug: group.slug, roles: (group.roles ?? []).map((r: any) => r.slug) } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={isEdit ? 'Gérer le groupe' : 'Nouveau groupe'}
  submitLabel={isEdit ? 'Enregistrer' : 'Créer le groupe'}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
