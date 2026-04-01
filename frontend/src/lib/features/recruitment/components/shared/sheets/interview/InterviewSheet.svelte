<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger
  } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Candidate, InterviewType, Interview } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";
  import { format } from "date-fns";

  let {
    open = $bindable(false),
    candidate = null,
    interview = null,
    onSuccess = null
  } = $props<{
    open: boolean,
    candidate?: Candidate | null | undefined,
    interview?: Interview | null,
    onSuccess?: () => void
  }>();

  // Form state
  let formType = $state<InterviewType>('VIDEO');
  let formDate = $state('');
  let formTime = $state('');
  let formDuration = $state(60);
  let formInterviewerId = $state('');
  let formLocation = $state('');
  let formDescription = $state('');

  $effect(() => {
    if (open) {
      if (interview) {
        formType = interview.type;
        const date = new Date(interview.scheduledDate);
        formDate = date.toISOString().split('T')[0];
        formTime = format(date, 'HH:mm');
        formDuration = interview.duration || 60;
        formInterviewerId = interview.interviewerId || '';
        formLocation = interview.location || '';
        formDescription = interview.description || '';
      } else {
        // Default to tomorrow 10:00 AM
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        formDate = tomorrow.toISOString().split('T')[0];
        formTime = "10:00";
        
        formType = 'VIDEO';
        formDuration = 60;
        formInterviewerId = '';
        formLocation = '';
        formDescription = '';
      }
    }
  });

  const interviewTypes: { value: InterviewType, label: string, icon: string, color: string }[] = [
    { value: 'PHONE', label: 'Téléphonique', icon: 'phone', color: 'text-blue-500' },
    { value: 'VIDEO', label: 'Vidéoconférence', icon: 'video', color: 'text-purple-500' },
    { value: 'ONSITE', label: 'Sur site', icon: 'map-pin', color: 'text-emerald-500' },
    { value: 'TECHNICAL', label: 'Technique', icon: 'code', color: 'text-amber-500' },
    { value: 'BEHAVIORAL', label: 'Comportemental', icon: 'users', color: 'text-indigo-500' }
  ];

  async function handleSave() {
    if (!candidate && !interview) return;
    if (!formDate || !formTime || !formInterviewerId) {
      notification.toast.error('Veuillez remplir les champs obligatoires');
      return;
    }

    try {
      const scheduledDate = `${formDate}T${formTime}:00`;
      const data = {
        candidateId: candidate?.id || interview!.candidateId,
        interviewerId: formInterviewerId,
        type: formType,
        scheduledDate,
        duration: formDuration,
        location: formLocation,
        description: formDescription
      };
      
      if (interview) {
        await recruitmentStore.updateInterview(interview.id, data);
        notification.toast.success('Entretien mis à jour');
      } else {
        await recruitmentStore.scheduleInterview(data);
        notification.toast.success('Entretien programmé avec succès');
      }

      open = false;
      onSuccess?.();
    } catch (error) {
      notification.toast.error("Erreur lors de l'enregistrement");
    }
  }

  const selectedTypeCfg = $derived(interviewTypes.find(t => t.value === formType) || interviewTypes[1]);
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <AppIcon name="calendar" size={20} />
        </div>
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
            {interview ? 'Modifier l\'entretien' : 'Programmer un entretien'}
          </Sheet.Title>
          <Sheet.Description class="text-[0.78rem] text-slate-500 truncate">
            {candidate ? `${candidate.firstName} ${candidate.lastName}` : interview ? `Entretien #${interview.id.slice(0, 8)}` : 'Chargement...'}
          </Sheet.Description>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <!-- Type d'entretien -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Type d'entretien <span class="text-red-500">*</span></Label>
          <Select type="single" value={formType} onValueChange={(v) => formType = v as any}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none!">
              <span class="truncate text-[0.85rem]! font-medium flex items-center gap-2">
                <AppIcon name={selectedTypeCfg.icon} size={17} class={selectedTypeCfg.color} />
                {selectedTypeCfg.label}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              {#each interviewTypes as type}
                <SelectItem value={type.value}>
                  <div class="flex items-center gap-2 text-[0.85rem]!">
                    <AppIcon name={type.icon} size={17} class={type.color} />
                    {type.label}
                  </div>
                </SelectItem>
              {/each}
            </SelectContent>
          </Select>
        </div>

        <!-- Date et Heure -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Date <span class="text-red-500">*</span></Label>
            <Input type="date" bind:value={formDate} class="h-10 border-slate-200 shadow-fine" />
          </div>
          <div class="space-y-2.5">
            <Label class="text-slate-900">Heure <span class="text-red-500">*</span></Label>
            <Input type="time" bind:value={formTime} class="h-10 border-slate-200 shadow-fine" />
          </div>
        </div>

        <!-- Durée -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Durée (minutes)</Label>
          <Select type="single" value={formDuration.toString()} onValueChange={(v) => formDuration = parseInt(v)}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none!">
              <span class="truncate text-[0.85rem] font-medium">{formDuration} minutes</span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              <SelectItem value="15" class="text-[0.85rem]">15 minutes</SelectItem>
              <SelectItem value="30" class="text-[0.85rem]">30 minutes</SelectItem>
              <SelectItem value="45" class="text-[0.85rem]">45 minutes</SelectItem>
              <SelectItem value="60" class="text-[0.85rem]">60 minutes</SelectItem>
              <SelectItem value="90" class="text-[0.85rem]">90 minutes</SelectItem>
              <SelectItem value="120" class="text-[0.85rem]">120 minutes</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Interviewer -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Interviewer <span class="text-red-500">*</span></Label>
          <Select type="single" value={formInterviewerId} onValueChange={(v) => formInterviewerId = v}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none!">
              <span class="truncate text-[0.85rem] font-medium">
                {formInterviewerId ? 'Interviewer sélectionné' : 'Sélectionner un interviewer...'}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              <SelectItem value="e1" class="text-[0.85rem]">Jean Dupont</SelectItem>
              <SelectItem value="e2" class="text-[0.85rem]">Marie Martin</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <!-- Lieu / Lien -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">{formType === 'ONSITE' ? 'Lieu' : 'Lien de réunion (Google Meet, Zoom, etc.)'}</Label>
          <Input 
            type="text" 
            bind:value={formLocation} 
            placeholder={formType === 'ONSITE' ? 'Salle de réunion 2' : 'https://meet.google.com/...'} 
            class="h-10 border-slate-200 shadow-fine"
          />
        </div>

        <!-- Description -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Notes / Description</Label>
          <Textarea 
            bind:value={formDescription} 
            placeholder="Détails sur l'entretien..." 
            class="min-h-20 border-slate-200 shadow-fine text-[0.85rem]"
          />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-primary text-white h-9 shadow-fine text-[0.88rem] hover:bg-primary/90 transition-all"
        >
          <AppIcon name="check" size={18} />
          {interview ? 'Mettre à jour' : 'Programmer'}
        </Button>
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 text-[0.88rem]">
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
