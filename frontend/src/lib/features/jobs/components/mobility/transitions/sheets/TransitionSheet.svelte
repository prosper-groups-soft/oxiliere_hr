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
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Transition, TransitionType } from "../../../../types/types";
  import { cn } from "@/utilities/common/css";
  import { fade, slide } from "svelte/transition";

  let {
    open = $bindable(false),
    transition = $bindable(null)
  } = $props<{
    open: boolean,
    transition?: Transition | null
  }>();

  // --- Form state ---
  let formEmployeeId = $state<string | undefined>(undefined); // Select uses string | undefined
  let formType = $state<TransitionType>('TRANSFER');
  let formFromPositionId = $state('');
  let formToPositionId = $state('');
  let formFromDeptId = $state('');
  let formToDeptId = $state('');
  let formDate = $state('');
  let formReason = $state('');

  $effect(() => {
    if (open) {
      if (transition) {
        formEmployeeId = String(transition.employeeId);
        formType = transition.type;
        formFromPositionId = transition.fromPositionId || '';
        formToPositionId = transition.toPositionId;
        formFromDeptId = transition.fromDepartmentId || '';
        formToDeptId = transition.toDepartmentId;
        formDate = transition.date;
        formReason = transition.reason || '';
      } else {
        formEmployeeId = undefined;
        formType = 'TRANSFER';
        formFromPositionId = '';
        formToPositionId = '';
        formFromDeptId = '';
        formToDeptId = jobsStore.departments[0]?.id ?? '';
        formDate = new Date().toISOString().split('T')[0];
        formReason = '';
      }
    }
  });

  function handleSave() {
    if (!formEmployeeId || (!formToPositionId && formType !== 'OFFBOARD') || !formToDeptId) {
      notification.toast.error('Veuillez compléter les champs requis');
      return;
    }

    const data: Omit<Transition, 'id'> = {
      employeeId: String(formEmployeeId),
      type: formType,
      fromPositionId: formFromPositionId || undefined,
      toPositionId: formToPositionId,
      fromDepartmentId: formFromDeptId || undefined,
      toDepartmentId: formToDeptId,
      date: formDate,
      reason: formReason || undefined
    };

    if (transition) {
      jobsStore.updateTransition(transition.id, data);
      notification.toast.success('Transition modifiée avec succès');
    } else {
      jobsStore.addTransition(data);
      notification.toast.success('Nouvelle transition enregistrée');
    }
    open = false;
  }

  function handleDelete() {
    if (!transition) return;
    
    notification.confirm({
      title: 'Supprimer cette transition',
      message: 'Êtes-vous sûr(e) de vouloir supprimer cet historique ? Cette action est irréversible.',
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: () => {
        jobsStore.deleteTransition(transition.id);
        notification.toast.success('Transition supprimée');
        open = false;
      }
    });
  }

  const selectedEmpl = $derived(formEmployeeId ? employeeStore.employees.find(e => String(e.id) === formEmployeeId) : null);
  const selectedToPos = $derived(jobsStore.positions.find(p => p.id === formToPositionId));
  const selectedToDept = $derived(jobsStore.getDepartmentById(formToDeptId));

  const transitionTypeIcons: Record<TransitionType, string> = {
    'PROMOTION': 'trending-up',
    'TRANSFER': 'refresh-cw',
    'HIRE': 'circle-check',
    'OFFBOARD': 'user-minus'
  };
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <!-- Header aligned with PositionSheet -->
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <AppIcon name="refresh-cw" size={20} />
        </div>
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
            {transition ? 'Modifier le mouvement' : 'Nouveau mouvement'}
          </Sheet.Title>
          <Sheet.Description class="text-[0.78rem] text-slate-500 truncate">
            {selectedEmpl?.name || 'Mise à jour de la situation employé'}
          </Sheet.Description>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-7" in:fade={{ duration: 200 }}>
        
        <!-- Employé (Select Pattern) -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Employé concerné <span class="text-red-500">*</span></Label>
          <Select type="single" value={formEmployeeId} onValueChange={(v) => formEmployeeId = v}>
            <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
              <span class="truncate text-[0.85rem] font-medium">
                {selectedEmpl?.name || 'Sélectionner un employé...'}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              {#each employeeStore.employees as emp}
                <SelectItem value={String(emp.id)} class="text-[0.85rem]">
                  {emp.name} <span class="text-slate-400 text-[0.85rem] ml-1">— {emp.jobTitle}</span>
                </SelectItem>
              {/each}
            </SelectContent>
          </Select>
        </div>

        <!-- Type de transition (Visual pattern from PositionSheet/Seniority style) -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Type de mouvement</Label>
          <div class="grid grid-cols-2 gap-3">
            {#each ['TRANSFER', 'PROMOTION', 'HIRE', 'OFFBOARD'] as type}
              <button 
                type="button"
                onclick={() => formType = type as TransitionType}
                class={cn(
                  "flex items-center gap-2.5 px-3 py-2.5 rounded-xl border text-[0.78rem] font-bold transition-all group",
                  formType === type 
                    ? "bg-primary/5 border-primary text-primary shadow-sm" 
                    : "bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50/50"
                )}
              >
                <div class={cn(
                  "h-7 w-7 rounded-lg flex items-center justify-center transition-colors",
                  formType === type ? "bg-primary text-white" : "bg-slate-100 text-slate-400 group-hover:bg-slate-200"
                )}>
                  <AppIcon name={transitionTypeIcons[type as TransitionType]} size={14} />
                </div>
                {type === 'TRANSFER' ? 'Mutation' : type === 'PROMOTION' ? 'Promotion' : type === 'HIRE' ? 'Embauche' : 'Départ'}
              </button>
            {/each}
          </div>
        </div>

        <!-- Grid for Date and other potential meta -->
        <div class="grid grid-cols-1 gap-4">
          <div class="space-y-2.5">
            <Label for="trans-date" class="text-slate-900">Date d'effet</Label>
            <Input 
              id="trans-date"
              type="date"
              bind:value={formDate}
              class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
            />
          </div>
        </div>

        {#if formType !== 'OFFBOARD'}
          <div class="p-5 rounded-2xl bg-slate-50 border border-slate-100 space-y-5" in:slide={{ duration: 300 }}>
            <p class="text-[0.65rem] font-black uppercase tracking-widest text-slate-400 mb-1">Nouvelle Affectation</p>
            
            <!-- Nouveau poste (Select pattern) -->
            <div class="space-y-2.5">
              <Label class="text-slate-900 text-[0.8rem]">Nouveau poste <span class="text-red-500">*</span></Label>
              <Select type="single" value={formToPositionId} onValueChange={(v) => formToPositionId = v}>
                <SelectTrigger class="h-9.5 w-full bg-white border-slate-200 shadow-fine rounded-md">
                  <span class="truncate text-[0.85rem] font-medium">
                    {selectedToPos?.title || 'Choisir un poste...'}
                  </span>
                </SelectTrigger>
                <SelectContent class="z-9999">
                  {#each jobsStore.positions as pos}
                    <SelectItem value={pos.id} class="text-[0.85rem]">
                      {pos.title}
                    </SelectItem>
                  {/each}
                </SelectContent>
              </Select>
            </div>

            <!-- Nouveau département (Select pattern) -->
            <div class="space-y-2.5">
              <Label class="text-slate-900 text-[0.8rem]">Département de destination <span class="text-red-500">*</span></Label>
              <Select type="single" value={formToDeptId} onValueChange={(v) => formToDeptId = v}>
                <SelectTrigger class="h-9.5 w-full bg-white border-slate-200 shadow-fine rounded-md">
                  <span class="truncate text-[0.85rem] font-medium">
                    {selectedToDept?.name || 'Sélectionner un département...'}
                  </span>
                </SelectTrigger>
                <SelectContent class="z-9999">
                  {#each jobsStore.departments as dept}
                    <SelectItem value={dept.id} class="text-[0.85rem]">
                      {dept.name}
                    </SelectItem>
                  {/each}
                </SelectContent>
              </Select>
            </div>
          </div>
        {/if}

        <!-- Raison -->
        <div class="space-y-2.5">
          <Label for="trans-reason" class="text-slate-900">Motif ou Commentaire</Label>
          <textarea 
            id="trans-reason"
            bind:value={formReason}
            class="w-full h-24 rounded-md border border-slate-200 px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400"
            placeholder="Précisez les raisons du mouvement (ex: Restructuration, Performance...)"
          ></textarea>
        </div>

      </div>
    </div>

    <!-- Footer aligned with PositionSheet -->
    <Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Button 
          onclick={handleSave} 
          class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all"
        >
          <AppIcon name="check" size={18} />
          Enregistrer
        </Button>
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            Annuler
          </Button>
        </Sheet.Close>
      </div>

      {#if transition}
        <Button 
          onclick={handleDelete}
          variant="ghost"
          class="w-full text-red-500 hover:text-red-600 hover:bg-red-50 font-medium h-9 text-[0.8rem] transition-colors"
        >
          <AppIcon name="trash" size={14} />
          Supprimer définitivement cet historique
        </Button>
      {/if}
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
