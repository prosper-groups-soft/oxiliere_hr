<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import { toast } from "@/utilities/ui/toast";
  import type { SeniorityLevelDefinition } from "../../../../types/types";
  import { slide } from "svelte/transition";

  let { 
    open = $bindable(false),
    level = $bindable(null)
  } = $props<{ 
    open: boolean, 
    level?: SeniorityLevelDefinition | null 
  }>();

  // --- Form state ---
  let formName = $state('');
  let formRank = $state(1);
  let formRequirements = $state<string[]>([]);
  let newRequirement = $state('');

  $effect(() => {
    if (open) {
      if (level) {
        formName = level.name;
        formRank = level.rank;
        formRequirements = [...level.requirements];
      } else {
        formName = '';
        formRank = (jobsStore.seniorityLevels.length + 1);
        formRequirements = [];
      }
      newRequirement = '';
    }
  });

  function addRequirement() {
    const val = newRequirement.trim();
    if (val) {
      if (!formRequirements.includes(val)) {
        formRequirements.push(val);
        newRequirement = '';
      } else {
        toast.error("Cette compétence est déjà listée");
      }
    }
  }

  function removeRequirement(req: string) {
    formRequirements = formRequirements.filter(r => r !== req);
  }

  function handleSave() {
    if (!formName || formRank <= 0) {
      toast.error("Veuillez remplir les informations obligatoires");
      return;
    }

    const data: Omit<SeniorityLevelDefinition, 'id'> = {
      name: formName.trim(),
      rank: formRank,
      requirements: formRequirements
    };

    if (level) {
      jobsStore.updateSeniorityLevel(level.id, data);
      toast.success(`Le niveau ${formName} a été mis à jour.`);
    } else {
      jobsStore.addSeniorityLevel(data);
      toast.success(`Le niveau ${formName} a été créé.`);
    }
    open = false;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full">
    <Sheet.Header class="px-6 py-5 border-b bg-white">
      <Sheet.Title class="text-[1rem] font-black text-slate-900 flex items-center gap-2">
        <div class="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
          <AppIcon name="layers" size={18} />
        </div>
        {level ? 'Modifier le niveau' : 'Nouveau niveau'}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto">
      <form id="seniority-form" class="p-6 space-y-6" onsubmit={(e) => { e.preventDefault(); handleSave(); }}>
        
        <div class="space-y-2">
          <Label for="snr-name">Nom du niveau</Label>
          <Input 
            id="snr-name" 
            bind:value={formName} 
            placeholder="ex: JUNIOR, SENIOR, EXPERT..." 
            class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine" 
          />
        </div>


        <div class="space-y-3">
          <Label>Compétences & Exigences</Label>
          
          <div class="flex gap-2">
            <Input 
              placeholder="Ajouter une exigence..." 
              bind:value={newRequirement}
              onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addRequirement())}
              class="h-9 bg-slate-50 border-slate-200 shadow-none focus:bg-white transition-colors"
            />
            <Button variant="secondary" onclick={addRequirement} class="h-9 w-9 p-0 shrink-0">
              <AppIcon name="plus" size={17} />
            </Button>
          </div>

          <div class="flex flex-wrap gap-2 pt-1">
            {#each formRequirements as req}
              <Badge variant="secondary" class="pl-3 pr-1 py-1 gap-1 border-slate-200 bg-slate-100 text-slate-700 font-medium cursor-pointer">
                <AppIcon name="circle-check" size={15} class="text-emerald-500/80" strokeWidth={1.7} />
                <span class="text-[0.82rem]!">{req}</span>
                <button 
                  type="button"
                  onclick={() => removeRequirement(req)}
                  class="h-5 w-5 rounded-full hover:bg-slate-200 flex items-center justify-center transition-colors"
                >
                  <AppIcon name="x" size={12} />
                </button>
              </Badge>
            {:else}
              <p class="text-[0.78rem] text-slate-500 flex items-center justify-center w-full">
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
              min={0}
              bind:value={formRank} 
              class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine" 
            />
          </div>

          <!-- Info Box -->
          <div class="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100/50" in:slide={{ duration: 300 }}>
            <div class="flex gap-3">
              <div class="p-1.5 rounded-lg bg-indigo-100 text-indigo-600 shrink-0 h-fit">
                <AppIcon name="info" size={16} />
              </div>
              <p class="text-[0.78rem] leading-relaxed text-slate-600 font-medium">
                Le rang définit l'ordre d'affichage dans la matrice. Le niveau 1 est généralement le point d'entrée.
              </p>
            </div>
          </div>
        </div>

      </form>
    </div>

    <Sheet.Footer class="p-6 border-t bg-slate-50/30 mt-auto">
      <div class="flex gap-3 w-full">
        <Button 
          type="submit" 
          form="seniority-form" 
          class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine hover:opacity-90 transition-all"
        >
          <AppIcon name="check" size={16} />
          Enregistrer
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

