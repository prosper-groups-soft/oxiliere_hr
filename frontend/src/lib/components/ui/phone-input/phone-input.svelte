<script lang="ts">
  import { Input } from '../input';
  import { Label } from '../label';
  import * as Select from '../select';
  import { 
    PHONE_PREFIXES, 
    DEFAULT_PREFIX, 
    formatPhoneNumber, 
    validatePhoneNumber, 
    type PhonePrefix 
  } from '@/hr/employees/constants/phone-prefixes';
  import ValidationError from '../validation-error';

  interface Props {
    id: string;
    label: string;
    placeholder?: string;
    value: string;
    onChange: (value: string) => void;
    errors?: Record<string, string>;
    class?: string;
    labelClass?: string;
    inputClass?: string;
  }

  let { 
    id, 
    label, 
    placeholder = 'Numéro de téléphone', 
    value, 
    onChange, 
    errors = {},
    class: className = '',
    labelClass = '',
    inputClass = ''
  }: Props = $props();

  // État local
  let selectedPrefix = $state<PhonePrefix>(DEFAULT_PREFIX);
  let phoneNumber = $state('');
  let isDropdownOpen = $state(false);

  // Synchronisation : Valeur externe -> État interne
  $effect(() => {
    if (value) {
      const foundPrefix = PHONE_PREFIXES.find(prefix => value.startsWith(prefix.code));
      if (foundPrefix) {
        selectedPrefix = foundPrefix;
        phoneNumber = value.replace(foundPrefix.code, '').trim();
      } else {
        phoneNumber = value.replace(/\D/g, '');
      }
    } else {
      phoneNumber = '';
    }
  });

  // Synchronisation : État interne -> Valeur externe
  $effect(() => {
    const fullNumber = phoneNumber ? `${selectedPrefix.code} ${phoneNumber}` : '';
    // On n'appelle onChange que si la valeur a réellement changé pour éviter les boucles
    if (fullNumber !== value) {
      onChange(fullNumber);
    }
  });

  function handlePhoneInput(e: Event) {
    const target = e.target as HTMLInputElement;
    let input = target.value.replace(/\D/g, ''); 
    
    input = input.slice(0, selectedPrefix.maxLength);
    phoneNumber = formatPhoneNumber(input, selectedPrefix);
  }

  function handlePrefixChange(prefixCode: string) {
    const newPrefix = PHONE_PREFIXES.find(p => p.code === prefixCode) || DEFAULT_PREFIX;
    
    let currentNumber = phoneNumber.replace(/\D/g, '');
    if (currentNumber.length > newPrefix.maxLength) {
      currentNumber = currentNumber.slice(0, newPrefix.maxLength);
      phoneNumber = formatPhoneNumber(currentNumber, newPrefix);
    }
    
    selectedPrefix = newPrefix;
    isDropdownOpen = false;
  }

  const isValid = $derived(
    phoneNumber && validatePhoneNumber(phoneNumber.replace(/\D/g, ''), selectedPrefix)
  );
</script>


<div class="space-y-1.5 {className}">
  <Label for={id} class="text-[0.84rem] text-slate-900 font-medium {labelClass}">
    {label}
  </Label>
  
  <div class="flex items-start gap-2">
    <!-- Sélecteur de préfixe -->
    <Select.Root 
      type="single" 
      value={selectedPrefix.code} 
      onValueChange={handlePrefixChange}
      open={isDropdownOpen}
      onOpenChange={(open) => isDropdownOpen = open}
    >
      <Select.Trigger class="h-10 py-2 w-24 shrink-0 border-slate-200 shadow-fine font-normal text-sm cursor-pointer flex items-center gap-1 bg-white">
        <span class="text-lg leading-none">{selectedPrefix.flag}</span>
        <span class="text-sm">{selectedPrefix.code}</span>
      </Select.Trigger>
      
      <Select.Content class="max-h-60 w-48 z-100">
        {#each PHONE_PREFIXES as prefix}
          <Select.SelectItem value={prefix.code} class="cursor-pointer">
            <div class="flex items-center gap-2">
              <span class="text-lg">{prefix.flag}</span>
              <div class="flex flex-col">
                <span class="text-sm font-medium">{prefix.code}</span>
                <span class="text-[0.85rem] text-slate-500 leading-tight">{prefix.name}</span>
              </div>
            </div>
          </Select.SelectItem>
        {/each}
      </Select.Content>
    </Select.Root>

    <!-- Champ de numéro -->
    <div class="flex-1 relative">
      <Input
        {id}
        type="tel"
        placeholder={placeholder}
        value={phoneNumber}
        oninput={handlePhoneInput}
        class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine pr-10 {inputClass}"
      />
      
      <!-- Indicateurs visuels (Validation) -->
      <div class="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center">
        {#if phoneNumber}
          {#if isValid}
            <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
          {:else}
            <svg class="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
          {/if}
        {/if}
      </div>
    </div>
  </div>
  
  <div class="flex justify-between items-center">
    <ValidationError {errors} field={id} />
    
    {#if selectedPrefix}
      <p class="text-[0.77rem] text-slate-400">
        Format: {selectedPrefix.maxLength} chiffres
      </p>
    {/if}
  </div>
</div>

