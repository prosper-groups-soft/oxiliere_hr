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
  import type { Candidate, CandidateSource } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";

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
  let formEmail = $state('');
  let formPhone = $state('');
  let formSource = $state<CandidateSource>('DIRECT');
  let formLocation = $state('');
  let formPosition = $state('');
  let formExperience = $state('');
  let formNotes = $state('');

  $effect(() => {
    if (open) {
      if (candidate) {
        formFirstName = candidate.firstName;
        formLastName = candidate.lastName;
        formEmail = candidate.email;
        formPhone = candidate.phone;
        formSource = candidate.source;
        formLocation = candidate.location || '';
        formPosition = candidate.position || '';
        formExperience = candidate.experience || '';
        formNotes = candidate.notes || '';
      } else {
        formFirstName = '';
        formLastName = '';
        formEmail = '';
        formPhone = '';
        formSource = 'DIRECT';
        formLocation = '';
        formPosition = '';
        formExperience = '';
        formNotes = '';
      }
    }
  });

  async function handleSave() {
    if (!formFirstName || !formLastName || !formEmail) {
      notification.toast.error('Veuillez remplir les informations de base');
      return;
    }

    try {
      const data = {
        firstName: formFirstName,
        lastName: formLastName,
        email: formEmail,
        phone: formPhone,
        source: formSource,
        location: formLocation,
        position: formPosition,
        experience: formExperience,
        notes: formNotes,
        campaignId: campaignId || recruitmentStore.activeCampaignId || ''
      };

      if (candidate) {
        await recruitmentStore.updateCandidate(candidate.id, data);
        notification.toast.success('Candidat mis à jour avec succès');
      } else {
        await recruitmentStore.addCandidate(data);
        notification.toast.success('Candidat ajouté avec succès');
      }
      open = false;
    } catch (error) {
      notification.toast.error('Erreur lors de l\'enregistrement');
    }
  }

  const sources: { value: CandidateSource, label: string, icon: string }[] = [
    { value: 'LINKEDIN', label: 'LinkedIn', icon: 'briefcase' },
    { value: 'CAREER_SITE', label: 'Site Carrière', icon: 'globe' },
    { value: 'REFERRAL', label: 'Cooptation', icon: 'users' },
    { value: 'DIRECT', label: 'Direct / Email', icon: 'mail' }
  ];
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <AppIcon name="user-plus" size={20} />
        </div>
        <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
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
              <Label class="text-slate-900">Prénom <span class="text-red-500">*</span></Label>
              <Input bind:value={formFirstName} placeholder="ex: Jean" class="h-10 shadow-fine" />
            </div>
            <div class="space-y-2">
              <Label class="text-slate-900">Nom <span class="text-red-500">*</span></Label>
              <Input bind:value={formLastName} placeholder="ex: Dupont" class="h-10 shadow-fine" />
            </div>
          </div>

          <div class="space-y-2">
            <Label class="text-slate-900">Email <span class="text-red-500">*</span></Label>
            <Input type="email" bind:value={formEmail} placeholder="jean.pierre@email.com" class="h-10 shadow-fine" />
          </div>

          <div class="space-y-2">
            <Label class="text-slate-900">Téléphone</Label>
            <Input type="tel" bind:value={formPhone} placeholder="+243 ..." class="h-10 shadow-fine" />
          </div>
        </div>

        <!-- Profil & Source -->
        <div class="space-y-4 pt-2"> 
          <div class="space-y-2">
            <Label class="text-slate-900">Source du candidat</Label>
            <Select type="single" value={formSource} onValueChange={(v) => formSource = v as any}>
              <SelectTrigger class="h-10 w-full shadow-fine">
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

          <div class="space-y-2">
            <Label class="text-slate-900">Poste actuel / visé</Label>
            <Input bind:value={formPosition} placeholder="ex: Développeur Senior" class="h-10 shadow-fine" />
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

        <!-- Notes -->
        <div class="space-y-2 pt-2">
          <Label class="text-slate-900">Notes & Résumé</Label>
          <Textarea 
            bind:value={formNotes} 
            placeholder="Compétences clés, points d'attention..." 
            class="min-h-24 shadow-fine text-[0.85rem]"
          />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-primary text-white h-9 shadow-fine hover:bg-primary/90 transition-all"
        >
          <AppIcon name="check" size={18} />
          {candidate ? 'Mettre à jour' : 'Enregistrer le candidat'}
        </Button>
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600">
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

