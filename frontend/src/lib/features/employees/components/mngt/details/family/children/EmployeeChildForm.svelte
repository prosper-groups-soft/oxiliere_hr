<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { toast } from "@/utilities/ui/toast";
  import type { Child } from "@/features/employees/types/types";

  let { onSave, initialData = null } = $props<{ 
    onSave: (child: Omit<Child, 'id'>) => void,
    initialData?: Child | null 
  }>();

  let name = $state("");
  let birthDate = $state("");
  let gender = $state("M");

  $effect(() => {
    name = initialData?.name ?? "";
    birthDate = initialData?.birthDate ?? "";
    gender = initialData?.gender ?? "M";
  });

  function handleSubmit() {
    if (!name || !birthDate) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }
    onSave({ name, birthDate, gender });
    toast.success(initialData ? `${name} a été mis à jour.` : `${name} a été ajouté avec succès.`);
    
    if (!initialData) {
      name = "";
      birthDate = "";
    }
  }
</script>


<form id="child-form" class="space-y-6" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
  <div class="space-y-2">
    <Label for="child-name">Nom complet</Label>
    <Input id="child-name" bind:value={name} placeholder="Prénom Nom" class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="space-y-2">
    <Label for="child-birthdate">Date de naissance</Label>
    <Input id="child-birthdate" type="date" bind:value={birthDate} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="space-y-2">
    <Label>Genre</Label>
    <div class="flex gap-4">
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="radio" value="M" bind:group={gender} class="w-4 h-4 text-primary" />
        <span class="text-sm">Masculin</span>
      </label>
      <label class="flex items-center gap-2 cursor-pointer">
        <input type="radio" value="F" bind:group={gender} class="w-4 h-4 text-primary" />
        <span class="text-sm">Féminin</span>
      </label>
    </div>
  </div>
</form>

