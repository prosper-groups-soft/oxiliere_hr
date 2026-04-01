<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { jobsStore } from "@/features/jobs/stores/jobs.svelte";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";


  // Get real departments from store
  const departments = $derived(
    jobsStore.departments.map(d => ({ value: d.id, label: d.name }))
  );

  // Get positions filtered by selected department
  const positions = $derived(() => {
    const deptId = onboardingStore.data.contract.departmentId;
    if (!deptId) return [];
    return jobsStore.positions
      .filter(p => p.departmentId === deptId)
      .map(p => ({ value: p.id, label: p.title }));
  });

  const contractTypes = [
    { value: "Permanent", label: "CDI (Permanent)" },
    { value: "Fixed-term", label: "CDD (Déterminé)" },
    { value: "Freelance", label: "Freelance" },
    { value: "Internship", label: "Stage" },
    { value: "Apprenticeship", label: "Alternance" }
  ];

  // Handle department change to update the labels and clear position on mismatch
  $effect(() => {
    const deptId = onboardingStore.data.contract.departmentId;
    if (deptId) {
      const dept = jobsStore.getDepartmentById(deptId);
      if (dept) {
        onboardingStore.updateContract({ department: dept.name });
        
        // Clear position if it doesn't belong to the new department
        const currentPosId = onboardingStore.data.contract.positionId;
        if (currentPosId) {
          const pos = jobsStore.positions.find(p => p.id === currentPosId);
          if (pos && pos.departmentId !== deptId) {
            onboardingStore.updateContract({ positionId: "", jobTitle: "" });
          }
        }
      }
    }
  });

  // Handle position change to update title label
  $effect(() => {
    const posId = onboardingStore.data.contract.positionId;
    if (posId) {
      const pos = jobsStore.positions.find(p => p.id === posId);
      if (pos) {
        onboardingStore.updateContract({ jobTitle: pos.title });
      }
    }
  });
</script>


{#snippet inputGroup(id: string, label: string, placeholder: string, type = "text", className: string = "")}
  <div class="space-y-1.5 {className}">
    <Label {id} class="text-[0.83rem] text-slate-900 font-medium">{label}</Label>
    <div class="relative">
      <Input 
        {id} 
        {type}
        {placeholder} 
        bind:value={onboardingStore.data.contract[id as keyof typeof onboardingStore.data.contract]}
        class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine {id === 'salary' ? 'pr-10' : ''}"
      />
      {#if id === 'salary'}
        <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-medium text-xs">$</span>
      {/if}
    </div>
  </div>
{/snippet}


{#snippet selectGroup(id: string, label: string, options: {value: string, label: string}[])}
  {@const currentVal = onboardingStore.data.contract[id as keyof typeof onboardingStore.data.contract] as string}
  <div class="space-y-1.5">
    <Label class="text-[0.83rem] text-slate-900 font-medium">{label}</Label>
    <Select.Root type="single" bind:value={onboardingStore.data.contract[id as keyof typeof onboardingStore.data.contract] as string}>
      <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm">
        {options.find(o => o.value === currentVal)?.label ?? "Sélectionner..."}
      </Select.Trigger>
      <Select.Content>
        {#each options as opt}
          <Select.SelectItem value={opt.value} label={opt.label}>
            {opt.label}
          </Select.SelectItem>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>
{/snippet}


<Card class="border-slate-200 shadow-none rounded-none border-0 py-0">
  <CardHeader class="px-0 pt-0">
    <CardTitle class="text-md font-bold text-slate-900 tracking-tight">
      Détails du contrat
    </CardTitle>
    <CardDescription class="text-[0.835rem]">Configurez le poste, le département et les conditions contractuelles.</CardDescription>
  </CardHeader>
  <CardContent class="px-0 py-0 space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
      {@render selectGroup("departmentId", "Département", departments)}
      {@render selectGroup("positionId", "Poste", positions())}
      {@render selectGroup("contractType", "Type de contrat", contractTypes)}
      {@render inputGroup("startDate", "Date de début", "", "date")}
      {@render inputGroup("salary", "Salaire annuel (net)", "0000", "number")}
    </div>
  </CardContent>
</Card>

