<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Badge } from "@/components/ui/badge";
  import * as Select from "@/components/ui/select";
  import { cn } from "@/utilities/common/css";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { 
    SeniorityLevelDefinition, 
    SeniorityLevel 
  } from "../../../../types/types";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import { slide } from "svelte/transition";
  import { z } from "zod";
  import ValidationError from "@/components/ui/validation-error";
  import { seniorityLevelSchema } from "../../../../schemas/seniority.schema";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";

  let { 
    open = $bindable(false),
    level = $bindable(null),
    onSave
  } = $props<{ 
    open: boolean, 
    level?: SeniorityLevelDefinition | null,
    onSave?: (data: Omit<SeniorityLevelDefinition, 'id'>, levelId?: string | null) => Promise<void> | void
  }>();

  // --- Form state ---
  let formLevel = $state<SeniorityLevel>('TRAINEE');
  let formName = $state('');
  let formRank = $state(1);
  let formRequirements = $state<string[]>([]);
  let newRequirement = $state('');
  
  // Validation errors
  let validationErrors = $state<Record<string, string>>({});
  
  // Submit state
  let isSubmitting = $state(false);
  
  // Check uniqueness constraints
  function getExistingLevels(): string[] {
    return jobsStore.seniorityLevels
      .filter(l => !level || l.id !== level.id) // Exclude current level when editing
      .map(l => l.level);
  }
  
  function getExistingRanks(): number[] {
    return jobsStore.seniorityLevels
      .filter(l => !level || l.id !== level.id) // Exclude current level when editing
      .map(l => l.rank);
  }
  
  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  $effect(() => {
    if (open) {
      if (level) {
        formLevel = level.level;
        formName = level.name;
        formRank = level.rank;
        formRequirements = [...level.requirements];
      } else {
        formLevel = 'TRAINEE';
        formName = SENIORITY_LABELS['TRAINEE'];
        formRank = (jobsStore.seniorityLevels.length + 1);
        formRequirements = [];
      }
      newRequirement = '';
      // Reset validation errors when opening
      validationErrors = {};
    } else {
      // Clear validation errors when closing the modal
      validationErrors = {};
    }
  });

  function addRequirement() {
    const val = newRequirement.trim();
    if (val) {
      if (!formRequirements.includes(val)) {
        formRequirements.push(val);
        newRequirement = '';
      } else {
        notification.toast.error("Cette compétence est déjà listée");
      }
    }
  }

  function removeRequirement(req: string) {
    formRequirements = formRequirements.filter(r => r !== req);
  }

  function validate(): boolean {
    validationErrors = {};
    
    // Check Zod schema
    const result = seniorityLevelSchema.safeParse({
      level: formLevel,
      rank: Number(formRank),
      requirements: formRequirements
    });
    
    if (!result.success) {
      result.error.issues.forEach((err: z.core.$ZodIssue) => {
        const field = String(err.path[0]);
        validationErrors = { ...validationErrors, [field]: err.message };
      });
      return false;
    }
    
    // Check duplicate level
    const existingLevels = getExistingLevels();
    if (existingLevels.includes(formLevel)) {
      validationErrors = { ...validationErrors, level: 'Ce niveau de séniorité existe déjà' };
      return false;
    }
    
    // Check duplicate rank
    const existingRanks = getExistingRanks();
    if (existingRanks.includes(Number(formRank))) {
      validationErrors = { ...validationErrors, rank: 'Ce rang est déjà attribué à un autre niveau' };
      return false;
    }
    
    return true;
  }

  async function handleSave() {
    if (!validate()) {
      notification.toast.error("Veuillez corriger les erreurs");
      return;
    }

    isSubmitting = true;

    const data: Omit<SeniorityLevelDefinition, 'id'> = {
      level: formLevel,
      name: SENIORITY_LABELS[formLevel],
      rank: Number(formRank),
      requirements: formRequirements
    };

    try {
      if (onSave) {
        // Utiliser la mutation API
        await onSave(data, level?.id ?? null);
      } else {
        // Fallback: utiliser le store local (legacy)
        if (level) {
          jobsStore.updateSeniorityLevel(level.id, data);
          notification.toast.success(`Le niveau ${formName} a été mis à jour.`);
        } else {
          jobsStore.addSeniorityLevel(data);
          notification.toast.success(`Le niveau ${formName} a été créé.`);
        }
      }
      open = false;
    } catch (error) {
      // Erreur déjà gérée par le service/notification
    } finally {
      isSubmitting = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-140 bg-white p-0 flex flex-col h-full">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900 flex items-center gap-2">
        {level ? 'Modifier le niveau' : 'Nouveau niveau'}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto">
      <form id="seniority-form" class="p-6 space-y-6" onsubmit={(e) => { e.preventDefault(); handleSave(); }}>
        
        <div class="space-y-2">
          <Label for="snr-level">Niveau de séniorité</Label>
          <Select.Root type="single" bind:value={formLevel}>
            <Select.Trigger class="h-9 bg-white border-slate-200 shadow-fine w-full cursor-pointer">
              {SENIORITY_LABELS[formLevel]}
            </Select.Trigger>
            <Select.Content class="bg-white z-300">
              {#each Object.entries(SENIORITY_LABELS) as [level, label]}
                <Select.Item value={level}>
                  <span class="flex items-center gap-2">
                    <span class="font-medium text-[0.876rem]">{level}</span>
                    <span class="text-slate-500 text-[0.876rem]">- {label}</span>
                  </span>
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
          <ValidationError errors={validationErrors} field="level" />
        </div>

        <div class="space-y-3">
          <Label>Compétences & Exigences</Label>
          
          <div class="flex gap-2">
            <Input 
              placeholder="Ajouter une exigence..." 
              bind:value={newRequirement}
              onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addRequirement())}
              class="h-9 bg-white border-slate-200 shadow-none focus:bg-white transition-colors"
            />
            <Button variant="secondary" onclick={addRequirement} class="h-9 w-9 p-0 shrink-0">
              <AppIcon name="plus" size={17} strokeWidth={1.5} />
            </Button>
          </div>

          <ValidationError errors={validationErrors} field="requirements" />
          
          <div class="flex flex-wrap gap-2 pt-1">
            {#each formRequirements as req}
              <Badge variant="secondary" class="pl-3 pr-1 py-1 gap-1 border-slate-200 bg-slate-100 text-slate-700 font-medium rounded-full cursor-pointer">
                <AppIcon name="circle-check" size={16} class="text-emerald-500/80" strokeWidth={1.7} />
                <span class="text-[0.85rem]!">{req}</span>
                <button 
                  type="button"
                  onclick={() => removeRequirement(req)}
                  class="h-5 w-5 rounded-full hover:bg-slate-200 flex items-center justify-center transition-colors cursor-pointer"
                >
                  <AppIcon name="x" size={14} />
                </button>
              </Badge>
            {:else}
              <p class="text-[0.85rem] text-slate-500 gap-1.5 flex items-center justify-center w-full">
                <AppIcon name="circle-x" size={16} class="text-slate-300" />
                Aucune compétence ajoutée.
              </p>
            {/each}
          </div>
        </div>

        <div class="space-y-3 pt-2">
          <div class="space-y-2">
            <Label for="snr-rank" class="text-slate-900 font-bold">Rang hiérarchique</Label>
            <Input 
              id="snr-rank" 
              type="number" 
              min={1}
              bind:value={formRank} 
              oninput={() => clearValidationError('rank')}
              class={cn(
                "h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
                validationErrors.rank && "border-red-500 focus:ring-red-500"
              )} 
            />
          </div>
          <ValidationError errors={validationErrors} field="rank" />

          <!-- Info Box -->
          <div class="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100/50" in:slide={{ duration: 300 }}>
            <div class="flex gap-3">
              <div class="p-1.5 rounded-lg bg-indigo-100 text-indigo-600 shrink-0 h-fit">
                <AppIcon name="info" size={17} />
              </div>
              <p class="text-[0.875rem] leading-relaxed text-slate-600 font-medium">
                Le rang définit l'ordre d'affichage dans la matrice. Le niveau 1 est généralement le point d'entrée.
              </p>
            </div>
          </div>
        </div>

      </form>
    </div>

    <Sheet.Footer class="p-6 py-2.5 border-t bg-slate-50/30 mt-auto">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-900">
            <AppIcon name="x" size={16} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          type="submit" 
          form="seniority-form"
          disabled={isSubmitting}
          class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine hover:opacity-90 transition-all"
        >
          {#if isSubmitting}
            <AnimateSpin class="border-white size-3" text="" />
          {:else}
            <AppIcon name="check" size={16} />
          {/if}
          Enregistrer
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>

