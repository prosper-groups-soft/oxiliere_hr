<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger
  } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { recruitmentStore } from "@/features/recruitment/stores/recruitment.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Candidate } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";

  let {
    open = $bindable(false),
    candidate = null,
    onSuccess = null
  } = $props<{
    open: boolean,
    candidate: Candidate | null | undefined,
    onSuccess?: () => void
  }>();

  // Form state
  let formSalaryMin = $state(0);
  let formSalaryMax = $state(0);
  let formCurrency = $state('CDF');
  let formStartDate = $state('');

  $effect(() => {
    if (open && candidate) {
      // Default to next month
      const nextMonth = new Date();
      nextMonth.setMonth(nextMonth.getMonth() + 1);
      nextMonth.setDate(1);
      formStartDate = nextMonth.toISOString().split('T')[0];
      
      formSalaryMin = 500;
      formSalaryMax = 1000;
      formCurrency = 'USD';
    }
  });

  async function handleSave() {
    if (!candidate) return;

    try {
      await recruitmentStore.createJobOffer({
        candidateId: candidate.id,
        positionId: candidate.positionId || '',
        salaryMin: formSalaryMin,
        salaryMax: formSalaryMax,
        currency: formCurrency,
        startDate: formStartDate
      });

      notification.toast.success('Offre d\'emploi créée avec succès');
      open = false;
      onSuccess?.();
    } catch (error) {
      notification.toast.error('Erreur lors de la création de l\'offre');
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
          <AppIcon name="file-text" size={20} />
        </div>
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
            Créer une offre d'emploi
          </Sheet.Title>
          <Sheet.Description class="text-[0.78rem] text-slate-500 truncate">
            {candidate ? `${candidate.firstName} ${candidate.lastName}` : 'Chargement...'}
          </Sheet.Description>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        
        <!-- Rémunération -->
        <div class="space-y-4 p-4 rounded-xl bg-slate-50 border border-slate-100">
           <Label class="text-slate-900 font-bold flex items-center gap-2">
             Rémunération proposée
           </Label>
           
           <div class="grid grid-cols-2 gap-4">
             <div class="space-y-2">
               <Label class="text-[0.75rem] text-slate-500 uppercase tracking-wider font-bold">Min</Label>
               <Input type="number" bind:value={formSalaryMin} class="h-10 bg-white border-slate-200 shadow-fine" />
             </div>
             <div class="space-y-2">
               <Label class="text-[0.75rem] text-slate-500 uppercase tracking-wider font-bold">Max</Label>
               <Input type="number" bind:value={formSalaryMax} class="h-10 bg-white border-slate-200 shadow-fine" />
             </div>
           </div>

           <div class="space-y-2">
             <Label class="text-[0.75rem] text-slate-500 uppercase tracking-wider font-bold">Devise</Label>
             <Select type="single" value={formCurrency} onValueChange={(v) => formCurrency = v}>
               <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
                 <span class="truncate text-[0.85rem] font-medium">{formCurrency}</span>
               </SelectTrigger>
               <SelectContent class="z-9999">
                 <SelectItem value="USD" class="text-[0.85rem]">USD - Dollar Américain</SelectItem>
                 <SelectItem value="EUR" class="text-[0.85rem]">EUR - Euro</SelectItem>
                 <SelectItem value="CDF" class="text-[0.85rem]">CDF - Franc Congolais</SelectItem>
               </SelectContent>
             </Select>
           </div>
        </div>

        <!-- Date de début -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Date de début prévue<span class="text-red-500">*</span></Label>
          <Input type="date" bind:value={formStartDate} class="h-10 border-slate-200 shadow-fine" />
          <p class="text-[0.8rem] text-slate-500">Date à laquelle le candidat devrait rejoindre l'entreprise.</p>
        </div>

        <div class="p-4 rounded-xl bg-amber-50 border border-amber-100 flex gap-3">
          <AppIcon name="alert-triangle" size={18} class="text-amber-600 shrink-0 mt-0.5" />
          <p class="text-[0.78rem] text-amber-700 leading-relaxed font-medium">
            En créant cette offre, le statut du candidat passera automatiquement à l'étape 
            <strong class="text-[0.78rem]">Offre</strong> dans le pipeline.
          </p>
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-emerald-600 text-white h-9 shadow-fine hover:bg-emerald-700 transition-all"
        >
          <AppIcon name="send" size={18} />
          Créer l'offre
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

