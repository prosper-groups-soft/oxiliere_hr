<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { calendarStore } from "@/hr/modules/calendar/stores/calendar.svelte";
  import { TYPE_OPTIONS_SINGULAR, STATUS_OPTIONS, RECURRENCE_OPTIONS } from "@/hr/modules/calendar/constants/event.constants";
  import type { CalendarEvent, EventType } from "@/hr/modules/calendar/types/types";
  import {
    createForm, FormView,
    text, date, textarea, select, switchField,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";
  import ConfirmAction from "@/hr/components/shared/actions/ConfirmAction.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";

  let {
    open = $bindable(false),
    calendarEvent = $bindable(null),
    initialDate = null,
    initialEndDate = null
  } = $props<{
    open: boolean,
    calendarEvent?: CalendarEvent | null,
    initialDate?: string | null,
    initialEndDate?: string | null
  }>();

  let isDeleting = $state(false);

  const eventFields: FieldConfig[] = [
    text('title', {
      label: "Titre de l'événement",
      required: true,
      placeholder: "ex: Noël, Pont du 15 août...",
      validators: [validators.required("Le titre est requis")]
    }),
    select('type', {
      label: "Type d'événement",
      required: true,
      defaultValue: 'holiday',
      dataSource: { type: 'static', values: TYPE_OPTIONS_SINGULAR.map(o => ({ value: o.value, label: o.label })) }
    }),
    date('defaultDate', {
      out: 'defaultDate',
      label: "Date de début",
      required: true,
      validators: [validators.required("La date de début est requise")]
    }),
    date('endDate', { label: "Date de fin (Optionnel)", placeholder: "Optionnel" }),
    text('startTime', { label: "Heure de début", placeholder: "HH:MM" }),
    text('endTime', { label: "Heure de fin", placeholder: "HH:MM" }),
    select('status', {
      label: "Statut",
      defaultValue: 'APPROVED',
      dataSource: { type: 'static', values: STATUS_OPTIONS }
    }),
    select('recurrent', {
      label: "Récurrence",
      defaultValue: 'NONE',
      dataSource: { type: 'static', values: RECURRENCE_OPTIONS }
    }),
    switchField('isWorkable', { label: "Jour travaillé", defaultValue: true }),
    textarea('description', { label: "Notes ou Description", placeholder: "Détails supplémentaires…" })
  ];

  const form = createForm({
    id: 'calendar-event-form',
    fields: eventFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-lg' },
    layout: {
      type: 'section',
      sections: [
        { title: "Informations", fields: ['title', 'type'] },
        { title: "Période", fields: ['defaultDate', 'endDate', 'startTime', 'endTime'] },
        { title: "Paramètres", fields: ['status', 'recurrent', 'isWorkable'] },
        { title: "Description", fields: ['description'] }
      ]
    },
    onSubmit: async (data) => {
      const payload: Record<string, any> = {
        title: data.title,
        type: data.type,
        defaultDate: data.defaultDate,
        endDate: data.endDate || undefined,
        startTime: data.startTime || undefined,
        endTime: data.endTime || undefined,
        description: data.description || undefined,
        status: data.status !== 'APPROVED' ? data.status : undefined,
        recurrent: data.recurrent !== 'NONE' ? data.recurrent : undefined,
        isWorkable: data.isWorkable,
      };
      if (calendarEvent) {
        await calendarStore.updateEvent(calendarEvent.id, payload);
      } else {
        await calendarStore.addEvent(payload);
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });

  async function handleDelete() {
    if (!calendarEvent) return;
    try {
      await calendarStore.deleteEvent(calendarEvent.id);
      open = false;
    } catch {}
  }

  // Defaults for create mode (initialDate/initialEndDate)
  const eventEntity = $derived(
    calendarEvent ?? (initialDate ? { defaultDate: initialDate, endDate: initialEndDate ?? undefined, type: 'holiday' as EventType, isWorkable: true, status: 'APPROVED', recurrent: 'NONE' } as any : null)
  );
</script>

<FormView
  {form}
  fields={eventFields}
  bind:open
  entity={eventEntity}
  title={calendarEvent ? "Modifier l'événement" : "Nouvel événement"}
  submitLabel={calendarEvent ? "Modifier" : "Créer l'événement"}
  submitIcon="check"
  showReset={false}
  actions={[
    cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })
  ]}
>
  {#snippet extras()}
    {#if calendarEvent}
      <div class="pt-4 border-t border-red-100">
        <div class="flex items-center justify-between p-4 rounded-xl bg-red-50/50 border border-red-100">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg bg-red-100 text-red-500">
              <AppIcon name="trash-2" size={18} />
            </div>
            <div>
              <p class="text-[0.85rem] font-semibold text-red-800">Supprimer l'événement</p>
              <p class="text-[0.78rem] text-red-600/70">Cette action est irréversible.</p>
            </div>
          </div>
          <ConfirmAction
            isConfirming={isDeleting}
            onRequest={() => isDeleting = true}
            onConfirm={handleDelete}
            onCancel={() => isDeleting = false}
            labels={{ action: 'Supprimer', confirm: 'Confirmer', cancel: '' }}
            icons={{ action: 'trash', confirm: 'check', cancel: 'x' }}
            variant="danger"
          />
        </div>
      </div>
    {/if}
  {/snippet}
</FormView>
