<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { toast } from "@/utilities/ui/toast";
  import type { Employee } from '@/features/employees/types/types';

  let { employee, onSave } = $props<{ 
    employee: Employee; 
    onSave: (data: Partial<Employee>) => void 
  }>();

  let name = $state("");
  let email = $state("");
  let phone = $state("");
  let jobTitle = $state("");
  let department = $state("");

  $effect(() => {
    name = employee.name;
    email = employee.email;
    phone = employee.phone || "";
    jobTitle = employee.jobTitle || "";
    department = employee.department;
  });

  function handleSubmit() {
    onSave({ name, email, phone, jobTitle, department });
    toast.success("Profil mis à jour avec succès.");
  }
</script>


<form id="profile-form" class="space-y-6" onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
  <div class="space-y-2">
    <Label for="emp-name">Nom complet</Label>
    <Input id="emp-name" bind:value={name} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="space-y-2">
      <Label for="emp-email">Email Professionnel</Label>
      <Input id="emp-email" type="email" bind:value={email} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
    </div>
    <div class="space-y-2">
      <Label for="emp-phone">Téléphone</Label>
      <Input id="emp-phone" type="tel" bind:value={phone} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
    </div>
  </div>

  <div class="space-y-2">
    <Label for="emp-job">Poste / Intitulé</Label>
    <Input id="emp-job" bind:value={jobTitle} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>

  <div class="space-y-2">
    <Label for="emp-dept">Département</Label>
    <Input id="emp-dept" bind:value={department} class="h-9.5 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" />
  </div>
</form>

