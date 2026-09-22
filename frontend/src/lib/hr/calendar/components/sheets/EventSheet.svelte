<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import * as Select from "@/components/ui/select";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { calendarStore } from "@/hr/calendar/stores/calendar.svelte";
  import { TYPE_OPTIONS_SINGULAR, STATUS_OPTIONS, RECURRENCE_OPTIONS } from "@/hr/calendar/constants/event.constants";
  import type { CalendarEvent, EventType } from "@/hr/calendar/types/types";
  import { EVENT_TYPE_LABELS } from "@/hr/calendar/types/types";
  import { fade } from "svelte/transition";
  import ValidationError from "@/components/ui/validation-error";
  import { cn } from "@/utilities/common/css";
  import ConfirmAction from "@/components/shared/actions/ConfirmAction.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";

  
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

  // Form state
  let formTitle = $state('');
  let formType = $state<EventType>('holiday');
  let formDate = $state('');
  let formEndDate = $state('');
  let formStartTime = $state('');
  let formEndTime = $state('');
  let formDescription = $state('');
  let formStatus = $state('APPROVED');
  let formRecurrent = $state('NONE');
  let formIsWorkable = $state(true);
  let isSaving = $state(false);
  let eventCode = $state('');

  // Validation state
  let validationErrors = $state<Record<string, string>>({});
  let isDeleting = $state(false);

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};
    if (!formTitle.trim()) {
      validationErrors.title = 'Le titre est requis';
    }
    if (!formDate) {
      validationErrors.date = 'La date de début est requise';
    }
    return Object.keys(validationErrors).length === 0;
  }

  $effect(() => {
    if (open) {
      validationErrors = {};
      isDeleting = false;

      if (calendarEvent) {
        formTitle = calendarEvent.title || '';
        formType = calendarEvent.type || 'holiday' as EventType;
        formDate = calendarEvent.defaultDate || '';
        formEndDate = calendarEvent.endDate || '';
        formStartTime = calendarEvent.startTime || '';
        formEndTime = calendarEvent.endTime || '';
        formDescription = calendarEvent.description || '';
        formStatus = calendarEvent.status || 'APPROVED';
        formRecurrent = calendarEvent.recurrent || 'NONE';
        formIsWorkable = calendarEvent.isWorkable ?? true;
        eventCode = calendarEvent.code || '';
      } else {
        formTitle = '';
        formType = 'holiday' as EventType;
        formDate = initialDate || new Date().toISOString().split('T')[0];
        formEndDate = initialEndDate || '';
        formStartTime = '';
        formEndTime = '';
        formDescription = '';
        formStatus = 'APPROVED';
        formRecurrent = 'NONE';
        formIsWorkable = true;
        eventCode = '';
      }
    }
  });

  const typeOptions = TYPE_OPTIONS_SINGULAR;

  const statusOptions = STATUS_OPTIONS;

  const recurrenceOptions = RECURRENCE_OPTIONS;

  async function handleSave() {
    if (!validateForm()) return;

    isSaving = true;
    try {
      const data = {
        title: formTitle,
        type: formType,
        defaultDate: formDate,
        endDate: formEndDate || undefined,
        startTime: formStartTime || undefined,
        endTime: formEndTime || undefined,
        description: formDescription || undefined,
        status: formStatus !== 'APPROVED' ? formStatus : undefined,
        recurrent: formRecurrent !== 'NONE' ? formRecurrent : undefined,
        isWorkable: formIsWorkable,
      };

      if (calendarEvent) {
        await calendarStore.updateEvent(calendarEvent.id, data);
      } else {
        await calendarStore.addEvent(data);
      }
      open = false;
    } catch (error) {
      // Error toast already handled by service/store
    } finally {
      isSaving = false;
    }
  }

  async function handleDelete() {
    if (!calendarEvent) return;

    try {
      await calendarStore.deleteEvent(calendarEvent.id);
      open = false;
    } catch (error) {
      // Error toast already handled by service/store
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-lg bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center justify-between">
        <Sheet.Title class="text-[1rem] font-bold text-slate-900 truncate">
          {calendarEvent ? "Modifier l'événement" : 'Nouvel événement'}
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <div class="space-y-2">
          <Label for="event-title" class="text-slate-900">Titre de l'événement <span class="text-red-500">*</span></Label>
          <Input
            id="event-title"
            bind:value={formTitle}
            placeholder="ex: Noël, Pont du 15 août..."
            oninput={() => clearValidationError('title')}
            class={cn("h-10 shadow-fine", validationErrors.title && "border-red-500 focus:ring-red-500")}
          />
          <ValidationError errors={validationErrors} field="title" />
        </div>

        <div class="space-y-2">
          <Label class="text-slate-900">Type d'événement</Label>
          <Select.Root type="single" value={formType} onValueChange={(v) => formType = v as EventType}>
            <Select.Trigger class="h-10 w-full shadow-fine">
              <span class="truncate text-[0.85rem] font-medium">{EVENT_TYPE_LABELS[formType] || formType}</span>
            </Select.Trigger>
            <Select.Content class="z-9999">
              {#each typeOptions as option}
                <Select.SelectItem value={option.value} class="text-[0.85rem]">{option.label}</Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="event-start-date" class="text-slate-900">Date de début <span class="text-red-500">*</span></Label>
            <Input
              id="event-start-date"
              type="date"
              bind:value={formDate}
              oninput={() => clearValidationError('date')}
              class={cn("h-10 shadow-fine", validationErrors.date && "border-red-500 focus:ring-red-500")}
            />
            <ValidationError errors={validationErrors} field="date" />
          </div>
          <div class="space-y-2">
            <Label class="text-slate-900">Date de fin (Optionnel)</Label>
            <Input type="date" bind:value={formEndDate} class="h-10 shadow-fine" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-slate-900">Heure de début</Label>
            <Input type="time" bind:value={formStartTime} class="h-10 shadow-fine" />
          </div>
          <div class="space-y-2">
            <Label class="text-slate-900">Heure de fin</Label>
            <Input type="time" bind:value={formEndTime} class="h-10 shadow-fine" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-slate-900">Statut</Label>
            <Select.Root type="single" value={formStatus} onValueChange={(v) => formStatus = v}>
              <Select.Trigger class="h-10 w-full shadow-fine">
                <span class="truncate text-[0.85rem] font-medium">
                  {statusOptions.find(o => o.value === formStatus)?.label || formStatus}
                </span>
              </Select.Trigger>
              <Select.Content class="z-9999">
                {#each statusOptions as option}
                  <Select.SelectItem value={option.value} class="text-[0.85rem]">{option.label}</Select.SelectItem>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>
          <div class="space-y-2">
            <Label class="text-slate-900">Récurrence</Label>
            <Select.Root type="single" value={formRecurrent} onValueChange={(v) => formRecurrent = v}>
              <Select.Trigger class="h-10 w-full shadow-fine">
                <span class="truncate text-[0.85rem] font-medium">
                  {recurrenceOptions.find(o => o.value === formRecurrent)?.label || formRecurrent}
                </span>
              </Select.Trigger>
              <Select.Content class="z-9999">
                {#each recurrenceOptions as option}
                  <Select.SelectItem value={option.value} class="text-[0.85rem]">{option.label}</Select.SelectItem>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>
        </div>

        <div class="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 border border-slate-200">
          <div class="flex items-center gap-2">
            <AppIcon name="briefcase" size={16} class="text-slate-500" />
            <Label class="text-slate-700 font-medium text-[0.85rem] cursor-pointer" for="is-workable">Jour travaillé</Label>
          </div>
          <Switch id="is-workable" bind:checked={formIsWorkable} class="cursor-pointer" />
        </div>

        <div class="space-y-2">
          <Label class="text-slate-900">Notes ou Description</Label>
          <Textarea 
            bind:value={formDescription} 
            placeholder="Détails supplémentaires..." 
            class="min-h-32 shadow-fine text-[0.85rem]"
          />
        </div>

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
      </div>
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium">
            <AppIcon name="x" size={18} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={handleSave} 
          disabled={isSaving}
          class="flex-1 bg-primary text-white h-9 shadow-fine hover:bg-primary/90 transition-all font-medium gap-2"
        >
          {#if isSaving}
            <AnimateSpin class="border-white size-3" text="" />
          {:else}
            <AppIcon name="check" size={18} />
          {/if}
          {calendarEvent ? 'Modifier' : "Créer l'événement"}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




