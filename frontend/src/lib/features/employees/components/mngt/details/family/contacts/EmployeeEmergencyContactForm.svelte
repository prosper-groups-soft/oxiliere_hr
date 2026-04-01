<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import { toast } from "@/utilities/ui/toast";
  import type { EmergencyContact } from "@/features/employees/types/types";

  let { onSave, initialData = null } = $props<{ 
    onSave: (contact: Omit<EmergencyContact, 'id'>) => void,
    initialData?: EmergencyContact | null 
  }>();

  let name = $state("");
  let relation = $state("");
  let phone = $state("");
  let primary = $state(false);

  $effect(() => {
    name = initialData?.name ?? "";
    relation = initialData?.relation ?? "";
    phone = initialData?.phone ?? "";
    primary = initialData?.primary ?? false;
  });

  function handleSubmit() {
    if (!name || !relation || !phone) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }
    onSave({ name, relation, phone, primary });
    toast.success(initialData ? `${name} a été mis à jour.` : `${name} a été ajouté aux contacts d'urgence.`);
    
    if (!initialData) {
      name = "";
      relation = "";
      phone = "";
      primary = false;
    }
  }
</script>


<form id="contact-form" class="space-y-6" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
  <div class="space-y-2">
    <Label for="contact-name">Nom complet</Label>
    <Input id="contact-name" bind:value={name} placeholder="Prénom Nom" class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="space-y-2">
    <Label for="contact-relation">Relation</Label>
    <Input id="contact-relation" bind:value={relation} placeholder="Ex: Époux, Soeur, Ami" class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="space-y-2">
    <Label for="contact-phone">Téléphone</Label>
    <Input id="contact-phone" type="tel" bind:value={phone} placeholder="+243 6 ..." class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="flex items-center space-x-3 bg-slate-50 p-3 rounded-lg border border-slate-100">
    <Checkbox id="contact-primary" bind:checked={primary} />
    <Label for="contact-primary" class="text-sm font-medium leading-none cursor-pointer flex-1">
      Contact d'urgence principal
      <p class="text-[0.85rem] text-muted-foreground font-normal mt-1">Sera affiché en priorité sur le profil.</p>
    </Label>
  </div>
</form>

