<script lang="ts">
  import { onboardingStore } from "../../../../stores/onboarding.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import type { Child } from "../../../../types/types";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import * as Select from "@/components/ui/select";
  import { slide } from "svelte/transition";

  interface Props {
    onClose: () => void;
  }

  let { onClose }: Props = $props();

  const genderOptions = [
    { value: "MALE", label: "Masculin" },
    { value: "FEMALE", label: "Féminin" },
    { value: "NOT_SPECIFIED", label: "Non spécifié" }
  ];

  let newChild = $state<Partial<Child>>({
    name: "",
    birthDate: "",
    gender: "NOT_SPECIFIED",
    isDependent: true
  });

  const currentGenderLabel = $derived(
    genderOptions.find(g => g.value === newChild.gender)?.label || "Sélectionner..."
  );

  function addChild() {
    if (!newChild.name || !newChild.birthDate) return;
    
    onboardingStore.addChild({
      id: `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: newChild.name,
      birthDate: newChild.birthDate,
      gender: newChild.gender || "NOT_SPECIFIED",
      isDependent: newChild.isDependent ?? true
    } as Child);
    
    newChild = { name: "", birthDate: "", gender: "NOT_SPECIFIED", isDependent: true };
    onClose();
  }
</script>

<div transition:slide class="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4 mb-6">
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="space-y-1.5">
      <Label class="text-[0.83rem] text-slate-900 font-medium">Nom complet</Label>
      <Input bind:value={newChild.name} placeholder="ex: KIBANGULA MUSUYU Prosper" class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
    </div>
    <div class="space-y-1.5">
      <Label class="text-[0.83rem] text-slate-900 font-medium">Date de naissance</Label>
      <Input bind:value={newChild.birthDate} type="date" class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
    </div>
    <div class="space-y-1.5">
      <Label class="text-[0.83rem] text-slate-900 font-medium">Genre</Label>
      <Select.Root type="single" bind:value={newChild.gender}>
        <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm">
          {currentGenderLabel}
        </Select.Trigger>
        <Select.Content>
          {#each genderOptions as opt}
            <Select.SelectItem value={opt.value} label={opt.label}>
              {opt.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>
    <div class="flex items-end pb-2">
      <div class="flex items-center space-x-2">
        <Checkbox id="isDependent" bind:checked={newChild.isDependent} />
        <Label for="isDependent" class="text-[0.83rem] font-medium leading-none cursor-pointer">Ayant droit (déduction fiscale)</Label>
      </div>
    </div>
  </div>
  <div class="flex justify-end pt-2 gap-2">
    <Button 
      variant="ghost" 
      onclick={onClose} 
      class="h-8 text-[0.8rem] text-slate-500 hover:text-slate-700 hover:bg-slate-100 px-4 flex items-center gap-1.5"
    >
      <AppIcon name="x" size={15} class="text-slate-500" />
      Annuler
    </Button>
    <Button 
      onclick={addChild} 
      disabled={!newChild.name || !newChild.birthDate} 
      size="sm" 
      class="h-8 bg-primary hover:bg-primary/90 text-white px-6 shadow-fine flex items-center gap-1.5"
    >
      <AppIcon name="plus" size={15} />
      Ajouter
    </Button>
  </div>
</div>
