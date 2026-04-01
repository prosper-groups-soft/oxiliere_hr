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
  import type { RecruitmentCampaign } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";

  let {
    open = $bindable(false),
    campaign = $bindable(null)
  } = $props<{
    open: boolean,
    campaign?: RecruitmentCampaign | null
  }>();

  // Form state
  let formTitle = $state('');
  let formJobName = $state('');
  let formLocation = $state('');
  let formType = $state<'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERNSHIP'>('FULL_TIME');
  let formTargetHires = $state(1);
  let formDescription = $state('');

  $effect(() => {
    if (open) {
      if (campaign) {
        formTitle = campaign.title || '';
        // Defensive check: use jobName, but fallback to department if it exists on the object (for transition)
        formJobName = campaign.jobName || (campaign as any).department || '';
        formLocation = campaign.location || '';
        formType = campaign.type || 'FULL_TIME';
        formTargetHires = campaign.targetHires || 1;
        formDescription = campaign.description || '';
      } else {
        formTitle = '';
        formJobName = '';
        formLocation = '';
        formType = 'FULL_TIME';
        formTargetHires = 1;
        formDescription = '';
      }
    }
  });

  const typeLabels: Record<string, string> = {
    'FULL_TIME': 'Temps plein',
    'PART_TIME': 'Temps partiel',
    'CONTRACT': 'Contractuel',
    'INTERNSHIP': 'Stage'
  };

  async function handleSave() {
    if (!formTitle || !formJobName) {
      notification.toast.error('Veuillez remplir les informations obligatoires (Titre et Poste)');
      return;
    }

    try {
      const data = {
        title: formTitle,
        jobName: formJobName,
        location: formLocation,
        type: formType,
        targetHires: formTargetHires,
        description: formDescription
      };

      if (campaign) {
        await recruitmentStore.updateCampaign(campaign.id, data);
        notification.toast.success('Campagne mise à jour avec succès');
      } else {
        await recruitmentStore.addCampaign(data);
        notification.toast.success('Campagne créée avec succès');
      }
      open = false;
    } catch (error) {
      notification.toast.error('Erreur lors de l\'enregistrement');
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-2">
        <div class="h-10 w-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <AppIcon name="briefcase" size={20} />
        </div>
        <Sheet.Title class="text-[1rem] font-bold text-slate-900 truncate">
          {campaign ? 'Modifier la campagne' : 'Nouvelle campagne'}
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <div class="space-y-2">
          <Label class="text-slate-900">Titre de la campagne <span class="text-red-500">*</span></Label>
          <Input bind:value={formTitle} placeholder="ex: Recrutement Tech Q3" class="h-10 shadow-fine" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-slate-900">Nom du poste <span class="text-red-500">*</span></Label>
            <Input bind:value={formJobName} placeholder="ex: Développeur Fullstack" class="h-10 shadow-fine" />
          </div>
          <div class="space-y-2">
            <Label class="text-slate-900">Localisation</Label>
            <Input bind:value={formLocation} placeholder="ex: Paris / Remote" class="h-10 shadow-fine" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-slate-900">Type de contrat</Label>
            <Select type="single" value={formType} onValueChange={(v) => formType = v as any}>
              <SelectTrigger class="h-10 w-full shadow-fine">
                <span class="truncate text-[0.85rem] font-medium">{typeLabels[formType] || formType}</span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="FULL_TIME" class="text-[0.85rem]">Temps plein</SelectItem>
                <SelectItem value="PART_TIME" class="text-[0.85rem]">Temps partiel</SelectItem>
                <SelectItem value="CONTRACT" class="text-[0.85rem]">Contractuel</SelectItem>
                <SelectItem value="INTERNSHIP" class="text-[0.85rem]">Stage</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-2">
            <Label class="text-slate-900">Nombre de postes</Label>
            <Input type="number" bind:value={formTargetHires} min="1" class="h-10 shadow-fine" />
          </div>
        </div>

        <div class="space-y-2">
          <Label class="text-slate-900">Description du besoin</Label>
          <Textarea 
            bind:value={formDescription} 
            placeholder="Détails sur le poste, l'équipe, etc..." 
            class="min-h-32 shadow-fine text-[0.85rem]"
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
          {campaign ? 'Enregistrer les modifications' : 'Créer la campagne'}
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

