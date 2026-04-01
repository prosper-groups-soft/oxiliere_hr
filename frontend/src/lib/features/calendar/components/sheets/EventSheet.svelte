<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import * as Select from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { 
    CalendarEvent, 
    EventType 
  } from "@/features/calendar/types/types";
  import { fade } from "svelte/transition";

  import { calendarStore } from "@/features/calendar/stores/calendar.svelte";

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
  let formDescription = $state('');

  $effect(() => {
    if (open) {
      if (calendarEvent) {
        formTitle = calendarEvent.title || '';
        formType = calendarEvent.type || 'holiday' as EventType;
        formDate = calendarEvent.defaultDate || '';
        formEndDate = calendarEvent.endDate || '';
        formDescription = ''; 
      } else {
        formTitle = '';
        formType = 'holiday' as EventType;
        formDate = initialDate || new Date().toISOString().split('T')[0];
        formEndDate = initialEndDate || '';
        formDescription = '';
      }
    }
  });

  const typeLabels: Record<EventType, string> = {
    'holiday': 'Jour Férié',
    'closure': 'Fermeture Entreprise',
    'training': 'Formation'
  };

  async function handleSave() {
    if (!formTitle || !formDate) {
      notification.toast.error('Veuillez remplir les informations obligatoires (Titre et Date)');
      return;
    }

    try {
      const data = {
        title: formTitle,
        type: formType,
        defaultDate: formDate,
        endDate: formEndDate || undefined,
      };

      if (calendarEvent) {
        calendarStore.updateEvent(calendarEvent.id, data);
        notification.toast.success('Événement mis à jour avec succès');
      } else {
        calendarStore.addEvent(data);
        notification.toast.success('Événement créé avec succès');
      }
      open = false;
    } catch (error) {
      notification.toast.error('Erreur lors de l\'enregistrement');
    }
  }

  function handleDelete() {
    if (calendarEvent && confirm('Êtes-vous sûr de vouloir supprimer cet événement ?')) {
      calendarStore.deleteEvent(calendarEvent.id);
      notification.toast.success('Événement supprimé');
      open = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <div class="h-10 w-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <AppIcon name="calendar" size={20} />
          </div>
          <Sheet.Title class="text-[1rem] font-bold text-slate-900 truncate">
            {calendarEvent ? 'Modifier l\'événement' : 'Nouvel événement'}
          </Sheet.Title>
        </div>

        {#if calendarEvent}
          <Button 
            variant="ghost" 
            size="icon" 
            class="h-9 w-9 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg"
            onclick={handleDelete}
          >
            <AppIcon name="trash" size={18} />
          </Button>
        {/if}
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <div class="space-y-2">
          <Label class="text-slate-900">Titre de l'événement <span class="text-red-500">*</span></Label>
          <Input bind:value={formTitle} placeholder="ex: Noël, Pont du 15 août..." class="h-10 shadow-fine" />
        </div>

        <div class="space-y-2">
          <Label class="text-slate-900">Type d'événement</Label>
          <Select.Root type="single" value={formType} onValueChange={(v) => formType = v as any}>
            <Select.Trigger class="h-10 w-full shadow-fine">
              <span class="truncate text-[0.85rem] font-medium">{typeLabels[formType] || formType}</span>
            </Select.Trigger>
            <Select.Content class="z-9999">
              <Select.SelectItem value="holiday" class="text-[0.85rem]">Jour Férié</Select.SelectItem>
              <Select.SelectItem value="closure" class="text-[0.85rem]">Fermeture Entreprise</Select.SelectItem>
              <Select.SelectItem value="training" class="text-[0.85rem]">Formation</Select.SelectItem>
            </Select.Content>
          </Select.Root>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-slate-900">Date de début <span class="text-red-500">*</span></Label>
            <Input type="date" bind:value={formDate} class="h-10 shadow-fine" />
          </div>
          <div class="space-y-2">
            <Label class="text-slate-900">Date de fin (Optionnel)</Label>
            <Input type="date" bind:value={formEndDate} class="h-10 shadow-fine" />
          </div>
        </div>

        <div class="space-y-2">
          <Label class="text-slate-900">Notes ou Description</Label>
          <Textarea 
            bind:value={formDescription} 
            placeholder="Détails supplémentaires..." 
            class="min-h-32 shadow-fine text-[0.85rem]"
          />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-primary text-white h-9 shadow-fine hover:bg-primary/90 transition-all font-medium"
        >
          <AppIcon name="check" size={18} />
          {calendarEvent ? 'Enregistrer les modifications' : 'Créer l\'événement'}
        </Button>
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium">
            Annuler
          </Button>
        </Sheet.Close>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>

