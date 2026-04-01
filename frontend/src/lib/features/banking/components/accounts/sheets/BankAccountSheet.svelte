<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { bankingStore } from "../../../stores/banking.svelte";
  import { toast } from "svelte-sonner";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import type { BankAccount, Currency, AccountType } from "../../../types/types";

  let { open = $bindable(false), account = $bindable(null) }: { open: boolean, account: BankAccount | null } = $props();

  let formData = $state({
    employeeId: 0,
    institutionId: "",
    accountName: "Compte Courant",
    accountNumber: "",
    iban: "",
    swift: "",
    currency: "USD" as Currency,
    type: "checking" as AccountType,
    isPrimary: true
  });

  // Load account data for editing
  $effect(() => {
    if (account) {
      formData = {
        employeeId: account.employeeId,
        institutionId: account.institutionId,
        accountName: account.accountName,
        accountNumber: account.accountNumber,
        iban: account.iban || "",
        swift: account.swift || "",
        currency: account.currency,
        type: account.type,
        isPrimary: account.isPrimary
      };
    } else {
      resetForm();
    }
  });

  const selectedEmployee = $derived(employeeStore.employees.find(e => e.id === formData.employeeId));
  const selectedInstitution = $derived(bankingStore.institutions.find(i => i.id === formData.institutionId));

  function resetForm() {
    formData = {
      employeeId: 0,
      institutionId: "",
      accountName: "Compte Courant",
      accountNumber: "",
      iban: "",
      swift: "",
      currency: "USD",
      type: "checking",
      isPrimary: true
    };
  }

  function handleSubmit() {
    if (!formData.employeeId || !formData.institutionId || !formData.accountNumber) {
      toast.error("Veuillez remplir tous les champs obligatoires");
      return;
    }

    const payload = {
      ...formData,
      employeeName: selectedEmployee?.name || ""
    };

    if (account) {
      bankingStore.updateAccount(account.id, payload);
      toast.success("Compte bancaire mis à jour");
    } else {
      bankingStore.addAccount(payload);
      toast.success("Compte bancaire ajouté");
    }

    open = false;
    account = null;
    resetForm();
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md p-0 overflow-hidden flex flex-col bg-white h-full">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900 text-left">
        {account ? "Modifier le Compte" : "Nouveau Compte Bancaire"}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
      <!-- Section 1: Propriétaire -->
      <div class="space-y-4">
        <h3 class="text-[0.65rem] font-bold uppercase tracking-widest text-slate-400">Titulaire</h3>
        
        <div class="space-y-2">
          <Label for="employee-trigger" class="text-[0.875rem] font-medium text-slate-700">Employé <span class="text-rose-500">*</span></Label>
          <Select.Root 
            type="single" 
            value={formData.employeeId ? formData.employeeId.toString() : ""}
            onValueChange={(v) => formData.employeeId = parseInt(v)}
          >
            <Select.Trigger id="employee-trigger" class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem] cursor-pointer">
              <div class="flex items-center gap-2">
                {#if selectedEmployee}
                  <Avatar class="h-5 w-5 rounded-full border border-slate-200">
                    <AvatarImage src={selectedEmployee.avatarUrl} />
                    <AvatarFallback class={cn("text-[0.5rem] font-bold", getAvatarPalette(selectedEmployee.name).bg, getAvatarPalette(selectedEmployee.name).text)}>
                      {getInitials(selectedEmployee.name)}
                    </AvatarFallback>
                  </Avatar>
                  <span class="text-[0.875rem] text-slate-800 font-medium">{selectedEmployee.name}</span>
                {:else}
                  <span class="text-slate-400 text-[0.87rem]">Sélectionner un employé...</span>
                {/if}
              </div>
            </Select.Trigger>
            <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
              {#each employeeStore.employees as emp}
                <Select.Item value={emp.id.toString()} label={emp.name}>
                   <div class="flex items-center gap-2">
                    <Avatar class="h-5 w-5 rounded-full border border-slate-200">
                      <AvatarImage src={emp.avatarUrl} />
                      <AvatarFallback class={cn("text-[0.5rem] font-bold", getAvatarPalette(emp.name).bg, getAvatarPalette(emp.name).text)}>
                        {getInitials(emp.name)}
                      </AvatarFallback>
                    </Avatar>
                    <span class="text-[0.875rem]">{emp.name}</span>
                  </div>
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>
      </div>

      <!-- Section 2: Institution -->
      <div class="space-y-4">
        <h3 class="text-[0.65rem] font-bold uppercase tracking-widest text-slate-400">Institution</h3>
        
        <div class="space-y-2">
          <Label for="bank" class="text-[0.875rem] font-medium text-slate-700">Service <span class="text-rose-500">*</span></Label>
          <Select.Root type="single" bind:value={formData.institutionId}>
            <Select.Trigger id="bank" class="w-full h-10 border-slate-200 bg-white shadow-fine text-[0.875rem] font-normal">
              {selectedInstitution?.name || "Séléctionnez une banque"}
            </Select.Trigger>
            <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
              {#each bankingStore.institutions as bank}
                <Select.Item value={bank.id} label={bank.name}>{bank.name}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-[0.875rem] font-medium text-slate-700">Devise</Label>
            <Select.Root type="single" bind:value={formData.currency}>
              <Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine uppercase text-[0.875rem] font-normal">{formData.currency}</Select.Trigger>
              <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
                <Select.Item value="USD" label="USD">USD</Select.Item>
                <Select.Item value="CDF" label="CDF">CDF</Select.Item>
                <Select.Item value="EUR" label="EUR">EUR</Select.Item>
              </Select.Content>
            </Select.Root>
          </div>
           <div class="space-y-2">
            <Label class="text-[0.875rem] font-medium text-slate-700">Type</Label>
            <Select.Root type="single" bind:value={formData.type}>
              <Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine flex items-center gap-2 text-[0.875rem] font-normal">
                {formData.type === 'checking' ? 'Courant' : formData.type === 'savings' ? 'Épargne' : 'M-Money'}
              </Select.Trigger>
              <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
                <Select.Item value="checking" label="Courant">Courant</Select.Item>
                <Select.Item value="savings" label="Épargne">Épargne</Select.Item>
                <Select.Item value="mobile_money" label="Mobile Money">Mobile Money</Select.Item>
              </Select.Content>
            </Select.Root>
          </div>
        </div>
      </div>

      <!-- Section 3: Coordonnées -->
      <div class="space-y-4">
        <h3 class="text-[0.65rem] font-bold uppercase tracking-widest text-slate-400">Coordonnées</h3>
        
        <div class="space-y-2">
            <Label for="accNum" class="text-[0.875rem] font-medium text-slate-700">Numéro de Compte <span class="text-rose-500">*</span></Label>
            <Input id="accNum" bind:value={formData.accountNumber} placeholder="Ex: 0001234567..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
        </div>

        <div class="space-y-2">
            <Label for="iban" class="text-[0.875rem] font-medium text-slate-700">IBAN (Optionnel)</Label>
            <Input id="iban" bind:value={formData.iban} placeholder="Ex: CD01..." class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      <Button 
        onclick={handleSubmit}
        class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer"
      >
        <AppIcon name="check" size={18} />
        {account ? "Mettre à jour" : "Enregistrer"}
      </Button>
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer" onclick={() => account = null}>
          Annuler
        </Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

