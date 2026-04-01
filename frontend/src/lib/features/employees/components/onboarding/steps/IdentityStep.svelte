<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";

</script>


{#snippet fieldGroup(id: string, label: string, placeholder: string, type = "text", value: any)}
  <div class="space-y-1.5">
    <Label {id} class="text-[0.83rem] text-slate-900 font-medium">
      {label}
    </Label>
    <Input 
      {id} 
      {type}
      {placeholder} 
      bind:value={onboardingStore.data.identity[id as keyof typeof onboardingStore.data.identity]}
      class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
    />
  </div>
{/snippet}


<Card class="border-slate-200 shadow-none rounded-none py-0">
  <CardHeader class="px-0 pt-0">
    <CardTitle class="text-md font-bold text-slate-900 tracking-tight">
      Informations personnelles
    </CardTitle>
    <CardDescription class="text-[0.835rem]">Configurez le poste, le département et les conditions contractuelles.</CardDescription>
  </CardHeader>
  <CardContent class="px-0 py-0 space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
      {@render fieldGroup("name", "Nom complet", "ex: Jean Dupont", "text", onboardingStore.data.identity.name)}
      {@render fieldGroup("email", "Email professionnel", "j.dupont@entreprise.com", "email", onboardingStore.data.identity.email)}
      {@render fieldGroup("phone", "Téléphone", "+243 810 000 000", "text", onboardingStore.data.identity.phone)}
      {@render fieldGroup("birthDate", "Date de naissance", "", "date", onboardingStore.data.identity.birthDate)}
    </div>
  </CardContent>
</Card>

