<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import ValidationError from "@/components/ui/validation-error";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import { Switch } from "@/components/ui/switch";
  import PhoneInput from "@/components/ui/phone-input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Candidate, CandidateSource, CreateCandidateInput, GenderStatus } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";
  import { useCreateCandidateMutation, useUpdateCandidateMutation, useUploadCandidatePhotoMutation, useUploadCandidateResumeMutation } from "@/features/recruitment/queries/recruitmentQueries";
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import { getMediaUrl } from "@/utilities/common/media";
  import { cn } from '@/utilities/common/css';
  import { CANDIDATE_SOURCE_OPTIONS, CANDIDATE_PRIORITY_LABELS, CANDIDATE_PRIORITY_OPTIONS, CANDIDATE_GENDER_OPTIONS, CANDIDATE_GENDER_LABELS } from '@/features/recruitment/constants/recruitment';


  let {
    open = $bindable(false),
    candidate = $bindable(null),
    campaignId = null
  } = $props<{
    open: boolean,
    candidate?: Candidate | null,
    campaignId?: string | null
  }>();

  // Form state
  let formFirstName = $state('');
  let formLastName = $state('');
  let formMiddleName = $state('');
  let formEmail = $state('');
  let formPhone = $state('');
  let formLinkedin = $state('');
  let formGender = $state<GenderStatus>('NOT_SPECIFIED');
  let formSource = $state<CandidateSource>('DIRECT');
  let formLocation = $state('');
  let formPosition = $state('');
  let formExperience = $state('');
  let formNotes = $state('');
  let formSummary = $state('');
  let formSkills = $state<string[]>([]);
  let formSkillsInput = $state(''); // pour l'input de saisie
  let formPhoto = $state<File | null>(null);
  let formPhotoPreview = $state('');
  let formResume = $state<File | null>(null);
  let formResumeName = $state('');

  // Multi-position selection
  let formPositionIds = $state<string[]>([]);
  let formPositionPriorities = $state<Record<string, 'LOW' | 'MEDIUM' | 'HIGH'>>({});

  // Mutations
  const createMutation = useCreateCandidateMutation();
  const updateMutation = useUpdateCandidateMutation();
  const uploadPhotoMutation = useUploadCandidatePhotoMutation();
  const uploadResumeMutation = useUploadCandidateResumeMutation();

  let isSaving = $state(false);
  let formErrors = $state<Record<string, string>>({});

  // Reset form when opening
  $effect(() => {
    if (open) {
      if (candidate) {
        formFirstName = candidate.firstName;
        formLastName = candidate.lastName;
        formMiddleName = candidate.middleName || '';
        formEmail = candidate.email;
        formPhone = candidate.phone;
        formLinkedin = candidate.linkedinUrl || '';
        formGender = candidate.gender || 'NOT_SPECIFIED';
        formSource = candidate.source;
        formLocation = candidate.location || '';
        formPosition = candidate.position || '';
        formExperience = candidate.experience || '';
        formNotes = candidate.notes || '';
        formSummary = candidate.summary || '';
        formSkills = candidate.skills || [];
        formPhotoPreview = getMediaUrl(candidate.avatarUrl || '') || '';
        formPhoto = null;
        formResume = null;
        formResumeName = '';
        // Restaurer les postes et leurs priorités depuis les applications groupées
        if (candidate.applications && candidate.applications.length > 0) {
          formPositionIds = candidate.applications.map((a: any) => a.positionId).filter(Boolean) as string[];
          const priorities: Record<string, 'LOW' | 'MEDIUM' | 'HIGH'> = {};
          for (const app of candidate.applications) {
            if (app.positionId) {
              priorities[app.positionId] = app.priority;
            }
          }
          formPositionPriorities = priorities;
        } else {
          formPositionIds = candidate.positionId ? [candidate.positionId] : [];
          formPositionPriorities = {};
        }
      } else {
        formFirstName = '';
        formLastName = '';
        formMiddleName = '';
        formEmail = '';
        formPhone = '';
        formLinkedin = '';
        formGender = 'NOT_SPECIFIED';
        formSource = 'DIRECT';
        formLocation = '';
        formPosition = '';
        formExperience = '';
        formNotes = '';
        formSummary = '';
        formSkills = [];
        formPhotoPreview = '';
        formPhoto = null;
        formResume = null;
        formResumeName = '';
        formPositionIds = [];
        formPositionPriorities = {};
      }
      formErrors = {};
    }
  });

  function togglePosition(positionId: string) {
    if (formPositionIds.includes(positionId)) {
      formPositionIds = formPositionIds.filter(id => id !== positionId);
      // Nettoyer la priorité associée
      const { [positionId]: _unused, ...rest } = formPositionPriorities;
      formPositionPriorities = rest;
    } else {
      formPositionIds = [...formPositionIds, positionId];
      // Priorité par défaut : MEDIUM
      formPositionPriorities = { ...formPositionPriorities, [positionId]: 'MEDIUM' };
    }
  }

  function handleAddSkill() {
    const trimmed = formSkillsInput.trim();
    if (trimmed && !formSkills.includes(trimmed)) {
      formSkills = [...formSkills, trimmed];
    }
    formSkillsInput = '';
  }

  function handleRemoveSkill(skill: string) {
    formSkills = formSkills.filter(s => s !== skill);
  }

  async function handleSave() {
    if (!formFirstName || !formLastName || !formEmail) {
      notification.toast.error('Veuillez remplir les informations de base');
      return;
    }

    // Reset form errors on each save attempt
    formErrors = {};

    try {
      isSaving = true;

      if (candidate) {
        // 1. Update profile + positions + priorities in one call
        const activeCampaignId = campaignId || recruitmentStore.activeCampaignId;
        await $updateMutation.mutateAsync({
          candidateId: candidate.id,
          data: {
            firstName: formFirstName,
            middleName: formMiddleName,
            lastName: formLastName,
            email: formEmail,
            phone: formPhone,
            linkedinProfile: formLinkedin,
            source: formSource,
            gender: formGender,
            location: formLocation,
            position: formPosition,
            experience: formExperience,
            summary: formSummary,
            skills: formSkills,
            notes: formNotes,
            offerId: activeCampaignId || undefined,
            positionIds: formPositionIds.length > 0 ? formPositionIds : undefined,
            positionPriorities: Object.keys(formPositionPriorities).length > 0 ? formPositionPriorities : undefined,
          }
        });

        // 2. Upload photo if selected
        if (formPhoto) {
          await $uploadPhotoMutation.mutateAsync({
            candidateId: candidate.id,
            file: formPhoto
          });
        }

        // 3. Upload resume if selected
        if (formResume) {
          await $uploadResumeMutation.mutateAsync({
            candidateId: candidate.id,
            file: formResume
          });
        }
      } else {
        const data: CreateCandidateInput = {
          firstName: formFirstName,
          middleName: formMiddleName,
          lastName: formLastName,
          email: formEmail,
          phone: formPhone,
          linkedinProfile: formLinkedin,
          source: formSource,
          gender: formGender,
          location: formLocation,
          position: formPosition,
          positionIds: formPositionIds.length > 0 ? formPositionIds : undefined,
          positionPriorities: Object.keys(formPositionPriorities).length > 0 ? formPositionPriorities : undefined,
          experience: formExperience,
          summary: formSummary,
          skills: formSkills.length > 0 ? formSkills : undefined,
          notes: formNotes,
          campaignId: campaignId || recruitmentStore.activeCampaignId || '',
          resumeFile: formResume || undefined,
        };

        const result = await $createMutation.mutateAsync(data) as Candidate | null;

        if (result && formPhoto) {
          await $uploadPhotoMutation.mutateAsync({
            candidateId: result.id,
            file: formPhoto
          });
        }
      }

      open = false;
    } catch (error) {
      console.error(error);
      const errorMsg = getFriendlyErrorMessage(error);
      if (errorMsg.includes('déjà postulé') || errorMsg.includes('already applied')) {
        formErrors = { email: errorMsg };
      } else {
        // For other errors, keep the toast
      }
    } finally {
      isSaving = false;
    }
  }

  function handlePhotoSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      formPhoto = target.files[0];
      formPhotoPreview = URL.createObjectURL(target.files[0]);
    }
  }

  function handleResumeSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      formResume = target.files[0];
      formResumeName = target.files[0].name;
    }
  }

  const sources = CANDIDATE_SOURCE_OPTIONS;

  const campaignPositions = $derived(recruitmentStore.currentCampaign?.positions ?? []);
  const hasCampaignPositions = $derived(campaignPositions.length > 0);
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-145 bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <Sheet.Title class="text-[1rem] font-bold text-slate-900 truncate">
          {candidate ? 'Modifier le candidat' : 'Nouveau candidat'}
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <!-- Informations personnelles -->
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label class="text-slate-900">Nom <span class="text-red-500">*</span></Label>
              <Input bind:value={formLastName} placeholder="ex: KIBANGULA" class="h-10 shadow-fine" />
            </div>
            <div class="space-y-2">
              <Label class="text-slate-900">Post-nom <span class="text-slate-400 text-sm">(optionnel)</span></Label>
              <Input bind:value={formMiddleName} placeholder="ex: MUSUYU" class="h-10 shadow-fine" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label class="text-slate-900">Prénom <span class="text-red-500">*</span></Label>
              <Input bind:value={formFirstName} placeholder="ex: Prosper" class="h-10 shadow-fine" />
            </div>
            <div class="space-y-2">
              <Label class="text-slate-900">Email <span class="text-red-500">*</span></Label>
              <Input type="email" bind:value={formEmail} placeholder="prosper@oxiliere.com" class="h-10 shadow-fine" />
              <ValidationError errors={formErrors} field="email" />
            </div>
          </div>
          
          <!-- Photo de profil -->
          <div class="space-y-2">
            <Label class="text-slate-900">Photo de profil</Label>
            <div class="flex items-center gap-4">
              <div class="relative w-16 h-16 rounded-full overflow-hidden bg-slate-100 border-2 border-slate-200 shrink-0">
                {#if formPhotoPreview}
                  <img src={formPhotoPreview} alt="Aperçu" class="w-full h-full object-cover" />
                {:else}
                  <div class="w-full h-full flex items-center justify-center text-slate-400">
                    <AppIcon name="camera" size={22} />
                  </div>
                {/if}
              </div>
              <label class="cursor-pointer">
                <input
                  type="file"
                  accept="image/*"
                  onchange={handlePhotoSelect}
                  class="hidden"
                />
                <span class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary bg-primary/5 border border-primary/20 rounded-lg hover:bg-primary/10 transition-colors">
                  <AppIcon name="upload" size={15} />
                  {formPhotoPreview ? 'Changer' : 'Ajouter une photo'}
                </span>
              </label>
            </div>
          </div>

          <PhoneInput
            id="candidate-phone"
            label="Téléphone"
            placeholder="Numéro de téléphone"
            value={formPhone}
            onChange={(v) => formPhone = v}
          />

          <div class="space-y-2">
            <Label class="text-slate-900">Profil LinkedIn</Label>
            <Input bind:value={formLinkedin} placeholder="https://linkedin.com/in/..." class="h-10 shadow-fine" />
          </div>

          <div class="space-y-2">
            <Label class="text-slate-900">Sexe / Genre</Label>
            <Select type="single" value={formGender} onValueChange={(v) => formGender = v as GenderStatus}>
              <SelectTrigger class="h-10 w-full shadow-fine cursor-pointer">
                <span class="truncate text-[0.85rem] font-medium flex items-center gap-2">
                  <AppIcon name={CANDIDATE_GENDER_OPTIONS.find(o => o.value === formGender)?.icon || 'help-circle'} size={17} />
                  {CANDIDATE_GENDER_LABELS[formGender] || 'Non spécifié'}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each CANDIDATE_GENDER_OPTIONS as opt}
                  <SelectItem value={opt.value} class="text-[0.85rem]!">
                    <div class="flex items-center gap-2 text-[0.85rem]!">
                      <AppIcon name={opt.icon} size={17} />
                      {opt.label}
                    </div>
                  </SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Profil & Source -->
        <div class="space-y-4 pt-2"> 
          <div class="space-y-2">
            <Label class="text-slate-900">Source du candidat</Label>
            <Select type="single" value={formSource} onValueChange={(v) => formSource = v as any}>
              <SelectTrigger class="h-10 w-full shadow-fine cursor-pointer">
                <span class="truncate text-[0.85rem] font-medium flex items-center gap-2">
                  <AppIcon name={sources.find(s => s.value === formSource)?.icon || 'mail'} size={17} />
                  {sources.find(s => s.value === formSource)?.label}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each sources as source}
                  <SelectItem value={source.value} class="text-[0.85rem]!">
                    <div class="flex items-center gap-2 text-[0.85rem]!">
                      <AppIcon name={source.icon} size={17} />
                      {source.label}
                    </div>
                  </SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>

          <!-- Multi-position selection: postes de la campagne -->
          <div class="space-y-2">
            <Label class="text-slate-900">
              Postes visés <span class="text-sm text-slate-400">(sélection multiple)</span>
            </Label>
            {#if hasCampaignPositions}
              <div class="border border-slate-200 rounded-lg p-3 space-y-2 bg-white shadow-fine">
                {#each campaignPositions as pos}
                  {@const isSelected = formPositionIds.includes(pos.id)}
                  <div
                    class={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-md transition-all",
                      "hover:bg-primary/5 hover:border-primary/20",
                      isSelected
                        ? "bg-primary/5 border border-primary/20"
                        : "border border-transparent"
                    )}
                  >
                    <Switch
                      checked={isSelected}
                      onCheckedChange={() => togglePosition(pos.id)}
                      class="cursor-pointer"
                    />
                    <div class="flex-1 min-w-0">
                      <span class="text-sm font-medium text-slate-800">
                        {pos.name}
                      </span>
                    </div>
                    {#if isSelected}
                      <Select
                        type="single"
                        value={formPositionPriorities[pos.id] || 'MEDIUM'}
                        onValueChange={(v: string) => {
                          formPositionPriorities = { ...formPositionPriorities, [pos.id]: v as 'LOW' | 'MEDIUM' | 'HIGH' };
                        }}
                      >
                        <SelectTrigger class="h-6! w-34 shadow-fine bg-white cursor-pointer">
                          <span class="truncate flex items-center gap-1 text-[0.85rem]">
                            <AppIcon
                              name="flag"
                              size={14}
                              class={cn(
                                "shrink-0",
                                formPositionPriorities[pos.id] === 'HIGH' ? 'text-rose-500' :
                                formPositionPriorities[pos.id] === 'MEDIUM' ? 'text-amber-500' :
                                'text-slate-400'
                              )}
                            />
                            {CANDIDATE_PRIORITY_LABELS[formPositionPriorities[pos.id] || 'MEDIUM']}
                          </span>
                        </SelectTrigger>
                        <SelectContent class="z-9999">
                          {#each CANDIDATE_PRIORITY_OPTIONS as opt}
                            <SelectItem value={opt.value}>
                              <div class="flex items-center gap-2 text-[0.85rem]">
                                <AppIcon name="flag" size={15} class={opt.color} />
                                {opt.label}
                              </div>
                            </SelectItem>
                          {/each}
                        </SelectContent>
                      </Select>
                    {/if}
                  </div>
                {/each}
              </div>
            {:else}
              <div class="text-sm text-slate-400 px-1 flex gap-1.5 justify-center items-center">
                <AppIcon name="circle-x" size={16} class="text-slate-300"/>
                Aucun poste défini pour cette campagne
              </div>
            {/if}
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label class="text-slate-900">Localisation</Label>
              <Input bind:value={formLocation} placeholder="Paris, France" class="h-10 shadow-fine" />
            </div>
            <div class="space-y-2">
              <Label class="text-slate-900">Expérience</Label>
              <Input bind:value={formExperience} placeholder="ex: 5 ans" class="h-10 shadow-fine" />
            </div>
          </div>
        </div>

        <!-- Compétences -->
        <div class="space-y-2 pt-2">
          <Label class="text-slate-900">Compétences</Label>
          <div class="flex flex-wrap gap-1.5 mb-2">
            {#each formSkills as skill}
              <span class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary/5 text-primary text-[0.82rem]">
                <AppIcon name="tag" size={13} />
                {skill}
                <button onclick={() => handleRemoveSkill(skill)} class="p-0.5 hover:bg-primary/10 rounded cursor-pointer">
                  <AppIcon name="x" size={13} />
                </button>
              </span>
            {/each}
          </div>
          <div class="flex gap-2">
            <Input
              bind:value={formSkillsInput}
              placeholder="ex: JavaScript, Gestion d'équipe..."
              class="h-10 shadow-fine flex-1"
              onkeydown={(e: KeyboardEvent) => { if (e.key === 'Enter') { e.preventDefault(); handleAddSkill(); } }}
            />
            <Button onclick={handleAddSkill} class="h-10 shrink-0 shadow-fine">
              <AppIcon name="plus" size={17} />
            </Button>
          </div>
        </div>

        <!-- CV / Résumé -->
        <div class="space-y-2 pt-2">
          <Label class="text-slate-900">CV / Résumé</Label>
          <div class="flex items-center gap-3">
            <label class="cursor-pointer flex-1">
              <input
                type="file"
                accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
                onchange={handleResumeSelect}
                class="hidden"
              />
              <div class="flex items-center gap-2 px-4 py-2.5 border-2 border-dashed border-slate-200 rounded-lg hover:border-primary/40 hover:bg-primary/5 transition-all cursor-pointer">
                <AppIcon name="file-text" size={20} class="text-slate-400" />
                <span class="text-sm text-slate-500">
                  {formResumeName || 'Cliquez pour ajouter ou remplacer le CV (PDF, DOCX, ...)'}
                </span>
              </div>
            </label>
            {#if formResumeName}
              <button onclick={() => { formResume = null; formResumeName = ''; }} class="p-1.5 text-slate-400 hover:text-red-500 transition-colors cursor-pointer">
                <AppIcon name="x" size={16} />
              </button>
            {/if}
          </div>
        </div>

        <!-- Notes -->
        <div class="space-y-2 pt-2">
          <Label class="text-slate-900">Notes internes</Label>
          <Textarea 
            bind:value={formNotes} 
            placeholder="Observations, points à suivre, remarques internes..." 
            class="min-h-24 shadow-fine text-[0.85rem]"
          />
        </div>

        <!-- Résumé / Summary -->
        <div class="space-y-2 pt-2">
          <Label class="text-slate-900">Résumé du profil</Label>
          <Textarea
            bind:value={formSummary}
            placeholder="Aperçu rapide du profil, synthèse des compétences..."
            class="min-h-24 shadow-fine text-[0.85rem]"
          />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
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
          {candidate ? 'Enregistrer' : 'Enregistrer'}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




