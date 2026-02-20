<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { 
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
  } from "@/components/ui/select";
  import { toast } from "@/utilities/ui/toast";
  import type { Document } from "@/features/employees/types/types";

  // On définit les props
  let { onSave, initialData = null } = $props<{ 
    onSave: (doc: Omit<Document, 'id'>) => void,
    initialData?: Document | null 
  }>();

  // État local du formulaire
  let name = $state("");
  let type = $state("PDF");
  let expiry = $state<string | null>(null);
  let size = $state("0 KB");

  // On synchronise l'état si on est en mode édition
  $effect(() => {
    name = initialData?.name ?? "";
    type = initialData?.type ?? "PDF";
    expiry = initialData?.expiry ?? null;
    size = initialData?.size ?? "0 KB";
  });


  const documentTypes = [
    { value: "PDF", label: "Document PDF" },
    { value: "JPG", label: "Image JPG" },
    { value: "PNG", label: "Image PNG" },
    { value: "DOC", label: "Document Word" },
    { value: "OTHER", label: "Autre" }
  ];


  const currentTypeLabel = $derived(
    documentTypes.find(t => t.value === type)?.label ?? "Choisir le type"
  );

  // La fonction qui sera appelée lors de la soumission du formulaire
  function handleSubmit(e: Event) {
    e.preventDefault(); // Empêche le rechargement de la page

    if (!name || !type) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    onSave({
      name,
      type,
      expiry,
      size,
      status: 'valid'
    });
    
    toast.success(initialData ? "Document mis à jour" : "Document ajouté au coffre-fort");
  }
</script>


<form id="document-form" onsubmit={handleSubmit} class="space-y-5 py-4">
  <div class="space-y-2">
    <Label for="doc-name">Nom du document</Label>
    <Input 
      id="doc-name" 
      bind:value={name} 
      placeholder="Ex: Contrat de travail, Passeport..." 
      required
    />
  </div>

  <div class="space-y-2">
    <Label class="text-sm">Type de fichier</Label>
    <Select type="single" bind:value={type}>
      <SelectTrigger class="h-10 w-100">
        <span class="truncate text-sm">{currentTypeLabel}</span>
      </SelectTrigger>
      <SelectContent>
        {#each documentTypes as docType}
          <SelectItem value={docType.value} class="text-sm">
            {docType.label}
          </SelectItem>
        {/each}
      </SelectContent>
    </Select>
  </div>

  <div class="space-y-2">
    <Label for="doc-expiry">Date d'expiration (optionnel)</Label>
    <Input id="doc-expiry" type="date" bind:value={expiry} />
  </div>
</form>

