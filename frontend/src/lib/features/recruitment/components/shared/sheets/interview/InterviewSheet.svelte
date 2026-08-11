<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { useScheduleInterviewMutation, useUpdateInterviewMutation } from "@/features/recruitment/queries/recruitmentQueries";
  import type { Candidate, InterviewType, Interview, InterviewStatus, CreateInterviewInput } from "@/features/recruitment/types/types";
  import { INTERVIEW_TYPE_CONFIG, INTERVIEW_STATUS_CONFIG } from "@/features/recruitment/constants/recruitment";
  import { fade } from "svelte/transition";
  import { format } from "date-fns";
  import { cn } from "@/utilities/common/css";
  import { useAllEmployees } from "@/features/employees/queries/employeeQueries";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

  
  let {
    open = $bindable(false),
    candidate = null,
    interview = null,
    onSuccess = null,
    applicationId = ''
  } = $props<{
    open: boolean,
    candidate?: Candidate | null | undefined,
    interview?: Interview | null,
    onSuccess?: () => void,
    applicationId?: string
  }>();

  // Fetch all employees for interviewer selection
  const employeesQuery = useAllEmployees();
  let allEmployees = $derived($employeesQuery.data || []);

  // Mutation hooks
  const scheduleInterviewMutation = useScheduleInterviewMutation();
  const updateInterviewMutation = useUpdateInterviewMutation();

  // Map employees to a { value, label, employee } list for the select
  let interviewerOptions = $derived(
    allEmployees.map((emp) => ({
      value: String(emp.id),
      label: emp.name,
      employee: emp
    }))
  );

  // Form state
  let formApplicationId = $state('');
  let formType = $state<InterviewType>('VIDEO');
  let formDate = $state('');
  let formTime = $state('');
  let formDuration = $state(60);
  let formInterviewerId = $state('');
  let formLocation = $state('');
  let formDescription = $state('');
  let formStatus = $state<InterviewStatus>('SCHEDULED');

  let isSaving = $state(false);

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
        formStatus = interview.status || 'SCHEDULED';
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
        formApplicationId = '';

        // Auto-select application: prefer prop, else single-app
        if (applicationId) {
          formApplicationId = applicationId;
        } else if (candidate?.applications && candidate.applications.length === 1) {
          const app = candidate.applications[0] as any;
          formApplicationId = app.id || app.applicationId || '';
        }
      }
    }
  });

  async function handleSave() {
    if (!candidate && !interview) return;
    if (!formDate || !formTime || !formInterviewerId) {
      notification.toast.error('Veuillez remplir les champs obligatoires');
      return;
    }
    if (!interview && !formApplicationId && candidate?.applications && candidate.applications.length > 0) {
      notification.toast.error('Veuillez sélectionner le poste concerné');
      return;
    }

    isSaving = true;
    try {
      const scheduledDate = `${formDate}T${formTime}:00`;
      
      if (interview) {
        await $updateInterviewMutation.mutateAsync({
          interviewId: interview.id,
          data: {
            interviewerId: formInterviewerId,
            type: formType,
            scheduledDate,
            duration: formDuration,
            location: formLocation,
            description: formDescription,
            status: formStatus
          }
        });
      } else {
        await $scheduleInterviewMutation.mutateAsync({
          applicationId: formApplicationId,
          interviewerId: formInterviewerId,
          type: formType,
          scheduledDate,
          duration: formDuration,
          location: formLocation,
          description: formDescription
        } as CreateInterviewInput);
      }

      onSuccess?.();
      open = false;
    } catch (error) {
      console.error("Erreur lors de l'enregistrement:", error);
    } finally {
      isSaving = false;
    }
  }

  const selectedApplicationName = $derived(
    candidate?.applications?.find(
      (a: any) => a.id === formApplicationId || a.applicationId === formApplicationId
    ) as any
  );

  const selectedTypeCfg = $derived(
    INTERVIEW_TYPE_CONFIG[formType] || INTERVIEW_TYPE_CONFIG['VIDEO']
  );

  const selectedInterviewer = $derived(
    interviewerOptions.find(o => o.value === formInterviewerId) || null
  );

  const interviewerPalette = $derived(
    selectedInterviewer
      ? getAvatarPalette(selectedInterviewer.label)
      : { bg: '', text: '' }
  );

  const interviewerPhoto = $derived(
    getMediaUrl(selectedInterviewer?.employee.profile_photo || selectedInterviewer?.employee.avatarUrl || '')
  );
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
            {interview ? "Modifier l'entretien" : 'Programmer un entretien'}
          </Sheet.Title>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <!-- Application (create mode only) -->
        {#if !interview && candidate?.applications && candidate.applications.length > 0}
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-semibold">
              Poste concerné <span class="text-red-400">*</span>
            </Label>
            <Select type="single" value={formApplicationId} onValueChange={(v) => formApplicationId = v}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none! cursor-pointer">
                <span class="truncate text-[0.85rem]! font-medium flex items-center gap-2">
                  {#if formApplicationId}
                    <AppIcon name="briefcase" size={17} class="text-indigo-500" />
                    {selectedApplicationName?.target_position_name || selectedApplicationName?.targetPositionName || 'Poste sélectionné'}
                  {:else}
                    <AppIcon name="circle-help" size={17} class="text-amber-400" />
                    Sélectionner le poste...
                  {/if}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each candidate.applications as app}
                  <SelectItem value={(app as any).id || (app as any).applicationId}>
                    <div class="flex items-center gap-2.5 text-[0.85rem]!">
                      <AppIcon name="briefcase" size={17} class="text-slate-400" />
                      <span class="truncate font-medium text-sm">
                        {(app as any).target_position_name || (app as any).targetPositionName || 'Poste sans titre'}
                      </span>
                    </div>
                  </SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>
        {/if}

        <!-- Status (edit mode only) -->
        {#if interview}
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-semibold">Statut</Label>
            <Select type="single" value={formStatus} onValueChange={(v) => formStatus = v as InterviewStatus}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none! cursor-pointer">
                <span class="truncate text-[0.85rem] font-medium flex items-center gap-2">
                  <AppIcon name={INTERVIEW_STATUS_CONFIG[formStatus]?.icon || 'info'} size={17} class={INTERVIEW_STATUS_CONFIG[formStatus]?.color || 'text-slate-400'} />
                  {INTERVIEW_STATUS_CONFIG[formStatus]?.label || formStatus}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each Object.entries(INTERVIEW_STATUS_CONFIG) as [value, cfg]}
                  <SelectItem value={value}>
                    <div class="flex items-center gap-2 text-[0.85rem]!">
                      <AppIcon name={cfg.icon} size={17} class={cfg.color} />
                      {cfg.label}
                    </div>
                  </SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>
        {/if}
        
        <!-- Type d'entretien -->
        <div class="space-y-2.5">
          <Label class="text-slate-900 font-semibold">
            Type d'entretien <span class="text-red-400">*</span>
          </Label>
          <Select type="single" value={formType} onValueChange={(v) => { formType = v as any; formLocation = ''; }}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none! cursor-pointer">
              <span class="truncate text-[0.85rem]! font-medium flex items-center gap-2">
                <AppIcon name={selectedTypeCfg.icon} size={17} class={selectedTypeCfg.color} />
                {selectedTypeCfg.label}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              {#each Object.entries(INTERVIEW_TYPE_CONFIG) as [value, cfg]}
                <SelectItem value={value}>
                  <div class="flex items-center gap-2 text-[0.85rem]!">
                    <AppIcon name={cfg.icon} size={17} class={cfg.color} />
                    {cfg.label}
                  </div>
                </SelectItem>
              {/each}
            </SelectContent>
          </Select>
        </div>
        
        <!-- Lieu / Lien / Téléphone -->
        <div class="space-y-2.5">
          <Label class="text-slate-900 font-semibold">
            {#if formType === 'ONSITE'}
              Lieu
            {:else if formType === 'PHONE'}
              Numéro de téléphone
            {:else}
              Lien de réunion
            {/if}
          </Label>
          <Input 
            type="text" 
            bind:value={formLocation} 
            placeholder={formType === 'ONSITE' ? 'Salle de réunion 2, Bâtiment A...' : formType === 'PHONE' ? '+243 ...' : 'https://meet.google.com/...'} 
            class="h-10 border-slate-200 shadow-fine"
          />
        </div>

        <!-- Date et Heure -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-semibold">
              Date <span class="text-red-400">*</span>
            </Label>
            <Input type="date" bind:value={formDate} class="h-10 border-slate-200 shadow-fine" />
          </div>
          <div class="space-y-2.5">
            <Label class="text-slate-900 font-semibold">
              Heure <span class="text-red-400">*</span>
            </Label>
            <Input type="time" bind:value={formTime} class="h-10 border-slate-200 shadow-fine" />
          </div>
        </div>

        <!-- Durée -->
        <div class="space-y-2.5">
          <Label class="text-slate-900 font-semibold">Durée (minutes)</Label>
          <Select type="single" value={formDuration.toString()} onValueChange={(v) => formDuration = parseInt(v)}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none! cursor-pointer">
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
          <Label class="text-slate-900 font-semibold">
            Interviewer <span class="text-red-400">*</span>
          </Label>
          <Select type="single" value={formInterviewerId} onValueChange={(v) => formInterviewerId = v}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md outline-none! cursor-pointer">
              {#if selectedInterviewer}
                <span class="truncate text-[0.85rem]! font-medium flex items-center gap-2">
                  <Avatar class="h-8 w-8 rounded-full border border-slate-200 shrink-0">
                    <AvatarImage src={interviewerPhoto} alt={selectedInterviewer.label} class="object-cover" />
                    <AvatarFallback class={cn("text-[0.65rem] font-bold", interviewerPalette.bg, interviewerPalette.text)}>
                      {getInitials(
                        selectedInterviewer.employee.last_name || '',
                        selectedInterviewer.employee.middle_name || '',
                        selectedInterviewer.employee.first_name || ''
                      )}
                    </AvatarFallback>
                  </Avatar>
                  {selectedInterviewer.label}
                </span>
              {:else}
                <span class="truncate text-[0.85rem]! font-medium text-slate-400 flex items-center gap-2">
                  <AppIcon name="user" size={17} class="text-slate-300" />
                  Sélectionner un interviewer...
                </span>
              {/if}
            </SelectTrigger>
            <SelectContent class="z-9999 max-h-64 overflow-y-auto">
              {#if $employeesQuery.isLoading}
                <div class="flex items-center justify-center py-4 text-slate-400 text-[0.85rem]">
                  <AnimateSpin textPosition="right" text="Chargement des employés" class="size-3" />
                </div>
              {:else if interviewerOptions.length === 0}
                <div class="px-3 py-4 text-slate-400 text-[0.82rem] text-center flex items-center justify-center gap-1">
                  <AppIcon name="circle-x" size={17} class="text-slate-300" />
                  Aucun employé trouvé
                </div>
              {:else}
                {#each interviewerOptions as opt}
                  <SelectItem value={opt.value} class="cursor-pointer">
                    <div class="flex items-center gap-2.5 text-[0.85rem]!">
                      <div class="flex flex-col min-w-0">
                        <span class="truncate font-medium text-[0.875rem]">{opt.label}</span>
                        <span class="text-[0.85rem] text-slate-400 truncate">{opt.employee.jobTitle || ''}</span>
                      </div>
                    </div>
                  </SelectItem>
                {/each}
              {/if}
            </SelectContent>
          </Select>
        </div>

        <!-- Description -->
        <div class="space-y-2.5">
          <Label class="text-slate-900 font-semibold">Notes / Description</Label>
          <Textarea 
            bind:value={formDescription} 
            placeholder="Détails sur l'entretien, questions à poser, contexte du candidat..."
            class="min-h-24 border-slate-200 shadow-fine text-[0.85rem]"
          />
        </div>

      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={18} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={handleSave} 
          disabled={isSaving}
          class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-70"
        >
          {#if isSaving}
            <AnimateSpin text="" class="size-3 border-white" />
          {:else}
            <AppIcon name="check" size={18} />
          {/if}
          {interview ? 'Mettre à jour' : 'Programmer'}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>



