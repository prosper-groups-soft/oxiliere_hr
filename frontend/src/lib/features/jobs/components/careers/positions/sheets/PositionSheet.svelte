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
  import { notification } from "@/stores/notification.svelte";
  import type { 
    JobPosition, 
    SeniorityLevel 
  } from "../../../../types/types";
  import { fade, slide } from "svelte/transition";

  let { 
    open = $bindable(false),
    position = $bindable(null),
    prefilledDeptId = ''
  } = $props<{ 
    open: boolean, 
    position?: JobPosition | null,
    prefilledDeptId?: string
  }>();

  // --- Form state ---
  let formTitle = $state('');
  let formDeptId = $state('');
  let formSeniority = $state<SeniorityLevel>('DÉBUTANT');
  let formSalaryMin = $state(0);
  let formSalaryMax = $state(0);
  let formRequirements = $state<string[]>([]);
  let formSkills = $state<{ name: string; level: number }[]>([]);
  let isEditing = $state(false);

  // UI state for adding new items
  let newReq = $state('');
  let newSkill = $state('');

  // Sync when position is passed for editing
  $effect(() => {
    if (open) {
      if (position) {
        isEditing = true;
        formTitle = position.title;
        formDeptId = position.departmentId;
        formSeniority = position.seniority;
        formSalaryMin = position.salaryRange.min;
        formSalaryMax = position.salaryRange.max;
        formRequirements = [...position.requirements];
        formSkills = [...position.skills];
      } else {
        isEditing = false;
        formTitle = '';
        formDeptId = prefilledDeptId || (jobsStore.departments[0]?.id ?? '');
        formSeniority = 'DÉBUTANT';
        formSalaryMin = 0;
        formSalaryMax = 0;
        formRequirements = [];
        formSkills = [];
      }
      newReq = '';
      newSkill = '';
    }
  });

  function addRequirement() {
    const val = newReq.trim();
    if (val && !formRequirements.includes(val)) {
      formRequirements = [...formRequirements, val];
      newReq = '';
    }
  }

  function addSkill() {
    const val = newSkill.trim();
    if (val && !formSkills.find(s => s.name.toLowerCase() === val.toLowerCase())) {
      formSkills = [...formSkills, { name: val, level: 3 }];
      newSkill = '';
    }
  }

  function removeRequirement(req: string) {
    formRequirements = formRequirements.filter(r => r !== req);
  }

  function removeSkill(name: string) {
    formSkills = formSkills.filter(s => s.name !== name);
  }

  function handleSave() {
    if (!formTitle.trim()) {
      notification.toast.error('Veuillez entrer un intitulé de poste');
      return;
    }

    const data: Omit<JobPosition, 'id'> = {
      title: formTitle.trim(),
      departmentId: formDeptId,
      seniority: formSeniority,
      salaryRange: {
        min: formSalaryMin,
        max: formSalaryMax,
        currency: 'CDF'
      },
      requirements: formRequirements,
      skills: formSkills
    };

    if (position) {
      jobsStore.updatePosition(position.id, data);
      notification.toast.success('Poste modifié avec succès');
    } else {
      jobsStore.addPosition(data);
      notification.toast.success('Nouveau poste créé avec succès');
    }
    open = false;
  }

  function handleDelete() {
    if (!position) return;
    
    notification.confirm({
      title: 'Supprimer ce poste',
      message: `Êtes-vous sûr(e) de vouloir supprimer "${position.title}" ? Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: () => {
        jobsStore.deletePosition(position.id);
        notification.toast.success('Poste supprimé avec succès');
        open = false;
      }
    });
  }

  const selectedDept = $derived(jobsStore.getDepartmentById(formDeptId));

</script>

<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
    <!-- Header -->
    <Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
          <AppIcon name="briefcase" size={20} />
        </div>
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
            {position ? 'Modifier le poste' : 'Nouveau poste'}
          </Sheet.Title>
          <Sheet.Description class="text-[0.78rem] text-slate-500 truncate">
            {selectedDept?.name || 'Sélectionnez une unité'}
          </Sheet.Description>
        </div>
      </div>
    </Sheet.Header>

    <!-- Form Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-7" in:fade={{ duration: 200 }}>
        <!-- Intitulé -->
        <div class="space-y-2.5">
          <Label for="pos-title" class="text-slate-900">
            Intitulé du poste <span class="text-red-500">*</span>
          </Label>
          <Input 
            id="pos-title" 
            bind:value={formTitle} 
            placeholder="ex: Developers Frontend Senior" 
            class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <!-- Unité / Département -->
          <div class="space-y-2.5">
            <Label class="text-slate-900">Unité organisationnelle</Label>
            <Select type="single" value={formDeptId} onValueChange={(v) => formDeptId = v}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
                <span class="truncate text-[0.85rem] font-medium">
                  {selectedDept?.name || 'Choisir une unité...'}
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

          <!-- Niveau de séniorité -->
          <div class="space-y-2.5">
            <Label class="text-slate-900">Niveau de séniorité</Label>
            <Select type="single" value={formSeniority} onValueChange={(v) => formSeniority = v as SeniorityLevel}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
                <span class="truncate text-[0.85rem] font-medium">
                  {jobsStore.seniorityLabels[formSeniority] || formSeniority}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each jobsStore.seniorityLevels as level}
                  <SelectItem value={level.name} class="text-[0.85rem]">
                    {jobsStore.seniorityLabels[level.name] || level.name}
                  </SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Exigences (Requirements) -->
        <div class="space-y-3">
          <Label class="text-slate-900 flex items-center gap-2">
            Exigences spécifiques
          </Label>
          <div class="flex gap-2">
            <Input 
              placeholder="Ajouter une exigence (Diplômes, années d'exp...)" 
              bind:value={newReq}
              onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addRequirement())}
              class="h-9 bg-slate-50 border-slate-200 shadow-none focus:bg-white transition-colors"
            />
            <Button variant="secondary" onclick={addRequirement} class="h-9 w-9 p-0 shrink-0">
              <AppIcon name="plus" size={17} />
            </Button>
          </div>
          <div class="flex flex-wrap gap-2 pt-1">
            {#each formRequirements as req}
              <div class="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-50 border border-slate-100 text-[0.78rem] font-medium text-slate-700 animate-in fade-in scale-in-95 duration-200 group">
                <AppIcon name="circle-check" size={15} class="text-emerald-500/80" strokeWidth={1.7} />
                {req}
                <button 
                  type="button"
                  onclick={() => removeRequirement(req)}
                  class="text-slate-400 hover:text-red-500 transition-colors"
                >
                  <AppIcon name="x" size={12} />
                </button>
              </div>
            {:else}
              <p class="text-[0.77rem] text-slate-400 flex justify-center items-center px-2 w-full">
                Aucune exigence spécifique définie.
              </p>
            {/each}
          </div>
        </div>

        <!-- Compétences (Skills) -->
        <div class="space-y-3">
          <Label class="text-slate-900 flex items-center gap-2">
            Compétences clés
            <span class="text-[0.82rem] font-normal text-slate-400">(Techniques, Soft Skills...)</span>
          </Label>
          <div class="flex gap-2">
            <Input 
              placeholder="ex: React, SQL, Management..." 
              bind:value={newSkill}
              onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
              class="h-9 bg-slate-50 border-slate-200 shadow-none focus:bg-white transition-colors"
            />
            <Button variant="secondary" onclick={addSkill} class="h-9 w-9 p-0 shrink-0">
              <AppIcon name="plus" size={17} />
            </Button>
          </div>
          <div class="flex flex-wrap gap-2 pt-1">
            {#each formSkills as skill}
              <div class="flex items-center gap-2 px-3 py-1 rounded-xl bg-blue-50/50 border border-blue-100/50 text-[0.78rem] font-bold text-blue-700 animate-in fade-in scale-in-95 duration-200">
                <AppIcon name="tag" size={14} class="opacity-80" />
                {skill.name}
                <button 
                  type="button"
                  onclick={() => removeSkill(skill.name)}
                  class="text-blue-400 hover:text-red-500 transition-colors ml-1"
                >
                  <AppIcon name="x" size={12} />
                </button>
              </div>
            {:else}
              <p class="text-[0.77rem] text-slate-400 flex justify-center items-center px-2 w-full">
                Aucune compétence clé définie.
              </p>
            {/each}
          </div>
        </div>

        <!-- Fourchette Salariale -->
        <div class="space-y-3 pt-2">
          <Label class="text-slate-900 font-bold">Fourchette budgétaire (FC)</Label>
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest ml-1">Minimum</span>
              <Input 
                id="pos-sal-min" 
                type="number" 
                bind:value={formSalaryMin} 
                class="h-9.5 bg-white border-slate-200 shadow-fine rounded-md text-slate-700" 
              />
            </div>
            <div class="space-y-1.5">
              <span class="text-[0.62rem] text-slate-400 uppercase tracking-widest ml-1">Maximum</span>
              <Input 
                id="pos-sal-max" 
                type="number" 
                bind:value={formSalaryMax} 
                class="h-9.5 bg-white border-slate-200 shadow-fine rounded-md text-slate-700" 
              />
            </div>
          </div>
        </div>

        <!-- Info Box -->
        <div class="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100/50" in:slide={{ duration: 300 }}>
          <div class="flex gap-3">
            <div class="p-1.5 rounded-lg bg-indigo-100 text-indigo-600 shrink-0 h-fit">
              <AppIcon name="info" size={16} />
            </div>
            <p class="text-[0.78rem] leading-relaxed text-slate-600 font-medium">
              Les exigences définies ici s'ajoutent à celles du niveau de séniorité séléctionné ({jobsStore.seniorityLabels[formSeniority]}).
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
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

      {#if position}
        <Button 
          onclick={handleDelete}
          variant="ghost"
          class="w-full text-red-500 hover:text-red-600 hover:bg-red-50 font-medium h-9 text-[0.8rem] transition-colors"
        >
          <AppIcon name="trash" size={14} />
          Supprimer définitivement ce poste
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

