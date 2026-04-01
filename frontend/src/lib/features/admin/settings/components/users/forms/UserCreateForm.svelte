<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import type { CreateUserInput } from "../../../types/user.types";
  import { USER_ROLES } from "../../../types/user.types";

  interface Props {
    formData?: CreateUserInput;
    onSubmit?: () => void;
  }

  let { formData = $bindable<CreateUserInput>({
    email: '',
    firstName: '',
    lastName: '',
    role: 'EMPLOYEE',
    department: '',
    phone: ''
  }), onSubmit }: Props = $props();

  let errors = $state<Partial<Record<keyof CreateUserInput, string>>>({});

  function validate(): boolean {
    errors = {};

    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Email invalide';
    }
    if (!formData.firstName || formData.firstName.length < 2) {
      errors.firstName = 'Prénom requis (min 2 caractères)';
    }
    if (!formData.lastName || formData.lastName.length < 2) {
      errors.lastName = 'Nom requis (min 2 caractères)';
    }

    return Object.keys(errors).length === 0;
  }

  function handleSubmit() {
    if (validate()) {
      onSubmit?.();
    }
  }

  const departments = [
    'Direction',
    'Ressources Humaines',
    'Finance',
    'Production',
    'Commercial',
    'Administration',
    'IT',
    'Logistique'
  ];
</script>


<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
  <!-- Email -->
  <div class="space-y-1.5">
    <Label for="email" class="text-[0.84rem]">Email <span class="text-red-500">*</span></Label>
    <Input
      id="email"
      type="email"
      bind:value={formData.email}
      placeholder="utilisateur@oxiliere.com"
      class="h-9.5 flex-1 text-[0.84rem] {errors.email ? 'border-red-300' : ''} shadow-fine"
    />
    {#if errors.email}
      <p class="text-[0.75rem] text-red-500">{errors.email}</p>
    {/if}
  </div>

  <!-- Names -->
  <div class="grid grid-cols-2 gap-3">
    <div class="space-y-1.5">
      <Label for="firstName" class="text-[0.84rem]">Prénom <span class="text-red-500">*</span></Label>
      <Input
        id="firstName"
        bind:value={formData.firstName}
        placeholder="Jean"
        class="h-9.5 flex-1 text-[0.84rem] {errors.firstName ? 'border-red-300' : ''} shadow-fine"
      />
      {#if errors.firstName}
        <p class="text-[0.75rem] text-red-500">{errors.firstName}</p>
      {/if}
    </div>
    <div class="space-y-1.5">
      <Label for="lastName" class="text-[0.84rem]">Nom <span class="text-red-500">*</span></Label>
      <Input
        id="lastName"
        bind:value={formData.lastName}
        placeholder="Mbuyi"
        class="h-9.5 flex-1 text-[0.84rem] {errors.lastName ? 'border-red-300' : ''} shadow-fine"
      />
      {#if errors.lastName}
        <p class="text-[0.75rem] text-red-500">{errors.lastName}</p>
      {/if}
    </div>
  </div>

  <!-- Role -->
  <div class="space-y-1.5">
    <Label for="role" class="text-[0.84rem]">Rôle <span class="text-red-500">*</span></Label>
    <Select.Root type="single" bind:value={formData.role}>
      <Select.Trigger id="role" class="h-9.5 w-full shadow-fine cursor-pointer text-[0.85rem]">
        {USER_ROLES.find(r => r.role === formData.role)?.label || 'Sélectionner un rôle'}
      </Select.Trigger>
      <Select.Content class="z-100 shadow-fine">
        {#each USER_ROLES as role}
          <Select.Item value={role.role} class="text-[0.85rem]">{role.label}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
    {#if formData.role}
      <p class="text-[0.75rem] text-slate-500">
        {USER_ROLES.find(r => r.role === formData.role)?.description}
      </p>
    {/if}
  </div>

  <!-- Department -->
  <div class="space-y-1.5">
    <Label for="department" class="text-[0.8rem]">Département</Label>
    <Select.Root type="single" bind:value={formData.department}>
      <Select.Trigger id="department" class="h-9.5 w-full shadow-fine text-[0.85rem] cursor-pointer">
        {formData.department || 'Non assigné'}
      </Select.Trigger>
      <Select.Content class="z-100 shadow-fine">
        <Select.Item value="">Non assigné</Select.Item>
        {#each departments as dept}
          <Select.Item value={dept} class="text-[0.84rem]">{dept}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
  </div>

  <!-- Phone -->
  <div class="space-y-1.5">
    <Label for="phone" class="text-[0.8rem]">Téléphone</Label>
    <Input
      id="phone"
      bind:value={formData.phone}
      placeholder="+243 81 234 5678"
      class="h-9.5 flex-1 text-[0.84rem] shadow-fine"
    />
  </div>
</form>

