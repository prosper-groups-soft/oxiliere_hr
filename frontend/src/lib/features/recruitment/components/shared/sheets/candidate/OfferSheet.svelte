<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { useUpdateApplicationOfferMutation } from "@/features/recruitment/queries/recruitmentQueries";
  import type { CandidateApplication } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";


  let {
    open = $bindable(false),
    application = null,
    onSuccess = null
  } = $props<{
    open: boolean,
    application: CandidateApplication | null | undefined,
    onSuccess?: () => void
  }>();

  const updateOfferMutation = useUpdateApplicationOfferMutation();

  // Form state
  let formSalaryMin = $state(0);
  let formSalaryMax = $state(0);
  let formCurrency = $state('USD');
  let formStartDate = $state('');

  let isSaving = $state(false);

  $effect(() => {
    if (open && application) {
      if (application.salaryMin) {
        formSalaryMin = application.salaryMin;
        formSalaryMax = application.salaryMax || formSalaryMin;
        formCurrency = application.salaryCurrency || 'USD';
        formStartDate = application.offerStartDate || '';
      } else {
        formSalaryMin = 0;
        formSalaryMax = 0;
        formCurrency = 'USD';
        formStartDate = '';
      }
    }
  });

  async function handleSave() {
    if (!application) return;

    isSaving = true;
    try {
      await $updateOfferMutation.mutateAsync({
        applicationId: application.applicationId,
        data: {
          salaryMin: formSalaryMin,
          salaryMax: formSalaryMax,
          salaryCurrency: formCurrency,
          offerStartDate: formStartDate
        }
      });

      onSuccess?.();
      open = false;
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement:', error);
    } finally {
      isSaving = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[0.99rem] font-bold text-slate-900 truncate">
            Créer une offre d'emploi
          </Sheet.Title>
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
          <AppIcon name="triangle-alert" size={18} class="text-amber-600 shrink-0 mt-0.5" />
          <p class="text-[0.82rem] text-amber-700 leading-relaxed font-medium">
            En créant cette offre, le statut du candidat passera automatiquement à l'étape 
            <strong class="text-[0.78rem]">Offre</strong> dans le pipeline.
          </p>
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600" disabled={isSaving}>
            <AppIcon name="x" size={18} class="text-slate-30" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={handleSave}
          disabled={isSaving}
          class="flex-1 bg-emerald-600 text-white h-9 shadow-fine hover:bg-emerald-700 transition-all disabled:opacity-60"
        >
          {#if isSaving}
            <AnimateSpin text="" class="size-3 border-white" />
            Enregistrement
          {:else}
            <AppIcon name="check" size={18} />
            Créer l'offre
          {/if}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
